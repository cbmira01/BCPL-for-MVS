# Milestone Runtime Extensions — Optional Modules and Global Registration

**Status (owner decision, 22 October 2026):** **R.0 — Evidence and contract CLOSED. R.1 — Generic registration foundation CLOSED.** **R.2 — Selective interoperability ACTIVE (initial BCPLDEMO increment); R.3 — Packaging and acceptance is not started.**

**R.1 owner closure:** The consolidated MVS acceptance campaign passed
24/24 integrated jobs (2760–2783), all five gates, and the 00..145
candidate-runtime panel (145 PASS / 0 FAIL / 1 expected SKIP 083).
See the [R.1 closure and acceptance record](runtime-extensions-r1-closure-20261022.md).
R.0's approved A–H ABI decisions and shared QUERY contract remain binding.
Earlier R.1 development and failed-run evidence remains historical, not
the current gate status. The G!150 FORMTREE/DEBUGINT issue remains
separate and unresolved. **No BOOT_OBJ or BOOT_DEVOBJ promotion** was
authorized by R.1 closure.

**R.2 owner decision (22 October 2026):** Permanent **G!203 / DEMOSVC** is allocated to **BCPLDEMO**, a maintained teaching/reference optional extension. Its source candidate has QUERY and GETVALUES opcodes, real BCEX/BCPLREG selection and a temporary link-run demonstration. See the [design decision](runtime-extensions-r2-bcpldemo-decision-20261022.md) and [example](../bootstrap-toolchain/extensions/bcpldemo/README.md). **Extension A passed its first actual MVS demonstration in JOB 3075** (six IFOX assemblies, IEWL, GO all RC=0000; expected BCPL marker and MAP verified). See [JOB 3075 evidence](runtime-extensions-r2-bcpldemo-job-3075-evidence-20261022.md). **The two-extension 0/A/B/A+B acceptance matrix remains pending.**

## 1. Purpose

Make independent native BCPL runtime services, beginning with proposed `BCPLQSAM`, `BCPLDEC`, and `BCPLTIME`, **optional at application link-edit time**, without rebuilding the compiler or editing BCPLMAIN whenever a new service is added.

Separate three decisions:

1. **Distribution:** Which optional objects and declarations are installed with Cambridge?
2. **Application link-edit:** Which available objects become part of a particular program load module?
3. **Program startup:** How do the *selected* modules' callable entry addresses reach the BCPL global vector?

A compiler build is not the same thing as a BCPL application build. An installation can carry all optional objects while most applications link none. MVS JCL / IEWL selects objects; BCPL runtime startup registers their globals. Running the already linked program does not select the modules. The ordinary run JCL supplies DD statements and other resources, not optional code-module selection.

This facility is a **project-designed extension** to reconstructed Cambridge, not claimed to be an authenticated feature of the original historical BCPL system. Do not make it a prerequisite for M4 self-hosting.

## 2. Actual reconstructed baseline

The current `bootstrap-toolchain/asm/bcplmain.asm` demonstrates the following:

- Generated BCPL code addresses `G!N` at `R12 + 4*N`. `G!0` records the global-vector extent.
- Startup obtains storage with MVS `GETMAIN`. At present it has 700 global-vector words, numbered 0..699; `GLOBCNT EQU 699`. Do not mistake this WIP extent for a historical or permanent limit.
- Startup paints globals other than `G!0` with historical uninitialized sentinels `X'C7D3F000' + 4*N`.
- The application compiled by CG370 has exported-global pairs in a trailing record: global byte offset `4*N` and a relocated procedure address, preceded by trailer control/sentinel words. BCPLMAIN walks these and writes addresses into `G`.
- After application imports, BCPLMAIN **explicitly refers to `BLIB`** and walks a BLIB trailer to install its exports. The mechanism is usable precedent, but the reference to BLIB is hard-coded, not generic discovery.
- BCPLMAIN also explicitly populates particular native-service global slots, including G!85 GETBYTE and G!86 PUTBYTE, and invokes binding support for other native runtime modules.
- The present importer writes into global slots directly; **do not assume duplicate-global detection or extension lifecycle management already exists**.
- A conventional MVS linkage edit resolves external symbols and relocations, but it does **not** automatically fill `G`. Merely issuing `INCLUDE ... (BCPLQSAM)` does not make its procedures callable through BCPL globals.

See the [Global Number Registry](global-number-registry.md) for recorded allocations and collisions. `richards-bcpltape/sys3/bcpl/libhdr` historical globals already assign `READREC:23`, `WRITEREC:24`, `TIMEOFDAY:27`, `TIME:28`, `DATE:29`, and document `FIRSTFREEGLOBAL=150`. Proposed QSAM and clock interfaces **must not silently replace these historical names and slots**. Existing G!150 is currently used by a provisional diagnostic in BCPLMAIN; `FIRSTFREEGLOBAL` is not an automatically safe allocator. Inventory every reserved and presently used slot before fixing an extension numbering policy.

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

### Approved R.0 shared dispatcher and QUERY interface (implementation pending)

**Owner-approved version-1 interface design (not yet implemented):** An optional System Extension, Standard Library or User/Site Library normally occupies **one allocated BCPL global-vector slot** containing the address of a single **dispatcher procedure**. The caller passes an operation number as the first argument. Internal procedures remain private and do not consume additional public `G!N` slots. Only justified exceptions should use multiple public slots.

For example, **illustrative global number only**:

```bcpl
GLOBAL $( TIMESVC:201 $)
MANIFEST $( T_QUERY=0; T_NOW=1; T_ADD=2; T_DIFF=3 $)
```

G!201 is now allocated to **BCPLTIME** by the [Global Number Registry](global-number-registry.md); the example's name `TIMESVC` is illustrative, not yet an approved public header symbol. G!200 is allocated to **BCPLQSAM**, and G!202 to **BCPLDEC**. The Global Number Registry owns the package's dispatcher slot; a package-specific API/header owns its *stable, local opcode numbers*. Compilation embeds the selected global and opcode constants; IEWL chooses which package is linked; the approved BCPLREG mechanism will install its **single** dispatcher address into G before START when implemented in R.1. No dynamic global-number assignment is required.

**Opcode 0 is reserved for `QUERY` in every participating optional package.** It must be side-effect free: no I/O, clock read, dataset OPEN, state-changing setup or allocation. It returns interface/capability information about a *linked and registered* package; it is **not** a package-discovery mechanism and cannot safely be called if that package's global remains unset. The build's link/registration and required-package checking must cover that case.

#### Capability query: caller-owned numeric descriptor, not a string

**Owner-approved version-1 signature** (see [shared QUERY contract](runtime-extensions-r0-query-abi-decision-20261021.md); MVS cross-package validation pending):

```text
PACKAGE_SVC(0, info_vector, capacity_words) -> positive_required_words | negative_error
PACKAGE_SVC(0, 0, 0)                       -> positive_required_words  (size inquiry)
```

The vector is writable BCPL word storage, capacity is in **32-bit BCPL words**, and `capacity_words` includes the *entire* descriptor. Query with a null vector and zero capacity returns the required size without writing. A sufficiently large buffer is filled, and the function returns the required word count. An undersized or invalid buffer produces a documented negative error and **must not write partially**. No pointer to an extension-owned lifetime-sensitive table is returned. An immutable static table can still be an *internal* implementation detail copied into the client's vector. Exact argument-register and pointer validation remain R.0 obligations.

**Owner-approved six-word version-1 prefix** (native cross-package tests pending):

| BCPL word | Field | Meaning |
| --- | --- | --- |
| `info!0` | descriptor format | Version of the *shared query layout* (initially 1) |
| `info!1` | API major | Package interface compatibility generation; incompatible changes increment major |
| `info!2` | API minor | Backwards-compatible additions increment minor |
| `info!3` | required words | Full descriptor size, including future appended words |
| `info!4` | supported operations | 32-bit bitmap: bit 0 means opcode 1 supported; bit N-1 means opcode N supported for 1..32 |
| `info!5` | capability flags | Versioned, package-defined secondary capabilities; initially zero if none |

Approved minimum descriptor size is **6 words**, so `VEC 5` is the BCPL allocation shape for packages whose entire descriptor requires only six words. Extra capability words (additional opcode maps or documented feature fields) may be appended in future versions *without altering this prefix*. Query-format and API-version compatibility rules must be recorded separately. A capability flag or advertised opcode indicates **implemented support**, not necessarily that an environmental resource (such as a particular DDNAME or clock state) will work when invoked. A feature can also be absent from an older compatible implementation.

**Approved common errors:** `-1` insufficient capacity (including a nonnull vector with zero capacity), `-2` unsupported nonzero opcode, and `-3` invalid QUERY argument pairing or negative capacity. No partial writes. Only a null vector with zero capacity is a valid size inquiry. A vector smaller than the *entire* returned descriptor length is rejected. The [shared QUERY contract](runtime-extensions-r0-query-abi-decision-20261021.md) governs first-error precedence, append-only semantics and API version matching; each package documents its other operation-specific statuses.

#### How client BCPL would consume the query

Schematic BCPL; uses provisional `TIMESVC` and opcode allocation; **not regression-tested source**:

```bcpl
LET INFO = VEC 5
LET NEED = TIMESVC(0, 0, 0)         // size inquiry; no write
// Reject non-positive NEED, or allocate VEC (NEED-1) if needed.
LET RC = TIMESVC(0, INFO, 6)       // valid only when NEED <= 6
// Require RC = NEED, INFO!0 = 1, INFO!1 = expected API major.
// Before invoking T_ADD=2, require bit 1 of INFO!4 to be set.
// Then use TIMESVC(T_ADD, date, delta, output), as defined by BCPLTIME.
```

A production example must check the returned required length and reserve the **entire** descriptor before calling QUERY with a nonnull pointer. **Prefix-only success is not supported**; a six-word buffer must fail without modification when a compatible package needs more words. Do not rely on QUERY to discover an unlinked or unregistered module.

**Why a numeric descriptor:** BCPL applications can inspect version and feature bits directly, with no EBCDIC parsing, storage ownership/lifetime ambiguity, or host-dependent text formatting. A human-readable module name or release string could be an *optional separate opcode*, not required for ABI negotiation. A flat version integer alone would not efficiently report optional functions.

**Wrappers are deferred.** Callers may initially invoke the dispatcher explicitly. Friendly BCPL helper functions can be added later as package source code without allocating additional public globals, but must not become a prerequisite for this contract.

A function-address table in the single slot is an alternate design, but it would require verified native BCPL procedure-pointer and indirect-call semantics and more lifetime guarantees. Prefer the **dispatcher** for the first implementation because it uses the proven BCPL call path; measure its overhead only if later workloads justify optimization. The shared query protocol and local opcodes remain stable if an implementation changes its private procedure layout.

**Historical R.0 evidence:** Q.0 JOB 2157 verified one synthetic dispatcher under MVS; the [two-dispatcher R.0 probe](../bootstrap-toolchain/probes/r0-query-probe/README.md) subsequently passed actual MVS JOB 2206. The fixture's G!298/G!299 are **not global-number allocations**; official G!200/201/202 ownership remains with BCPLQSAM/TIME/DEC. R.2 must repeat the two-dispatcher behavior under actual optional BCPLREG selection, not only isolated synthetic linkage.

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
4. **Global slots and dispatcher namespaces:** authoritative static Global Number Registry; historical G!0..G!149 and occupied G!150+; one dispatcher slot per optional package by default; package-owned stable opcode allocations; capacity policy and collision checks.
5. **Conflict handling:** duplicate declarations within a module, between selected modules, against app/BLIB/core; explicit intentional override if ever supported, otherwise fail cleanly before START. No silent last-write-wins.
6. **Dependencies:** what happens when QSAM depends on a core service or another optional module, and how the link and registration table express it.
7. **Initialization and finalization:** entries alone versus optional init/finalization hook, sequencing, failure cleanup, and correct MVS save-area/register discipline. Prefer no hooks for stateless facilities. The approved [BCPLQSAM Q.0 staging/resource decision](qsam-q0-staging-resource-design-decision.md) establishes a requirement for **generic normal-termination finalization** of linked stateful extensions on FINISH and STOP(n), before final core storage reclamation. R.0 must specify safe descriptor/hook representation, sequencing, failure reporting and absence of a linked optional module; it does not yet implement this facility.
8. **Missing optional functions:** a BCPL `GLOBAL` reference is indirect through `G`, so omission can escape the linkage editor; define a preflight declared-requirements check or reliable failure mode. Never claim ordinary link-edit checks all missing globals.
9. **ABI/versioning and opcode 0:** the [shared QUERY v1 contract](runtime-extensions-r0-query-abi-decision-20261021.md) is **owner-approved**; independent two-dispatcher MVS execution remains pending, as does the later integrated rejection of incompatible extension descriptors.
10. **Testing:** preserving existing BLIB and native service behavior without modifying current accepted artifacts ahead of gates.

### Owner-approved R.0 registration/finalization model; A–H accepted

The [Q.0 limits/failure/finalization review](qsam-q0-record-limits-failures-finalization-review.md)
now records an **owner-approved architectural decision**: a
versioned, bounded, linker-selected `BCPLREG` table with
relocated package descriptors, each with an optional finalizer
address; finalizers run exactly once in reverse registration order
on normal `FINISH` and `STOP(n)`, **before** `BCPLIO.IOFIN` and
`BCPLMEM.MEMDRAIN`. Duplicate/malformed exports or unsatisfied
declared package requirements are rejected before `START`.
A returned finalizer error produces a diagnostic and **RC=8 on
ordinary FINISH**; `STOP(n)` retains n. The byte-level descriptors and 8-byte public finalizer ABI were
**subsequently approved** in [A–H](runtime-extensions-r0-owner-abi-decisions.md).
Decision G's numerical limits and diagnostic values were subsequently
**approved** and its isolated 14-case MVS count/size test **PASSED**
(JOB 2203). Remaining contract/evidence tasks are listed in the
[R.0 gate review](runtime-extensions-r0-gate-review-20261021.md).
This paragraph records the former R.0 design stage. R.1 has since verified integrated registration through temporary BCPLMAIN/registrar/link overlays; the accepted `BOOT_OBJ` objects remain unchanged.

## 7. March roadmap with explicit gates

| March | Objective | Deliverable and exit gate |
| --- | --- | --- |
| **R.0 — Evidence and contract** | Inventory the actual CG370 trailer, global initialization/import ordering, BLIB and native binders, link-editor behavior, and slot map; evaluate dispatcher/opcode-0 capability ABI | Recorded verified ABI; static global-number registry policy, one-slot dispatcher decision, candidate six-word QUERY descriptor and client tests, chosen registrar/descriptor formats, collision and empty-table rules; **no speculative source refactor** |
| **R.1 — Generic registration foundation (CLOSED 22 October 2026)** | Implement one minimal, linker-driven registration path with an empty registry and one trivial optional assembler service | Gate accepted: 24 integrated MVS jobs PASS, all five gates PASS, fresh 145 PASS / 0 FAIL / 1 expected SKIP 083 ([closure record](runtime-extensions-r1-closure-20261022.md)) |
| **R.2 — Selective interoperability** | Link two independent optional extension *probes*, individually and together; if practical one compiled BCPL extension export plus one assembler export | 0/A/B/A+B combinations work without BCPLMAIN rebuild; each linked dispatcher answers opcode 0 and rejects unsupported calls, client inspects version/opcode bitmap; collisions, invalid descriptor, missing dependency/slot, absent module diagnosed deterministically; inspect linkage maps |
| **R.3 — Packaging and acceptance** | Stable user-facing link-edit recipe, BCPL declaration conventions, developer template and reproducible rebuild from Git | Full native regression baseline; separately accepted object PDS installation decision; documented accepted startup contract and actual JES/IEWL evidence |

The probes should be *tiny*, not premature implementations of QSAM/DEC/TIME. Subsequent feature milestones own their APIs and behavior. A failed gate can suspend R without blocking M4.

## 8. Relationship to other milestones

- **Milestone QSAM:** depends on a stable optional-registration mechanism for *automatic* global installation; it may continue isolated linkage/ABI experiments without R, but should not invent its own registrar.
- **Milestone Decimal Arithmetic:** uses the shared registration architecture for `BCPLDEC`; decimal descriptors, arithmetic semantics and rounding remain that milestone's responsibility.
- **Milestone Date and Time Services:** uses the same architecture for `BCPLTIME`; calendar and MVS TIME semantics remain separate.
- **M4 self-hosting:** **not blocked** by R. Reconstructing the compiler remains higher priority if schedule conflicts arise.

A historical BCPL system already exposed global names `READREC`, `WRITEREC`, `TIME`, and `DATE`. New optional modules must either choose distinct names/globals or deliberately implement proven historical contracts as an entirely separate acceptance decision. Do not quietly reinterpret legacy symbols.

## 9. Reproduction, evidence and repository layout

Authoritative namespace: `config/dspal.yaml` and `tools/datasets/dspal`. Candidate assembler objects: `BOOT_DEVOBJ`; accepted core objects: `BOOT_OBJ`. Do not use superseded historical `HERC02.BCPL.OBJ` conventions, do not populate `CAMB_*` for this work, and do not migrate prebuilt objects.

Proposed deliverables (paths provisional pending R.0): an assembler registration-table template, a minimal `BCPLREG` consumer, two miniature optional services, BCPL declaration headers/examples, link-edit JCL, regression checks, and gate records under `packaging/`. Document exact observed MVS job IDs, condition codes, map/cross-reference excerpts and commands; never mark a test PASS by inspection alone.

The goal is **a stable, simple, historically intelligible extension pattern**, not a plugin loader, dependency manager, or dynamic linker.

## 10. Next review — R.2 — Selective interoperability

R.0 and R.1 are closed. BCPLDEMO design and permanent G!203 allocation are owner approved; extension A code is a candidate awaiting MVS testing. Before the complete R.2 acceptance campaign, review the two small
independent optional extension probe designs (A and B), including their
BCEX descriptors, BCPLREG selection, opcode-0 QUERY results, and the
0/A/B/A+B link/edit matrix. Reuse the R.1 registration core rather than
rebuilding BCPLMAIN per selection. Plan expected failures for collisions,
malformed descriptors, missing required dependencies and absent modules,
plus IEWL MAP and MVS output verification. If practical, include one
compiled BCPL export alongside an assembler export. Keep the probes
small; QSAM/DEC/TIME functionality is owned by their separate milestones.
Do not promote BOOT_OBJ or BOOT_DEVOBJ without an independent owner decision.
