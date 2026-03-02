---
title: Permutation Group Elements (`OSCAR v1.2-v1.3`)
concept: permutation-group-element
kind: type
order: 11
profiles: [oscar-v1.2, oscar-v1.3]
---
In OSCAR v1.2 and v1.3, `PermGroupElem` still uses the bare type name, and its
parent group follows the `PermGroup` variant with nested `data.attrs`.

## Encoding Notes

- Use `_type: "PermGroupElem"`.
- Store the permutation word under `data`.
- Refer to the parent group according to the matching `PermGroup` encoding.

{{ CANONICAL_EXAMPLE_PAYLOAD }}

{{ DOCUMENTED_PROFILES }}

{{ ROSETTA_EXAMPLES }}
