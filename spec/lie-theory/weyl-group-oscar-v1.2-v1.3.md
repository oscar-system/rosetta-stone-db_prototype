---
title: Weyl Groups (`OSCAR v1.2-v1.3`)
concept: weyl-group
kind: type
order: 6
profiles: [oscar-v1.2, oscar-v1.3]
---
In OSCAR v1.2 and v1.3, `WeylGroup` uses the bare type name `"WeylGroup"` and
stores the ambient root system reference under `data.root_system`.

## Encoding Notes

- Use `_type: "WeylGroup"`.
- Store the referenced root system under `data.root_system`.
- Resolve that reference through `_refs`.

{{ CANONICAL_EXAMPLE_PAYLOAD }}

{{ DOCUMENTED_PROFILES }}

{{ ROSETTA_EXAMPLES }}
