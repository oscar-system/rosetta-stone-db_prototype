---
title: Univariate Polynomial
kind: type
order: 10
---

A univariate polynomial payload is interpreted relative to a polynomial ring
stored in `_type.params` or `_refs`. The coefficients and exponents are encoded
as structured JSON data rather than as presentation text.

## Encoding rules

- Set `_type` to an object with `name: "PolyRingElem"`.
- Use `_type.params` to point to the ambient polynomial ring.
- Encode each term structurally under `data` so that reconstruction does not
  depend on parsing pretty-printed algebra.

{{ CANONICAL_EXAMPLE_PAYLOAD }}

{{ DOCUMENTED_PROFILES }}

{{ ROSETTA_EXAMPLES }}
