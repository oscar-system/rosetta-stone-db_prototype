---
title: Pc Groups (`OSCAR v1.1-v1.3`)
concept: pc-group
kind: type
order: 8
profiles: [oscar-v1.1, oscar-v1.2, oscar-v1.3]
---
In OSCAR v1.1 through v1.3, `PcGroup` still uses the bare type name
`"PcGroup"`, but the main GAP payload is moved behind `_refs`.

## Encoding Notes

- Use `_type: "PcGroup"`.
- Store the group payload as a reference id under `data`.
- Resolve the referenced object through `_refs`.

{{ CANONICAL_EXAMPLE_PAYLOAD }}

{{ DOCUMENTED_PROFILES }}

{{ ROSETTA_EXAMPLES }}
