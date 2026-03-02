---
title: Elements of Subgroups of Finitely Presented Groups (`OSCAR v1.1-v1.3`)
concept: subgroup-of-finitely-presented-group-element
kind: type
order: 13
profiles: [oscar-v1.1, oscar-v1.2, oscar-v1.3]
---
In OSCAR v1.1 through v1.3, `SubFPGroupElem` uses the bare type name
`"SubFPGroupElem"` and refers to its subgroup context through `_refs`.

## Encoding Notes

- Use `_type: "SubFPGroupElem"`.
- Store the word data under `data`.
- Refer to the ambient subgroup through `_refs`.

{{ CANONICAL_EXAMPLE_PAYLOAD }}

{{ DOCUMENTED_PROFILES }}

{{ ROSETTA_EXAMPLES }}
