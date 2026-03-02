#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
WEBPAGE_DIR = SCRIPT_DIR.parent / "webpage"
if str(WEBPAGE_DIR) not in sys.path:
    sys.path.insert(0, str(WEBPAGE_DIR))

from mrdi_compare import CompareError, compare_json, CompareState


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
