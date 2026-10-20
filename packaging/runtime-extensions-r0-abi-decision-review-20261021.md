# Milestone Runtime Extensions — R.0 exact ABI decision review

**Date:** 21 October 2026. **March:** R.0 — Evidence and contract
(**open**); R.1 — Generic registration foundation **not started**.
**Owner disposition:** Decisions **A–H approved** (20 October 2026),
recorded in the [owner decision record](runtime-extensions-r0-owner-abi-decisions.md).
This preserves the original engineering review and JOB 2195 evidence;
approval does not install a production binary contract or close R.0. Read with the [three-question review](runtime-extensions-r0-three-design-questions-review-20261020.md),
[earlier candidate ABI](runtime-extensions-r0-candidate-binary-abi-20261020.md),
[global-owner audit](runtime-extensions-r0-global-ownership-audit-20261021.md)
and [actual JOB 2195 evidence](runtime-extensions-r0-batch-job-2195-evidence-20261021.md).

## Evidence already demonstrated (not ABI acceptance)

- JOBs **2187–2192**: independently relocated bounded descriptor
  symbols, positive case and five specific rejection cases.
- JOB **2195**: IFOX/IEWL/GO all RC=0000; **14** package-selection,
  requirement, dependency, ordering, version and collision cases plus
  **six** assembler simulated finalizer cases actually passed.
- The fixtures have tight limits (**three selected packages,
  one export and one package dependency each**); they are not a
  production-general parser or proof against forged pointers.
- The finalizer simulation exercised conventional assembler calls
  and returned statuses. It **did not invoke actual BCPLMAIN**
  `FINIMPL`, `STOPENT`, `FINEXIT`, `IOFIN` or `MEMDRAIN`.

## Approved v1 wire layout — outstanding R.0 verification

All numeric and pointer fields are System/370 **fullword byte
addresses** (not BCPL word pointers). Character IDs are uppercase,
blank-padded **EBCDIC**, exactly eight bytes; every `A(symbol)`
field is IEWL relocated. Tables and descriptors are linked data
in separately validated extents.

### `BCPLREG` table

| Offset | Bytes | Recommended v1 field |
| ---: | ---: | --- |
| 0 | 4 | EBCDIC `CL4'BCRG'` |
| 4 | 4 | Layout version `F'1'` |
| 8 | 4 | Header length `F'28'` |
| 12 | 4 | Total table length `28 + 8*N + 8*M` |
| 16 | 4 | Selected descriptor count `N` |
| 20 | 4 | Application required-package count `M` |
| 24 | 4 | Reserved zero |
| 28 | 8*N | `(A(descriptor_begin), A(descriptor_end))` |
| 28+8*N | 8*M | Application-required `CL8` package IDs |

A real **empty registry** is mandatory in a no-extension build:
`N=M=0`, span **28 bytes**. No speculative weak IEWL symbol
resolution, sentinel-only scanning or runtime package discovery.
The entry order is explicitly **dependency-first**. An application
build manifest provides required-package IDs; a BCPL `GLOBAL`
declaration by itself does not prove link-time selection.

### Package descriptor

| Offset | Bytes | Recommended v1 field |
| ---: | ---: | --- |
| 0 | 4 | EBCDIC `CL4'BCEX'` |
| 4 | 4 | Layout version `F'1'` |
| 8 | 4 | Header length `F'48'` |
| 12 | 4 | Total descriptor bytes `48 + 8*K + 16*D` |
| 16 | 8 | Fixed `CL8` package ID |
| 24 | 4 | API major |
| 28 | 4 | API minor |
| 32 | 4 | Export count `K` |
| 36 | 4 | Relocated finalizer address, or zero |
| 40 | 4 | Package dependency count `D` |
| 44 | 4 | Reserved zero |
| 48 | 8*K | `(F'G_NUMBER', A(entry))` exports |
| 48+8*K | 16*D | `(CL8 dependent_ID, F'required_major', F'minimum_minor')` |

Recommend the official registry's **one public dispatcher slot per
package** as the default; K>1 only by explicit, documented exception.
Package API major must match required major; available minor must be
**at least** the required minimum. Reject duplicate package IDs,
duplicate exported globals, missing/transitive requirements and
incorrect dependency order before START.

**Compatibility note:** The [earlier draft](runtime-extensions-r0-candidate-binary-abi-20261020.md)
had **4-byte single references** and **40-byte package headers**.
The revised fixtures demonstrate independently linked begin/end
**pairs** and dependency-bearing **48-byte headers**. These
previously published layouts must not both be called v1.
Owner approval **supersedes** that older draft; final ABI
macro/source definitions still belong to R.1.

### Pointer/extent safety is a build-plus-runtime contract

- Use mandatory linker-resolved trusted **begin/end** for the
  table and every selected package descriptor, in separate data
  CSECTs with inspectable IEWL symbols/MAP.
- Validate alignment, positive ordered extents, magic/version,
  header-size and total-size equality, counts/capacities and
  overflow-safe length formulas **before reading variable fields**.
- Independently verify the extent symbol/object sources at
  **build/link time**. Begin/end relocated labels supplied by a
  hostile object are **not** general memory safety protection.
- Choose and test **maximum counts/table bytes, diagnostic statuses,
  empty-list validity and unexpected nonzero finalizer addresses**
  before publishing an accepted ABI. The current three-package
  test limit is **not** a proposed production maximum.

### Proposed finalizer call contract — clarify fixture/public difference

Existing [earlier 8-byte public candidate](runtime-extensions-r0-candidate-binary-abi-20261020.md):
`R1 -> (F'reason', F'stop_code')`, with 0=FINISH, 1=STOP,
R15 on entry=finalizer address, R14=return, R13=valid MVS save
area, R15 return=0 or nonzero error; callee preserves R2–R12 and R13.

In contrast, **JOB 2195 uses a test-only 16-byte block**:
`(+0 reason, +4 stop_code, +8 trace_pointer, +12
injected_error_mask)`. The final two fields are instrumentation
for verification and **must not silently become production ABI**.

**Owner-approved version-1 decision:** Public v1 requires only
the **8-byte prefix** (`reason`, `stop_code`). Keep test trace
and fault injection private to the fixture. Maintain conventional
R1/R13/R14/R15 MVS linkage; caller preserves live BCPL registers,
and finalizers may lazily release private resources. No initializer
hook in v1. Always attempt all applicable finalizers **once** in
reverse dependency-first registration order, before IOFIN and
MEMDRAIN. An ordinary FINISH with returned finalizer failure yields
RC=8; STOP(n) preserves n and records a diagnostic. Unrecovered
abends remain outside ordinary returned-error policy.

**Not yet demonstrated:** real BCPLMAIN bridge register/save-area
discipline, exactly-once integration in FINEXIT, preserving STOPRC
and preexisting stream close behavior.

## Approved global-owner validation rule (actual-trailer evidence pending)

Prior to optional publication, construct an effective per-executable
ledger containing **actual** application and BLIB trailer exports,
all native service writers, the official reservations, and selected
package exports. Preserve exact **already accepted** legacy
precedence (notably G!76 conditional WRITEF), but allow **no new
optional-module overwrites**. Validate **all** selected entries and
the transitive dependency closure transactionally; install zero
optional G!N entries upon any rejection. See the [separate audit](runtime-extensions-r0-global-ownership-audit-20261021.md)
for why a complete actual-export ledger is still pending.

## R.0 owner decisions A–H (approved; evidence gates remain)

| Decision | Owner disposition | Outstanding evidence / detail |
| --- | --- | --- |
| **A** — Trusted extent model | **Approved** — linked begin/end plus build/link verification | Independently verify true source/extent; relocated forged symbols not general protection |
| **B** — Registry format | **Approved** — 28-byte `BCRG`, 8-byte pairs, 8-byte required IDs, real empty object | Verify complete bounded validation |
| **C** — Package format | **Approved** — 48-byte `BCEX`, 8-byte exports, 16-byte dependencies, version rule | Test production-sized bounds and dependencies |
| **D** — Dependency/lifecycle | **Approved** — app/package requirements, transitive preflight, dependency-first, lazy, reverse finalization | Real finalizer lifecycle integration is R.1 |
| **E** — Global ownership/collision | **Approved** — Global Number Registry authority, effective ledger, no new optional overwrites, transactional validation | Decode actual app/BLIB trailers and verify historic precedence |
| **F** — Finalizer ABI | **Approved** — 8-byte public block and MVS linkage; JOB 2195 extras private | Verify real `BCPLMAIN` bridge in R.1 |
| **G** — Defensive limits/diagnostics | **Approved in principle** | **Exact maxima and diagnostic codes still require R.0 selection/verification** |
| **H** — Startup integration boundary | **Approved** — one generic `BCPLMAIN` adaptation, before-`START` validation, finalization before IOFIN/MEMDRAIN | Production implementation in R.1; current core unchanged |

**R.0 remains open.** Owner approvals A–H are recorded, but exact
G maxima/diagnostics, actual app/BLIB export and legacy-overlap evidence,
and the R.0 gate review remain. Approval is not implementation.
Actual integrated registration/finalizer code and demonstrations
belong to **R.1 — Generic registration foundation** and later
marches, not to this documentation package.
