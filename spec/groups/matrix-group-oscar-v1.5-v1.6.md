---
title: Matrix Groups (`OSCAR v1.5-v1.6`)
concept: matrix-group
kind: type
order: 5
profiles: [oscar-v1.5, oscar-v1.6]
---
`MatrixGroup` is the older OSCAR encoding for matrix groups. In the current
corpus this form appears in OSCAR v1.5 and v1.6.

## Encoding Notes

- Use a typed `_type` object whose `name` is `"MatrixGroup"`.
- Record the ambient base ring and degree in `_type.params`.
- Store generators and descriptive metadata under `data`.

{{ CANONICAL_EXAMPLE_PAYLOAD }}

{{ DOCUMENTED_PROFILES }}

{{ ROSETTA_EXAMPLES }}
