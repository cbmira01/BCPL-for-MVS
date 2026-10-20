# Milestone Runtime Extensions — R.0 evidence and contract review

**March:** R.0 — Evidence and contract (**in progress**, 2026-10-20).
**Implementation:** none. R.1 — Generic registration foundation
**not started**. This is the first evidence/contract record under the
already named Runtime Extensions milestone, **not a new milestone or
renumbered march**.

**Authority:** [Milestone Runtime Extensions](milestone-runtime-extensions.md),
[Cambridge runtime and library nomenclature](runtime-and-library-nomenclature.md),
[Global Number Registry](global-number-registry.md),
[BCPLQSAM Q.0 approved error and R.0 policy](qsam-q0-error-and-r0-design-decisions-20261020.md),
and Git-controlled `bootstrap-toolchain/asm/bcplmain.asm`,
`bootstrap-toolchain/asm/bcplio.asm`.

## 1. Source evidence already visible in the current runtime

| Evidence | Current source behavior | Contract consequence |
| --- | --- | --- |
| BCPLMAIN globals | `GINIT` paints a 700-word vector (0..699) with sentinel values; `GSCAN/GINST` walks CG370 application export pairs | The future importer must use bounded extents and reject collisions |
| BLIB linkage | `GIDONE/BLIMP` explicitly refer to relocated `BLIB` and write its exported globals | Optional object presence must never be confused with automatic global publication; BLIB precedence requires auditing |
| Native services | BCPLMAIN explicitly installs native runtime globals | A new registrar cannot silently overwrite current core assignments |
| `FINIMPL/STOPENT/FINEXIT` | `FINIMPL` clears `STOPRC`, `STOPENT` stores R7; `FINEXIT` calls `IOFIN`, then `RELMEM` | A generic finalizer call must run **before IOFIN**, must keep STOP code, and must not break save-area discipline |
| `RELMEM` | Calls `MEMDRAIN` then `MEMBIND` and frees remaining dynamic base | A finalizer must finish while private storage and MVS services remain valid |
| BCPLIO IOFIN | Flushes pending output and closes active streams; invokes `IODRAIN` | Shared ordering affects observable output and requires regression evidence |

These are **source observations**, not a tested R.0 registrar.
No binary descriptor, selector table, finalizer invocation, or
collision detector currently exists.

## 2. Owner-approved architectural contract

- A single per-application IEWL-selected, link-relocated
  **`BCPLREG` registration object** enumerates explicitly selected
  package descriptors. Empty registry is supported. Header
  conceptually provides signature, format version, total byte
  length, and entry count for bounded validation.
- Package descriptors conceptually provide identity/version,
  global-number/address exports, and optional finalizer entry.
  Default is one stable BCPL global dispatcher per package;
  no extra cleanup global.
- Unlinked packages have no entry and must not be queried as a
  discovery mechanism. Required-but-absent packages and malformed,
  out-of-range, duplicate, or conflicting exports cause
  deterministic failure **before START**.
- Finalizers are invoked exactly once in **reverse registration
  order**, before **BCPLIO.IOFIN**, before **BCPLMEM.MEMDRAIN**.
  Stateless packages have no finalizer.
- `STOP(n)` completion stays **n**; a returned finalizer error
  generates a diagnostic without overwriting it. For ordinary
  `FINISH`, any returned implicit-finalizer failure generates a
  diagnostic and changes completion to **RC=8**. No guarantee for
  unrecovered abend exits.
- Descriptors and hooks must use a single generic mechanism for
  independently compiled BCPL and assembler services; no
  BCPLQSAM-specific registrar or teardown call.

This approves the **model and observable lifecycle policy**, not a
particular System/370 byte layout. No new global numbers are
allocated by this review.

## 3. Technical ABI items requiring R.0 evidence

| Question | Required method and evidence |
| --- | --- |
| Header binary layout | Compare compact count/length/sentinel formats against actual IFOX alignment and relocations; document offsets and end marker before code |
| Descriptor ABI | Define exact assembler entry pointer relocation, export count, names/versions and optional finalizer pointer; demonstrate IEWL output |
| Existing CG370 exports | Verify relative trailer extent, relocation, application vs BLIB precedence and START validation with a real listing |
| G!N collision policy | Explicitly reject duplicates against application, BLIB, core and peer descriptors before START |
| Missing package and dependencies | Decide explicit requirement mechanism; prove absent optional module leaves sentinel yet required absence fails predictably |
| Finalizer ABI | Register/save-area/stack discipline, return status, diagnostics and abnormal-close ownership; prove one reverse-order invocation |
| Normal termination | `FINISH` RC=0 when clean; `FINISH` RC=8 on returned finalizer failure; `STOP(8)` preserves RC=8 even if finalizer fails |
| Empty/selected registry | Link/run 0 and 1 test module with no compiler rebuild; later R.2 proves two independent selections |
| Regression | Preserve existing BCPLIO FINISH/STOP stream closure and historical BLIB behavior |

**Do not implement R.1 before R.0 resolves exact layouts and
startup/finalizer diagnostics.** No extra milestone/march numbers
have been introduced.

The [three-question follow-up review](runtime-extensions-r0-three-design-questions-review-20261020.md)
addresses independently checked descriptor extents, transitive
package dependencies and collision checking with legacy import
precedence. It is **engineering recommendation, not owner-approved
ABI**. The [partial BCPLMAIN native global-owner inventory](runtime-extensions-r0-native-global-owner-inventory-20261020.md)
records actual direct assignments; application and BLIB trailer
exports remain to be decoded from the final linked program.

## 4. Next R.0 work package

1. Extract precise actual System/370 assembler linkage and register
   saves for `BCPLMAIN`, `BLIB`, generated CG370 exports and
   `BCPLIO.IOFIN`; record a table of offsets and symbols.
2. Compare proposed relocatable count/length descriptors and
   minimal hook calling conventions without changing accepted objects.
3. Prepare isolated MVS test-only registrar/ordering probes and
   negative examples: empty, singleton, collision, missing module,
   double finalizer and returned finalizer failure.
4. Ask the owner to approve the **exact** descriptor and finalizer
   ABI after inspection of test evidence, then decide whether
   the R.0 gate is satisfied. **R.1 remains unstarted**.

**R.0 experiment added (test-only):** The owner approved the revised
bounds/dependency/collision design for **R.0 testing**, not final ABI.
A [six-profile isolated descriptor/linkage experiment](../bootstrap-toolchain/probes/r0-registration-probes/README.md)
is prepared, with a valid profile and five targeted rejection fixtures.
The initial Morkies validation found a **test-generator syntax
error** (`test_generator.py`, missing `)`) before submission.
After the correction the owner ran the four Python tests, all six
JCL profile dry-runs, and [JOBs 2187–2192](runtime-extensions-r0-first-probes-evidence-20261020.md)
with **six RC=0000 steps and the required actual QOUT marker in
every job**. The [20-case dependency/simulated-finalizer batch](runtime-extensions-r0-batch-job-2195-evidence-20261021.md)
**PASSED as JOB 2195** with six IFOX steps, IEWL and GO all
RC=0000 and twenty actual QOUT records (14 D, 6 F). No
production importer/finalizer has been implemented; the
standalone test's FINISH/STOP simulations are not BCPLMAIN execution. See the
[decision record](runtime-extensions-r0-testing-decision-20261020.md).

**The parallel Q.0 concurrent-DCB probe has now passed** in
[JOBs 2183–2186](qsam-q0-concurrent-dcb-evidence-20261020.md),
including sixteen simultaneously OPEN DCBs at GO REGION=256K.
Those jobs do **not** implement or validate the R.0 contract.

## 5. Candidate binary ABI review now available

See [R.0 candidate exact byte layout and finalizer calling convention](runtime-extensions-r0-candidate-binary-abi-20261020.md).
It inventories current BCPLMAIN application-trailer and BLIB
imports, the G!0..699 capacity and FINEXIT cleanup sequence.
It proposes a relocatable `BCPLREG` header, explicit package
descriptors and a separate assembler finalizer ABI. The earlier
single-pointer/40-byte proposal was refined through successful
bounded test-only MVS evidence; the [21 October ABI review](runtime-extensions-r0-abi-decision-review-20261021.md)
now requests the owner's decision on the revised paired-extent
48-byte package candidate. **Subsequently, decisions A–H were owner-approved** in the
[R.0 decision record](runtime-extensions-r0-owner-abi-decisions.md);
G's numeric values and actual application/BLIB trailer evidence remain open.
The approved higher-level registration/finalization model and
FINISH RC=8/STOP(n) policy have not changed.
