from __future__ import annotations

from content import render_content_template, render_page_nav, replace_placeholders
from settings import CATEGORY_TITLES, PARTIALS_DIR, ROOT_INDEX_MD, ROSETTA_INDEX_MD, SCHEMA_PATH, SPEC_INDEX_MD, SPEC_INDEX_SOURCE
from utils import fenced_block, github_edit_url, profile_href, rel_link, render_data_for_markdown


def render_profiles_table(example_ids, examples, page_path):
    rows = []
    for example_id in example_ids:
        example = examples[example_id]
        example_path = ROOT_INDEX_MD.parent / example.output_relpath_md
        example_href = rel_link(page_path, example_path)
        for system_name, system in sorted(example.systems.items()):
            for output in system.outputs.values():
                namespaces = output.namespaces or [{"name": "", "url": "", "version": ""}]
                for namespace in namespaces:
                    namespace_name = namespace["name"] or system_name
                    version = namespace["version"] or "unspecified"
                    url = namespace["url"]
                    profile_label = namespace_name
                    if url:
                        profile_label = f"[{namespace_name}]({url})"
                    rows.append(
                        f"| {profile_label} | `{version}` | [{example.title}]({example_href}) | `{output.root_type or ''}` |"
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
            for output in system.outputs.values():
                root_type = output.root_type
                if output.data_file is not None and examples[example_id].spec_ids and spec_id in examples[example_id].spec_ids and root_type:
                    from settings import TYPE_SPEC_BY_ROOT_TYPE
                    if TYPE_SPEC_BY_ROOT_TYPE.get(root_type) == spec_id:
                        return render_data_for_markdown(output.data_file)
    return None


def render_page_profiles(profile_ids, profile_catalog, page_path):
    if not profile_ids:
        return ""
    if page_path.name == "profiles.md" and page_path.parent.name == "core":
        return ""

    profiles_path = profile_href(page_path)
    links = []
    for profile_id in profile_ids:
        profile = profile_catalog[profile_id]
        links.append(f"[{profile.title}]({profiles_path}#{profile_id})")
    return f"**Profiles:** {', '.join(links)}"


def render_profile_definitions(profile_catalog, spec_catalog, examples, page_path):
    lines = []
    for profile_id, profile in profile_catalog.items():
        lines.append(f"<a id=\"{profile_id}\"></a>")
        lines.append(f"## {profile.title}")
        lines.append("")
        lines.append(profile.description)
        lines.append("")
        lines.append(f"- Identifier: `{profile.id}`")
        lines.append(f"- Kind: {profile.kind}")
        lines.append(f"- Status: {profile.status}")
        if profile.released_on:
            lines.append(f"- Released on: {profile.released_on}")
        if profile.based_on:
            based_on_links = []
            for base_id in profile.based_on:
                base = profile_catalog[base_id]
                based_on_links.append(f"[{base.title}](#{base_id})")
            lines.append(f"- Based on: {', '.join(based_on_links)}")
        else:
            lines.append("- Based on: none")
        lines.append("")
        if profile.spec_ids:
            lines.append("### Directly Documented Pages")
            lines.append("")
            for spec_id in profile.spec_ids:
                spec_page = spec_catalog[spec_id]
                lines.append(f"- [{spec_page.title}]({rel_link(page_path, spec_page.path_md)})")
            lines.append("")
        if profile.example_ids:
            lines.append("### Direct Example Pages")
            lines.append("")
            for example_id in profile.example_ids:
                example = examples[example_id]
                example_path = ROOT_INDEX_MD.parent / example.output_relpath_md
                lines.append(f"- [{example.title}]({rel_link(page_path, example_path)})")
            lines.append("")
    return "\n".join(lines).rstrip()


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
                ],
                edit_link=("Edit this page", github_edit_url(SPEC_INDEX_SOURCE)),
                active_label="Specification",
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


def render_spec_placeholders(body, spec_page, examples, page_path, profile_catalog, spec_catalog):
    return replace_placeholders(
        body,
        {
            "CANONICAL_EXAMPLE_PAYLOAD": render_spec_sample(spec_page, examples),
            "DOCUMENTED_PROFILES": render_spec_profiles(spec_page, examples, page_path),
            "ROSETTA_EXAMPLES": render_spec_examples(spec_page, examples, page_path),
            "PROFILE_DEFINITIONS": render_profile_definitions(
                profile_catalog,
                spec_catalog,
                examples,
                page_path,
            ),
        },
    )


def build_spec_page_markdown(spec_page, examples, profile_catalog, spec_catalog):
    page_path = spec_page.path_md
    lines = [
        render_page_nav(
            [
                ("Front Page", rel_link(page_path, ROOT_INDEX_MD)),
                ("Specification", rel_link(page_path, SPEC_INDEX_MD)),
                ("Rosetta Stone", rel_link(page_path, ROSETTA_INDEX_MD)),
            ],
            edit_link=("Edit this page", github_edit_url(spec_page.source_path)),
            active_label="Specification",
        ),
        f"# Specification: {spec_page.title}",
        "",
        render_page_profiles(spec_page.profiles, profile_catalog, page_path),
        "",
        render_spec_placeholders(
            spec_page.body,
            spec_page,
            examples,
            page_path,
            profile_catalog,
            spec_catalog,
        ),
    ]
    return "\n".join(lines).rstrip() + "\n"
