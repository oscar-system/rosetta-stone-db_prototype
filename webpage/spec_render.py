from __future__ import annotations

from html import escape

from content import render_content_template, render_page_nav, replace_placeholders
from settings import CATEGORY_TITLES, PARTIALS_DIR, PROFILE_ORDER, ROOT_INDEX_MD, ROSETTA_INDEX_MD, SCHEMA_PATH, SPEC_INDEX_MD, SPEC_INDEX_SOURCE, resolve_type_spec
from utils import fenced_block, github_edit_url, profile_href, rel_link, render_data_for_markdown


def output_profile_sort_key(output):
    if output.profile_id is None:
        return (10_000, "")
    return (PROFILE_ORDER.get(output.profile_id, 10_000), output.profile_id)


def render_profiles_table(example_ids, examples, page_path):
    spec_id = page_path.relative_to(page_path.parents[1]).with_suffix("").as_posix()
    rows = []
    for example_id in example_ids:
        example = examples[example_id]
        example_path = ROOT_INDEX_MD.parent / example.output_relpath_md
        example_href = rel_link(page_path, example_path)
        for system_name, system in sorted(example.systems.items()):
            for output in sorted(system.outputs.values(), key=output_profile_sort_key):
                if resolve_type_spec(output.root_type, output.profile_id) != spec_id:
                    continue
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

    rows.sort()
    return [
        "| Profile | Version | Example | Root type |",
        "| --- | --- | --- | --- |",
        *rows,
        "",
    ]


def sample_payload_for_spec(spec_id, example_ids, examples):
    candidates = []
    for example_id in example_ids:
        example = examples[example_id]
        for system in example.systems.values():
            for output in system.outputs.values():
                root_type = output.root_type
                if output.data_file is not None and examples[example_id].spec_ids and spec_id in examples[example_id].spec_ids and root_type:
                    if resolve_type_spec(root_type, output.profile_id) == spec_id:
                        candidates.append(output)

    if not candidates:
        return None

    best_output = max(candidates, key=output_profile_sort_key)
    return render_data_for_markdown(best_output.data_file)


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


def render_other_versions(spec_page, spec_catalog, page_path):
    if spec_page.concept_id is None:
        return ""

    related_pages = [
        candidate
        for candidate in spec_catalog.values()
        if candidate.id != spec_page.id and candidate.concept_id == spec_page.concept_id
    ]
    if not related_pages:
        return ""

    related_pages.sort(
        key=lambda candidate: (
            candidate.order if candidate.order is not None else 10_000,
            candidate.title.lower(),
        )
    )
    links = [
        f"[{candidate.title}]({rel_link(page_path, candidate.path_md)})"
        for candidate in related_pages
    ]
    return f"**Other versions:** {', '.join(links)}"


def render_profile_definitions(profile_catalog, spec_catalog, examples, page_path):
    shared_profiles = [
        profile_catalog[profile_id]
        for profile_id in profile_catalog
        if profile_catalog[profile_id].kind != "application"
    ]
    application_profiles = [
        profile_catalog[profile_id]
        for profile_id in profile_catalog
        if profile_catalog[profile_id].kind == "application"
    ]

    sections = []
    for profile in shared_profiles:
        sections.append(render_profile_section_markdown(profile, profile_catalog, spec_catalog, page_path))

    if application_profiles:
        if sections:
            sections.append("")
        sections.append("## OSCAR Profiles")
        sections.append("")
        sections.append(render_application_profile_tabs(application_profiles, profile_catalog, spec_catalog, page_path))

    return "\n".join(sections).rstrip()


def render_profile_section_markdown(profile, profile_catalog, spec_catalog, page_path):
    lines = [f"<a id=\"{profile.id}\"></a>", f"## {profile.title}", "", profile.description, ""]
    lines.extend(render_profile_metadata_lines(profile, profile_catalog))
    lines.append("")
    if profile.spec_ids:
        lines.append("### Directly Documented Pages")
        lines.append("")
        for spec_id in profile.spec_ids:
            spec_page = spec_catalog[spec_id]
            lines.append(f"- [{spec_page.title}]({rel_link(page_path, spec_page.path_md)})")
        lines.append("")
    return "\n".join(lines).rstrip()


def render_profile_metadata_lines(profile, profile_catalog):
    lines = [
        f"- Identifier: `{profile.id}`",
        f"- Kind: {profile.kind}",
        f"- Status: {profile.status}",
    ]
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
    return lines


def render_profile_metadata_html_items(profile, profile_catalog):
    items = [
        f"Identifier: <code>{escape(profile.id)}</code>",
        f"Kind: {escape(profile.kind)}",
        f"Status: {escape(profile.status)}",
    ]
    if profile.released_on:
        items.append(f"Released on: {escape(profile.released_on)}")
    if profile.based_on:
        based_on_links = []
        for base_id in profile.based_on:
            base = profile_catalog[base_id]
            based_on_links.append(f'<a href="#{escape(base_id)}">{escape(base.title)}</a>')
        items.append(f"Based on: {', '.join(based_on_links)}")
    else:
        items.append("Based on: none")
    return items


def render_application_profile_tabs(application_profiles, profile_catalog, spec_catalog, page_path):
    container_id = "tabs_spec_profiles_applications"
    lines = [
        f'<div class="output-tabs" data-tabs id="{container_id}">',
        '<div class="output-tab-list" role="tablist" aria-label="Application profiles">',
    ]

    default_profile = application_profiles[-1]
    for profile in application_profiles:
        button_id = f"{container_id}_tab_{profile.id.replace('-', '_')}"
        default_attr = ' data-tab-default="true"' if profile.id == default_profile.id else ""
        lines.append(
            f'<button type="button" class="output-tab-btn" role="tab" '
            f'id="{button_id}" aria-controls="{profile.id}" '
            f'data-tab-target="{profile.id}" data-tab-hashes="{profile.id}"{default_attr}>'
            f"{escape(profile.title)}</button>"
        )

    lines.append("</div>")

    for profile in application_profiles:
        lines.append(f'<div class="output-tab-panel" role="tabpanel" id="{profile.id}">')
        lines.append(f"<h3>{escape(profile.title)}</h3>")
        lines.append(f"<p>{escape(profile.description)}</p>")
        lines.append("<ul>")
        for item in render_profile_metadata_html_items(profile, profile_catalog):
            lines.append(f"<li>{item}</li>")
        lines.append("</ul>")
        if profile.spec_ids:
            lines.append("<h4>Directly Documented Pages</h4>")
            lines.append("<ul>")
            for spec_id in profile.spec_ids:
                spec_page = spec_catalog[spec_id]
                href = rel_link(page_path, spec_page.path_md)
                lines.append(f'<li><a href="{escape(href)}">{escape(spec_page.title)}</a></li>')
            lines.append("</ul>")
        lines.append("</div>")

    lines.append("</div>")
    return "\n".join(lines)


def build_spec_index_markdown(spec_catalog):
    category_rank = {name: idx for idx, name in enumerate(CATEGORY_TITLES.keys())}
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
            category_rank.get(spec.section, 999),
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
        render_other_versions(spec_page, spec_catalog, page_path),
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
