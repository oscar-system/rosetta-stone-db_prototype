---
title: Rational Numbers
kind: type
order: 8
---

Rational numbers are represented as typed values whose payload is a textual
fraction such as `"42//23"`. The field context is part of the type.

## Encoding rules

- Use a typed encoding such as `QQFieldElem` rather than a bare JSON number.
- Store the rational value under `data` using the profile's textual normal form.
- Record the ambient field in `_type.params` when required by the profile.

{{ CANONICAL_EXAMPLE_PAYLOAD }}

{{ DOCUMENTED_PROFILES }}

{{ ROSETTA_EXAMPLES }}
