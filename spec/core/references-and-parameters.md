---
title: References and Parameters
kind: core
order: 3
profiles: [basic-v1]
---

Complex mathematical objects often depend on ambient rings, fields, spaces, or
other context that should be stored once and reused. The format handles this
with parametric types and UUID-addressed reference objects.

## Rules

- When a type depends on contextual objects, encode that dependency in
  `_type.params`.
- If the parameter is itself a structured object, place it in `_refs` and refer
  to it by UUID.
- Use `_refs` for recursive constructions, shared ambient objects, and cases
  where object identity matters beyond isomorphism.
- UUID keys in `_refs` should remain stable throughout the active producing
  session.

## Why this matters

- Two mathematically isomorphic objects can still play different computational
  roles, and the reference graph preserves that distinction.
- A later consumer can reconstruct the full serialization context instead of
  reverse-engineering it from the payload alone.

{{ DOCUMENTED_PROFILES }}

{{ ROSETTA_EXAMPLES }}
