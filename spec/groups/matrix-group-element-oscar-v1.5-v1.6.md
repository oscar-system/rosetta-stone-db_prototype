---
title: Matrix Group Elements (`OSCAR v1.5-v1.6`)
concept: matrix-group-element
kind: type
order: 7
profiles: [oscar-v1.5, oscar-v1.6]
---
`MatrixGroupElem` is the older OSCAR encoding for matrix-group elements. In the
current corpus this form appears in OSCAR v1.5 and v1.6.

## Encoding Notes

- Use a typed `_type` object whose `name` is `"MatrixGroupElem"`.
- Store the matrix entries under `data`.
- Refer to the ambient group using the matching `MatrixGroup` encoding.

{{ CANONICAL_EXAMPLE_PAYLOAD }}

{{ DOCUMENTED_PROFILES }}

{{ ROSETTA_EXAMPLES }}
