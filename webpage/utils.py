from __future__ import annotations

import json
import os
import re
from pathlib import Path
from urllib.parse import quote

from settings import GITHUB_EDIT_BASE, LANGUAGE_BY_SUFFIX, ROOT


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower())
    return slug.strip("-")


def rel_link(from_path: Path, to_path: Path) -> str:
    return os.path.relpath(to_path, start=from_path.parent).replace(os.sep, "/")


def github_edit_url(path: Path) -> str:
    relpath = path.resolve().relative_to(ROOT).as_posix()
    return GITHUB_EDIT_BASE + quote(relpath, safe="/")


def profile_href(from_path: Path) -> str:
    return rel_link(from_path, ROOT / "_site" / "spec" / "core" / "profiles.md")


def language_for_file(path: Path) -> str:
    return LANGUAGE_BY_SUFFIX.get(path.suffix, "")


def fenced_block(content: str, language: str) -> str:
    fence = "```"
    if "```" in content:
        fence = "````"
    return f"{fence}{language}\n{content.rstrip()}\n{fence}"


def format_json_compact(value, indent_size: int = 2, max_width: int = 100) -> str:
    def inline_repr(obj):
        return json.dumps(obj, ensure_ascii=False, separators=(", ", ": "))

    def format_node(obj, level):
        current_indent = " " * (indent_size * level)
        next_indent = " " * (indent_size * (level + 1))

        if not isinstance(obj, (list, dict)):
            return json.dumps(obj, ensure_ascii=False)

        inline = inline_repr(obj)
        if len(current_indent) + len(inline) <= max_width:
            return inline

        if isinstance(obj, list):
            if not obj:
                return "[]"
            entries = []
            for item in obj:
                item_repr = format_node(item, level + 1)
                item_lines = item_repr.splitlines()
                entry = [next_indent + item_lines[0]]
                for line in item_lines[1:]:
                    if line.startswith(next_indent):
                        line = line[len(next_indent):]
                    entry.append(next_indent + line)
                entries.append("\n".join(entry))
            return "[\n" + ",\n".join(entries) + "\n" + current_indent + "]"

        if not obj:
            return "{}"

        entries = []
        for key, item in obj.items():
            item_repr = format_node(item, level + 1)
            item_lines = item_repr.splitlines()
            key_prefix = next_indent + json.dumps(key, ensure_ascii=False) + ": "
            if len(item_lines) == 1:
                entries.append(key_prefix + item_lines[0])
                continue
            entry_lines = [key_prefix + item_lines[0]]
            for line in item_lines[1:]:
                if line.startswith(next_indent):
                    line = line[len(next_indent):]
                entry_lines.append(next_indent + line)
            entries.append("\n".join(entry_lines))
        return "{\n" + ",\n".join(entries) + "\n" + current_indent + "}"

    return format_node(value, 0)


def render_data_for_markdown(path: Path) -> str:
    raw = path.read_text(encoding="utf-8")
    if path.suffix in {".json", ".mrdi"}:
        try:
            parsed = json.loads(raw)
            return format_json_compact(parsed, indent_size=2, max_width=100)
        except json.JSONDecodeError:
            return raw
    return raw
