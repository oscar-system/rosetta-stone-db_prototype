---
title: Integers
kind: type
order: 2
profiles: [basic-v1]
---

Integer-valued data appears in several closely related data types, including
machine integers such as `Base.Int`, arbitrary-precision integers such as
`BigInt`, and machine-sized variants such as `Int16` and `UInt64`.

## Encoding rules

- Encode the value under `data` as a decimal string.
- Use `_type` to distinguish the specific integer family instead of overloading
  one generic integer name.
- Reserve application-specific algebraic integer encodings such as `ZZRingElem`
  for their dedicated profile-specific pages.

{{ CANONICAL_EXAMPLE_PAYLOAD }}

{{ DOCUMENTED_PROFILES }}

{{ ROSETTA_EXAMPLES }}
