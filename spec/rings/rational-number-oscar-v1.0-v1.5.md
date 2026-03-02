---
title: Rational Numbers (`OSCAR v1.0-v1.5`)
concept: rational-number
kind: type
order: 7
profiles: [oscar-v1.0, oscar-v1.1, oscar-v1.2, oscar-v1.3, oscar-v1.4, oscar-v1.5]
---
In OSCAR v1.0 through v1.5, rational numbers are encoded with the bare type name
`"QQFieldElem"` and a textual fraction payload.

## Encoding rules

- Use `_type: "QQFieldElem"`.
- Store the rational value under `data` using a textual fraction such as `"42//23"`.
- The ambient field is implicit in the type name.

{{ CANONICAL_EXAMPLE_PAYLOAD }}

{{ DOCUMENTED_PROFILES }}

{{ ROSETTA_EXAMPLES }}
