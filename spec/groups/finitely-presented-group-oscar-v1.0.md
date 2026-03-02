---
title: Finitely Presented Groups (`OSCAR v1.0`)
concept: finitely-presented-group
kind: type
order: 1
profiles: [oscar-v1.0]
---
In OSCAR v1.0, `FPGroup` is encoded with a bare `_type` string and an inline
`data.X` payload that stores the underlying GAP object directly.

## Encoding Notes

- Use `_type: "FPGroup"`.
- Store the underlying group description directly under `data.X`.
- No `_refs` indirection is used for the ambient group payload.

{{ CANONICAL_EXAMPLE_PAYLOAD }}

{{ DOCUMENTED_PROFILES }}

{{ ROSETTA_EXAMPLES }}
