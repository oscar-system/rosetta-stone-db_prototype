---
title: Subgroups of Pc Groups (`OSCAR v1.1-v1.3`)
concept: subgroup-of-pc-group
kind: type
order: 14
profiles: [oscar-v1.1, oscar-v1.2, oscar-v1.3]
---
In OSCAR v1.1 through v1.3, `SubPcGroup` uses the bare type name
`"SubPcGroup"` and stores its parent-group context through `_refs`.

## Encoding Notes

- Use `_type: "SubPcGroup"`.
- Store subgroup data under `data`.
- Refer to the parent group through `_refs`.

{{ CANONICAL_EXAMPLE_PAYLOAD }}

{{ DOCUMENTED_PROFILES }}

{{ ROSETTA_EXAMPLES }}
