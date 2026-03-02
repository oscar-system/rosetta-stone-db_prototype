---
title: Namespaces, Profiles, and Versions
kind: core
order: 2
---

The format does not impose a universal mathematical semantics. Instead, each
file points to the namespace and software version that define the meaning of its
types and payloads.

## Rules

- Use `_ns` to record the profile that governs the file or subtree.
- A namespace entry is typically encoded as `"Name": ["URL", "version"]`.
- When two systems use different meanings or different serializations, they
  should be treated as different profiles rather than forced into one shared
  meaning.
- If a profile changes its encoding, keep the old profile/version rows
  documented and add the new ones instead of rewriting history.

## Practical consequence

- A type page such as Bool should document profile-specific encodings and the
  versions in which they appear.
- The tables on generated spec pages are built from the current rosetta-stone
  corpus, so they serve as an evolving compatibility log.
- This structure also leaves room for future Oscar, Magma, polymake, or other
  profiles once matching examples are added.
