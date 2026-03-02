from __future__ import annotations

from html import escape
from html.parser import HTMLParser
import re
from urllib.parse import urlsplit, urlunsplit

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

    def render_link(self, element):
        template = '<a href="{}"{}>{}</a>'
        title = f' title="{self.escape_html(element.title)}"' if element.title else ""
        url = self.escape_url(rewrite_link_target(element.dest))
        body = self.render_children(element)
        return template.format(url, title, body)

    def render_image(self, element):
        template = '<img src="{}" alt="{}"{} />'
        title = f' title="{self.escape_html(element.title)}"' if element.title else ""
        url = self.escape_url(rewrite_link_target(element.dest))
        render_func = self.render
        self.render = self.render_plain_text  # type: ignore
        body = self.render_children(element)
        self.render = render_func  # type: ignore
        return template.format(url, body, title)


def rewrite_link_target(target: str) -> str:
    if not target:
        return target

    parts = urlsplit(target)
    if parts.scheme or parts.netloc or target.startswith(("#", "/")):
        return target

    path = parts.path
    if path.endswith(".md"):
        path = f"{path[:-3]}.html"

    return urlunsplit((parts.scheme, parts.netloc, path, parts.query, parts.fragment))


class RawHtmlLinkRewriter(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.parts: list[str] = []

    def handle_starttag(self, tag, attrs):
        self.parts.append(self._render_tag(tag, attrs, closing=False))

    def handle_startendtag(self, tag, attrs):
        self.parts.append(self._render_tag(tag, attrs, closing=True))

    def handle_endtag(self, tag):
        self.parts.append(f"</{tag}>")

    def handle_data(self, data):
        self.parts.append(data)

    def handle_entityref(self, name):
        self.parts.append(f"&{name};")

    def handle_charref(self, name):
        self.parts.append(f"&#{name};")

    def handle_comment(self, data):
        self.parts.append(f"<!--{data}-->")

    def handle_decl(self, decl):
        self.parts.append(f"<!{decl}>")

    def handle_pi(self, data):
        self.parts.append(f"<?{data}>")

    def unknown_decl(self, data):
        self.parts.append(f"<![{data}]>")

    def _render_tag(self, tag, attrs, closing):
        rendered_attrs = []
        for name, value in attrs:
            if value is None:
                rendered_attrs.append(name)
                continue
            if name in {"href", "src"}:
                value = rewrite_link_target(value)
            rendered_attrs.append(f'{name}="{escape(value, quote=True)}"')
        attrs_suffix = f" {' '.join(rendered_attrs)}" if rendered_attrs else ""
        ending = " /" if closing else ""
        return f"<{tag}{attrs_suffix}{ending}>"


def rewrite_html_links(html_text: str) -> str:
    parser = RawHtmlLinkRewriter()
    parser.feed(html_text)
    parser.close()
    return "".join(parser.parts)


def protect_math_segments(text: str) -> tuple[str, dict[str, str]]:
    replacements: dict[str, str] = {}
    patterns = [
        re.compile(r"\$\$.*?\$\$", flags=re.DOTALL),
        re.compile(r"\\\[.*?\\\]", flags=re.DOTALL),
        re.compile(r"\\\(.*?\\\)", flags=re.DOTALL),
    ]

    def replace(match):
        token = f"@@MATH{len(replacements)}@@"
        replacements[token] = escape(match.group(0), quote=False)
        return token

    protected = text
    for pattern in patterns:
        protected = pattern.sub(replace, protected)
    return protected, replacements


def restore_math_segments(text: str, replacements: dict[str, str]) -> str:
    restored = text
    for token, original in replacements.items():
        restored = restored.replace(token, original)
    return restored


def markdown_to_html(md_text: str) -> str:
    text = md_text
    nav_html = ""
    nav_match = re.match(r'(<div class="page-nav">.*?</div>\n+)', text, flags=re.DOTALL)
    if nav_match:
        nav_html = nav_match.group(1)
        text = text[nav_match.end():].lstrip("\n")
    text, math_replacements = protect_math_segments(text)
    renderer = marko.Markdown(renderer=HeadingIdRenderer, extensions=["gfm"])
    html = nav_html + renderer.convert(text)
    html = restore_math_segments(html, math_replacements)
    return rewrite_html_links(html)


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
