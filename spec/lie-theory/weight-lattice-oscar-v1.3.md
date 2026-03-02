---
title: Weight Lattices (`OSCAR v1.3`)
concept: weight-lattice
kind: type
order: 4
profiles: [oscar-v1.3]
---
In OSCAR v1.3, `WeightLattice` uses a typed `_type` object whose payload still
stores the referenced root system inline under `data.root_system`.

## Encoding Notes

- Use `_type.name = "WeightLattice"`.
- Store the ambient root system reference under `data.root_system`.
- Resolve that reference through `_refs`.

{{ CANONICAL_EXAMPLE_PAYLOAD }}

{{ DOCUMENTED_PROFILES }}

{{ ROSETTA_EXAMPLES }}
