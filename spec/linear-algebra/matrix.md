---
title: Matrix
kind: type
order: 9
profiles: [basic-v1]
---

Matrices are two-dimensional homogeneous containers. The current corpus records
the element type in `_type.params` and stores rows as arrays.

## Encoding rules

- Set `_type` to an object with `name: "Matrix"`.
- Record the entry type in `_type.params`.
- Store the matrix payload under `data` as an array of rows.

{{ CANONICAL_EXAMPLE_PAYLOAD }}

{{ DOCUMENTED_PROFILES }}

{{ ROSETTA_EXAMPLES }}
