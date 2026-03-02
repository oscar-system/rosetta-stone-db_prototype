---
title: Weyl Group Elements (`OSCAR v1.3`)
concept: weyl-group-element
kind: type
order: 7
profiles: [oscar-v1.3]
---
In OSCAR v1.3, `WeylGroupElem` still uses a typed `_type` object, but its
payload shape differs from OSCAR v1.2 before the surrounding `WeylGroup`
encoding changes again in OSCAR v1.4.

## Encoding Notes

- Use `_type.name = "WeylGroupElem"`.
- Store the reduced word under `data`.
- Refer to the parent group according to the OSCAR v1.3 `WeylGroup` encoding.

{{ CANONICAL_EXAMPLE_PAYLOAD }}

{{ DOCUMENTED_PROFILES }}

{{ ROSETTA_EXAMPLES }}
