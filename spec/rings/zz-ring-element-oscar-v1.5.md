---
title: ZZRingElem (`OSCAR v1.5`)
concept: zz-ring-element
kind: type
order: 5
profiles: [oscar-v1.5]
---
In OSCAR v1.5, elements of `ZZ` are encoded with the bare type name
`"ZZRingElem"` and a decimal string payload.

## Encoding rules

- Use `_type: "ZZRingElem"`.
- Store the value under `data` as a decimal string.
- The ambient ring is implicit in the type name.

{{ CANONICAL_EXAMPLE_PAYLOAD }}

{{ DOCUMENTED_PROFILES }}

{{ ROSETTA_EXAMPLES }}
