---
title: Multivariate Polynomial
kind: type
order: 11
profiles: [oscar-v1.0, oscar-v1.1, oscar-v1.2, oscar-v1.3, oscar-v1.4, oscar-v1.5, oscar-v1.6, oscar-v1.7, oscar-v1.8]
---

Multivariate polynomials extend the same idea to several variables. The payload
is a structured list of terms, while the ambient ring and coefficient context
are carried by the type parameters and references.

## Encoding rules

- Set `_type` to an object with `name: "MPolyRingElem"`.
- Reference the ambient multivariate polynomial ring through `_type.params`.
- Encode monomials and coefficients structurally under `data` instead of using a
  textual polynomial syntax.

{{ CANONICAL_EXAMPLE_PAYLOAD }}

{{ DOCUMENTED_PROFILES }}

{{ ROSETTA_EXAMPLES }}
