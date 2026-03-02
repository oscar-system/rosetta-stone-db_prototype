from __future__ import annotations

from pathlib import Path
import json

MODULE_DIR = Path(__file__).resolve().parent
ROOT = MODULE_DIR.parent
CONTENT_DIR = ROOT / "content"
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
LANGUAGE_BY_SUFFIX = _CONFIG["language_by_suffix"]
PROFILE_DEFINITIONS = _CONFIG["profiles"]

GITHUB_EDIT_BASE = "https://github.com/oscar-system/rosetta-stone-db_prototype/edit/main/"
