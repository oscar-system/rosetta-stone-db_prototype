{{ PAGE_NAV }}

<div class="hero">
<p><strong>The MaRDI File Format</strong></p>
<h1>The MaRDI File Format: A FAIR File Format for Mathematical Software</h1>
<p>This website has two complementary roles. It documents the file format itself, including terminology, structure, and profile-specific encodings, and it also collects a rosetta stone of worked examples that show how concrete mathematical objects are serialized in practice.</p>
<p>The format is JSON-based, but its semantics are intentionally tied to explicit namespaces and software versions. That keeps the container format stable while allowing mathematical software systems and their serializations to evolve over time.</p>
<p>This is the format currently used by <a href="https://www.oscar-system.org">OSCAR</a>; see also the <a href="https://github.com/oscar-system/Oscar.jl">Oscar.jl repository</a>.</p>
</div>

<div class="card-grid">
  <a class="card" href="./spec/index.md">
    <strong>The specification</strong>
    <span>Read the file-level rules, terminology, profile/version notes, and type pages.</span>
  </a>
  <a class="card" href="./rosetta/index.md">
    <strong>The rosetta stone</strong>
    <span>Browse concrete examples, generation code, and emitted `.mrdi` payloads.</span>
  </a>
</div>

## What this site covers

- The overall JSON object model, including `_type`, `data`, `_ns`, and `_refs`.
- Profile-specific encodings, with documented namespace and version tables derived from the example corpus.
- Cross-links between the specification and concrete serialized examples.

<div class="note-box">
The specification pages fix terminology explicitly. In particular, this site uses <strong>data type</strong> for the value named by <code>_type</code>, <strong>payload</strong> for the value under <code>data</code>, and <strong>profile</strong> for a namespace-specific encoding contract.
</div>

## Start here

- [Open the specification](./spec/index.md)
- [Open the rosetta stone](./rosetta/index.md)
- [Browse this repository](https://github.com/oscar-system/rosetta-stone-db_prototype)

<div class="footer-note">
<p><strong>Disclaimer.</strong> This prototype is part of ongoing work on a FAIR file format for mathematical software. Supported by <a href="https://www.mardi4nfdi.de">MaRDI</a> and by <a href="https://www.computeralgebra.de/sfb/">DFG SFB/TRR-195</a>.</p>
</div>
