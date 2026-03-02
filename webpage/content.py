from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


FrontmatterValue = str | list[str]


@dataclass(frozen=True)
class FrontmatterEntry:
    value: FrontmatterValue
    line: int


@dataclass(frozen=True)
class Frontmatter:
    path: Path
    entries: dict[str, FrontmatterEntry]

    def get(self, key: str) -> FrontmatterValue | None:
        entry = self.entries.get(key)
        if entry is None:
            return None
        return entry.value

    @staticmethod
    def _value_description(value: object) -> str:
        if isinstance(value, list):
            return "a list"
        if isinstance(value, str):
            return "a string"
        return f"a {type(value).__name__}"

    def require_str(self, key: str, default: str | None = None) -> str:
        value = self.get(key)
        if value is None:
            if default is not None:
                return default
            raise ValueError(f"Error, missing '{key}' value in {self.path}")
        if isinstance(value, str):
            return value
        raise ValueError(
            f"Error, unsupported '{key}' value in {self.path}:{self.line_for(key)}: "
            f"expected a string, got {self._value_description(value)}"
        )

    def optional_str(self, key: str) -> str | None:
        value = self.get(key)
        if value is None:
            return None
        if isinstance(value, str):
            return value
        raise ValueError(
            f"Error, unsupported '{key}' value in {self.path}:{self.line_for(key)}: "
            f"expected a string, got {self._value_description(value)}"
        )

    def str_list(self, key: str) -> list[str]:
        value = self.get(key)
        if value is None:
            return []
        if isinstance(value, list):
            return list(value)
        raise ValueError(
            f"Error, unsupported '{key}' value in {self.path}:{self.line_for(key)}: "
            f"expected a list, got {self._value_description(value)}"
        )

    def optional_int(self, key: str) -> int | None:
        value = self.get(key)
        if value is None:
            return None
        if not isinstance(value, str):
            raise ValueError(
                f"Error, unsupported '{key}' value in {self.path}:{self.line_for(key)}: "
                f"expected an integer, got {self._value_description(value)}"
            )
        try:
            return int(value)
        except ValueError as exc:
            raise ValueError(
                f"Error, unsupported '{key}' value in {self.path}:{self.line_for(key)}: "
                f"expected an integer, got {value!r}"
            ) from exc

    def line_for(self, key: str) -> int:
        entry = self.entries.get(key)
        if entry is None:
            raise KeyError(key)
        return entry.line


def parse_description(path: Path) -> tuple[Frontmatter, str]:
    text = path.read_text(encoding="utf-8")
    entries: dict[str, FrontmatterEntry] = {}
    body = text

    if text.startswith("---\n"):
        parts = text.split("\n---\n", 1)
        if len(parts) == 2:
            header_block = parts[0][4:]
            body = parts[1]
            for line_number, line in enumerate(header_block.splitlines(), start=2):
                if ":" not in line:
                    continue
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()
                if value.startswith("[") and value.endswith("]"):
                    items = [
                        item.strip().strip("'\"")
                        for item in value[1:-1].split(",")
                        if item.strip()
                    ]
                    entries[key] = FrontmatterEntry(value=items, line=line_number)
                else:
                    entries[key] = FrontmatterEntry(value=value, line=line_number)

    return Frontmatter(path=path, entries=entries), body.lstrip()


def load_markdown_source(path: Path) -> str:
    return path.read_text(encoding="utf-8").rstrip() + "\n"


def replace_placeholders(text: str, replacements: dict[str, str]) -> str:
    rendered = text
    for key, value in replacements.items():
        rendered = rendered.replace(f"{{{{ {key} }}}}", value)
    return re.sub(r"\n{3,}", "\n\n", rendered).strip() + "\n"


def render_content_template(path: Path, replacements: dict[str, str]) -> str:
    return replace_placeholders(load_markdown_source(path), replacements)


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def render_page_nav(
    links: list[tuple[str, str]],
    edit_link: tuple[str, str] | None = None,
    active_label: str | None = None,
) -> str:
    items = []
    for label, href in links:
        classes = []
        if label == active_label:
            classes.append("page-nav-active")
        class_attr = f' class="{" ".join(classes)}"' if classes else ""
        items.append(f'<a{class_attr} href="{href}">{label}</a>')
    if edit_link is not None:
        label, href = edit_link
        items.append(f'<a class="page-nav-edit" href="{href}">{label}</a>')
    return '<div class="page-nav">' + "".join(items) + "</div>\n"
