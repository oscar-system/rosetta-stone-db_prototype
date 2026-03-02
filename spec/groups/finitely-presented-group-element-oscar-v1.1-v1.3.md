---
title: Elements of Finitely Presented Groups (`OSCAR v1.1-v1.3`)
concept: finitely-presented-group-element
kind: type
order: 2
profiles: [oscar-v1.1, oscar-v1.2, oscar-v1.3]
---
In OSCAR v1.1 through v1.3, `FPGroupElem` keeps the bare type name
`"FPGroupElem"`, but its parent group is referenced through `_refs`.

## Encoding Notes

- Use `_type: "FPGroupElem"`.
- Store the word data under `data`.
- Refer to the parent group through a reference id stored in the parameters.

{{ CANONICAL_EXAMPLE_PAYLOAD }}

{{ DOCUMENTED_PROFILES }}

{{ ROSETTA_EXAMPLES }}
