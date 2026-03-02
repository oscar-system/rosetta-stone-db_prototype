---
title: Pc Groups (`OSCAR v1.4-v1.8`)
concept: pc-group
kind: type
order: 8
profiles: [oscar-v1.4, oscar-v1.5, oscar-v1.6, oscar-v1.7, oscar-v1.8]
---
In OSCAR v1.4 through v1.8, `PcGroup` uses a typed `_type` object and relies
on `_refs` for the underlying GAP data.

## Encoding Notes

- Use a typed `_type` object whose `name` is `"PcGroup"`.
- Store the parent-group reference inside `_type.params`.
- Resolve the underlying GAP payload through `_refs`.

{{ CANONICAL_EXAMPLE_PAYLOAD }}

{{ DOCUMENTED_PROFILES }}

{{ ROSETTA_EXAMPLES }}
