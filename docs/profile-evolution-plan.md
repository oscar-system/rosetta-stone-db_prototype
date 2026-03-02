# Profile Evolution and Format Variants

This note records a proposed direction for handling changes in the MaRDI file
format over time, especially changes that affect only some data types such as
`bool`.

It is a planning document only. It does not yet imply code changes.

## Goals

We want to support all of the following:

- versioned or evolving serialization formats
- explicit compatibility information
- comparison of outputs across different OSCAR releases
- preservation of the conceptual identity of a data type such as `bool`
- pragmatic growth of the corpus without requiring a perfect specification
  upfront

At the same time, we want to avoid introducing too many overlapping notions of
versioning too early.

## Working Distinctions

For planning purposes, it is useful to distinguish the following concepts:

- **Conceptual example**
  A mathematical object such as a specific boolean, matrix, polyhedron, or
  permutation group.
- **Generator**
  Code in some system that constructs the conceptual example.
- **Serialized output**
  One concrete emitted file in the MaRDI format.
- **Profile**
  A named and versioned compatibility layer for the serialization format.
- **Producer version**
  A concrete implementation release, such as OSCAR 1.7 or OSCAR 1.8.

The important point is that producer version and serialization profile are
related, but they are not the same thing.

## Current Recommendation

At this stage, we should **not yet introduce standalone version identifiers for
individual data types** such as `bool-v1` and `bool-v2` as first-class metadata
in the data model.

Instead, changes such as the upcoming boolean change should be represented
through **profile evolution**:

- `basic-v1` contains the current boolean format
- `basic-v2` will contain the revised boolean format
- `oscar-v1.7` is based on `basic-v1`
- `oscar-v1.8` is based on `basic-v2`

This keeps the compatibility story at the profile level and avoids immediately
tracking a second axis of format-version identifiers throughout all dependent
types.

## Why Not Type Variants Yet?

If we assign separate variant identifiers to individual data types right away,
we quickly run into questions such as:

- which permutation-group format uses which boolean format?
- does a higher-level format really depend on the precise boolean encoding?
- how should such dependencies be displayed on the website?

These questions are real, but addressing them now would add substantial
complexity. In many cases, the useful compatibility information is already
captured by profiles.

The current recommendation is therefore:

- use profiles as the primary compatibility mechanism
- duplicate spec/example pages only where formats actually differ
- revisit explicit type-variant identifiers later if profile-based handling
  becomes too clumsy

## Proposed Profile Metadata

Profiles should gain a small amount of lifecycle metadata.

At minimum:

- `id`
- `title`
- `kind`
- `based_on`
- `status`

Optional:

- `released_on`

Possible status values:

- `stable`
- `draft`

For the near future, this suggests:

- `basic-v1`: stable
- `oscar-v1.7`: stable
- `basic-v2`: draft
- `oscar-v1.8`: draft

with `oscar-v1.7` based on `basic-v1` and `oscar-v1.8` based on `basic-v2`.

## Spec Pages

For unchanged types, a single spec page can continue to list multiple profiles.

Example:

- `spec/basics/integers.md` may list both `basic-v1` and `basic-v2`

For changed types, we should use separate profile-specific pages while keeping
their conceptual relationship visible.

Example:

- `spec/basics/bool-basic-v1.md`
- `spec/basics/bool-basic-v2.md`

This is deliberately explicit, even if it introduces some duplication.

The website should then present these as two specifications of the same
conceptual type `bool`, attached to different profiles.

Possible later improvement:

- introduce an explicit "conceptual type" grouping so the website can display
  both pages under one heading or switcher

That grouping can be added later without requiring it now in the stored data.

## Rosetta Examples

The main missing concept on the rosetta side is not "different OSCAR versions"
by itself, but rather **multiple serialized outputs for one conceptual
example/system pair**.

We should therefore aim for this model:

- one `description.md` per conceptual example
- one generator per system where possible
- multiple serialized outputs per system/example
- each output annotated with profile metadata
- producer-version metadata added where useful

This avoids duplicating the conceptual example just because one system emits
multiple variants over time.

An important consequence is that an example may need multiple outputs even when
its top-level specification page does not split. For example, a tuple example
may need both `basic-v1` and `basic-v2` outputs simply because one component is
a boolean, even if the tuple format itself remains unchanged.

## Possible Future Layout for Outputs

One plausible future layout is:

```text
rosetta/basics/bool/
  description.md
  systems/
    Oscar.jl/
      generate.jl
      outputs/
        basic-v1/
          data.mrdi
        basic-v2/
          data.mrdi
```

This makes profile membership explicit at the output level.

The current recommendation is that output directories should be named by the
most specific relevant profile for the top-level serialized object.

Examples:

- for a top-level `bool` example, use `basic-v1` and `basic-v2`
- for a top-level tuple example affected only through nested booleans, still use
  `basic-v1` and `basic-v2`
- for a top-level symmetric-group example, use `oscar-v1.7` and `oscar-v1.8`

This means there is no single global naming rule beyond "outputs are tagged by
profile id". The appropriate profile may depend on the example.

Producer-version metadata can still be attached separately to each output if
desired.

## Website Implications

The website should eventually reflect three layers:

- conceptual example or conceptual type
- profile-specific serialization pages
- concrete producer outputs

For example, a future `bool` section might show:

- conceptual type: `bool`
- spec page for `basic-v1`
- spec page for `basic-v2`
- rosetta example output for OSCAR under `basic-v1`
- rosetta example output for OSCAR under `basic-v2`

Unchanged types would continue to have a single page listing several profiles.

At the same time, example pages should still be allowed to show multiple outputs
whose serialized files differ, even if the page's top-level specification is
unchanged. This is necessary to make cross-profile comparison useful.

## Recommended Order of Work

The recommended implementation order is:

1. Add lifecycle metadata to profiles.
   Define `basic-v2` and mark it as draft.
   Keep `oscar-v1.8` as draft and based on `basic-v2`.

2. Extend the rosetta data model to support multiple outputs per system/example.
   This is the main structural prerequisite for comparing releases and profiles.

3. Update website rendering to display multiple outputs per system.
   Group first by system, then by profile, and later optionally by producer
   version.

4. Introduce the first profile-specific divergence.
   Use `bool` as the first example:
   - duplicate the bool spec page for `basic-v1` and `basic-v2`
   - add multiple bool outputs in the rosetta corpus

5. Reassess whether explicit type-level variant identifiers are still needed.
   If profile-based duplication remains manageable, we may not need them yet.

## Open Questions

- Should the website eventually expose an explicit "conceptual type" layer for
  changed types such as `bool`?
- How much metadata do we want to record for producer version, for example an
  exact OSCAR release number or commit?
- Should draft profiles be rendered differently from stable profiles on the
  website?
