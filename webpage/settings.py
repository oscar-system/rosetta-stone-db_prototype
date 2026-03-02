from __future__ import annotations

from pathlib import Path
import json

from content import parse_description

MODULE_DIR = Path(__file__).resolve().parent
ROOT = MODULE_DIR.parent
CONTENT_DIR = ROOT / "content"
PROFILE_SOURCE_DIR = ROOT / "profiles"
ROSETTA_SOURCE_DIR = ROOT / "rosetta"
SPEC_SOURCE_DIR = ROOT / "spec"
SITE_DIR = ROOT / "_site"
TEMPLATE_PATH = ROOT / "templates" / "default.html"
FRONT_PAGE_SOURCE = CONTENT_DIR / "front-page.md"
ROSETTA_INDEX_SOURCE = CONTENT_DIR / "rosetta-index.md"
SPEC_INDEX_SOURCE = CONTENT_DIR / "spec-index.md"
PARTIALS_DIR = CONTENT_DIR / "partials"
ROOT_INDEX_MD = SITE_DIR / "index.md"
ROSETTA_DIR = SITE_DIR / "rosetta"
ROSETTA_INDEX_MD = ROSETTA_DIR / "index.md"
SPEC_SITE_DIR = SITE_DIR / "spec"
SPEC_INDEX_MD = SPEC_SITE_DIR / "index.md"
SCHEMA_PATH = ROOT / "paper" / "data.json"

_CONFIG = json.loads((MODULE_DIR / "config.json").read_text(encoding="utf-8"))

CATEGORY_TITLES = _CONFIG["category_titles"]
SUBCATEGORY_TITLES = _CONFIG["subcategory_titles"]
TYPE_SPEC_BY_ROOT_TYPE = _CONFIG["type_spec_by_root_type"]
TYPE_SPEC_BY_ROOT_TYPE_AND_PROFILE = _CONFIG.get("type_spec_by_root_type_and_profile", {})
LANGUAGE_BY_SUFFIX = _CONFIG["language_by_suffix"]
def load_profile_definitions():
    definitions = {}
    for profile_path in sorted(PROFILE_SOURCE_DIR.glob("*.md")):
        metadata, body = parse_description(profile_path)
        profile_id = profile_path.stem
        definitions[profile_id] = {
            "title": metadata.require_str("title", profile_id),
            "kind": metadata.require_str("kind", "application"),
            "status": metadata.require_str("status", "draft"),
            "based_on": metadata.str_list("based_on"),
            "released_on": metadata.optional_str("released_on"),
            "description": body.strip(),
        }
    return definitions


PROFILE_DEFINITIONS = load_profile_definitions()
PROFILE_ORDER = {profile_id: index for index, profile_id in enumerate(PROFILE_DEFINITIONS.keys())}

GITHUB_EDIT_BASE = "https://github.com/oscar-system/rosetta-stone-db_prototype/edit/main/"


def resolve_type_spec(root_type: str | None, profile_id: str | None) -> str | None:
    if root_type is None:
        return None

    profile_map = TYPE_SPEC_BY_ROOT_TYPE_AND_PROFILE.get(root_type)
    if isinstance(profile_map, dict) and profile_id is not None:
        spec_id = profile_map.get(profile_id)
        if isinstance(spec_id, str):
            return spec_id

    spec_id = TYPE_SPEC_BY_ROOT_TYPE.get(root_type)
    return spec_id if isinstance(spec_id, str) else None
