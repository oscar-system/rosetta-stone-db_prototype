---
title: Permutation Group Elements (`OSCAR v1.4-v1.5`)
concept: permutation-group-element
kind: type
order: 11
profiles: [oscar-v1.4, oscar-v1.5]
---
In OSCAR v1.4 and v1.5, `PermGroupElem` still uses the bare type name, and its
parent group follows the `PermGroup` variant with top-level `attrs`.

## Encoding Notes

- Use `_type: "PermGroupElem"`.
- Store the permutation word under `data`.
- Refer to the parent group according to the matching `PermGroup` encoding.

{{ CANONICAL_EXAMPLE_PAYLOAD }}

{{ DOCUMENTED_PROFILES }}

{{ ROSETTA_EXAMPLES }}
