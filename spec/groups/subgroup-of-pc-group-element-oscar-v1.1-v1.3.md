---
title: Elements of Subgroups of Pc Groups (`OSCAR v1.1-v1.3`)
concept: subgroup-of-pc-group-element
kind: type
order: 15
profiles: [oscar-v1.1, oscar-v1.2, oscar-v1.3]
---
In OSCAR v1.1 through v1.3, `SubPcGroupElem` uses the bare type name
`"SubPcGroupElem"` and refers to its subgroup context through `_refs`.

## Encoding Notes

- Use `_type: "SubPcGroupElem"`.
- Store the exponent vector under `data`.
- Refer to the subgroup context through `_refs`.

{{ CANONICAL_EXAMPLE_PAYLOAD }}

{{ DOCUMENTED_PROFILES }}

{{ ROSETTA_EXAMPLES }}
