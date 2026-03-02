---
title: Pc Group Elements (`OSCAR v1.0`)
concept: pc-group-element
kind: type
order: 9
profiles: [oscar-v1.0]
---
In OSCAR v1.0, `PcGroupElem` uses a bare `_type` string and stores the parent
group information inline in the parameter payload.

## Encoding Notes

- Use `_type: "PcGroupElem"`.
- Store the exponent vector under `data`.
- Inline the parent group description in the parameters.

{{ CANONICAL_EXAMPLE_PAYLOAD }}

{{ DOCUMENTED_PROFILES }}

{{ ROSETTA_EXAMPLES }}
