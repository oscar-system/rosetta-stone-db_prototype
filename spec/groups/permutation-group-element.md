---
title: Permutation Group Elements (`OSCAR v1.6-v1.8`)
concept: permutation-group-element
kind: type
order: 11
profiles: [oscar-v1.6, oscar-v1.7, oscar-v1.8]
---
In OSCAR v1.6 through v1.8, `PermGroupElem` refers to a `PermGroup` whose
attributes live in a top-level `attrs` block and use the newer nested encodings.

## Encoding Notes

- Use `_type: "PermGroupElem"`.
- Store the permutation word under `data`.
- Refer to the parent group according to the matching OSCAR v1.6-v1.8
  `PermGroup` encoding.

{{ CANONICAL_EXAMPLE_PAYLOAD }}

{{ DOCUMENTED_PROFILES }}

{{ ROSETTA_EXAMPLES }}
