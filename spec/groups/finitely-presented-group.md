---
title: Finitely Presented Groups (`OSCAR v1.4-v1.8`)
concept: finitely-presented-group
kind: type
order: 1
profiles: [oscar-v1.4, oscar-v1.5, oscar-v1.6, oscar-v1.7, oscar-v1.8]
---
In OSCAR v1.4 through v1.8, `FPGroup` moves to a typed `_type` object and the
ambient GAP data is carried through `_type.params` and `_refs`.

## Encoding Notes

- Use a typed `_type` object whose `name` is `"FPGroup"`.
- Store the parent-group reference inside `_type.params`.
- The root `data` payload is empty; the ambient GAP object is resolved through
  `_refs`.

{{ CANONICAL_EXAMPLE_PAYLOAD }}

{{ DOCUMENTED_PROFILES }}

{{ ROSETTA_EXAMPLES }}
