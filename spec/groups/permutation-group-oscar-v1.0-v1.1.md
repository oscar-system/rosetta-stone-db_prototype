---
title: Permutation Groups (`OSCAR v1.0-v1.1`)
concept: permutation-group
kind: type
order: 10
profiles: [oscar-v1.0, oscar-v1.1]
---
In OSCAR v1.0 and v1.1, `PermGroup` is encoded with a bare `_type` string and
all group attributes live directly inside `data`.

## Encoding Notes

- Use `_type: "PermGroup"`.
- Store the degree and generators under `data`.
- No top-level `attrs` block is used.

{{ CANONICAL_EXAMPLE_PAYLOAD }}

{{ DOCUMENTED_PROFILES }}

{{ ROSETTA_EXAMPLES }}
