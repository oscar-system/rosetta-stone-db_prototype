---
title: Matrix Groups (`OSCAR v1.7-v1.8`)
concept: matrix-group
kind: type
order: 6
profiles: [oscar-v1.7, oscar-v1.8]
---
`MatGroup` is the current OSCAR encoding for matrix groups. In the present
corpus this form appears in OSCAR v1.7 and the draft OSCAR v1.8 profile.

## Encoding Notes

- Use a typed `_type` object whose `name` is `"MatGroup"`.
- Record the ambient base ring and degree in `_type.params`.
- Store generators and descriptive metadata under `data`.

{{ CANONICAL_EXAMPLE_PAYLOAD }}

{{ DOCUMENTED_PROFILES }}

{{ ROSETTA_EXAMPLES }}
