---
title: Residue Ring Elements
kind: type
order: 5
profiles: [oscar-v1.7, oscar-v1.8]
---
`ZZModRingElem` and `zzModRingElem` record elements of residue rings.

## Encoding Notes

- Use `_type` to distinguish the concrete residue-ring element family.
- Store the element payload under `data` and recover the parent ring from the surrounding profile-specific context.
- See the linked examples for the currently documented encodings.

{{ CANONICAL_EXAMPLE_PAYLOAD }}

{{ DOCUMENTED_PROFILES }}

{{ ROSETTA_EXAMPLES }}
