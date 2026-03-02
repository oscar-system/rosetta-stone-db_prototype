---
title: Finitely Presented Groups (`OSCAR v1.1-v1.3`)
concept: finitely-presented-group
kind: type
order: 1
profiles: [oscar-v1.1, oscar-v1.2, oscar-v1.3]
---
In OSCAR v1.1 through v1.3, `FPGroup` still uses the bare type name
`"FPGroup"`, but the ambient GAP object moves into `_refs` and `data.X`
becomes a reference id.

## Encoding Notes

- Use `_type: "FPGroup"`.
- Store the group payload under `data.X` as a reference id.
- Resolve that reference through `_refs`.

{{ CANONICAL_EXAMPLE_PAYLOAD }}

{{ DOCUMENTED_PROFILES }}

{{ ROSETTA_EXAMPLES }}
