#!/usr/bin/env python3
import shutil

from discovery import build_profile_catalog, build_spec_catalog, build_system_index, discover_examples, discover_spec_pages
from html_renderer import render_html_page
from rosetta_render import build_example_markdown, build_front_page_markdown, build_rosetta_index_markdown
from settings import ROOT_INDEX_MD, ROSETTA_INDEX_MD, SITE_DIR, SPEC_INDEX_MD
from spec_render import build_spec_index_markdown, build_spec_page_markdown


def main():
    if SITE_DIR.exists():
        shutil.rmtree(SITE_DIR)

    examples = discover_examples()
    systems = build_system_index(examples)
    spec_pages = discover_spec_pages()
    spec_catalog = build_spec_catalog(spec_pages, examples)
    profile_catalog = build_profile_catalog(spec_pages, examples)

    SITE_DIR.mkdir(parents=True, exist_ok=True)

    ROOT_INDEX_MD.write_text(build_front_page_markdown(), encoding="utf-8")
    ROSETTA_INDEX_MD.parent.mkdir(parents=True, exist_ok=True)
    ROSETTA_INDEX_MD.write_text(build_rosetta_index_markdown(examples, systems), encoding="utf-8")
    SPEC_INDEX_MD.parent.mkdir(parents=True, exist_ok=True)
    SPEC_INDEX_MD.write_text(build_spec_index_markdown(spec_catalog), encoding="utf-8")

    for spec_id in sorted(spec_catalog.keys()):
        spec_page = spec_catalog[spec_id]
        spec_page.path_md.parent.mkdir(parents=True, exist_ok=True)
        spec_page.path_md.write_text(
            build_spec_page_markdown(spec_page, examples, profile_catalog, spec_catalog),
            encoding="utf-8",
        )
        print(f"Wrote {spec_page.path_md}")

    for example_id in sorted(examples.keys()):
        example = examples[example_id]
        example_page_path = ROOT_INDEX_MD.parent / example.output_relpath_md
        example_page_path.parent.mkdir(parents=True, exist_ok=True)
        example_page_path.write_text(
            build_example_markdown(example, systems, spec_catalog, profile_catalog),
            encoding="utf-8",
        )
        print(f"Wrote {example_page_path}")

    print(f"Wrote {ROOT_INDEX_MD}")
    print(f"Wrote {ROSETTA_INDEX_MD}")
    print(f"Wrote {SPEC_INDEX_MD}")

    for md_path in sorted(SITE_DIR.rglob("*.md")):
        render_html_page(md_path)


if __name__ == "__main__":
    main()
