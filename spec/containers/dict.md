---
title: Dictionary
kind: type
order: 5
profiles: [basic-v1]
---

Dictionaries map keys to values. In the current corpus, the key and value types
are recorded explicitly inside `_type.params`.

## Encoding rules

- Set `_type` to an object with `name: "Dict"`.
- Record key and value types under `_type.params`, for example `key_params` and
  `value_params`.
- Serialize the payload under `data` as a JSON object from encoded keys to
  encoded values.

{{ CANONICAL_EXAMPLE_PAYLOAD }}

{{ DOCUMENTED_PROFILES }}

{{ ROSETTA_EXAMPLES }}
