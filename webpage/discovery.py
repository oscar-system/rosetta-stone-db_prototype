from __future__ import annotations

import json
from pathlib import Path

from content import parse_description
from models import ExampleOutput, ExamplePage, ExampleSystem, Profile, SpecPage
from settings import PROFILE_DEFINITIONS, ROSETTA_SOURCE_DIR, SPEC_SITE_DIR, SPEC_SOURCE_DIR, resolve_type_spec


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


def find_generate_files(path: Path) -> list[Path]:
    return [p for p in sorted(path.iterdir()) if p.is_file() and p.name.startswith("generate.")]


def find_data_file(path: Path) -> Path | None:
    return next(
        (p for p in sorted(path.iterdir()) if p.is_file() and p.name.startswith("data.")),
        None,
    )


def infer_legacy_output_id(example_profiles: list[str]) -> str:
    if len(example_profiles) == 1:
        return example_profiles[0]
    return "default"


def build_output(
    output_id: str,
    output_path: Path,
    generate_files: list[Path],
) -> ExampleOutput:
    data_file = find_data_file(output_path)
    parsed_data = load_serialized_payload(data_file)
    return ExampleOutput(
        id=output_id,
        path=output_path,
        data_file=data_file,
        generate_files=list(generate_files),
        parsed_data=parsed_data,
        root_type=normalize_type_name(parsed_data.get("_type")) if isinstance(parsed_data, dict) else None,
        namespaces=extract_namespaces(parsed_data),
        profile_id=output_id if output_id != "default" else None,
    )


def discover_system_outputs(system_dir: Path, example_profiles: list[str]) -> ExampleSystem:
    shared_generate_files = find_generate_files(system_dir)
    outputs: dict[str, ExampleOutput] = {}
    outputs_root = system_dir / "outputs"

    if outputs_root.exists():
        output_dirs = sorted(path for path in outputs_root.iterdir() if path.is_dir())
        for output_dir in output_dirs:
            output_generate_files = find_generate_files(output_dir) or shared_generate_files
            outputs[output_dir.name] = build_output(
                output_dir.name,
                output_dir,
                output_generate_files,
            )
        if not output_dirs and find_data_file(system_dir) is not None:
            legacy_output_id = infer_legacy_output_id(example_profiles)
            outputs[legacy_output_id] = build_output(
                legacy_output_id,
                system_dir,
                shared_generate_files,
            )
    else:
        legacy_output_id = infer_legacy_output_id(example_profiles)
        outputs[legacy_output_id] = build_output(
            legacy_output_id,
            system_dir,
            shared_generate_files,
        )

    return ExampleSystem(
        path=system_dir,
        shared_generate_files=shared_generate_files,
        outputs=outputs,
    )


def discover_examples() -> dict[str, ExamplePage]:
    examples: dict[str, ExamplePage] = {}
    for group_dir in sorted(path for path in ROSETTA_SOURCE_DIR.iterdir() if path.is_dir()):
        group_id = group_dir.name
        for example_dir in sorted(path for path in group_dir.iterdir() if path.is_dir()):
            description_path = example_dir / "description.md"
            if not description_path.exists():
                continue

            metadata, body = parse_description(description_path)
            example_profiles = metadata.str_list("profiles")
            example_slug = example_dir.name
            example_id = f"{group_id}-{example_slug}"

            systems: dict[str, ExampleSystem] = {}
            systems_root = example_dir / "systems"
            if systems_root.exists():
                for system_dir in sorted(path for path in systems_root.iterdir() if path.is_dir()):
                    systems[system_dir.name] = discover_system_outputs(system_dir, example_profiles)

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
                profiles=example_profiles,
                body=body,
                systems=systems,
                unavailable_profiles=metadata.str_list("unavailable_profiles"),
                unavailable_note=metadata.optional_str("unavailable_note"),
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
            concept_id=metadata.optional_str("concept"),
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
            concept_id=spec.concept_id,
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
            for output in system.outputs.values():
                spec_id = resolve_type_spec(output.root_type, output.profile_id)
                if spec_id:
                    related_specs.add(spec_id)

                parsed_data = output.parsed_data
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
            status=definition["status"],
            based_on=list(definition.get("based_on", [])),
            description=definition["description"],
            released_on=definition.get("released_on"),
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
