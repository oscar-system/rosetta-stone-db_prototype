#!/usr/bin/env python3
from pathlib import Path
import re

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
        body,
        "",
        "## Systems",
        "",
    ]

    for system_name in sorted(systems.keys()):
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


if __name__ == "__main__":
    main()
