---
title: Floating-Point Numbers
kind: type
order: 4
profiles: [basic-v1]
---
`Float64` currently appears as the basic floating-point type in the corpus. This page records the current `basic v1` encoding and links to the corresponding examples.

## Encoding Notes

- Use `_type` to distinguish the concrete floating-point family such as `Float64`.
- Store the payload under `data` in the profile-specific representation documented by the active namespace.
- See the linked examples for the current payload shape.

{{ CANONICAL_EXAMPLE_PAYLOAD }}

{{ DOCUMENTED_PROFILES }}

{{ ROSETTA_EXAMPLES }}
