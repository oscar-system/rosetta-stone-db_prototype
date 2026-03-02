---
title: Subgroups of Finitely Presented Groups (`OSCAR v1.1-v1.3`)
concept: subgroup-of-finitely-presented-group
kind: type
order: 12
profiles: [oscar-v1.1, oscar-v1.2, oscar-v1.3]
---
In OSCAR v1.1 through v1.3, `SubFPGroup` uses the bare type name
`"SubFPGroup"` and records the ambient parent by reference through `_refs`.

## Encoding Notes

- Use `_type: "SubFPGroup"`.
- Store subgroup data under `data`.
- Refer to the parent group through `_refs`.

{{ CANONICAL_EXAMPLE_PAYLOAD }}

{{ DOCUMENTED_PROFILES }}

{{ ROSETTA_EXAMPLES }}
