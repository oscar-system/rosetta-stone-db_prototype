from __future__ import annotations

import re
import marko
from marko.html_renderer import HTMLRenderer

from content import load_text
from settings import TEMPLATE_PATH
from utils import slugify


def _heading_plain_text(node):
    if isinstance(node, str):
        return node
    if isinstance(node, list):
        return "".join(_heading_plain_text(child) for child in node)
    children = getattr(node, "children", None)
    if children is None:
        return ""
    return _heading_plain_text(children)


class HeadingIdRenderer(HTMLRenderer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._heading_id_counts = {}

    def render_heading(self, element):
        rendered = self.render_children(element)
        text = _heading_plain_text(getattr(element, "children", "")).strip()
        base = slugify(text) or f"h{element.level}"
        count = self._heading_id_counts.get(base, 0) + 1
        self._heading_id_counts[base] = count
        heading_id = base if count == 1 else f"{base}-{count}"
        return f'<h{element.level} id="{heading_id}">{rendered}</h{element.level}>\n'


def rewrite_markdown_links(md_text: str) -> str:
    pattern = re.compile(r"(\[[^\]]+\]\()([^)]+)\)")
    href_pattern = re.compile(r'(href=")([^"\s]+)(")')

    def rewrite_target(target: str) -> str:
        if "://" in target or target.startswith(("#", "/")):
            return target
        if ".md" in target:
            return re.sub(r"\.md(?=(#|$))", ".html", target)
        return target

    def replace_link(match):
        prefix = match.group(1)
        target = match.group(2)
        target = rewrite_target(target)
        return f"{prefix}{target})"

    def replace_href(match):
        prefix = match.group(1)
        target = match.group(2)
        suffix = match.group(3)
        target = rewrite_target(target)
        return f"{prefix}{target}{suffix}"

    return href_pattern.sub(replace_href, pattern.sub(replace_link, md_text))


def markdown_to_html(md_text: str) -> str:
    text = rewrite_markdown_links(md_text)
    nav_html = ""
    nav_match = re.match(r'(<div class="page-nav">.*?</div>\n+)', text, flags=re.DOTALL)
    if nav_match:
        nav_html = nav_match.group(1)
        text = text[nav_match.end():].lstrip("\n")
    renderer = marko.Markdown(renderer=HeadingIdRenderer, extensions=["gfm"])
    return nav_html + renderer.convert(text)


def extract_title(md_text: str, fallback: str) -> str:
    for line in md_text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    match = re.search(r"<h1>(.*?)</h1>", md_text, flags=re.IGNORECASE | re.DOTALL)
    if match:
        return re.sub(r"<[^>]+>", "", match.group(1)).strip() or fallback
    return fallback


def render_html_page(md_path):
    md_text = md_path.read_text(encoding="utf-8")
    content_html = markdown_to_html(md_text)
    title = extract_title(md_text, md_path.stem)
    full_html = load_text(TEMPLATE_PATH)
    full_html = full_html.replace("{{ title }}", title)
    full_html = full_html.replace("{{ content }}", content_html)
    html_path = md_path.with_suffix(".html")
    html_path.write_text(full_html, encoding="utf-8")
    print(f"Wrote {html_path}")
