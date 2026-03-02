from __future__ import annotations

from pathlib import Path

from content import load_markdown_source, render_content_template, render_page_nav
from mrdi_compare import equivalent_json
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

        for output_group in equivalent_output_groups(outputs):
            representative = choose_representative_output(output_group)

            if len(outputs) > 1:
                if len(output_group) > 1:
                    system_lines.append(
                        f"#### Equivalent outputs for "
                        f"{output_label_list(page_path, output_group, profile_catalog)}"
                    )
                else:
                    system_lines.append(
                        f"#### {output_heading(page_path, representative.id, profile_catalog)}"
                    )
                system_lines.append("")

            if len(output_group) > 1:
                system_lines.append(
                    "These serialized outputs are equivalent up to UUID renaming "
                    "and recorded namespace version strings."
                )
                system_lines.append("")

            if representative.generate_files and representative.generate_files != shared_generate_files:
                system_lines.extend(render_generate_sections(representative.generate_files))

            data_file = representative.data_file
            if data_file is not None:
                if len(output_group) > 1:
                    system_lines.append(
                        f"#### Representative data file (`{data_file.name}`)"
                    )
                else:
                    system_lines.append(f"#### Data file (`{data_file.name}`)")
                system_lines.append("")
                data = render_data_for_markdown(data_file)
                system_lines.append(fenced_block(data, language_for_file(data_file)))
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
    groups: list[list[object]] = []
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
