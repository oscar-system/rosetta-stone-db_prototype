---
title: Integers
kind: type
order: 2
profiles: [basic-v1]
---

Integer-valued data appears in several closely related data types, including
machine integers such as `Base.Int`, arbitrary-precision integers such as
`BigInt`, and algebraic integers such as `ZZRingElem`.

## Encoding rules

- Encode the value under `data` as a decimal string.
- Use `_type` to distinguish the specific integer family instead of overloading
  one generic integer name.
- When an integer value depends on ambient algebraic structure, use a parametric
  type such as `ZZRingElem` with the required context in `params` or `_refs`.

{{ CANONICAL_EXAMPLE_PAYLOAD }}

{{ DOCUMENTED_PROFILES }}

{{ ROSETTA_EXAMPLES }}
