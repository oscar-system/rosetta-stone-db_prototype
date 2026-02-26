#!/usr/bin/env python3
from pathlib import Path
import re
import html

ROOT = Path(__file__).parent.parent
DESCRIPTIONS_DIR = ROOT / "example_descriptions"
SYSTEMS_DIR = ROOT / "systems"
SITE_DIR = ROOT / "_site"
INDEX_MD = SITE_DIR / "index.md"

LANGUAGE_BY_SUFFIX = {
    ".jl": "julia",
    ".pl": "perl",
    ".sh": "bash",
    ".json": "json",
    ".lp": "text",
    ".ine": "text",
    ".md": "markdown",
}

HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title}</title>
  <script>
    MathJax = {{
      tex: {{
        inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
        displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']]
      }}
    }};
  </script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.11.1/styles/github.min.css" />
  <script defer src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.11.1/highlight.min.js"></script>
  <script>
    window.addEventListener("DOMContentLoaded", function () {{
      if (window.hljs) {{
        window.hljs.highlightAll();
      }}
    }});
  </script>
  <script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
  <style>
    body {{
      margin: 0;
      padding: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #fafaf9;
      color: #1a1a1a;
      line-height: 1.5;
    }}
    main {{
      max-width: 1000px;
      margin: 2rem auto;
      background: white;
      padding: 2rem;
      border: 1px solid #e5e5e5;
      border-radius: 10px;
    }}
    pre {{
      overflow-x: auto;
      padding: 1rem;
      border-radius: 6px;
    }}
    code {{
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    }}
    table {{
      border-collapse: collapse;
      width: 100%;
    }}
    th, td {{
      border: 1px solid #ddd;
      padding: 0.4rem 0.6rem;
      text-align: left;
      vertical-align: top;
    }}
    a {{
      color: #0b57d0;
    }}
  </style>
</head>
<body>
  <main>
{content}
  </main>
</body>
</html>
"""


def parse_description(path):
    text = path.read_text(encoding="utf-8")
    metadata = {}
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


def discover_examples():
    examples = {}
    for path in sorted(DESCRIPTIONS_DIR.glob("*.md")):
        metadata, body = parse_description(path)
        examples[path.stem] = {
            "id": path.stem,
            "path": path,
            "title": metadata.get("title", path.stem),
            "body": body,
        }
    return examples


def discover_system_examples():
    systems = {}
    for system_dir in sorted(path for path in SYSTEMS_DIR.iterdir() if path.is_dir()):
        examples = {}
        for example_dir in sorted(path for path in system_dir.iterdir() if path.is_dir()):
            data_file = next((p for p in sorted(example_dir.iterdir()) if p.name.startswith("data.")), None)
            generate_file = next((p for p in sorted(example_dir.iterdir()) if p.name.startswith("generate.")), None)
            examples[example_dir.name] = {
                "path": example_dir,
                "data_file": data_file,
                "generate_file": generate_file,
            }
        systems[system_dir.name] = examples
    return systems


def language_for_file(path):
    return LANGUAGE_BY_SUFFIX.get(path.suffix, "")


def fenced_block(content, language):
    fence = "```"
    if "```" in content:
        fence = "````"
    return f"{fence}{language}\n{content.rstrip()}\n{fence}"


def slugify(value):
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower())
    return slug.strip("-")


def build_index_markdown(examples, systems):
    system_names = sorted(systems.keys())
    lines = [
        "# Rosetta Stone Overview",
        "",
        "| Example | " + " | ".join(system_names) + " |",
        "| --- | " + " | ".join("---" for _ in system_names) + " |",
    ]

    for example_id in sorted(examples.keys()):
        title = examples[example_id]["title"]
        row = [f"[{title}](./{example_id}.md)"]
        for system_name in system_names:
            if example_id in systems[system_name]:
                anchor = slugify(system_name)
                row.append(f"[X](./{example_id}.md#{anchor})")
            else:
                row.append("")
        lines.append("| " + " | ".join(row) + " |")

    lines.append("")
    return "\n".join(lines)


def build_example_markdown(example, systems):
    body_lines = example["body"].splitlines()
    if body_lines and body_lines[0].startswith("# "):
        body = "\n".join(body_lines[1:]).lstrip()
    else:
        body = example["body"].rstrip()

    lines = [
        f"# {example['title']}",
        "",
        "[Back to index](./index.md)",
        "",
        body,
        "",
        "## Systems",
        "",
    ]

    for system_name in sorted(systems.keys()):
        lines.append(f'<a id="{slugify(system_name)}"></a>')
        lines.append("")
        lines.append(f"### {system_name}")
        lines.append("")

        system_example = systems[system_name].get(example["id"])
        if system_example is None:
            lines.append("Example not available for this system")
            lines.append("")
            continue

        generate_file = system_example["generate_file"]
        data_file = system_example["data_file"]

        if generate_file is not None:
            lines.append(f"#### Generate code (`{generate_file.name}`)")
            lines.append("")
            code = generate_file.read_text(encoding="utf-8")
            lines.append(fenced_block(code, language_for_file(generate_file)))
            lines.append("")

        if data_file is not None:
            lines.append(f"#### Data file (`{data_file.name}`)")
            lines.append("")
            data = data_file.read_text(encoding="utf-8")
            lines.append(fenced_block(data, language_for_file(data_file)))
            lines.append("")

        if generate_file is None and data_file is None:
            lines.append("No generator or data file available for this system")
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def rewrite_markdown_links(md_text):
    pattern = re.compile(r"(\[[^\]]+\]\()(\./[^)\s]+)\)")

    def replace_link(match):
        prefix = match.group(1)
        target = match.group(2)
        if ".md" in target:
            target = re.sub(r"\.md(?=(#|$))", ".html", target)
        return f"{prefix}{target})"

    return pattern.sub(replace_link, md_text)


def escape_inline(text):
    escaped = html.escape(text, quote=False)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', escaped)
    return escaped


def render_table(table_lines):
    rows = []
    for line in table_lines:
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        parts = [cell.strip() for cell in stripped.strip("|").split("|")]
        rows.append(parts)

    if len(rows) < 2:
        return "\n".join(f"<p>{escape_inline(line)}</p>" for line in table_lines)

    headers = rows[0]
    body_rows = rows[2:] if len(rows) > 2 else []
    header_html = "".join(f"<th>{escape_inline(cell)}</th>" for cell in headers)
    body_html = []
    for row in body_rows:
        body_cells = "".join(f"<td>{escape_inline(cell)}</td>" for cell in row)
        body_html.append(f"<tr>{body_cells}</tr>")

    return (
        "<table>\n"
        f"<thead><tr>{header_html}</tr></thead>\n"
        f"<tbody>{''.join(body_html)}</tbody>\n"
        "</table>"
    )


def markdown_to_html(md_text):
    text = rewrite_markdown_links(md_text)
    lines = text.splitlines()
    out = []
    paragraph = []
    in_code = False
    code_lang = ""
    code_lines = []
    table_lines = []

    def flush_paragraph():
        nonlocal paragraph
        if paragraph:
            joined = " ".join(part.strip() for part in paragraph if part.strip())
            if joined:
                out.append(f"<p>{escape_inline(joined)}</p>")
            paragraph = []

    def flush_table():
        nonlocal table_lines
        if table_lines:
            out.append(render_table(table_lines))
            table_lines = []

    for line in lines:
        stripped = line.strip()

        if in_code:
            if stripped.startswith("```"):
                code = html.escape("\n".join(code_lines), quote=False)
                klass = f' class="language-{code_lang}"' if code_lang else ""
                out.append(f"<pre><code{klass}>{code}</code></pre>")
                in_code = False
                code_lang = ""
                code_lines = []
            else:
                code_lines.append(line)
            continue

        if stripped.startswith("```"):
            flush_paragraph()
            flush_table()
            in_code = True
            code_lang = stripped[3:].strip()
            code_lines = []
            continue

        if stripped.startswith("|"):
            flush_paragraph()
            table_lines.append(line)
            continue
        else:
            flush_table()

        if not stripped:
            flush_paragraph()
            continue

        if stripped.startswith("<") and stripped.endswith(">"):
            flush_paragraph()
            out.append(line)
            continue

        heading_match = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if heading_match:
            flush_paragraph()
            level = len(heading_match.group(1))
            content = escape_inline(heading_match.group(2).strip())
            out.append(f"<h{level}>{content}</h{level}>")
            continue

        paragraph.append(line)

    flush_paragraph()
    flush_table()
    return "\n".join(out)


def extract_title(md_text, fallback):
    for line in md_text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def render_html_page(md_path):
    md_text = md_path.read_text(encoding="utf-8")
    content_html = markdown_to_html(md_text)
    title = extract_title(md_text, md_path.stem)
    full_html = HTML_TEMPLATE.format(title=title, content=content_html)
    html_path = md_path.with_suffix(".html")
    html_path.write_text(full_html, encoding="utf-8")
    print(f"Wrote {html_path}")


def main():
    examples = discover_examples()
    systems = discover_system_examples()

    SITE_DIR.mkdir(parents=True, exist_ok=True)
    INDEX_MD.write_text(build_index_markdown(examples, systems), encoding="utf-8")

    for example_id in sorted(examples.keys()):
        example_page_path = SITE_DIR / f"{example_id}.md"
        page_content = build_example_markdown(examples[example_id], systems)
        example_page_path.write_text(page_content, encoding="utf-8")
        print(f"Wrote {example_page_path}")

    print(f"Wrote {INDEX_MD}")

    for md_path in sorted(SITE_DIR.glob("*.md")):
        render_html_page(md_path)


if __name__ == "__main__":
    main()
