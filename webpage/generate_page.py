#!/usr/bin/env python3
from pathlib import Path
import json
import os
import re

import marko
from marko.html_renderer import HTMLRenderer

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
SITE_DIR = ROOT / "_site"
ROOT_INDEX_MD = SITE_DIR / "index.md"
ROSETTA_DIR = SITE_DIR / "rosetta"
ROSETTA_INDEX_MD = ROSETTA_DIR / "index.md"
SPEC_DIR = SITE_DIR / "spec"
SPEC_INDEX_MD = SPEC_DIR / "index.md"
SCHEMA_PATH = ROOT / "paper" / "data.json"

CATEGORY_TITLES = {
    "basics": "Basics",
    "containers": "Containers",
    "rings": "Rings",
    "linear-algebra": "Linear Algebra",
    "groups": "Groups",
    "lie-theory": "Lie Theory",
    "polyhedral": "Polyhedral Geometry",
}

SUBCATEGORY_TITLES = {
    "groups": {
        "abelian": "Abelian Groups",
        "permutation": "Permutation Groups",
        "matrix": "Matrix Groups",
        "free": "Free Groups",
        "fp": "Finitely Presented Groups",
        "pc": "Pc Groups",
        "__other__": "Other",
    },
    "polyhedral": {
        "polyhedra": "Polyhedra",
        "fans": "Fans",
        "cones": "Cones",
        "matroids": "Matroids",
        "optimization": "Optimization",
        "complexes-subdivisions": "Complexes and Subdivisions",
        "phylogenetic": "Phylogenetic",
        "combinatorics": "Combinatorics",
        "__other__": "Other",
    },
    "lie-theory": {
        "root-data": "Root Data",
        "weight-lattice": "Weight Lattice",
        "weyl-group": "Weyl Group",
        "__other__": "Other",
    },
}

TYPE_SPEC_BY_ROOT_TYPE = {
    "Bool": "bool",
    "Base.Int": "integers",
    "BigInt": "integers",
    "Int16": "integers",
    "UInt64": "integers",
    "ZZRingElem": "integers",
    "String": "string",
    "Vector": "vector",
    "Dict": "dict",
    "Set": "set",
    "Tuple": "tuple",
    "QQFieldElem": "rational-number",
    "Matrix": "matrix",
    "PolyRingElem": "univariate-polynomial",
    "MPolyRingElem": "multivariate-polynomial",
}

SPEC_PAGES = [
    {
        "id": "data-model",
        "title": "Overall Data Model",
        "lede": (
            "The MaRDI file format stores mathematical objects as annotated JSON trees. "
            "A file combines type information, serialized data, namespaces, and optional "
            "reference objects that provide the context required to interpret the payload."
        ),
        "sections": [
            (
                "Terminology",
                [
                    "A **file** is the top-level JSON object.",
                    "A **data type** is the value of `_type`, either as a string or as an object with a `name` and optional `params`.",
                    "A **payload** is the subtree stored under `data`.",
                    "A **profile** is a namespace-specific encoding contract, for example the Oscar profile identified by an `Oscar` entry in `_ns`.",
                    "A **reference object** is an entry in `_refs`, addressed by UUID and reused from types or payloads.",
                ],
            ),
            (
                "Core object members",
                [
                    "`_type` is required and names the data type that determines how `data` must be interpreted.",
                    "`data` stores the serialized payload; it may be a string, array, object, or a foreign schema-defined subtree.",
                    "`_ns` declares which namespace and software version define the semantics.",
                    "`_refs` stores referenced objects so recursive and shared constructions can be serialized without duplication.",
                ],
            ),
            (
                "Design intent",
                [
                    "The format follows the paper's approach of separating syntax from semantics: JSON fixes the container syntax, while semantics are supplied by a concrete namespace and version.",
                    "The format is intentionally extensible. New types, new namespaces, and namespace-specific payloads can be added without redesigning the whole file format.",
                    "References are session-stable UUIDs rather than position-based indices, which makes reused mathematical context easier to track across files and workflows.",
                ],
            ),
        ],
    },
    {
        "id": "namespaces-and-versions",
        "title": "Namespaces, Profiles, and Versions",
        "lede": (
            "The format does not impose a universal mathematical semantics. Instead, each "
            "file points to the namespace and software version that define the meaning of "
            "its types and payloads."
        ),
        "sections": [
            (
                "Rules",
                [
                    "Use `_ns` to record the profile that governs the file or subtree.",
                    "A namespace entry is typically encoded as `\"Name\": [\"URL\", \"version\"]`.",
                    "When two systems use different meanings or different serializations, they should be treated as different profiles rather than forced into one shared meaning.",
                    "If a profile changes its encoding, keep the old profile/version rows documented and add the new ones instead of rewriting history.",
                ],
            ),
            (
                "Practical consequence",
                [
                    "A type page such as Bool should document profile-specific encodings and the versions in which they appear.",
                    "The tables on generated spec pages are built from the current rosetta-stone corpus, so they serve as an evolving compatibility log.",
                    "This structure also leaves room for future Oscar, Magma, polymake, or other profiles once matching examples are added.",
                ],
            ),
        ],
    },
    {
        "id": "references-and-parameters",
        "title": "References and Parameters",
        "lede": (
            "Complex mathematical objects often depend on ambient rings, fields, spaces, or "
            "other context that should be stored once and reused. The format handles this "
            "with parametric types and UUID-addressed reference objects."
        ),
        "sections": [
            (
                "Rules",
                [
                    "When a type depends on contextual objects, encode that dependency in `_type.params`.",
                    "If the parameter is itself a structured object, place it in `_refs` and refer to it by UUID.",
                    "Use `_refs` for recursive constructions, shared ambient objects, and cases where object identity matters beyond isomorphism.",
                    "UUID keys in `_refs` should remain stable throughout the active producing session.",
                ],
            ),
            (
                "Why this matters",
                [
                    "Two mathematically isomorphic objects can still play different computational roles, and the reference graph preserves that distinction.",
                    "A later consumer can reconstruct the full serialization context instead of reverse-engineering it from the payload alone.",
                ],
            ),
        ],
    },
    {
        "id": "bool",
        "title": "Bool",
        "lede": (
            "The Bool data type encodes logical truth values. In the current corpus, the "
            "payload is the string `\"true\"` or `\"false\"`, interpreted according to the "
            "active profile."
        ),
        "sections": [
            (
                "Encoding rules",
                [
                    "Set `_type` to `\"Bool\"`.",
                    "Encode the payload under `data` as the lowercase string `\"true\"` or `\"false\"`.",
                    "Treat the namespace/version table below as the profile log for this type.",
                ],
            ),
        ],
    },
    {
        "id": "integers",
        "title": "Integers",
        "lede": (
            "Integer-valued data appears in several closely related data types, including "
            "machine integers such as `Base.Int`, arbitrary-precision integers such as "
            "`BigInt`, and algebraic integers such as `ZZRingElem`."
        ),
        "sections": [
            (
                "Encoding rules",
                [
                    "Encode the value under `data` as a decimal string.",
                    "Use `_type` to distinguish the specific integer family instead of overloading one generic integer name.",
                    "When an integer value depends on ambient algebraic structure, use a parametric type such as `ZZRingElem` with the required context in `params` or `_refs`.",
                ],
            ),
        ],
    },
    {
        "id": "string",
        "title": "String",
        "lede": (
            "String is the basic textual data type. It is useful both on its own and as a "
            "building block inside container types such as dictionaries and tuples."
        ),
        "sections": [
            (
                "Encoding rules",
                [
                    "Set `_type` to `\"String\"`.",
                    "Store the UTF-8 string payload directly under `data`.",
                    "When strings appear as keys or components inside other payloads, their role is determined by the surrounding type.",
                ],
            ),
        ],
    },
    {
        "id": "vector",
        "title": "Vector",
        "lede": (
            "Vectors are homogeneous ordered containers. Their element type is recorded in "
            "`_type.params`, and the payload is an array whose entries follow that element "
            "type's serialization rules."
        ),
        "sections": [
            (
                "Encoding rules",
                [
                    "Set `_type` to an object with `name: \"Vector\"`.",
                    "Record the element type in `_type.params`.",
                    "Store the entries in order under `data` as a JSON array.",
                ],
            ),
        ],
    },
    {
        "id": "dict",
        "title": "Dictionary",
        "lede": (
            "Dictionaries map keys to values. In the current corpus, the key and value types "
            "are recorded explicitly inside `_type.params`."
        ),
        "sections": [
            (
                "Encoding rules",
                [
                    "Set `_type` to an object with `name: \"Dict\"`.",
                    "Record key and value types under `_type.params`, for example `key_params` and `value_params`.",
                    "Serialize the payload under `data` as a JSON object from encoded keys to encoded values.",
                ],
            ),
        ],
    },
    {
        "id": "set",
        "title": "Set",
        "lede": (
            "Sets are unordered homogeneous containers. The payload is stored as an array, "
            "while the mathematical set semantics come from the data type rather than the "
            "JSON container alone."
        ),
        "sections": [
            (
                "Encoding rules",
                [
                    "Set `_type` to an object with `name: \"Set\"`.",
                    "Record the element type in `_type.params`.",
                    "Store the elements under `data` as an array; consumers should apply set semantics rather than relying on JSON order.",
                ],
            ),
        ],
    },
    {
        "id": "tuple",
        "title": "Tuple",
        "lede": (
            "Tuples are ordered heterogeneous containers. The parameter list records the type "
            "of each component in position order."
        ),
        "sections": [
            (
                "Encoding rules",
                [
                    "Set `_type` to an object with `name: \"Tuple\"`.",
                    "Record the component types in `_type.params` as an ordered list.",
                    "Store the component payloads under `data` as a JSON array of the same length.",
                ],
            ),
        ],
    },
    {
        "id": "rational-number",
        "title": "Rational Numbers",
        "lede": (
            "Rational numbers are represented as typed values whose payload is a textual "
            "fraction such as `\"42//23\"`. The field context is part of the type."
        ),
        "sections": [
            (
                "Encoding rules",
                [
                    "Use a typed encoding such as `QQFieldElem` rather than a bare JSON number.",
                    "Store the rational value under `data` using the profile's textual normal form.",
                    "Record the ambient field in `_type.params` when required by the profile.",
                ],
            ),
        ],
    },
    {
        "id": "matrix",
        "title": "Matrix",
        "lede": (
            "Matrices are two-dimensional homogeneous containers. The current corpus records "
            "the element type in `_type.params` and stores rows as arrays."
        ),
        "sections": [
            (
                "Encoding rules",
                [
                    "Set `_type` to an object with `name: \"Matrix\"`.",
                    "Record the entry type in `_type.params`.",
                    "Store the matrix payload under `data` as an array of rows.",
                ],
            ),
        ],
    },
    {
        "id": "univariate-polynomial",
        "title": "Univariate Polynomial",
        "lede": (
            "A univariate polynomial payload is interpreted relative to a polynomial ring "
            "stored in `_type.params` or `_refs`. The coefficients and exponents are "
            "encoded as structured JSON data rather than as presentation text."
        ),
        "sections": [
            (
                "Encoding rules",
                [
                    "Set `_type` to an object with `name: \"PolyRingElem\"`.",
                    "Use `_type.params` to point to the ambient polynomial ring.",
                    "Encode each term structurally under `data` so that reconstruction does not depend on parsing pretty-printed algebra.",
                ],
            ),
        ],
    },
    {
        "id": "multivariate-polynomial",
        "title": "Multivariate Polynomial",
        "lede": (
            "Multivariate polynomials extend the same idea to several variables. The payload "
            "is a structured list of terms, while the ambient ring and coefficient context "
            "are carried by the type parameters and references."
        ),
        "sections": [
            (
                "Encoding rules",
                [
                    "Set `_type` to an object with `name: \"MPolyRingElem\"`.",
                    "Reference the ambient multivariate polynomial ring through `_type.params`.",
                    "Encode monomials and coefficients structurally under `data` instead of using a textual polynomial syntax.",
                ],
            ),
        ],
    },
]

LANGUAGE_BY_SUFFIX = {
    ".jl": "julia",
    ".pl": "perl",
    ".sh": "bash",
    ".json": "json",
    ".lp": "text",
    ".ine": "text",
    ".md": "markdown",
    ".mrdi": "json",
}

HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title}</title>
  <script>
    MathJax = {{
      tex: {{
        inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
        displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']]
      }}
    }};
  </script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.11.1/styles/github.min.css" />
  <script defer src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.11.1/highlight.min.js"></script>
  <script defer src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.11.1/languages/julia.min.js"></script>
  <script>
    window.addEventListener("DOMContentLoaded", function () {{
      document.querySelectorAll("pre > code").forEach(function (codeBlock) {{
        var pre = codeBlock.parentElement;
        if (!pre || pre.querySelector(".copy-code-btn")) {{
          return;
        }}
        var button = document.createElement("button");
        button.type = "button";
        button.className = "copy-code-btn";
        button.textContent = "Copy";
        button.addEventListener("click", function () {{
          navigator.clipboard.writeText(codeBlock.textContent || "").then(function () {{
            button.textContent = "Copied";
            setTimeout(function () {{ button.textContent = "Copy"; }}, 1200);
          }});
        }});
        pre.appendChild(button);
      }});

      if (window.hljs) {{
        window.hljs.highlightAll();
      }}
    }});
  </script>
  <script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
  <style>
    :root {{
      --page-bg: linear-gradient(180deg, #f3eee2 0%, #fbfaf6 26%, #f6f7f2 100%);
      --panel-bg: rgba(255, 255, 255, 0.94);
      --border: #ddd3c2;
      --text: #1d1b18;
      --muted: #5c554a;
      --accent: #0d5c63;
      --accent-soft: #e5f0ef;
      --code-bg: #f3f4f6;
      --shadow: 0 24px 80px rgba(68, 55, 32, 0.08);
    }}
    * {{
      box-sizing: border-box;
    }}
    body {{
      margin: 0;
      padding: 0;
      font-family: "Iowan Old Style", "Palatino Linotype", "Book Antiqua", Palatino, Georgia, serif;
      background: var(--page-bg);
      color: var(--text);
      line-height: 1.6;
    }}
    main {{
      max-width: 1080px;
      margin: 2rem auto;
      background: var(--panel-bg);
      padding: 2.25rem;
      border: 1px solid var(--border);
      border-radius: 18px;
      box-shadow: var(--shadow);
      backdrop-filter: blur(6px);
    }}
    h1, h2, h3 {{
      font-family: Georgia, "Times New Roman", serif;
      line-height: 1.2;
      letter-spacing: -0.02em;
    }}
    h1 {{
      font-size: clamp(2rem, 4vw, 3.4rem);
      margin-top: 0;
    }}
    h2 {{
      margin-top: 2.2rem;
      padding-top: 0.2rem;
      border-top: 1px solid #eee4d6;
    }}
    p, li, table, code {{
      font-size: 1rem;
    }}
    .page-nav {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.75rem;
      margin-bottom: 1.5rem;
      color: var(--muted);
      font-size: 0.95rem;
    }}
    .page-nav a {{
      padding: 0.25rem 0.7rem;
      border: 1px solid var(--border);
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.75);
      text-decoration: none;
    }}
    .hero {{
      padding: 1.4rem 1.5rem;
      border: 1px solid var(--border);
      border-radius: 16px;
      background:
        radial-gradient(circle at top right, rgba(13, 92, 99, 0.12), transparent 32%),
        linear-gradient(135deg, rgba(229, 240, 239, 0.9), rgba(255, 249, 240, 0.95));
      margin-bottom: 1.8rem;
    }}
    .card-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 1rem;
      margin: 1.4rem 0 1.8rem;
    }}
    .card {{
      display: block;
      padding: 1rem 1.1rem;
      border: 1px solid var(--border);
      border-radius: 14px;
      background: #fffdf9;
      text-decoration: none;
      color: inherit;
    }}
    .card:hover {{
      border-color: #bba778;
      transform: translateY(-1px);
    }}
    .card strong {{
      display: block;
      font-size: 1.05rem;
      margin-bottom: 0.35rem;
    }}
    .note-box {{
      padding: 1rem 1.1rem;
      border-left: 4px solid var(--accent);
      background: var(--accent-soft);
      border-radius: 10px;
      margin: 1.25rem 0;
    }}
    .footer-note {{
      margin-top: 2rem;
      padding-top: 1rem;
      border-top: 1px solid var(--border);
      color: var(--muted);
      font-size: 0.95rem;
    }}
    pre {{
      overflow-x: auto;
      padding: 1rem;
      border-radius: 10px;
      position: relative;
      background: var(--code-bg);
      border: 1px solid #e1e3e8;
    }}
    .copy-code-btn {{
      position: absolute;
      top: 0.5rem;
      right: 0.5rem;
      border: 1px solid #c9c9c9;
      background: #fff;
      color: #222;
      border-radius: 4px;
      font-size: 0.75rem;
      padding: 0.2rem 0.5rem;
      cursor: pointer;
    }}
    .copy-code-btn:hover {{
      background: #f2f2f2;
    }}
    code {{
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    }}
    table {{
      border-collapse: collapse;
      width: auto;
      max-width: 100%;
      display: block;
      overflow-x: auto;
    }}
    th, td {{
      border: 1px solid #ddd;
      padding: 0.45rem 0.65rem;
      text-align: left;
      vertical-align: top;
      background: rgba(255, 255, 255, 0.8);
    }}
    a {{
      color: var(--accent);
    }}
    @media (max-width: 700px) {{
      main {{
        margin: 1rem;
        padding: 1.2rem;
      }}
      .page-nav {{
        gap: 0.5rem;
      }}
      .page-nav a {{
        font-size: 0.9rem;
      }}
    }}
  </style>
</head>
<body>
  <main>
{content}
  </main>
</body>
</html>
"""


def slugify(value):
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower())
    return slug.strip("-")


def rel_link(from_path, to_path):
    return os.path.relpath(to_path, start=from_path.parent).replace(os.sep, "/")


def _heading_plain_text(node):
    if isinstance(node, str):
        return node
    if isinstance(node, list):
        return "".join(_heading_plain_text(child) for child in node)
    children = getattr(node, "children", None)
    if children is None:
        return ""
    return _heading_plain_text(children)


class HeadingIdRenderer(HTMLRenderer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._heading_id_counts = {}

    def render_heading(self, element):
        rendered = self.render_children(element)
        text = _heading_plain_text(getattr(element, "children", "")).strip()
        base = slugify(text) or f"h{element.level}"
        count = self._heading_id_counts.get(base, 0) + 1
        self._heading_id_counts[base] = count
        heading_id = base if count == 1 else f"{base}-{count}"
        return f'<h{element.level} id="{heading_id}">{rendered}</h{element.level}>\n'


def parse_description(path):
    text = path.read_text(encoding="utf-8")
    metadata = {}
    body = text

    if text.startswith("---\n"):
        parts = text.split("\n---\n", 1)
        if len(parts) == 2:
            header_block = parts[0][4:]
            body = parts[1]
            for line in header_block.splitlines():
                if ":" not in line:
                    continue
                key, value = line.split(":", 1)
                metadata[key.strip()] = value.strip()

    return metadata, body.lstrip()


def load_serialized_payload(path):
    if path is None or path.suffix not in {".json", ".mrdi"}:
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def normalize_type_name(type_value):
    if isinstance(type_value, str):
        return type_value
    if isinstance(type_value, dict):
        name = type_value.get("name")
        if isinstance(name, str):
            return name
    return None


def extract_namespaces(parsed):
    namespaces = []
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


def discover_examples():
    examples = {}
    for group_dir in sorted(path for path in DATA_DIR.iterdir() if path.is_dir()):
        group_id = group_dir.name
        for example_dir in sorted(path for path in group_dir.iterdir() if path.is_dir()):
            description_path = example_dir / "description.md"
            if not description_path.exists():
                continue

            metadata, body = parse_description(description_path)
            example_slug = example_dir.name
            example_id = f"{group_id}-{example_slug}"

            systems = {}
            systems_root = example_dir / "systems"
            if systems_root.exists():
                for system_dir in sorted(path for path in systems_root.iterdir() if path.is_dir()):
                    data_file = next((p for p in sorted(system_dir.iterdir()) if p.name.startswith("data.")), None)
                    generate_file = next(
                        (p for p in sorted(system_dir.iterdir()) if p.name.startswith("generate.")), None
                    )
                    parsed_data = load_serialized_payload(data_file)
                    systems[system_dir.name] = {
                        "path": system_dir,
                        "data_file": data_file,
                        "generate_file": generate_file,
                        "parsed_data": parsed_data,
                        "root_type": normalize_type_name(parsed_data.get("_type")) if isinstance(parsed_data, dict) else None,
                        "namespaces": extract_namespaces(parsed_data),
                    }

            raw_order = metadata.get("order")
            parsed_order = None
            if raw_order is not None:
                try:
                    parsed_order = int(raw_order)
                except ValueError:
                    parsed_order = None

            examples[example_id] = {
                "id": example_id,
                "slug": example_slug,
                "output_relpath_md": f"rosetta/{group_id}/{example_slug}.md",
                "path": description_path,
                "title": metadata.get("title", example_slug),
                "category": metadata.get("category", metadata.get("group", group_id)),
                "subcategory": metadata.get("subcategory"),
                "order": parsed_order,
                "body": body,
                "systems": systems,
            }
    return examples


def build_system_index(examples):
    systems = {}
    for example_id, example in examples.items():
        for system_name, files in example["systems"].items():
            systems.setdefault(system_name, {})
            systems[system_name][example_id] = files
    return systems


def build_spec_catalog(examples):
    catalog = {}
    for spec in SPEC_PAGES:
        page = dict(spec)
        page["path_md"] = SPEC_DIR / f"{spec['id']}.md"
        page["example_ids"] = []
        catalog[spec["id"]] = page

    for example_id, example in examples.items():
        related_specs = set()
        for system in example["systems"].values():
            root_type = system.get("root_type")
            spec_id = TYPE_SPEC_BY_ROOT_TYPE.get(root_type)
            if spec_id:
                related_specs.add(spec_id)

            parsed_data = system.get("parsed_data")
            if isinstance(parsed_data, dict) and parsed_data.get("_refs"):
                related_specs.add("references-and-parameters")

        example["spec_ids"] = sorted(related_specs)
        for spec_id in example["spec_ids"]:
            if spec_id in catalog:
                catalog[spec_id]["example_ids"].append(example_id)

    return catalog


def language_for_file(path):
    return LANGUAGE_BY_SUFFIX.get(path.suffix, "")


def fenced_block(content, language):
    fence = "```"
    if "```" in content:
        fence = "````"
    return f"{fence}{language}\n{content.rstrip()}\n{fence}"


def render_data_for_markdown(path):
    raw = path.read_text(encoding="utf-8")
    if path.suffix in {".json", ".mrdi"}:
        try:
            parsed = json.loads(raw)
            return format_json_compact(parsed, indent_size=2, max_width=100)
        except json.JSONDecodeError:
            return raw
    return raw


def format_json_compact(value, indent_size=2, max_width=100):
    def inline_repr(obj):
        return json.dumps(obj, ensure_ascii=False, separators=(", ", ": "))

    def format_node(obj, level):
        current_indent = " " * (indent_size * level)
        next_indent = " " * (indent_size * (level + 1))

        if not isinstance(obj, (list, dict)):
            return json.dumps(obj, ensure_ascii=False)

        inline = inline_repr(obj)
        if len(current_indent) + len(inline) <= max_width:
            return inline

        if isinstance(obj, list):
            if not obj:
                return "[]"
            entries = []
            for item in obj:
                item_repr = format_node(item, level + 1)
                item_lines = item_repr.splitlines()
                entry = [next_indent + item_lines[0]]
                for line in item_lines[1:]:
                    if line.startswith(next_indent):
                        line = line[len(next_indent):]
                    entry.append(next_indent + line)
                entries.append("\n".join(entry))
            return "[\n" + ",\n".join(entries) + "\n" + current_indent + "]"

        if not obj:
            return "{}"

        entries = []
        for key, item in obj.items():
            item_repr = format_node(item, level + 1)
            item_lines = item_repr.splitlines()
            key_prefix = next_indent + json.dumps(key, ensure_ascii=False) + ": "
            if len(item_lines) == 1:
                entries.append(key_prefix + item_lines[0])
                continue
            entry_lines = [key_prefix + item_lines[0]]
            for line in item_lines[1:]:
                if line.startswith(next_indent):
                    line = line[len(next_indent):]
                entry_lines.append(next_indent + line)
            entries.append("\n".join(entry_lines))
        return "{\n" + ",\n".join(entries) + "\n" + current_indent + "}"

    return format_node(value, 0)


def render_page_nav(links):
    items = [f'<a href="{href}">{label}</a>' for label, href in links]
    return '<div class="page-nav">' + "".join(items) + "</div>"


def spec_link_lines(page_path, spec_ids, spec_catalog):
    if not spec_ids:
        return []

    lines = [
        "## Related Specification",
        "",
    ]
    for spec_id in spec_ids:
        spec_page = spec_catalog[spec_id]
        href = rel_link(page_path, spec_page["path_md"])
        lines.append(f"- [{spec_page['title']}]({href})")
    lines.append("")
    return lines


def build_front_page_markdown():
    return """<div class="hero">
<p><strong>The MaRDI File Format</strong></p>
<h1>The MaRDI File Format: A FAIR File Format for Mathematical Software</h1>
<p>This website has two complementary roles. It documents the file format itself, including terminology, structure, and profile-specific encodings, and it also collects a rosetta stone of worked examples that show how concrete mathematical objects are serialized in practice.</p>
<p>The format is JSON-based, but its semantics are intentionally tied to explicit namespaces and software versions. That keeps the container format stable while allowing mathematical software systems and their serializations to evolve over time.</p>
</div>

<div class="card-grid">
  <a class="card" href="./spec/index.md">
    <strong>The specification</strong>
    <span>Read the file-level rules, terminology, profile/version notes, and type pages.</span>
  </a>
  <a class="card" href="./rosetta/index.md">
    <strong>The rosetta stone</strong>
    <span>Browse concrete examples, generation code, and emitted `.mrdi` payloads.</span>
  </a>
</div>

## What this site covers

- The overall JSON object model, including `_type`, `data`, `_ns`, and `_refs`.
- Profile-specific encodings, with documented namespace and version tables derived from the example corpus.
- Cross-links between the specification and concrete serialized examples.

<div class="note-box">
The specification pages fix terminology explicitly. In particular, this site uses <strong>data type</strong> for the value named by <code>_type</code>, <strong>payload</strong> for the value under <code>data</code>, and <strong>profile</strong> for a namespace-specific encoding contract.
</div>

## Start here

- [Open the specification](./spec/index.md)
- [Open the rosetta stone](./rosetta/index.md)

<div class="footer-note">
<p><strong>Disclaimer.</strong> This prototype is part of ongoing work on a FAIR file format for mathematical software. Supported by <a href="https://www.mardi4nfdi.de">MaRDI</a> and by <a href="https://www.computeralgebra.de/sfb/">DFG SFB/TRR-195</a>.</p>
</div>
"""


def build_rosetta_index_markdown(examples, systems):
    system_names = sorted(systems.keys())
    category_rank = {name: idx for idx, name in enumerate(CATEGORY_TITLES.keys())}
    subcategory_rank = {
        category: {name: idx for idx, name in enumerate(titles.keys())}
        for category, titles in SUBCATEGORY_TITLES.items()
    }

    grouped_examples = {}
    for example_id, example in examples.items():
        grouped_examples.setdefault(example["category"], []).append(example_id)

    sorted_groups = sorted(
        grouped_examples.keys(),
        key=lambda name: (category_rank.get(name, 999), name.lower()),
    )

    lines = [
        render_page_nav(
            [
                ("Front Page", "../index.md"),
                ("Specification", "../spec/index.md"),
            ]
        ),
        "# Rosetta Stone",
        "",
        "This section is the example corpus. Each page contains a human-readable description, "
        "generation code when available, the emitted serialized data, and links back to the "
        "relevant specification pages.",
        "",
        "## Table of Contents",
        "",
    ]

    for group_id in sorted_groups:
        display_name = CATEGORY_TITLES.get(group_id, group_id.replace("-", " ").title())
        lines.append(f"- [{display_name}](#{slugify(display_name)})")
    lines.append("")

    for group_id in sorted_groups:
        display_name = CATEGORY_TITLES.get(group_id, group_id.replace("-", " ").title())
        lines.append(f"## {display_name}")
        lines.append("")
        group_examples = grouped_examples[group_id]

        subgrouped = {}
        for example_id in group_examples:
            sub = examples[example_id].get("subcategory") or "__other__"
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
                    examples[exid]["order"] if examples[exid]["order"] is not None else 10_000,
                    examples[exid]["title"].lower(),
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
                title = example["title"]
                relpath = f"./{example['category']}/{example['slug']}.md"
                row = [f"[{title}]({relpath})"]
                for system_name in visible_systems:
                    if example_id in systems[system_name]:
                        anchor = slugify(system_name)
                        row.append(f"[X]({relpath}#{anchor})")
                    else:
                        row.append("")
                lines.append("| " + " | ".join(row) + " |")
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def build_example_markdown(example, systems, spec_catalog):
    body = example["body"].rstrip()

    available_systems = [
        system_name
        for system_name in sorted(systems.keys())
        if example["id"] in systems[system_name]
    ]

    page_path = SITE_DIR / example["output_relpath_md"]
    lines = [
        render_page_nav(
            [
                ("Front Page", rel_link(page_path, ROOT_INDEX_MD)),
                ("Rosetta Stone", rel_link(page_path, ROSETTA_INDEX_MD)),
                ("Specification", rel_link(page_path, SPEC_INDEX_MD)),
            ]
        ),
        f"# {example['title']}",
        "",
        body,
        "",
    ]

    lines.extend(spec_link_lines(page_path, example.get("spec_ids", []), spec_catalog))

    lines.extend(
        [
            "## Systems",
            "",
        ]
    )

    for system_name in available_systems:
        lines.append(f"### {system_name}")
        lines.append("")

        system_example = systems[system_name].get(example["id"])
        generate_file = system_example["generate_file"]
        data_file = system_example["data_file"]

        if generate_file is not None:
            lines.append(f"#### Generate code (`{generate_file.name}`)")
            lines.append("")
            code = generate_file.read_text(encoding="utf-8")
            lines.append(fenced_block(code, language_for_file(generate_file)))
            lines.append("")

        if data_file is not None:
            lines.append(f"#### Data file (`{data_file.name}`)")
            lines.append("")
            data = render_data_for_markdown(data_file)
            lines.append(fenced_block(data, language_for_file(data_file)))
            lines.append("")

        if generate_file is None and data_file is None:
            lines.append("No generator or data file available for this system.")
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def render_profiles_table(example_ids, examples, page_path):
    rows = []
    for example_id in example_ids:
        example = examples[example_id]
        example_path = SITE_DIR / example["output_relpath_md"]
        example_href = rel_link(page_path, example_path)
        for system_name, system in sorted(example["systems"].items()):
            namespaces = system.get("namespaces") or [{"name": "", "url": "", "version": ""}]
            for namespace in namespaces:
                namespace_name = namespace["name"] or system_name
                version = namespace["version"] or "unspecified"
                url = namespace["url"]
                profile_label = namespace_name
                if url:
                    profile_label = f"[{namespace_name}]({url})"
                rows.append(
                    f"| {profile_label} | `{version}` | [{example['title']}]({example_href}) | `{system.get('root_type') or ''}` |"
                )

    if not rows:
        return ["No documented profiles yet.", ""]

    return [
        "| Profile | Version | Example | Root type |",
        "| --- | --- | --- | --- |",
        *rows,
        "",
    ]


def sample_payload_for_spec(spec_id, example_ids, examples):
    for example_id in example_ids:
        example = examples[example_id]
        for system in example["systems"].values():
            root_type = system.get("root_type")
            if TYPE_SPEC_BY_ROOT_TYPE.get(root_type) == spec_id and system.get("data_file") is not None:
                return render_data_for_markdown(system["data_file"])
    return None


def build_spec_index_markdown(spec_catalog):
    type_pages = [
        spec
        for spec in SPEC_PAGES
        if spec["id"]
        not in {"data-model", "namespaces-and-versions", "references-and-parameters"}
    ]
    lines = [
        render_page_nav(
            [
                ("Front Page", "../index.md"),
                ("Rosetta Stone", "../rosetta/index.md"),
            ]
        ),
        "# Specification",
        "",
        "This section describes the MaRDI file format itself. It fixes terminology, explains "
        "the overall JSON object model, documents namespaces and versioned profiles, and "
        "collects type-level encoding notes linked to concrete examples in the rosetta stone.",
        "",
        "## Core pages",
        "",
        f"- [Overall Data Model](./data-model.md)",
        f"- [Namespaces, Profiles, and Versions](./namespaces-and-versions.md)",
        f"- [References and Parameters](./references-and-parameters.md)",
        "",
        "## Data Types",
        "",
    ]

    for spec in type_pages:
        lines.append(f"- [{spec['title']}](./{spec['id']}.md)")

    lines.extend(
        [
            "",
            "## Schema Basis",
            "",
            "The current schema basis used by this prototype is reproduced below from "
            "`paper/data.json`, which in turn reflects the JSON Schema discussion from the paper.",
            "",
            fenced_block(render_data_for_markdown(SCHEMA_PATH), "json"),
            "",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def build_spec_page_markdown(spec_page, spec_catalog, examples):
    page_path = spec_page["path_md"]
    lines = [
        render_page_nav(
            [
                ("Front Page", rel_link(page_path, ROOT_INDEX_MD)),
                ("Specification Index", rel_link(page_path, SPEC_INDEX_MD)),
                ("Rosetta Stone", rel_link(page_path, ROSETTA_INDEX_MD)),
            ]
        ),
        f"# {spec_page['title']}",
        "",
        spec_page["lede"],
        "",
    ]

    for heading, bullets in spec_page["sections"]:
        lines.append(f"## {heading}")
        lines.append("")
        for bullet in bullets:
            lines.append(f"- {bullet}")
        lines.append("")

    sample = sample_payload_for_spec(spec_page["id"], spec_page["example_ids"], examples)
    if sample is not None:
        lines.extend(
            [
                "## Canonical Example Payload",
                "",
                "The following payload is taken directly from the current rosetta-stone corpus.",
                "",
                fenced_block(sample, "json"),
                "",
            ]
        )

    lines.extend(
        [
            "## Documented Profiles in This Corpus",
            "",
            "This table records the profile/version pairs currently represented by the "
            "rosetta-stone examples for this data type. Add new rows as new systems or "
            "encoding revisions are documented.",
            "",
        ]
    )
    lines.extend(render_profiles_table(spec_page["example_ids"], examples, page_path))

    if spec_page["example_ids"]:
        lines.extend(
            [
                "## Rosetta Stone Examples",
                "",
            ]
        )
        for example_id in spec_page["example_ids"]:
            example = examples[example_id]
            example_href = rel_link(page_path, SITE_DIR / example["output_relpath_md"])
            lines.append(f"- [{example['title']}]({example_href})")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def rewrite_markdown_links(md_text):
    pattern = re.compile(r"(\[[^\]]+\]\()((?:\./|\.\./)[^)\s]+)\)")

    def replace_link(match):
        prefix = match.group(1)
        target = match.group(2)
        if ".md" in target:
            target = re.sub(r"\.md(?=(#|$))", ".html", target)
        return f"{prefix}{target})"

    return pattern.sub(replace_link, md_text)


def markdown_to_html(md_text):
    text = rewrite_markdown_links(md_text)
    renderer = marko.Markdown(renderer=HeadingIdRenderer, extensions=["gfm"])
    return renderer.convert(text)


def extract_title(md_text, fallback):
    for line in md_text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    match = re.search(r"<h1>(.*?)</h1>", md_text, flags=re.IGNORECASE | re.DOTALL)
    if match:
        return re.sub(r"<[^>]+>", "", match.group(1)).strip() or fallback
    return fallback


def render_html_page(md_path):
    md_text = md_path.read_text(encoding="utf-8")
    content_html = markdown_to_html(md_text)
    title = extract_title(md_text, md_path.stem)
    full_html = HTML_TEMPLATE.format(title=title, content=content_html)
    html_path = md_path.with_suffix(".html")
    html_path.write_text(full_html, encoding="utf-8")
    print(f"Wrote {html_path}")


def main():
    examples = discover_examples()
    systems = build_system_index(examples)
    spec_catalog = build_spec_catalog(examples)

    SITE_DIR.mkdir(parents=True, exist_ok=True)
    for old_file in SITE_DIR.rglob("*"):
        if old_file.is_file() and old_file.suffix in {".md", ".html"}:
            old_file.unlink()

    ROOT_INDEX_MD.write_text(build_front_page_markdown(), encoding="utf-8")
    ROSETTA_INDEX_MD.parent.mkdir(parents=True, exist_ok=True)
    ROSETTA_INDEX_MD.write_text(build_rosetta_index_markdown(examples, systems), encoding="utf-8")
    SPEC_INDEX_MD.parent.mkdir(parents=True, exist_ok=True)
    SPEC_INDEX_MD.write_text(build_spec_index_markdown(spec_catalog), encoding="utf-8")

    for spec_id in sorted(spec_catalog.keys()):
        spec_page = spec_catalog[spec_id]
        spec_page["path_md"].write_text(
            build_spec_page_markdown(spec_page, spec_catalog, examples),
            encoding="utf-8",
        )
        print(f"Wrote {spec_page['path_md']}")

    for example_id in sorted(examples.keys()):
        example_page_path = SITE_DIR / examples[example_id]["output_relpath_md"]
        example_page_path.parent.mkdir(parents=True, exist_ok=True)
        page_content = build_example_markdown(examples[example_id], systems, spec_catalog)
        example_page_path.write_text(page_content, encoding="utf-8")
        print(f"Wrote {example_page_path}")

    print(f"Wrote {ROOT_INDEX_MD}")
    print(f"Wrote {ROSETTA_INDEX_MD}")
    print(f"Wrote {SPEC_INDEX_MD}")

    for md_path in sorted(SITE_DIR.rglob("*.md")):
        render_html_page(md_path)


if __name__ == "__main__":
    main()
