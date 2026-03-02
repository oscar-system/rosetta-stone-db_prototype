---
title: Permutation Groups (`OSCAR v1.4-v1.5`)
concept: permutation-group
kind: type
order: 10
profiles: [oscar-v1.4, oscar-v1.5]
---
In OSCAR v1.4 and v1.5, `PermGroup` moves attributes out of `data` into a
top-level `attrs` dictionary, while the root type is still the bare string
`"PermGroup"`.

## Encoding Notes

- Use `_type: "PermGroup"`.
- Store the degree and generators under `data`.
- Store group attributes under top-level `attrs`.

{{ CANONICAL_EXAMPLE_PAYLOAD }}

{{ DOCUMENTED_PROFILES }}

{{ ROSETTA_EXAMPLES }}
