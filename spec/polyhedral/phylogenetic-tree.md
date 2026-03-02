---
title: Phylogenetic Trees (`OSCAR v1.6-v1.8`)
concept: phylogenetic-tree
kind: type
order: 11
profiles: [oscar-v1.6, oscar-v1.7, oscar-v1.8]
---
From OSCAR v1.6 onward, `PhylogeneticTree` uses a parametric root type and a
structured payload that separates the polymake tree from additional OSCAR-level
data such as vertex permutations.

## Encoding Notes

- Use a typed `_type` object whose `name` is `"PhylogeneticTree"`.
- Record the coefficient field in `_type.params`.
- Store the tree data under `data`, with at least `pm_tree` and any additional OSCAR-specific fields required by the profile.

{{ CANONICAL_EXAMPLE_PAYLOAD }}

{{ DOCUMENTED_PROFILES }}

{{ ROSETTA_EXAMPLES }}
