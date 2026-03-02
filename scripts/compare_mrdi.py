#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


class CompareError(Exception):
    pass


@dataclass
class CompareState:
    uuid_map: dict[str, str] = field(default_factory=dict)
    reverse_uuid_map: dict[str, str] = field(default_factory=dict)
    ignore_namespace_versions: bool = False

    def clone(self) -> "CompareState":
        return CompareState(
            uuid_map=dict(self.uuid_map),
            reverse_uuid_map=dict(self.reverse_uuid_map),
            ignore_namespace_versions=self.ignore_namespace_versions,
        )


def is_uuid_string(value: object) -> bool:
    return isinstance(value, str) and UUID_RE.match(value) is not None


def bind_uuid(left: str, right: str, path: str, state: CompareState) -> None:
    mapped_right = state.uuid_map.get(left)
    if mapped_right is not None:
        if mapped_right != right:
            raise CompareError(
                f"{path}: UUID {left!r} was previously matched with "
                f"{mapped_right!r}, not {right!r}"
            )
        return

    mapped_left = state.reverse_uuid_map.get(right)
    if mapped_left is not None and mapped_left != left:
        raise CompareError(
            f"{path}: UUID {right!r} is already matched with {mapped_left!r}, "
            f"so it cannot also match {left!r}"
        )

    state.uuid_map[left] = right
    state.reverse_uuid_map[right] = left


def compare_strings(left: str, right: str, path: str, state: CompareState) -> None:
    if state.ignore_namespace_versions and is_namespace_version_path(path):
        return

    left_is_uuid = is_uuid_string(left)
    right_is_uuid = is_uuid_string(right)
    if left_is_uuid or right_is_uuid:
        if not (left_is_uuid and right_is_uuid):
            raise CompareError(
                f"{path}: expected matching UUID status, got {left!r} and {right!r}"
            )
        bind_uuid(left, right, path, state)
        return

    if left != right:
        raise CompareError(f"{path}: expected {left!r}, got {right!r}")


def is_namespace_version_path(path: str) -> bool:
    if "._ns." not in path:
        return False
    _, namespace_tail = path.rsplit("._ns.", 1)
    if "[" not in namespace_tail:
        return False
    return namespace_tail.endswith("[1]")


def compare_refs_dict(
    left: dict[str, object],
    right: dict[str, object],
    path: str,
    state: CompareState,
) -> None:
    if len(left) != len(right):
        raise CompareError(
            f"{path}: expected {len(left)} reference entries, got {len(right)}"
        )

    unmatched_right = set(right.keys())
    for left_key, left_value in left.items():
        if not isinstance(left_key, str):
            raise CompareError(f"{path}: non-string key {left_key!r} in left refs")

        mapped_key = state.uuid_map.get(left_key)
        if mapped_key is not None:
            if mapped_key not in right:
                raise CompareError(
                    f"{path}: mapped UUID key {mapped_key!r} missing from right refs"
                )
            compare_json(
                left_value,
                right[mapped_key],
                f"{path}.{left_key}",
                state,
            )
            unmatched_right.discard(mapped_key)
            continue

        candidates = sorted(unmatched_right)
        success = False
        last_error = None
        for candidate in candidates:
            candidate_state = state.clone()
            try:
                compare_strings(left_key, candidate, f"{path}.<key>", candidate_state)
                compare_json(
                    left_value,
                    right[candidate],
                    f"{path}.{left_key}",
                    candidate_state,
                )
            except CompareError as exc:
                last_error = exc
                continue

            state.uuid_map = candidate_state.uuid_map
            state.reverse_uuid_map = candidate_state.reverse_uuid_map
            unmatched_right.remove(candidate)
            success = True
            break

        if not success:
            if last_error is not None:
                raise last_error
            raise CompareError(f"{path}: could not match UUID key {left_key!r}")


def compare_dicts(
    left: dict[str, object],
    right: dict[str, object],
    path: str,
    state: CompareState,
) -> None:
    if "_refs" in left or "_refs" in right:
        left_keys = set(left.keys())
        right_keys = set(right.keys())
        if left_keys != right_keys:
            raise CompareError(
                f"{path}: expected keys {sorted(left_keys)!r}, got {sorted(right_keys)!r}"
            )
        for key in sorted(left.keys()):
            child_path = f"{path}.{key}" if path else key
            if key == "_refs":
                if not isinstance(left[key], dict) or not isinstance(right[key], dict):
                    raise CompareError(f"{child_path}: expected dict-valued _refs")
                compare_refs_dict(left[key], right[key], child_path, state)
            else:
                compare_json(left[key], right[key], child_path, state)
        return

    left_keys = set(left.keys())
    right_keys = set(right.keys())
    if left_keys != right_keys:
        raise CompareError(
            f"{path}: expected keys {sorted(left_keys)!r}, got {sorted(right_keys)!r}"
        )

    for key in sorted(left.keys()):
        compare_json(left[key], right[key], f"{path}.{key}" if path else key, state)


def compare_json(left: object, right: object, path: str, state: CompareState) -> None:
    if isinstance(left, str) and isinstance(right, str):
        compare_strings(left, right, path, state)
        return

    if type(left) is not type(right):
        raise CompareError(
            f"{path}: expected type {type(left).__name__}, got {type(right).__name__}"
        )

    if isinstance(left, dict):
        compare_dicts(left, right, path, state)
        return

    if isinstance(left, list):
        if len(left) != len(right):
            raise CompareError(
                f"{path}: expected list length {len(left)}, got {len(right)}"
            )
        for index, (left_item, right_item) in enumerate(zip(left, right)):
            compare_json(left_item, right_item, f"{path}[{index}]", state)
        return

    if left != right:
        raise CompareError(f"{path}: expected {left!r}, got {right!r}")


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def compare_files(
    left_path: Path,
    right_path: Path,
    *,
    ignore_namespace_versions: bool = False,
) -> None:
    left = load_json(left_path)
    right = load_json(right_path)
    compare_json(
        left,
        right,
        "$",
        CompareState(ignore_namespace_versions=ignore_namespace_versions),
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare two .mrdi/.json files up to consistent UUID renaming."
    )
    parser.add_argument("left", type=Path)
    parser.add_argument("right", type=Path)
    parser.add_argument(
        "--ignore-namespace-versions",
        action="store_true",
        help="ignore version strings in _ns entries",
    )
    args = parser.parse_args()

    try:
        compare_files(
            args.left,
            args.right,
            ignore_namespace_versions=args.ignore_namespace_versions,
        )
    except CompareError as exc:
        print(f"NOT EQUIVALENT: {exc}", file=sys.stderr)
        return 1

    print("Equivalent up to UUID renaming.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
