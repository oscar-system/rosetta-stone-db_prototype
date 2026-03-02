---
title: Weight Lattice Elements (`OSCAR v1.3`)
concept: weight-lattice-element
kind: type
order: 5
profiles: [oscar-v1.3]
---
In OSCAR v1.3, `WeightLatticeElem` already uses a typed `_type` object, but its
referenced `WeightLattice` payload still stores `root_system` under `data`.

## Encoding Notes

- Use `_type.name = "WeightLatticeElem"`.
- Store coordinates under `data`.
- Refer to the parent lattice according to the OSCAR v1.3 `WeightLattice`
  encoding.

{{ CANONICAL_EXAMPLE_PAYLOAD }}

{{ DOCUMENTED_PROFILES }}

{{ ROSETTA_EXAMPLES }}
