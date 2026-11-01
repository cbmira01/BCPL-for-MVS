# Repository and MVS dataset lineage refactor — deferred proposal

**Status:** ARCHITECTURAL PROPOSAL ONLY. Not authorized for implementation.
**Recorded:** 2026-10-08
**Scope:** GitHub repository organization first; separate, later MVS PDS namespace
migration. This document captures design decisions and alternatives for a
future explicitly requested refactor march. It does **not** change current
source locations, commands, datasets, manifests, or regression baselines.

## Motivation and correction to the existing model

The present MVS dataset structure (`HERC02.BCPL.SOURCE`, `INTCODE`,
`ASM`, `JCL`, `OBJ`, `LOAD`, etc.) is useful **operationally** but
does not represent the project's distinct compiler lineages. Organizing
only by artifact type obscures ownership and conflates independently
meaningful test results. The long-term organizing axis should be
**lineage and function first**, artifact type second.

The project has at least three related but distinct lines of work:

| Line | Purpose | Illustrative owned artifacts |
| --- | --- | --- |
| **MR10KIT** | Reconstructed historical MR10 INTCODE bootstrap system; runnable independently and retained as a baseline | MR10 compiler/interpreter, INTCODE, runtime/library, JCL, regressions, demos |
| **NATIV** | Cross-generation bootstrap/native reconstruction, especially demoted Cambridge sources executable via MR10-compatible infrastructure | Demotion, resident Cambridge compiler image, diagnostic CG370 variants, BCPLMAIN work-in-progress, native object builds, JCL, native regressions |
| **CAMBRG** | Eventual native production Cambridge BCPL environment; ultimately usable without MR10 interpretation in normal compilation | Native compiler, native libraries/runtime, full source and headers, object/load modules, demos, JCL, regressions |

NATIV is an intersection/bridge, **not** simply another spelling of
CAMBRG. Bootstrap dependency is conceptually MR10KIT plus historical
Cambridge source -> NATIV -> CAMBRG. NATIV may remain valuable for recovery
and diagnostic work even when CAMBRG becomes native/self-hosted; it should
not be a hidden normal-build prerequisite for a mature CAMBRG.

### Fourth namespace: SHARED

`SHARED` is **not a fourth BCPL implementation**. It holds resources
whose **semantics and representation are independent of all consuming
compiler lines**. It is not an all-purpose location for resources used by
two lines. Legitimate cross-line dependencies should remain explicit.

Plausible future `HERC02.BCPL.SHARED.*` resources:
- Canonical, immutable test-input datasets (FB/80, VB, binary records,
  EBCDIC/padding/byte-packing and integer boundary fixtures).
- Selected cross-line reference data **when expected semantics really agree**;
  implementation-specific expected results remain with their regressions.
- General-purpose MVS system probes (QSAM, DDs, reopening/concatenation,
  IFOX object format, IEWL symbol resolution), with independent ownership.
- Possibly environment-neutral JCL procedures or executable utilities
  after verifying absence of BCPL implementation/ABI dependencies.

Normally **not** SHARED: MR10/Cambridge historical compiler source,
source headers that happen to share a name (e.g., LIBHDR), BLIB objects,
BCPLMAIN, implementation-specific regression drivers and reports,
compiler/runtime load modules, or outputs whose ABI/provenance differs.

Common fixtures should normally be read-only during tests (`DISP=SHR`).
Each line writes its own temporary/owned result datasets, preventing
cross-suite contamination. Do not allocate an empty SHARED hierarchy
speculatively: establish only demonstrated common resources.

The correct HLQ is **HERC02**, not `HER02` (the latter occasionally
appeared in informal discussion).

## Proposed repository organization (illustrative, not a migration map)

```text
BCPL-for-MVS/
  mr10kit/
    compiler/  intcode/  runtime/  regression/  demos/  jcl/
  nativ/
    bootstrap/ compiler/ runtime/ regression/ demos/
    object-library/ jcl/
  cambrg/
    compiler/ runtime/ regression/ demos/ jcl/
  shared/
    fixtures/ system-probes/
  richards-bcpltape/       # immutable historical evidence, separate category
  tools/                  # common host infrastructure can remain centralized
  docker/  config/  docs/  packaging/
```

This diagram is not instructions to populate every directory. Initially
`cambrg/` may contain only its ownership README. Historical source should
**not** be copied into CAMBRG just for structural symmetry. Likewise,
there is no requirement that every source directory correspond to one
MVS PDS, or that every subsystem have the same PDS types.

### Explicit ownership, including tools

Before moves, inventory **every existing top-level directory and major
script**; annotate:
1. Primary owner: MR10KIT, NATIV, CAMBRG, SHARED, or HISTORICAL EVIDENCE.
2. Purpose and exact consumers.
3. Inputs, outputs and generated/authoritative status.
4. Git path and any current managed PDS mapping.
5. Cross-line dependencies, including invoked tools and runtime ABI.
6. Planned disposition: remain shared in place, move, reference fixture,
   retire after validation, or defer.
7. Regression/job evidence required to accept the move.

Tool ownership matters as much as source ownership: MR10 compiler test
drivers belong to MR10KIT, native regression and Cambridge demotion tools
to NATIV, eventual native production compiler build tools to CAMBRG.
Generic host `dspal`, JES submission, job summaries, Docker infrastructure
and other implementation-neutral tooling can remain centralized under
`tools/` and carry the SHARED classification. *Ownership does not
mandate physical relocation.*

The historical tape tree `richards-bcpltape/` should remain preserved
as evidence, independently of the three active lines and SHARED.
Generated/demoted code has explicit derivation/provenance and belongs
to NATIV; do not silently revise canonical historic sources. BLIB built
from demoted source is presently a NATIV artifact; BLIB built later with
the undemoted production Cambridge compiler should be a separately
provenanced CAMBRG artifact. BCPLMAIN-wip presently belongs to NATIV;
assign mature runtime ownership only after its interface stabilizes.

### Regression and demonstration independence

Regression suites and demonstrations must be owned by a line, not
classified just by source language. An MR10KIT test and a NATIV test
prove different facts even with identical input BCPL. Likewise future
CAMBRG self-hosted regressions require their own acceptance evidence.
Regression **identifiers must remain stable** (e.g., NATIV regression
067 remains 067); test reports belong to the executing line.

Canonical shared input *fixtures* may be referenced by multiple harnesses,
but test program, expected result, execution record, and pass/fail assertion
normally belong to the line. Avoid duplicate historical evidence or
rewriting the tests solely to achieve folder symmetry. Ultimately the
three suites should be executable separately and under one whole-project
acceptance entry point.

## Later MVS dataset hierarchy (conceptual, NOT IMPLEMENTED)

```text
HERC02.BCPL.MR10KIT.<type>
HERC02.BCPL.NATIV.<type>
HERC02.BCPL.CAMBRG.<type>
HERC02.BCPL.SHARED.<type>
```

Names are intentionally short enough for MVS dataset qualifiers
(MR10KIT=7, NATIV=5, CAMBRG=6, SHARED=6; maximum qualifier 8). Examples
might include `SOURCE`, `INTCODE`, `ASM`, `JCL`, `REGRESS`,
`DEMO`, `OBJ`, `LOAD`, according to **actual** needs, not a blanket
identical collection for each line. Real dataset naming, allocation
attributes, member limits, footprint, volume placement and lifecycle
operations require a separate design/verification process.

A future `dspal` manifest might recognize a selected subsystem for
`stat`, `put`, `populate`, `submit`, `initbcpl`, and especially
`purgebcpl`, with explicit scope and safeguards. A proposed
`--system` switch is illustrative only. A NATIV build legitimately
consuming MR10KIT resources must declare that dependency instead of
silently copying components to SHARED. **No PDS renames, allocation,
purge, or manifest rekeying are authorized by this document.**

## Boundaries, ordering and acceptance

**No refactor now.** Do not bundle directory restructuring with BCPLMAIN
ABI/global-vector development, compiler changes, the Stage B runtime
linkage march, or the BLIB-object packaging experiment.

When explicitly authorized:
1. Freeze a demonstrably good branch/baseline, prepare the ownership
   inventory and cross-line dependency map, and review migration risks.
2. Propose a *limited repository refactor*, starting with independently
   owned regressions and demos (or the smallest tractable coherent area).
   Update imports, paths, wrappers, READMEs, JCL source mappings and
   generated-artifact references in the same tested slice.
3. Run each affected MR10KIT suite independently; run NATIV's complete
   native regression suite (69/69 is the historical previously observed
   reference, **not** a promise of current test results); verify sample
   build jobs and `dspal` unchanged. Preserve stable regression numbers.
4. Commit migration and its evidence only after validation; repeat by
   independent slices. Avoid unrelated cleanup or renaming.
5. **Later, as a separate explicitly authorized project**, design the
   physically partitioned MVS PDS layout, dataset provisioning,
   manifest namespaces, safe population/purge scopes, and staged data
   migration. Confirm before/after functionality and recovery paths.

A future project-level acceptance convention can report independently:
**MR10KIT PASS**, **NATIV PASS**, **CAMBRG PASS**, plus shared
infrastructure verification; none substitutes for the others.

## Operating principle

> Assign ownership by lineage and semantics, not by a common filename
> or object format. Share only representation-independent fixtures and
> infrastructure; preserve explicit bootstrap dependencies, historical
> provenance, and independent regression evidence.

**This document records intent and options, not an active task or a
change to any current runtime/build architecture.**
