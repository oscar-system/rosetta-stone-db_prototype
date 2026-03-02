---
title: Matrix Group Elements
kind: type
order: 7
profiles: [oscar-v1.5, oscar-v1.6, oscar-v1.7, oscar-v1.8]
---
`MatGroupElem` is unchanged across the OSCAR versions currently represented in
the corpus, so one specification page covers OSCAR v1.5 through v1.8.

## Encoding Notes

- Set `_type` to `"MatGroupElem"` when this type appears at the root of a serialized object.
- Interpret the payload under `data` according to the active namespace and profile version.
- Follow the linked examples for the currently documented payload shape and referenced ambient objects.

{{ CANONICAL_EXAMPLE_PAYLOAD }}

{{ DOCUMENTED_PROFILES }}

{{ ROSETTA_EXAMPLES }}
