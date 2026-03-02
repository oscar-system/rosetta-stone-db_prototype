---
title: Bool (`basic v2`)
concept: bool
kind: type
order: 2
profiles: [basic-v2]
---

The Bool data type encodes logical truth values in the `basic v2` profile.

## Encoding rules

- Set `_type` to `"Bool"`.
- Encode the payload under `data` as the JSON boolean `true` or `false`.
- Treat the namespace/version table below as the profile log for this type.

{{ CANONICAL_EXAMPLE_PAYLOAD }}

{{ DOCUMENTED_PROFILES }}

{{ ROSETTA_EXAMPLES }}
