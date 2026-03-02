from __future__ import annotations

from content import render_content_template, render_page_nav, replace_placeholders
from settings import CATEGORY_TITLES, PARTIALS_DIR, ROOT_INDEX_MD, ROSETTA_INDEX_MD, SCHEMA_PATH, SPEC_INDEX_MD, SPEC_INDEX_SOURCE
from utils import fenced_block, rel_link, render_data_for_markdown


def render_profiles_table(example_ids, examples, page_path):
    rows = []
    for example_id in example_ids:
        example = examples[example_id]
        example_path = ROOT_INDEX_MD.parent / example.output_relpath_md
        example_href = rel_link(page_path, example_path)
        for system_name, system in sorted(example.systems.items()):
            namespaces = system.namespaces or [{"name": "", "url": "", "version": ""}]
            for namespace in namespaces:
                namespace_name = namespace["name"] or system_name
                version = namespace["version"] or "unspecified"
                url = namespace["url"]
                profile_label = namespace_name
                if url:
                    profile_label = f"[{namespace_name}]({url})"
                rows.append(
                    f"| {profile_label} | `{version}` | [{example.title}]({example_href}) | `{system.root_type or ''}` |"
                )

    if not rows:
        return ["No documented profiles yet.", ""]

    return [
        "| Profile | Version | Example | Root type |",
        "| --- | --- | --- | --- |",
        *rows,
        "",
    ]


def sample_payload_for_spec(spec_id, example_ids, examples):
    for example_id in example_ids:
        example = examples[example_id]
        for system in example.systems.values():
            root_type = system.root_type
            if system.data_file is not None and examples[example_id].spec_ids and spec_id in examples[example_id].spec_ids and root_type:
                from settings import TYPE_SPEC_BY_ROOT_TYPE
                if TYPE_SPEC_BY_ROOT_TYPE.get(root_type) == spec_id:
                    return render_data_for_markdown(system.data_file)
    return None


def build_spec_index_markdown(spec_catalog):
    core_pages = sorted(
        (spec for spec in spec_catalog.values() if spec.kind == "core"),
        key=lambda spec: (
            spec.order if spec.order is not None else 10_000,
            spec.title.lower(),
        ),
    )
    type_pages = sorted(
        (spec for spec in spec_catalog.values() if spec.kind != "core"),
        key=lambda spec: (
            spec.section,
            spec.order if spec.order is not None else 10_000,
            spec.title.lower(),
        ),
    )
    core_lines = [f"- [{spec.title}](./{spec.id}.md)" for spec in core_pages]

    type_lines = []
    current_section = None
    for spec in type_pages:
        if spec.section != current_section:
            if current_section is not None:
                type_lines.append("")
            current_section = spec.section
            section_title = (
                CATEGORY_TITLES.get(current_section, current_section.replace("-", " ").title())
                if current_section
                else "Other"
            )
            type_lines.append(f"### {section_title}")
            type_lines.append("")
        type_lines.append(f"- [{spec.title}](./{spec.id}.md)")

    return render_content_template(
        SPEC_INDEX_SOURCE,
        {
            "PAGE_NAV": render_page_nav(
                [
                    ("Front Page", "../index.md"),
                    ("Rosetta Stone", "../rosetta/index.md"),
                ]
            ),
            "CORE_PAGES": "\n".join(core_lines),
            "TYPE_PAGES": "\n".join(type_lines),
            "SCHEMA_BASIS": fenced_block(render_data_for_markdown(SCHEMA_PATH), "json"),
        },
    )


def render_spec_examples(spec_page, examples, page_path):
    if not spec_page.example_ids:
        return ""

    lines = []
    for example_id in spec_page.example_ids:
        example = examples[example_id]
        example_href = rel_link(page_path, ROOT_INDEX_MD.parent / example.output_relpath_md)
        lines.append(f"- [{example.title}]({example_href})")
    return render_content_template(
        PARTIALS_DIR / "spec-examples.md",
        {
            "EXAMPLE_LINKS": "\n".join(lines),
        },
    )


def render_spec_profiles(spec_page, examples, page_path):
    return render_content_template(
        PARTIALS_DIR / "spec-profiles.md",
        {
            "PROFILE_TABLE": "\n".join(render_profiles_table(spec_page.example_ids, examples, page_path)),
        },
    )


def render_spec_sample(spec_page, examples):
    sample = sample_payload_for_spec(spec_page.id, spec_page.example_ids, examples)
    if sample is None:
        return ""

    return render_content_template(
        PARTIALS_DIR / "spec-sample.md",
        {
            "SAMPLE_PAYLOAD": fenced_block(sample, "json"),
        },
    )


def render_spec_placeholders(body, spec_page, examples, page_path):
    return replace_placeholders(
        body,
        {
            "CANONICAL_EXAMPLE_PAYLOAD": render_spec_sample(spec_page, examples),
            "DOCUMENTED_PROFILES": render_spec_profiles(spec_page, examples, page_path),
            "ROSETTA_EXAMPLES": render_spec_examples(spec_page, examples, page_path),
        },
    )


def build_spec_page_markdown(spec_page, examples):
    page_path = spec_page.path_md
    lines = [
        render_page_nav(
            [
                ("Front Page", rel_link(page_path, ROOT_INDEX_MD)),
                ("Specification Index", rel_link(page_path, SPEC_INDEX_MD)),
                ("Rosetta Stone", rel_link(page_path, ROSETTA_INDEX_MD)),
            ]
        ),
        f"# {spec_page.title}",
        "",
        render_spec_placeholders(spec_page.body, spec_page, examples, page_path),
    ]
    return "\n".join(lines).rstrip() + "\n"
