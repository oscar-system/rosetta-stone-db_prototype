---
title: Set
kind: type
order: 6
---

Sets are unordered homogeneous containers. The payload is stored as an array,
while the mathematical set semantics come from the data type rather than the
JSON container alone.

## Encoding rules

- Set `_type` to an object with `name: "Set"`.
- Record the element type in `_type.params`.
- Store the elements under `data` as an array; consumers should apply set
  semantics rather than relying on JSON order.

{{ CANONICAL_EXAMPLE_PAYLOAD }}

{{ DOCUMENTED_PROFILES }}

{{ ROSETTA_EXAMPLES }}
