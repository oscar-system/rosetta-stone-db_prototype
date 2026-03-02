---
title: Overall Data Model
kind: core
order: 1
profiles: [basic-v1]
---

The MaRDI file format stores mathematical objects as annotated JSON trees. A
file combines type information, serialized data, namespaces, and optional
reference objects that provide the context required to interpret the payload.

## Terminology

- A **file** is the top-level JSON object.
- A **data type** is the value of `_type`, either as a string or as an object
  with a `name` and optional `params`.
- A **payload** is the subtree stored under `data`.
- A **profile** is a namespace-specific encoding contract, for example the Oscar
  profile identified by an `Oscar` entry in `_ns`.
- A **reference object** is an entry in `_refs`, addressed by UUID and reused
  from types or payloads.

## Core object members

- `_type` is required and names the data type that determines how `data` must
  be interpreted.
- `data` stores the serialized payload; it may be a string, array, object, or a
  foreign schema-defined subtree.
- `_ns` declares which namespace and software version define the semantics.
- `_refs` stores referenced objects so recursive and shared constructions can be
  serialized without duplication.

## Design intent

- The format follows the paper's approach of separating syntax from semantics:
  JSON fixes the container syntax, while semantics are supplied by a concrete
  namespace and version.
- The format is intentionally extensible. New types, new namespaces, and
  namespace-specific payloads can be added without redesigning the whole file
  format.
- References are session-stable UUIDs rather than position-based indices, which
  makes reused mathematical context easier to track across files and workflows.
