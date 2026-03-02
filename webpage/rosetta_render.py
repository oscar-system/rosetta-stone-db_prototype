from __future__ import annotations

from html import escape
from pathlib import Path
import re

from content import load_markdown_source, render_content_template, render_page_nav
from mrdi_compare import equivalent_json
from models import ExampleOutput
from settings import (
    CATEGORY_TITLES,
    FRONT_PAGE_SOURCE,
    PARTIALS_DIR,
    PROFILE_ORDER,
    ROOT_INDEX_MD,
    ROSETTA_INDEX_MD,
    ROSETTA_INDEX_SOURCE,
    SPEC_INDEX_MD,
    SUBCATEGORY_TITLES,
)
from utils import fenced_block, github_edit_url, language_for_file, profile_href, rel_link, render_data_for_markdown, slugify


def spec_link_lines(page_path, spec_ids, spec_catalog):
    if not spec_ids:
        return []

    lines = []
    for spec_id in spec_ids:
        spec_page = spec_catalog[spec_id]
        href = rel_link(page_path, spec_page.path_md)
        lines.append(f"- [{spec_page.title}]({href})")
    return render_content_template(
        PARTIALS_DIR / "example-related-spec.md",
        {
            "SPEC_LINKS": "\n".join(lines),
        },
    ).splitlines() + [""]


def profile_lines(page_path, profile_ids, profile_catalog):
    if not profile_ids:
        return []

    profile_page = profile_href(page_path)
    links = []
    for profile_id in profile_ids:
        profile = profile_catalog[profile_id]
        links.append(f"[{profile.title}]({profile_page}#{profile_id})")
    return [f"**Profiles:** {', '.join(links)}", ""]


def build_front_page_markdown():
    return render_content_template(
        FRONT_PAGE_SOURCE,
        {
            "PAGE_NAV": render_page_nav(
                [],
                edit_link=("Edit this page", github_edit_url(FRONT_PAGE_SOURCE)),
            ),
        },
    )


def build_rosetta_index_markdown(examples, systems):
    system_names = sorted(systems.keys())
    category_rank = {name: idx for idx, name in enumerate(CATEGORY_TITLES.keys())}
    subcategory_rank = {
        category: {name: idx for idx, name in enumerate(titles.keys())}
        for category, titles in SUBCATEGORY_TITLES.items()
    }

    grouped_examples: dict[str, list[str]] = {}
    for example_id, example in examples.items():
        grouped_examples.setdefault(example.category, []).append(example_id)

    sorted_groups = sorted(
        grouped_examples.keys(),
        key=lambda name: (category_rank.get(name, 999), name.lower()),
    )

    toc_lines = []
    for group_id in sorted_groups:
        display_name = CATEGORY_TITLES.get(group_id, group_id.replace("-", " ").title())
        toc_lines.append(f"- [{display_name}](#{slugify(display_name)})")

    lines = []
    for group_id in sorted_groups:
        display_name = CATEGORY_TITLES.get(group_id, group_id.replace("-", " ").title())
        lines.append(f"## {display_name}")
        lines.append("")
        group_examples = grouped_examples[group_id]

        subgrouped: dict[str, list[str]] = {}
        for example_id in group_examples:
            sub = examples[example_id].subcategory or "__other__"
            subgrouped.setdefault(sub, []).append(example_id)

        ordered_subgroups = sorted(
            subgrouped.keys(),
            key=lambda sub: (subcategory_rank.get(group_id, {}).get(sub, 999), sub.lower()),
        )

        for sub in ordered_subgroups:
            if len(ordered_subgroups) > 1:
                display_sub = (
                    SUBCATEGORY_TITLES.get(group_id, {}).get(sub)
                    or sub.replace("-", " ").title()
                )
                lines.append(f"### {display_sub}")
                lines.append("")

            sub_examples = sorted(
                subgrouped[sub],
                key=lambda exid: (
                    examples[exid].order if examples[exid].order is not None else 10_000,
                    examples[exid].title.lower(),
                ),
            )
            visible_systems = [
                system_name
                for system_name in system_names
                if any(example_id in systems[system_name] for example_id in sub_examples)
            ]

            lines.append("| Example | " + " | ".join(visible_systems) + " |")
            lines.append("| --- | " + " | ".join("---" for _ in visible_systems) + " |")
            for example_id in sub_examples:
                example = examples[example_id]
                relpath = f"./{example.category}/{example.slug}.md"
                row = [f"[{example.title}]({relpath})"]
                for system_name in visible_systems:
                    if example_id in systems[system_name]:
                        anchor = slugify(system_name)
                        row.append(f"[X]({relpath}#{anchor})")
                    else:
                        row.append("")
                lines.append("| " + " | ".join(row) + " |")
            lines.append("")

    return render_content_template(
        ROSETTA_INDEX_SOURCE,
        {
            "PAGE_NAV": render_page_nav(
                [
                    ("Front Page", "../index.md"),
                    ("Specification", "../spec/index.md"),
                ],
                edit_link=("Edit this page", github_edit_url(ROSETTA_INDEX_SOURCE)),
                active_label="Rosetta Stone",
            ),
            "TABLE_OF_CONTENTS": "\n".join(toc_lines),
            "EXAMPLE_TABLES": "\n".join(lines).rstrip(),
        },
    )


def build_example_markdown(example, systems, spec_catalog, profile_catalog):
    body = example.body.rstrip()
    available_systems = [
        system_name
        for system_name in sorted(systems.keys())
        if example.id in systems[system_name]
    ]

    page_path = ROOT_INDEX_MD.parent / example.output_relpath_md
    lines = [
        render_page_nav(
            [
                ("Front Page", rel_link(page_path, ROOT_INDEX_MD)),
                ("Rosetta Stone", rel_link(page_path, ROSETTA_INDEX_MD)),
                ("Specification", rel_link(page_path, SPEC_INDEX_MD)),
            ],
            edit_link=("Edit this page", github_edit_url(example.path)),
            active_label="Rosetta Stone",
        ),
        f"# Example: {example.title}",
        "",
        *profile_lines(page_path, example.profiles, profile_catalog),
        body,
        "",
    ]

    lines.extend(spec_link_lines(page_path, example.spec_ids, spec_catalog))

    system_lines = []
    for system_name in available_systems:
        system_lines.append(f"### {system_name}")
        system_lines.append("")

        system_example = systems[system_name].get(example.id)
        outputs = sorted(system_example.outputs.values(), key=lambda output: output.id)
        shared_generate_files = system_example.shared_generate_files

        if shared_generate_files:
            system_lines.extend(render_generate_sections(shared_generate_files))

        if outputs:
            system_lines.append("#### Data outputs")
            system_lines.append("")
            system_lines.extend(
                render_output_tabs(
                    page_path,
                    example.id,
                    system_name,
                    outputs,
                    shared_generate_files,
                    profile_catalog,
                )
            )
            system_lines.append("")

        if not shared_generate_files and not any(output.data_file is not None for output in outputs):
            system_lines.append(load_markdown_source(PARTIALS_DIR / "example-no-system.md").strip())
            system_lines.append("")

    lines.extend(
        render_content_template(
            PARTIALS_DIR / "example-systems.md",
            {
                "SYSTEM_SECTIONS": "\n".join(system_lines).rstrip(),
            },
        ).splitlines() + [""]
    )

    return "\n".join(lines).rstrip() + "\n"


def render_generate_sections(generate_files: list[Path]) -> list[str]:
    lines = []
    for generate_file in generate_files:
        lines.append(
            f"#### Generate code (`{generate_file.name}`) [ [edit]({github_edit_url(generate_file)}) ]"
        )
        lines.append("")
        code = generate_file.read_text(encoding="utf-8")
        lines.append(fenced_block(code, language_for_file(generate_file)))
        lines.append("")
    return lines


def output_heading(page_path, output_id, profile_catalog):
    if output_id in profile_catalog:
        profile = profile_catalog[output_id]
        href = profile_href(page_path)
        return f"Output for [{profile.title}]({href}#{output_id})"
    return f"Output `{output_id}`"


def output_sort_key(output):
    if output.profile_id is None:
        return (10_000, output.id)
    return (PROFILE_ORDER.get(output.profile_id, 10_000), output.id)


def choose_representative_output(outputs):
    return max(outputs, key=output_sort_key)


def outputs_are_equivalent(left, right):
    if left.generate_files != right.generate_files:
        return False
    if left.parsed_data is None or right.parsed_data is None:
        return left.data_file == right.data_file
    return equivalent_json(
        left.parsed_data,
        right.parsed_data,
        ignore_namespace_versions=True,
    )


def equivalent_output_groups(outputs):
    groups: list[list[ExampleOutput]] = []
    for output in sorted(outputs, key=output_sort_key):
        matched_group = None
        for group in groups:
            if outputs_are_equivalent(group[0], output):
                matched_group = group
                break
        if matched_group is None:
            groups.append([output])
        else:
            matched_group.append(output)
    return groups


def output_label(page_path, output_id, profile_catalog):
    if output_id in profile_catalog:
        profile = profile_catalog[output_id]
        href = profile_href(page_path)
        return f"[{profile.title}]({href}#{output_id})"
    return f"`{output_id}`"


def output_label_list(page_path, outputs, profile_catalog):
    labels = [
        output_label(page_path, output.id, profile_catalog)
        for output in sorted(outputs, key=output_sort_key)
    ]
    return ", ".join(labels)


def tab_slug(value):
    return slugify(value).replace("-", "_")


def render_output_tabs(
    page_path,
    example_id,
    system_name,
    outputs,
    shared_generate_files,
    profile_catalog,
):
    output_groups = equivalent_output_groups(outputs)
    container_id = f"tabs_{tab_slug(example_id)}_{tab_slug(system_name)}"
    lines = [
        f'<div class="output-tabs" data-tabs id="{container_id}">',
        '<div class="output-tab-list" role="tablist" aria-label="Serialized outputs">',
    ]

    for group_index, output_group in enumerate(output_groups):
        panel_id = f"{container_id}_panel_{group_index}"
        representative = choose_representative_output(output_group)
        button_id = f"{container_id}_tab_{tab_slug(representative.id)}"
        lines.append(
            f'<button type="button" class="output-tab-btn" role="tab" '
            f'id="{button_id}" aria-controls="{panel_id}" '
            f'data-tab-target="{panel_id}">'
            f"{escape(output_group_button_label(output_group, profile_catalog))}</button>"
        )

    lines.append("</div>")

    for group_index, output_group in enumerate(output_groups):
        representative = choose_representative_output(output_group)
        panel_id = f"{container_id}_panel_{group_index}"
        panel_lines = [
            f'<div class="output-tab-panel" role="tabpanel" id="{panel_id}">'
        ]

        label_list = output_label_list_html(page_path, output_group, profile_catalog)
        panel_lines.append(
            f"<p><strong>Profiles:</strong> {label_list}</p>"
        )

        if representative.generate_files and representative.generate_files != shared_generate_files:
            panel_lines.extend(render_generate_sections_html(representative.generate_files))

        if representative.data_file is not None:
            language = language_for_file(representative.data_file)
            data = render_data_for_markdown(representative.data_file)
            panel_lines.append(
                f"<p><strong>Data file:</strong> <code>{escape(representative.data_file.name)}</code></p>"
            )
            panel_lines.append(
                f'<pre><code class="language-{escape(language)}">{escape(data)}</code></pre>'
            )

        if len(output_group) > 1:
            panel_lines.append(
                "<p>This serialized output is equivalent for these profiles up to "
                "UUID renaming and recorded namespace version strings.</p>"
            )

        panel_lines.append("</div>")
        lines.extend(panel_lines)

    lines.append("</div>")
    return lines


def output_button_label(output_id, profile_catalog):
    if output_id in profile_catalog:
        return profile_catalog[output_id].title
    return output_id


def output_group_button_label(outputs, profile_catalog):
    sorted_outputs = sorted(outputs, key=output_sort_key)
    titles = []
    for output in sorted_outputs:
        if output.id not in profile_catalog:
            return ", ".join(
                output_button_label(candidate.id, profile_catalog)
                for candidate in sorted_outputs
            )
        titles.append(profile_catalog[output.id].title)

    if len(titles) == 1:
        return titles[0]

    range_label = merged_title_range(titles)
    return range_label if range_label is not None else ", ".join(titles)


def merged_title_range(titles):
    parsed = [split_trailing_version(title) for title in titles]
    if any(item is None for item in parsed):
        return None

    prefixes = {item[0] for item in parsed if item is not None}
    if len(prefixes) != 1:
        return None

    first_prefix, first_version = parsed[0]
    last_prefix, last_version = parsed[-1]
    if first_prefix != last_prefix:
        return None

    return f"{first_prefix}{first_version}-{last_version}"


def split_trailing_version(title):
    match = re.match(r"^(.*?)(\d+(?:\.\d+)*)$", title)
    if match is None:
        return None
    return match.group(1), match.group(2)


def output_label_html(page_path, output_id, profile_catalog):
    if output_id in profile_catalog:
        profile = profile_catalog[output_id]
        href = profile_href(page_path)
        return f'<a href="{escape(href)}#{escape(output_id)}">{escape(profile.title)}</a>'
    return f"<code>{escape(output_id)}</code>"


def output_label_list_html(page_path, outputs, profile_catalog):
    labels = [
        output_label_html(page_path, output.id, profile_catalog)
        for output in sorted(outputs, key=output_sort_key)
    ]
    return ", ".join(labels)


def render_generate_sections_html(generate_files: list[Path]) -> list[str]:
    lines = []
    for generate_file in generate_files:
        code = generate_file.read_text(encoding="utf-8")
        language = language_for_file(generate_file)
        edit_url = github_edit_url(generate_file)
        lines.append(
            "<div class=\"output-tab-generate-block\">"
            f"<p><strong>Generate code:</strong> <code>{escape(generate_file.name)}</code> "
            f'[ <a href="{escape(edit_url)}">edit</a> ]</p>'
            f'<pre><code class="language-{escape(language)}">{escape(code)}</code></pre>'
            "</div>"
        )
    return lines
