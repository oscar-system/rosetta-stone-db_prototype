---
title: Matrix Group Elements (`OSCAR v1.7-v1.8`)
concept: matrix-group-element
kind: type
order: 7
profiles: [oscar-v1.7, oscar-v1.8]
---
`MatGroupElem` is the current OSCAR encoding for matrix-group elements. In the
current corpus this form appears in OSCAR v1.7 and v1.8.

## Encoding Notes

- Use a typed `_type` object whose `name` is `"MatGroupElem"`.
- Store the matrix entries under `data`.
- Refer to the ambient group using the matching `MatGroup` encoding.

{{ CANONICAL_EXAMPLE_PAYLOAD }}

{{ DOCUMENTED_PROFILES }}

{{ ROSETTA_EXAMPLES }}
