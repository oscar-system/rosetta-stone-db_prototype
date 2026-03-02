---
title: Elements of Finitely Presented Groups (`OSCAR v1.4-v1.8`)
concept: finitely-presented-group-element
kind: type
order: 2
profiles: [oscar-v1.4, oscar-v1.5, oscar-v1.6, oscar-v1.7, oscar-v1.8]
---
In OSCAR v1.4 through v1.8, `FPGroupElem` uses a typed `_type` object and
refers to its parent group through `_type.params` and `_refs`.

## Encoding Notes

- Use a typed `_type` object whose `name` is `"FPGroupElem"`.
- Store the word data under `data`.
- Refer to the parent group through `_type.params`.

{{ CANONICAL_EXAMPLE_PAYLOAD }}

{{ DOCUMENTED_PROFILES }}

{{ ROSETTA_EXAMPLES }}
