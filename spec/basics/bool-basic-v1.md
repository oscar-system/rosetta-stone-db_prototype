---
title: Bool (`basic v1`)
concept: bool
kind: type
order: 1
profiles: [basic-v1]
---

The Bool data type encodes logical truth values in the `basic v1` profile.

## Encoding rules

- Set `_type` to `"Bool"`.
- Encode the payload under `data` as the lowercase string `"true"` or
  `"false"`.
- Treat the namespace/version table below as the profile log for this type.

{{ CANONICAL_EXAMPLE_PAYLOAD }}

{{ DOCUMENTED_PROFILES }}

{{ ROSETTA_EXAMPLES }}
