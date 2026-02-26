#!/usr/bin/env python3
from pathlib import Path
import re
import html
import json

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
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
  <script defer src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.11.1/languages/julia.min.js"></script>
  <script>
    window.addEventListener("DOMContentLoaded", function () {{
      document.querySelectorAll("pre > code").forEach(function (codeBlock) {{
        var pre = codeBlock.parentElement;
        if (!pre || pre.querySelector(".copy-code-btn")) {{
          return;
        }}
        var button = document.createElement("button");
        button.type = "button";
        button.className = "copy-code-btn";
        button.textContent = "Copy";
        button.addEventListener("click", function () {{
          navigator.clipboard.writeText(codeBlock.textContent || "").then(function () {{
            button.textContent = "Copied";
            setTimeout(function () {{ button.textContent = "Copy"; }}, 1200);
          }});
        }});
        pre.appendChild(button);
      }});

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
      position: relative;
      background: #f3f4f6;
    }}
    .copy-code-btn {{
      position: absolute;
      top: 0.5rem;
      right: 0.5rem;
      border: 1px solid #c9c9c9;
      background: #fff;
      color: #222;
      border-radius: 4px;
      font-size: 0.75rem;
      padding: 0.2rem 0.5rem;
      cursor: pointer;
    }}
    .copy-code-btn:hover {{
      background: #f2f2f2;
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
    for group_dir in sorted(path for path in DATA_DIR.iterdir() if path.is_dir()):
        group_id = group_dir.name
        for example_dir in sorted(path for path in group_dir.iterdir() if path.is_dir()):
            description_path = example_dir / "description.md"
            if not description_path.exists():
                continue

            metadata, body = parse_description(description_path)
            example_slug = example_dir.name
            example_id = f"{group_id}-{example_slug}"

            systems = {}
            systems_root = example_dir / "systems"
            if systems_root.exists():
                for system_dir in sorted(path for path in systems_root.iterdir() if path.is_dir()):
                    data_file = next((p for p in sorted(system_dir.iterdir()) if p.name.startswith("data.")), None)
                    generate_file = next((p for p in sorted(system_dir.iterdir()) if p.name.startswith("generate.")), None)
                    systems[system_dir.name] = {
                        "path": system_dir,
                        "data_file": data_file,
                        "generate_file": generate_file,
                    }

            examples[example_id] = {
                "id": example_id,
                "slug": example_slug,
                "output_relpath_md": f"{group_id}/{example_slug}.md",
                "path": description_path,
                "title": metadata.get("title", example_slug),
                "category": metadata.get("category", metadata.get("group", group_id)),
                "subcategory": metadata.get("subcategory"),
                "body": body,
                "systems": systems,
            }
    return examples


def build_system_index(examples):
    systems = {}
    for example_id, example in examples.items():
        for system_name, files in example["systems"].items():
            systems.setdefault(system_name, {})
            systems[system_name][example_id] = files
    return systems


def language_for_file(path):
    return LANGUAGE_BY_SUFFIX.get(path.suffix, "")


def fenced_block(content, language):
    fence = "```"
    if "```" in content:
        fence = "````"
    return f"{fence}{language}\n{content.rstrip()}\n{fence}"


def render_data_for_markdown(path):
    raw = path.read_text(encoding="utf-8")
    if path.suffix == ".json":
        try:
            parsed = json.loads(raw)
            return format_json_compact(parsed, indent_size=2, max_width=100)
        except json.JSONDecodeError:
            return raw
    return raw


def format_json_compact(value, indent_size=2, max_width=100):
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


def slugify(value):
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower())
    return slug.strip("-")


def build_index_markdown(examples, systems):
    system_names = sorted(systems.keys())
    group_titles = {
        "basics": "Basics",
        "rings": "Rings",
        "linear-algebra": "Linear Algebra",
        "groups": "Groups",
        "polyhedral": "Polyhedral Geometry",
    }
    group_order = {
        "basics": 0,
        "rings": 1,
        "linear-algebra": 2,
        "groups": 3,
        "polyhedral": 4,
    }
    subgroup_titles = {
        "abelian": "Abelian Groups",
        "permutation": "Permutation Groups",
        "free": "Free Groups",
        "fp": "Finitely Presented Groups",
        "pc": "Pc Groups",
        "__other__": "Other",
    }
    subgroup_order = {
        "groups": {
            "abelian": 0,
            "permutation": 1,
            "free": 2,
            "fp": 3,
            "pc": 4,
            "__other__": 99,
        }
    }
    lines = [
        "# Rosetta Stone Overview",
        "",
    ]

    grouped_examples = {}
    for example_id, example in examples.items():
        grouped_examples.setdefault(example["category"], []).append(example_id)

    sorted_groups = sorted(
        grouped_examples.keys(),
        key=lambda name: (group_order.get(name, 999), name.lower()),
    )

    for group_id in sorted_groups:
        display_name = group_titles.get(group_id, group_id.replace("-", " ").title())
        lines.append(f"## {display_name}")
        lines.append("")
        group_examples = grouped_examples[group_id]

        # Optional subgrouping within a category (currently used for Groups).
        subgrouped = {}
        for example_id in group_examples:
            sub = examples[example_id].get("subcategory") or "__other__"
            subgrouped.setdefault(sub, []).append(example_id)

        ordered_subgroups = sorted(
            subgrouped.keys(),
            key=lambda sub: (subgroup_order.get(group_id, {}).get(sub, 999), sub.lower()),
        )

        for sub in ordered_subgroups:
            if len(ordered_subgroups) > 1:
                lines.append(f"### {subgroup_titles.get(sub, sub.replace('-', ' ').title())}")
                lines.append("")

            lines.append("| Example | " + " | ".join(system_names) + " |")
            lines.append("| --- | " + " | ".join("---" for _ in system_names) + " |")

            sub_examples = sorted(
                subgrouped[sub],
                key=lambda exid: examples[exid]["title"].lower(),
            )
            for example_id in sub_examples:
                example = examples[example_id]
                title = example["title"]
                relpath = example["output_relpath_md"]
                row = [f"[{title}](./{relpath})"]
                for system_name in system_names:
                    if example_id in systems[system_name]:
                        anchor = slugify(system_name)
                        row.append(f"[X](./{relpath}#{anchor})")
                    else:
                        row.append("")
                lines.append("| " + " | ".join(row) + " |")
            lines.append("")

    lines.append("")
    return "\n".join(lines)


def build_example_markdown(example, systems):
    body_lines = example["body"].splitlines()
    if body_lines and body_lines[0].startswith("# "):
        body = "\n".join(body_lines[1:]).lstrip()
    else:
        body = example["body"].rstrip()

    available_systems = [
        system_name
        for system_name in sorted(systems.keys())
        if example["id"] in systems[system_name]
    ]

    lines = [
        f"# {example['title']}",
        "",
        "[Back to index](../index.md)",
        "",
        body,
        "",
        "## Systems",
        "",
    ]

    for system_name in available_systems:
        lines.append(f'<a id="{slugify(system_name)}"></a>')
        lines.append("")
        lines.append(f"### {system_name}")
        lines.append("")

        system_example = systems[system_name].get(example["id"])
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
            data = render_data_for_markdown(data_file)
            lines.append(fenced_block(data, language_for_file(data_file)))
            lines.append("")

        if generate_file is None and data_file is None:
            lines.append("No generator or data file available for this system")
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def rewrite_markdown_links(md_text):
    pattern = re.compile(r"(\[[^\]]+\]\()((?:\./|\.\./)[^)\s]+)\)")

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
    systems = build_system_index(examples)

    SITE_DIR.mkdir(parents=True, exist_ok=True)
    for old_file in SITE_DIR.rglob("*"):
        if old_file.is_file() and old_file.suffix in {".md", ".html"}:
            old_file.unlink()

    INDEX_MD.write_text(build_index_markdown(examples, systems), encoding="utf-8")

    for example_id in sorted(examples.keys()):
        example_page_path = SITE_DIR / examples[example_id]["output_relpath_md"]
        example_page_path.parent.mkdir(parents=True, exist_ok=True)
        page_content = build_example_markdown(examples[example_id], systems)
        example_page_path.write_text(page_content, encoding="utf-8")
        print(f"Wrote {example_page_path}")

    print(f"Wrote {INDEX_MD}")

    for md_path in sorted(SITE_DIR.rglob("*.md")):
        render_html_page(md_path)


if __name__ == "__main__":
    main()
