---
title: Weyl Group Elements (`OSCAR v1.2`)
concept: weyl-group-element
kind: type
order: 7
profiles: [oscar-v1.2]
---
In OSCAR v1.2, `WeylGroupElem` already uses a typed `_type` object, but it
refers to a `WeylGroup` encoded with the older bare-type representation.

## Encoding Notes

- Use `_type.name = "WeylGroupElem"`.
- Store the reduced word under `data`.
- Refer to the parent group according to the OSCAR v1.2 `WeylGroup` encoding.

{{ CANONICAL_EXAMPLE_PAYLOAD }}

{{ DOCUMENTED_PROFILES }}

{{ ROSETTA_EXAMPLES }}
