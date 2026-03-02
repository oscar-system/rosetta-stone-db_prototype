---
title: Permutation Group Elements (`OSCAR v1.0-v1.1`)
concept: permutation-group-element
kind: type
order: 11
profiles: [oscar-v1.0, oscar-v1.1]
---
In OSCAR v1.0 and v1.1, `PermGroupElem` uses the bare type name and refers to a
parent permutation group whose attributes, if any, remain inside `data`.

## Encoding Notes

- Use `_type: "PermGroupElem"`.
- Store the permutation word under `data`.
- Refer to the parent group according to the matching `PermGroup` encoding.

{{ CANONICAL_EXAMPLE_PAYLOAD }}

{{ DOCUMENTED_PROFILES }}

{{ ROSETTA_EXAMPLES }}
