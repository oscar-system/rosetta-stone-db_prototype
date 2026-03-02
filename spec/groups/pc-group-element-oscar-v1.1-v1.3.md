---
title: Pc Group Elements (`OSCAR v1.1-v1.3`)
concept: pc-group-element
kind: type
order: 9
profiles: [oscar-v1.1, oscar-v1.2, oscar-v1.3]
---
In OSCAR v1.1 through v1.3, `PcGroupElem` keeps the bare type name
`"PcGroupElem"`, but its parent group is referenced through `_refs`.

## Encoding Notes

- Use `_type: "PcGroupElem"`.
- Store the exponent vector under `data`.
- Refer to the parent group through a reference id in the parameters.

{{ CANONICAL_EXAMPLE_PAYLOAD }}

{{ DOCUMENTED_PROFILES }}

{{ ROSETTA_EXAMPLES }}
