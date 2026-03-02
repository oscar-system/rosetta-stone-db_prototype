---
title: Pc Groups (`OSCAR v1.0`)
concept: pc-group
kind: type
order: 8
profiles: [oscar-v1.0]
---
In OSCAR v1.0, `PcGroup` is encoded with a bare `_type` string and an inline
payload for the underlying GAP object.

## Encoding Notes

- Use `_type: "PcGroup"`.
- Store the underlying GAP object directly inside `data`.
- No `_refs` indirection is used for the group payload.

{{ CANONICAL_EXAMPLE_PAYLOAD }}

{{ DOCUMENTED_PROFILES }}

{{ ROSETTA_EXAMPLES }}
