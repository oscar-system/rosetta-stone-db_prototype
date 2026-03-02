---
title: Phylogenetic Trees (`OSCAR v1.0-v1.5`)
concept: phylogenetic-tree
kind: type
order: 10
profiles: [oscar-v1.0, oscar-v1.1, oscar-v1.2, oscar-v1.3, oscar-v1.4, oscar-v1.5]
---
In OSCAR v1.0 through v1.5, phylogenetic trees are serialized with a bare root type
name and the underlying polymake object directly as the `data` payload.

## Encoding Notes

- Use `_type: "PhylogeneticTree"` at the root.
- Store the polymake tree object directly under `data`.
- Preserve the embedded polymake namespace and type information inside that payload.

{{ CANONICAL_EXAMPLE_PAYLOAD }}

{{ DOCUMENTED_PROFILES }}

{{ ROSETTA_EXAMPLES }}
