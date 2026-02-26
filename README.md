# Rosetta Stone DB (prototype)

This repository is a prototype "Rosetta stone" for serialization of mathematical
objects across computer algebra systems.

It stores:
- a human-readable description per example
- code to generate the object in a given system
- the serialized data emitted by that system

It also generates a browsable static site with:
- an index table grouped by category (and optional subcategory)
- per-example pages with code and serialized data for each available system
- Markdown and HTML output

## Repository layout

### Input data

All source data lives under `data/`:

`data/<category>/<example-slug>/description.md`  
`data/<category>/<example-slug>/systems/<SystemName>/generate.*`  
`data/<category>/<example-slug>/systems/<SystemName>/data.*`

Example:

`data/polyhedral/complete-graph/description.md`  
`data/polyhedral/complete-graph/systems/Oscar.jl/generate.jl`  
`data/polyhedral/complete-graph/systems/Oscar.jl/data.json`

### Site generator

- Script: `webpage/generate_page.py`
- Input: `data/`
- Output directory: `_site/` (generated files, ignored by git)

Generated output includes:
- `_site/index.md`
- `_site/index.html`
- one `.md` and one `.html` page per example in category subdirectories, e.g.
  `_site/groups/free-group.md` and `_site/groups/free-group.html`

## Metadata in `description.md`

Each example description starts with YAML frontmatter:

```yaml
---
title: Complete graph
category: polyhedral
subcategory: combinatorics
---
```

Required:
- `title`
- `category`

Optional:
- `subcategory` (used for sub-grouping and sorting in the index)

`category` and `subcategory` are internal keys (slug-like). Display names and
ordering are configured in `webpage/generate_page.py`.

## Local development

Install dependencies:

```bash
pip install -r requirements.txt
```

Generate the site:

```bash
python3 webpage/generate_page.py
```

Notes:
- Markdown is converted to HTML using `marko` (with GFM extension).
- Math rendering uses MathJax in generated HTML.
- Code blocks use highlight.js and include a copy button.
- JSON `data.*` is rendered with compact pretty-printing on pages.

## GitHub Pages

The repository contains a workflow at
`.github/workflows/publish-pages.yml` that:
- installs Python dependencies
- runs `python3 webpage/generate_page.py`
- publishes `_site/` via GitHub Pages

Dependabot config for GitHub Actions updates is in:
- `.github/dependabot.yml`

## Guidelines for good examples

### Prefer distinctive values
Use values that are easy to identify in serialized output. Tiny or repetitive
values are harder to match across systems.

### Avoid overly symmetric objects
Prefer examples that make structure visible in serialized form (for example,
nontrivial matrices instead of highly symmetric zero matrices).
