---
title: ZZRingElem (`OSCAR v1.6-v1.8`)
concept: zz-ring-element
kind: type
order: 6
profiles: [oscar-v1.6, oscar-v1.7, oscar-v1.8]
---
From OSCAR v1.6 onward, elements of `ZZ` are encoded as parametric typed
values that make the ambient ring explicit.

## Encoding rules

- Use a typed `_type` object with `name: "ZZRingElem"`.
- Record the ambient ring in `_type.params`, typically as `{"_type": "ZZRing"}`.
- Store the value under `data` as a decimal string.

{{ CANONICAL_EXAMPLE_PAYLOAD }}

{{ DOCUMENTED_PROFILES }}

{{ ROSETTA_EXAMPLES }}
