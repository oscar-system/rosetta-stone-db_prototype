---
title: String
kind: type
order: 3
---

String is the basic textual data type. It is useful both on its own and as a
building block inside container types such as dictionaries and tuples.

## Encoding rules

- Set `_type` to `"String"`.
- Store the UTF-8 string payload directly under `data`.
- When strings appear as keys or components inside other payloads, their role is
  determined by the surrounding type.

{{ CANONICAL_EXAMPLE_PAYLOAD }}

{{ DOCUMENTED_PROFILES }}

{{ ROSETTA_EXAMPLES }}
