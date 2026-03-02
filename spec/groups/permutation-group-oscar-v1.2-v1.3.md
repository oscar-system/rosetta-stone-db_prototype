---
title: Permutation Groups (`OSCAR v1.2-v1.3`)
concept: permutation-group
kind: type
order: 10
profiles: [oscar-v1.2, oscar-v1.3]
---
In OSCAR v1.2 and v1.3, `PermGroup` still uses the bare type name
`"PermGroup"`, but group attributes are nested inside `data.attrs`.

## Encoding Notes

- Use `_type: "PermGroup"`.
- Store the degree and generators under `data`.
- Store attributes under `data.attrs`.

{{ CANONICAL_EXAMPLE_PAYLOAD }}

{{ DOCUMENTED_PROFILES }}

{{ ROSETTA_EXAMPLES }}
