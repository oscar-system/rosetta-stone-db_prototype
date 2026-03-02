---
title: Finite Field Elements
kind: type
order: 4
profiles: [oscar-v1.0, oscar-v1.1, oscar-v1.2, oscar-v1.3, oscar-v1.4, oscar-v1.5, oscar-v1.6, oscar-v1.7, oscar-v1.8]
---
`FqFieldElem` represents elements of finite fields in the current OSCAR profile.

## Encoding Notes

- Set `_type` to the concrete finite-field element type used by the active profile.
- Encode the payload together with whatever ambient references are required to recover the parent field.
- Treat the linked examples as the current authoritative shape for this prototype.

{{ CANONICAL_EXAMPLE_PAYLOAD }}

{{ DOCUMENTED_PROFILES }}

{{ ROSETTA_EXAMPLES }}
