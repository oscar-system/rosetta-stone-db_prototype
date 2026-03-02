---
title: Vector
kind: type
order: 4
profiles: [basic-v1]
---

Vectors are homogeneous ordered containers. Their element type is recorded in
`_type.params`, and the payload is an array whose entries follow that element
type's serialization rules.

## Encoding rules

- Set `_type` to an object with `name: "Vector"`.
- Record the element type in `_type.params`.
- Store the entries in order under `data` as a JSON array.

{{ CANONICAL_EXAMPLE_PAYLOAD }}

{{ DOCUMENTED_PROFILES }}

{{ ROSETTA_EXAMPLES }}
