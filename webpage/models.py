from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ExampleSystem:
    path: Path
    data_file: Path | None
    generate_file: Path | None
    parsed_data: dict | list | None
    root_type: str | None
    namespaces: list[dict[str, str]]


@dataclass
class ExamplePage:
    id: str
    slug: str
    output_relpath_md: str
    path: Path
    title: str
    category: str
    subcategory: str | None
    order: int | None
    profiles: list[str]
    body: str
    systems: dict[str, ExampleSystem]
    spec_ids: list[str] = field(default_factory=list)


@dataclass
class SpecPage:
    id: str
    title: str
    kind: str
    order: int | None
    profiles: list[str]
    body: str
    section: str
    source_path: Path
    path_md: Path
    example_ids: list[str] = field(default_factory=list)


@dataclass
class Profile:
    id: str
    title: str
    kind: str
    status: str
    based_on: list[str]
    description: str
    released_on: str | None = None
    spec_ids: list[str] = field(default_factory=list)
    example_ids: list[str] = field(default_factory=list)
