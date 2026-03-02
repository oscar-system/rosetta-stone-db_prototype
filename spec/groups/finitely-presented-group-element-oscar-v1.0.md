---
title: Elements of Finitely Presented Groups (`OSCAR v1.0`)
concept: finitely-presented-group-element
kind: type
order: 2
profiles: [oscar-v1.0]
---
In OSCAR v1.0, `FPGroupElem` uses a bare `_type` string, and its ambient group
is encoded directly inside the parameter payload.

## Encoding Notes

- Use `_type: "FPGroupElem"`.
- Store the word data under `data`.
- Inline the parent group description in the element parameters rather than
  referring to `_refs`.

{{ CANONICAL_EXAMPLE_PAYLOAD }}

{{ DOCUMENTED_PROFILES }}

{{ ROSETTA_EXAMPLES }}
