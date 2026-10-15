# Milestone Runtime Extensions — Optional Modules and Global Registration

**Status:** Proposed architectural milestone; not started (2026-10-15). This document records decisions, evidence, hypotheses, and a staged investigation. It does **not** claim an implemented facility.

## 1. Purpose

Make independent native BCPL runtime services, beginning with proposed `BCPLQSAM`, `BCPLDEC`, and `BCPLTIME`, **optional at application link-edit time**, without rebuilding the compiler or editing BCPLMAIN whenever a new service is added.

Separate three decisions:

1. **Distribution:** Which optional objects and declarations are installed with Cambridge?
2. **Application link-edit:** Which available objects become part of a particular program load module?
3. **Program startup:** How do the *selected* modules' callable entry addresses reach the BCPL global vector?

A compiler build is not the same thing as a BCPL application build. An installation can carry all optional objects while most applications link none. MVS JCL / IEWL selects objects; BCPL runtime startup registers their globals. Running the already linked program does not select the modules. The ordinary run JCL supplies DD statements and other resources, not optional code-module selection.

This facility is a **project-designed extension** to reconstructed Cambridge, not claimed to be an authenticated feature of the original historical BCPL system. Do not make it a prerequisite for M4 self-hosting.

## 2. Actual reconstructed baseline

The current `native-compiler/asm/bcplmain.asm` demonstrates the following:

- Generated BCPL code addresses `G!N` at `R12 + 4*N`. `G!0` records the global-vector extent.
- Startup obtains storage with MVS `GETMAIN`. At present it has 700 global-vector words, numbered 0..699; `GLOBCNT EQU 699`. Do not mistake this WIP extent for a historical or permanent limit.
- Startup paints globals other than `G!0` with historical uninitialized sentinels `X'C7D3F000' + 4*N`.
- The application compiled by CG370 has exported-global pairs in a trailing record: global byte offset `4*N` and a relocated procedure address, preceded by trailer control/sentinel words. BCPLMAIN walks these and writes addresses into `G`.
- After application imports, BCPLMAIN **explicitly refers to `BLIB`** and walks a BLIB trailer to install its exports. The mechanism is usable precedent, but the reference to BLIB is hard-coded, not generic discovery.
- BCPLMAIN also explicitly populates particular native-service global slots, including G!85 GETBYTE and G!86 PUTBYTE, and invokes binding support for other native runtime modules.
- The present importer writes into global slots directly; **do not assume duplicate-global detection or extension lifecycle management already exists**.
- A conventional MVS linkage edit resolves external symbols and relocations, but it does **not** automatically fill `G`. Merely issuing `INCLUDE ... (BCPLQSAM)` does not make its procedures callable through BCPL globals.

See `richards-bcpltape/sys3/bcpl/libhdr`: historical globals already assign `READREC:23`, `WRITEREC:24`, `TIMEOFDAY:27`, `TIME:28`, `DATE:29`, and document `FIRSTFREEGLOBAL=150`. Proposed QSAM and clock interfaces **must not silently replace these historical names and slots**. Existing G!150 is currently used by a provisional diagnostic in BCPLMAIN; `FIRSTFREEGLOBAL` is not an automatically safe allocator. Inventory every reserved and presently used slot before fixing an extension numbering policy.

The prior runtime object library work with BLIB establishes *independent object building*, but not a generic optional-module registration protocol.

### Shared terminology and package ownership

See [Cambridge runtime and library nomenclature](runtime-and-library-nomenclature.md) for the distinction among Core Runtime, Base Library (BLIB), System Extensions, Standard Libraries and User/Site Libraries, and among headers, source modules, object modules and packages. The same optional registration protocol should serve independently developed User/Site Libraries, not only project-supplied System Extensions. R.0 must establish a source-controlled official global-number allocation registry together with a realistic installation-level policy for site/private globals and collision detection. This is separate from per-application BCPLREG registration.

## 3. Architectural principles

- **Core remains small:** the native compiler, BCPLMAIN coordination and the essential historical runtime remain mandatory as appropriate. The three proposed extension modules are not core.
- **No compiler awareness:** adding BCPLQSAM, BCPLDEC, or BCPLTIME must not require code-generation changes or an option switch in the compiler.
- **Link-time selection:** application JCL names required optional object members, using explicit `INCLUDE` statements initially. No runtime dynamic module discovery, `LOAD` interface, or self-registering control section scan is assumed.
- **Automatic startup registration:** after link-edit, BCPLMAIN (or one core registration helper) imports only the selected extensions into `G` before entering `START`. The BCPL application should not need to make registration calls.
- **One-time generic core adaptation:** an accepted registration framework may require a *single* deliberate modification to BCPLMAIN. Once installed, adding or omitting future extension modules must not require BCPLMAIN source changes or recompilation.
- **Transparent ABI:** preserve CG370's entry trailer semantics, register/linkage conventions, relocation behavior and the distinction between BCPL word pointers and assembler machine addresses.
- **Safe by default:** keep unselected globals uninitialized; reject malformed descriptors, out-of-range numbers and unexpected collisions, with useful diagnostics. Do not overwrite core globals inadvertently.
- **Source authority:** Git-controlled text sources and JCL are authoritative. All module objects, registration objects and load modules are rebuildable; no binary migration.
- **Incremental work:** preserve `BCPLIO` and existing stream semantics. No change to accepted objects until individually validated.

## 4. Proposed general registration model

The preferred starting point is a small **application-specific registration object**, provisionally named `BCPLREG`, which contains a fixed, versioned list of references to selected extension descriptors. This table is ordinary assembler/object data that IEWL can relocate.

A useful conceptual organization is:

```text
       linked load module
         BCPL application and its CG370 global trailer
         BCPLMAIN + essential runtime, including BLIB
         BCPLQSAM [selected]
         BCPLDEC  [selected]
         BCPLTIME [not selected]
         BCPLREG:
             version, entry count, registration entries
             -> QSAM export descriptor
             -> DEC export descriptor
```

Startup (conceptually):

```text
 allocate G; initialize historical missing-global sentinels
 import application's generated CG370 exports
 import mandatory historical BLIB and native core services
 validate BCPLREG table version/length/entries
 for each selected module, validate and register its exports
 initialize only selected modules that need an init hook, if supported
 verify START and any declared requirements; enter START
```

**Important:** this order is a *design target*, not a description of today's exact startup ordering. Existing precedence and overriding by core/BLIB must first be audited. Duplicate global policy must be defined explicitly before changing that ordering.

Two possible **export descriptor** representations deserve comparison:

| Representation | Advantages | Risks / open questions |
| --- | --- | --- |
| **CG370-compatible global trailer** | Reuses the existing program/BLIB importer; BCPL-written extension modules naturally produce it | Assumes section layout, prefix, size encoding and relocations; assembler services need an adapter; generalized bounded parser required |
| **Explicit global-number / relocated-address pairs** | Straightforward for assembler services; table easily inspected in IEWL listings | Introduces a second export encoding unless normalized by a common registration helper |

**Provisional preference:** one *logical* importer/validator, with a validated adapter for compiler-generated trailers and an explicit-pair descriptor for native assembler routines if necessary. Do not force a fabricated CG370 module prefix on an assembler CSECT merely for cosmetic uniformity. R.0 must decide the minimum safe interoperable representation.

It is not yet decided whether BCPLREG's table has an explicit `END` marker, count, version and byte length, or how its CSECT obtains the referenced entries. A null/empty registry must be a supported legitimate state. A fixed `BCPLREG` object included even in minimal application builds is acceptable; avoid weak-symbol tricks or non-historical IEWL features unless directly proven on MVS 3.8.

## 5. Application link and source model

Illustrative link-editor control statements (**schematic**, not current production JCL; all DD names and members must be checked against the live manifest):

```jcl
//SYSLIN DD *
  INCLUDE CORE(MYPROG)
  INCLUDE CORE(BCPLMAIN)
  INCLUDE CORE(BLIB)
  INCLUDE EXT(BCPLQSAM)
  INCLUDE EXT(BCPLDEC)
  INCLUDE REGOBJ(BCPLREG)
  ENTRY MYPROG
  NAME MYPROG(R)
/*
```

`CORE`, `EXT`, and `REGOBJ` are *illustrative IEWL DD names*, not manifest datasets; `MYPROG` and `ENTRY` also require the true native compiler linkage contract. An explicit `INCLUDE` of an optional module must be matched by the corresponding entry in the separately assembled `BCPLREG` object. An unselected module is absent from both. Linkage-editor external-symbol resolution must detect a registry entry pointing to an unlinked descriptor, under validated NCAL/LET settings; startup must still validate logical registration contents.

The BCPL application separately imports a library-specific `GLOBAL` declaration/header defining agreed names and slot numbers. That header makes names available **at compile time**, but neither pulls in objects nor registers functions. A declaration alone must not be presented as an availability guarantee.

**No new optional-module selection occurs in the RUN job.** DDs such as `INDATA` or `SYSPRINT` describe I/O allocations; they are not registration instructions.

## 6. Contract questions to settle in R.0

1. **Compiler-generated exports:** layout, relocation, control marker, safe section length, validation and existing BLIB treatment.
2. **Assembler exports:** entry address representation, calling convention (R7..R10 arguments, etc.), memory ownership, and whether a single object can export multiple global procedures.
3. **Registration table:** ownership, version, bounds, linker-resolved references, empty-table representation, and deterministic selection order.
4. **Global slots:** authoritative registry; historical G!0..G!149; occupied G!150 and above; no accidental collisions; capacity policy and maximum global number.
5. **Conflict handling:** duplicate declarations within a module, between selected modules, against app/BLIB/core; explicit intentional override if ever supported, otherwise fail cleanly before START. No silent last-write-wins.
6. **Dependencies:** what happens when QSAM depends on a core service or another optional module, and how the link and registration table express it.
7. **Initialization:** entries alone versus optional init/finalization hook, sequencing, failure cleanup, and correct MVS save-area/register discipline. Prefer no hooks for stateless facilities.
8. **Missing optional functions:** a BCPL `GLOBAL` reference is indirect through `G`, so omission can escape the linkage editor; define a preflight declared-requirements check or reliable failure mode. Never claim ordinary link-edit checks all missing globals.
9. **ABI/versioning:** module signature/version, rejection of incompatible extension descriptors, and programmer documentation.
10. **Testing:** preserving existing BLIB and native service behavior without modifying current accepted artifacts ahead of gates.

## 7. March roadmap with explicit gates

| March | Objective | Deliverable and exit gate |
| --- | --- | --- |
| **R.0 — Evidence and contract** | Inventory the actual CG370 trailer, global initialization/import ordering, BLIB and native binders, link-editor behavior, and slot map | Recorded verified ABI; chosen registry/descriptor formats, collision policy, empty-table and optional-init contracts, compatibility tests; **no speculative source refactor** |
| **R.1 — Generic registration foundation** | Implement one minimal, linker-driven registration path with an empty registry and one trivial optional assembler service | Compile/link/run demonstrations prove `START` runs with empty registry and a chosen extension's global is installed; core BLIB regression evidence preserved |
| **R.2 — Selective interoperability** | Link two independent optional extension *probes*, individually and together; if practical one compiled BCPL extension export plus one assembler export | 0/A/B/A+B combinations work without BCPLMAIN rebuild; collisions, invalid descriptor, missing dependency/slot, absent module diagnosed deterministically; inspect linkage maps |
| **R.3 — Packaging and acceptance** | Stable user-facing link-edit recipe, BCPL declaration conventions, developer template and reproducible rebuild from Git | Full native regression baseline; separately accepted object PDS installation decision; documented accepted startup contract and actual JES/IEWL evidence |

The probes should be *tiny*, not premature implementations of QSAM/DEC/TIME. Subsequent feature milestones own their APIs and behavior. A failed gate can suspend R without blocking M4.

## 8. Relationship to other milestones

- **Milestone QSAM:** depends on a stable optional-registration mechanism for *automatic* global installation; it may continue isolated linkage/ABI experiments without R, but should not invent its own registrar.
- **Milestone Decimal Arithmetic:** uses the shared registration architecture for `BCPLDEC`; decimal descriptors, arithmetic semantics and rounding remain that milestone's responsibility.
- **Milestone Date and Time Services:** uses the same architecture for `BCPLTIME`; calendar and MVS TIME semantics remain separate.
- **M4 self-hosting:** **not blocked** by R. Reconstructing the compiler remains higher priority if schedule conflicts arise.

A historical BCPL system already exposed global names `READREC`, `WRITEREC`, `TIME`, and `DATE`. New optional modules must either choose distinct names/globals or deliberately implement proven historical contracts as an entirely separate acceptance decision. Do not quietly reinterpret legacy symbols.

## 9. Reproduction, evidence and repository layout

Authoritative namespace: `config/dspal.yaml` and `tools/datasets/dspal`. Candidate assembler objects: `NATIVE_DEVOBJ`; accepted core objects: `NATIVE_OBJ`. Do not use superseded historical `HERC02.BCPL.OBJ` conventions, do not populate `CAMB_*` for this work, and do not migrate prebuilt objects.

Proposed deliverables (paths provisional pending R.0): an assembler registration-table template, a minimal `BCPLREG` consumer, two miniature optional services, BCPL declaration headers/examples, link-edit JCL, regression checks, and gate records under `packaging/`. Document exact observed MVS job IDs, condition codes, map/cross-reference excerpts and commands; never mark a test PASS by inspection alone.

The goal is **a stable, simple, historically intelligible extension pattern**, not a plugin loader, dependency manager, or dynamic linker.

## 10. Immediate handoff

Begin **R.0 only**. Read the current `native-compiler/asm/bcplmain.asm`, BLIB/object integration JCL, runtime ABI records, the compiled module trailer conventions, historical `LIBHDR`, the current dataset manifest and the native regression harness. Propose the simplest linker-relocatable table and a bounded global importer that leave core behavior intact. Present exact duplicate/absence/startup rules before implementing or changing existing accepted objects.
