---
title: Tuple
kind: type
order: 7
profiles: [basic-v1]
---

Tuples are ordered heterogeneous containers. The parameter list records the type
of each component in position order.

## Encoding rules

- Set `_type` to an object with `name: "Tuple"`.
- Record the component types in `_type.params` as an ordered list.
- Store the component payloads under `data` as a JSON array of the same length.

{{ CANONICAL_EXAMPLE_PAYLOAD }}

{{ DOCUMENTED_PROFILES }}

{{ ROSETTA_EXAMPLES }}
