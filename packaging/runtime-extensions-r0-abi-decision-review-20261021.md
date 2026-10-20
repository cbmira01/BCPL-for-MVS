# Milestone Runtime Extensions — R.0 exact ABI decision review

**Date:** 21 October 2026. **March:** R.0 — Evidence and contract
(**open**); R.1 — Generic registration foundation **not started**.
**Purpose:** Present **engineering recommendations requiring owner
approval**, not install a production binary contract or mark R.0
closed. Read with the [three-question review](runtime-extensions-r0-three-design-questions-review-20261020.md),
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

## Recommended v1 wire contract — owner decision requested

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
Accepting this review would supersede the older draft, with new
final ABI macro/source definitions still required in R.1.

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

**Recommendation requiring owner decision:** Public v1 requires only
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

## Proposed global-owner validation rule

Prior to optional publication, construct an effective per-executable
ledger containing **actual** application and BLIB trailer exports,
all native service writers, the official reservations, and selected
package exports. Preserve exact **already accepted** legacy
precedence (notably G!76 conditional WRITEF), but allow **no new
optional-module overwrites**. Validate **all** selected entries and
the transitive dependency closure transactionally; install zero
optional G!N entries upon any rejection. See the [separate audit](runtime-extensions-r0-global-ownership-audit-20261021.md)
for why a complete actual-export ledger is still pending.

## R.0 owner decision checklist (all currently open)

| Decision | Engineering recommendation | Acceptance status |
| --- | --- | --- |
| A. Trusted extent model | Mandatory begin/end linker symbols + source-controlled build/link verification | **Not yet owner-approved as final ABI** |
| B. Table format | `BCRG` 28-byte header, 8-byte selected pair, 8-byte required ID; real empty object | **Open** |
| C. Package format | `BCEX` 48-byte header + `8*K` exports + `16*D` dependencies; version rule above | **Open** |
| D. Dependency/lifecycle | Application + package requirements; strict dependency-first order, lazy initialization, reverse teardown | **Open for exact ABI** (general lifecycle policy approved) |
| E. Collision policy | Effective legacy-owner ledger, exact historical waivers only, transactional no-new-overwrite rule | **Open for exact ABI** |
| F. Finalizer register/parameter ABI | MVS linkage, public 8-byte block; fixture-only extra trace/error words | **Open** |
| G. Defensive limits/diagnostics | Choose maximum counts/bytes and stable error diagnostics after bounded evidence | **Open** |
| H. Startup integration boundary | One generic BCPLMAIN adaptation; parse/check before START; finalizer before IOFIN/MEMDRAIN; no accepted-object change during R.0 | **Open** |

**R.0 closure is not requested by this review.** An owner decision
on A–H, actual app/BLIB export and legacy-overlap evidence,
and the R.0 gate review must precede declaring an accepted ABI.
Actual integrated registration/finalizer code and demonstrations
belong to **R.1 — Generic registration foundation** and later
marches, not to this documentation package.
