# Milestone Runtime Extensions — R.0 three unresolved ABI questions

**Status:** engineering review and **candidate recommendations for owner
decision** (20 October 2026). **Not an approved binary ABI or a test
result.** R.0 — Evidence and contract remains open; R.1 — Generic
registration foundation has not started. No compiler, runtime, object
PDS, assembler or JCL is changed by this review.

Read with [Milestone Runtime Extensions](milestone-runtime-extensions.md),
[official nomenclature](runtime-and-library-nomenclature.md),
[Global Number Registry](global-number-registry.md), the
[earlier candidate wire format](runtime-extensions-r0-candidate-binary-abi-20261020.md)
and the [R.0 source audit](runtime-extensions-r0-evidence-and-contract-20261020.md).
The owner has **already approved the general BCPLREG model**,
pre-START collision rejection, reverse-order finalizers,
ordinary FINISH RC=8 for a returned finalizer failure, and
STOP(n) preservation. The **exact** representation remains open.

## 1. Can the startup code safely read a descriptor?

**Source evidence:** `bootstrap-toolchain/asm/bcplmain.asm` imports
application globals by a backward scan beginning at `MODEND`, obtained
from the generated application's prefix halfword at +10. It imports
BLIB globals by a separate backward scan. Neither is a general
link-edited load-module length/ownership test. JOB 2157 proved a
relocated `DC A(Q0DISP)` target in the generated application's
trailer. No MVS job yet proves safely bounded `BCPLREG`/package
descriptor access.

**Critical point:** `length` read from a potentially invalid pointer
cannot be used to prove that the pointer itself is valid. A
post-dereference length check is not protection from an invalid read.

**Recommended refinement (UNAPPROVED):**

1. Provide link-resolved **begin and end symbols** for the
   `BCPLREG` table, each package descriptor's **data** extent, and
   the selected package entry addresses. Keep the descriptor data
   contiguous in its own CSECT, separate from arbitrary execution
   code and literal pools. Generate both labels from checked IFOX
   source, rather than interpreting a forged CG370 module prefix.
2. An explicitly selected table entry carries **two relocated
   addresses**, descriptor start and descriptor end, instead of
   the prior single descriptor pointer. Thus the earlier candidate
   `BCPLREG` size expression `28+4*N+8*M` would become
   **`28+8*N+8*M`**, pending further design.
3. The startup entry receives the trusted `BCPLREG` begin/end
   addresses through **mandatory linked externals**. Require a real
   empty table for applications with no optional packages: do
   not depend on unproven weak-linker behavior. Verify the
   beginning/end symbols and extents in the IEWL MAP during the
   R.0 test program.
4. Before accessing fields beyond the fixed header, require aligned,
   ordered begin/end addresses and a bounded physical span.
   Validate magic, version, nonnegative counts, overflow-safe
   `header + entry-count * stride + required-count * stride`,
   exact equality of declared length with the **independent**
   start/end span, and fixed field alignment. Do the same for
   each descriptor before reading export/dependency arrays.
5. Give the v1 format a small explicit documented maximum for
   selected packages, dependencies and table bytes, chosen by
   test evidence rather than by MVS's theoretical address space.
   Reject unsupported counts; never use a sentinel-only unbounded
   walk.

**Security/robustness limitation:** Two relocated labels from a
maliciously crafted object are not proof that arbitrary memory is
safe. A runtime pointer range check is useful only when its backing
extent is **trusted independently**. The candidate therefore also
requires a reproducible, source-controlled **build/link-time
validation** of every generated descriptor object and its
start/end/map symbols. A corrupt load module or deliberately forged
link-editor externals are **outside the promised ordinary recoverable
error surface** unless further genuine MVS protection evidence
exists. Never advertise universal avoidance of S0C4 abends.

**Required negative tests:** wrong total byte count, zero span,
reversed span, odd/misaligned address, unsupported count, duplicate
table entry, truncated descriptor, and invalid version. Build
**bounded valid-memory fixtures** rather than intentionally
dereferencing arbitrary bad addresses. Record assembler, IEWL,
startup diagnostic and GO return codes.

## 2. How do dependencies work without a new loader?

**Source evidence:** `GLOBAL` is a compile-time declaration.
IEWL can resolve explicit externals, but absence of an optional
global need not be caught by IEWL. The previously proposed
`BCPLREG` required-ID list handles application requirements;
a package descriptor currently has **no dependent-package list**.

**Recommended refinement (UNAPPROVED):**

- Retain the `BCPLREG` **application required-package list**.
  Generate it from an explicit per-application build manifest,
  not by guessing which global names BCPL source may call.
- Each selected package descriptor additionally declares **its
  mandatory optional-package dependencies**: an eight-character
  package ID, required API major and minimum compatible minor.
  Dependencies on guaranteed Core Runtime/BLIB services should be
  separately documented, not fictitious optional package entries.
- Ensure the selected registry satisfies the **transitive closure**
  of package requirements before publishing optional globals. Reject
  missing packages, repeated package IDs, incompatible versions and
  dependency cycles before `START`.
- Make the **explicit BCPLREG selection order dependency-first**.
  A selected package B must precede package A when A depends on B;
  reject reversed ordering. This allows reverse-registration
  finalization to close A before B. Avoid a new general-purpose
  dynamic dependency sorter at runtime.
- For the first ABI, **no initializer hook**: optional services may
  lazily initialize private state on their first dispatched call;
  finalizers must be harmless for never-used packages. A package
  requiring eager initializers would require an expressly approved
  later design change. Do not assume lazy initialization is already
  implemented in BCPLQSAM.

**Binary-format consequence:** The earlier candidate 40-byte
descriptor with no dependencies is incomplete for this policy.
A possible *replacement*, still **UNAPPROVED**, is a 48-byte header
with count D at offset 40 and zero reserved word at offset 44,
followed by K eight-byte exports and D sixteen-byte dependency
records `(CL8 ID, F'major', F'minimum_minor')`. This makes
descriptor bytes **`48+8*K+16*D`**. No offsets have been
committed to an assembler macro or public ABI.

**Required tests:** zero dependencies; one satisfied dependency;
a required package not selected; wrong API major/minor;
a transitive missing dependency; a cycle; same ID selected twice;
dependency order reversed; and stateful A using B with finalizers
invoked A-before-B. Distinguish unresolved IEWL symbols from
successful link followed by deterministic pre-START rejection.

## 3. How can collisions be found without breaking BLIB?

**Direct source evidence in `bootstrap-toolchain/asm/bcplmain.asm`:**

- `GINIT` fills G!1–G!699 with `X'C7D3F000'+4*N` sentinels.
- `GSCAN/GINST` scans and **writes application** trailer pairs.
- `GIDONE/BLIMP` then walks and **writes BLIB** trailer pairs.
- The runtime then writes selected native entries, including
  G!14, G!85–88, G!150 and others. G!76 is a documented special
  fallback: use `WRITEST` only when BLIB's WRITEF slot remains
  unset. G!30 is `STOPENT`.
- The Global Number Registry reserves **G!200 BCPLQSAM**,
  **G!201 BCPLTIME** and **G!202 BCPLDEC**. It also records
  historical G!94 duplicate naming and an unresolved G!150
  cross-component conflict. Those are not new vacant globals.

A check that only compares an optional export against the
**final** G!N sentinel misses a prior writer overwritten by BLIB
or native installation. Rejecting every overlap in the
historical import paths could also change accepted BLIB behavior.

**Recommended refinement (UNAPPROVED):**

1. Build an authoritative **slot-owner ledger** at link-preparation
   time: decoded application CG370 trailer pairs, decoded BLIB
   trailer pairs, the explicit native `BCPLMAIN` assignment map,
   reserved historical and System Extension slots, and each
   selected optional descriptor's exports.
2. Mark each legacy collision as `historical/accepted precedence`
   or `unresolved` with exact symbol, source and test evidence.
   **No blanket waiver** for every app/BLIB overlap and no
   silent last-writer-wins for an optional module.
3. Before START, validate selected exports against that ledger:
   in-range number, unique number within a descriptor, no overlap
   among selected packages, and no overlap with effective app/BLIB/
   core owners or another package's reserved slot. A new selected
   `BCPLQSAM` descriptor may own G!200; another package may not.
4. **Do not retroactively reject an otherwise unchanged legacy
   executable** because existing BLIB/native imports have an
   explicitly documented and regression-tested precedence.
   Audit any unresolved historical overlap separately before
   declaring an R.0 acceptance gate satisfied.
5. Make checks transactional: validate the entire table, including
   dependency graph and export ownership, **before publishing any
   optional G!N entry**. Keep the current runtime import order
   intact until the ledger and tests justify changing it.

**Required tests:** empty registry with existing BLIB regression
unchanged; two optional modules exporting the same global; one
optional module exporting a reserved core global; duplicate export
within one descriptor; mismatched package/global allocation;
one selected G!200 vs an app-injected test-only G!200; and
unchanged legitimate G!76 behavior.

## 4. Recommended R.0 evidence sequence

| Order | Task | Exit evidence |
| --- | --- | --- |
| 1 | **Static ownership audit** of the actual CG370/BLIB trailers and native assignments | Authoritative per-slot ledger with citations to sources/listing and precisely enumerated legacy overlaps |
| 2 | **Isolated linker extent experiment** using start/end symbols in dedicated table CSECTs | IFOX RC, IEWL relocations/MAP, consistent begin/end and guarded v1 lengths |
| 3 | **Dependency and collision validation fixtures** | Missing/duplicate/cyclic/bad-version combinations rejected before any optional G!N publication |
| 4 | **Minimal finalizer ordering proof** using an assembler test harness | One reverse-order invocation, normal FINISH RC=8 on returned failure, STOP(n) preserved, no BCPLIO regression |
| 5 | **Owner's exact ABI decision and R.0 gate review** | Approve or revise byte offsets and hook ABI based on evidence; R.1 remains unstarted until approved |

All executable experiments are **future, test-only R.0 evidence**, not
a request to create production registration/finalizer code in this
review. Follow the project's current `BOOT_*` namespace; keep
generated JCL in ignored `workarea/`, do not install objects to
`BOOT_OBJ` or `BOOT_DEVOBJ`, and do not touch the
`cambridge-compiler/` tree.

## 5. Owner decisions still required

1. **Bounded explicit begin/end relocation** (and a verified
   build/link-time object extent) rather than trusting only
   self-reported length fields.
2. **Two-level dependencies** (application required-package IDs,
   plus package-local dependencies), strict dependency-first
   registration order and lazy initialization in v1.
3. **Pre-START combined slot-owner ledger**, preserving explicitly
   verified legacy BLIB precedence but rejecting collisions
   involving newly selected optional exports.
4. Whether to accept the proposed **48-byte descriptor** with
   16-byte dependency entries, and the revised `BCPLREG`
   selected-entry stride of 8 bytes. Both are candidates,
   not yet official ABI assignments.

These refinements should be discussed and approved **before**
implementation. A successful isolated R.0 linker probe would
support them, but would not automatically accept production R.1.
