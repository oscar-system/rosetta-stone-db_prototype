from __future__ import annotations

from pathlib import Path
import re


def parse_description(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    metadata: dict[str, str] = {}
    body = text

    if text.startswith("---\n"):
        parts = text.split("\n---\n", 1)
        if len(parts) == 2:
            header_block = parts[0][4:]
            body = parts[1]
            for line in header_block.splitlines():
                if ":" not in line:
                    continue
                key, value = line.split(":", 1)
                metadata[key.strip()] = value.strip()

    return metadata, body.lstrip()


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
) -> str:
    items = [f'<a href="{href}">{label}</a>' for label, href in links]
    if edit_link is not None:
        label, href = edit_link
        items.append(f'<a class="page-nav-edit" href="{href}">{label}</a>')
    return '<div class="page-nav">' + "".join(items) + "</div>\n"
