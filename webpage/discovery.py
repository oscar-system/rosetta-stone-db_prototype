from __future__ import annotations

import json
from pathlib import Path

from content import parse_description
from models import ExamplePage, ExampleSystem, Profile, SpecPage
from settings import PROFILE_DEFINITIONS, ROSETTA_SOURCE_DIR, SPEC_SITE_DIR, SPEC_SOURCE_DIR, TYPE_SPEC_BY_ROOT_TYPE


def load_serialized_payload(path: Path | None):
    if path is None or path.suffix not in {".json", ".mrdi"}:
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def normalize_type_name(type_value) -> str | None:
    if isinstance(type_value, str):
        return type_value
    if isinstance(type_value, dict):
        name = type_value.get("name")
        if isinstance(name, str):
            return name
    return None


def extract_namespaces(parsed) -> list[dict[str, str]]:
    namespaces: list[dict[str, str]] = []
    if not isinstance(parsed, dict):
        return namespaces

    ns = parsed.get("_ns")
    if not isinstance(ns, dict):
        return namespaces

    for namespace_name, value in ns.items():
        url = ""
        version = ""
        if isinstance(value, list):
            if len(value) >= 1:
                url = str(value[0])
            if len(value) >= 2:
                version = str(value[1])
        elif isinstance(value, str):
            version = value
        namespaces.append(
            {
                "name": namespace_name,
                "url": url,
                "version": version,
            }
        )
    return namespaces


def discover_examples() -> dict[str, ExamplePage]:
    examples: dict[str, ExamplePage] = {}
    for group_dir in sorted(path for path in ROSETTA_SOURCE_DIR.iterdir() if path.is_dir()):
        group_id = group_dir.name
        for example_dir in sorted(path for path in group_dir.iterdir() if path.is_dir()):
            description_path = example_dir / "description.md"
            if not description_path.exists():
                continue

            metadata, body = parse_description(description_path)
            example_slug = example_dir.name
            example_id = f"{group_id}-{example_slug}"

            systems: dict[str, ExampleSystem] = {}
            systems_root = example_dir / "systems"
            if systems_root.exists():
                for system_dir in sorted(path for path in systems_root.iterdir() if path.is_dir()):
                    data_file = next((p for p in sorted(system_dir.iterdir()) if p.name.startswith("data.")), None)
                    generate_file = next(
                        (p for p in sorted(system_dir.iterdir()) if p.name.startswith("generate.")),
                        None,
                    )
                    parsed_data = load_serialized_payload(data_file)
                    systems[system_dir.name] = ExampleSystem(
                        path=system_dir,
                        data_file=data_file,
                        generate_file=generate_file,
                        parsed_data=parsed_data,
                        root_type=normalize_type_name(parsed_data.get("_type")) if isinstance(parsed_data, dict) else None,
                        namespaces=extract_namespaces(parsed_data),
                    )

            parsed_order = metadata.optional_int("order")

            examples[example_id] = ExamplePage(
                id=example_id,
                slug=example_slug,
                output_relpath_md=f"rosetta/{group_id}/{example_slug}.md",
                path=description_path,
                title=metadata.require_str("title", example_slug),
                category=metadata.require_str(
                    "category",
                    metadata.require_str("group", group_id),
                ),
                subcategory=metadata.optional_str("subcategory"),
                order=parsed_order,
                profiles=metadata.str_list("profiles"),
                body=body,
                systems=systems,
            )
    return examples


def build_system_index(examples: dict[str, ExamplePage]) -> dict[str, dict[str, ExampleSystem]]:
    systems: dict[str, dict[str, ExampleSystem]] = {}
    for example_id, example in examples.items():
        for system_name, files in example.systems.items():
            systems.setdefault(system_name, {})
            systems[system_name][example_id] = files
    return systems


def discover_spec_pages() -> dict[str, SpecPage]:
    spec_pages: dict[str, SpecPage] = {}
    for spec_path in sorted(SPEC_SOURCE_DIR.rglob("*.md")):
        metadata, body = parse_description(spec_path)
        parsed_order = metadata.optional_int("order")

        relpath = spec_path.relative_to(SPEC_SOURCE_DIR)
        spec_id = relpath.with_suffix("").as_posix()
        spec_pages[spec_id] = SpecPage(
            id=spec_id,
            title=metadata.require_str("title", spec_id.replace("-", " ").title()),
            kind=metadata.require_str("kind", "type"),
            order=parsed_order,
            profiles=metadata.str_list("profiles"),
            body=body.rstrip(),
            section=metadata.require_str(
                "section",
                relpath.parent.as_posix() if relpath.parent != Path(".") else "",
            ),
            source_path=spec_path,
            path_md=SPEC_SITE_DIR / relpath,
        )
    return spec_pages


def build_spec_catalog(spec_pages: dict[str, SpecPage], examples: dict[str, ExamplePage]) -> dict[str, SpecPage]:
    catalog = {
        spec_id: SpecPage(
            id=spec.id,
            title=spec.title,
            kind=spec.kind,
            order=spec.order,
            profiles=list(spec.profiles),
            body=spec.body,
            section=spec.section,
            source_path=spec.source_path,
            path_md=spec.path_md,
        )
        for spec_id, spec in spec_pages.items()
    }

    for example_id, example in examples.items():
        related_specs: set[str] = set()
        for system in example.systems.values():
            root_type = system.root_type
            spec_id = TYPE_SPEC_BY_ROOT_TYPE.get(root_type)
            if spec_id:
                related_specs.add(spec_id)

            parsed_data = system.parsed_data
            if isinstance(parsed_data, dict) and parsed_data.get("_refs"):
                related_specs.add("core/references-and-parameters")

        example.spec_ids = sorted(related_specs)
        for spec_id in example.spec_ids:
            if spec_id in catalog:
                catalog[spec_id].example_ids.append(example_id)

    return catalog


def build_profile_catalog(
    spec_pages: dict[str, SpecPage],
    examples: dict[str, ExamplePage],
) -> dict[str, Profile]:
    catalog = {
        profile_id: Profile(
            id=profile_id,
            title=definition["title"],
            kind=definition["kind"],
            based_on=list(definition.get("based_on", [])),
            description=definition["description"],
        )
        for profile_id, definition in PROFILE_DEFINITIONS.items()
    }

    for spec_id, spec_page in spec_pages.items():
        for profile_id in spec_page.profiles:
            if profile_id in catalog:
                catalog[profile_id].spec_ids.append(spec_id)

    for example_id, example in examples.items():
        for profile_id in example.profiles:
            if profile_id in catalog:
                catalog[profile_id].example_ids.append(example_id)

    return catalog
