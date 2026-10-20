# Milestone Runtime Extensions — R.0 owner ABI decisions A–H

**Owner approval:** 20 October 2026. **March:** R.0 — Evidence and contract (**open**).
**Next march:** R.1 — Generic registration foundation (**not started**).
**Authority:** This record captures the owner's explicit approval of decisions
A–H in the [exact ABI review](runtime-extensions-r0-abi-decision-review-20261021.md).
It supersedes incompatible *design proposals*, not observed test evidence.
The approval does **not** declare R.0 closed, install a registrar, accept
MVS objects, or authorize production implementation.

The approved design uses MVS/System/370 **byte addresses** in linked
assembler structures, not BCPL word pointers. Identifiers are
blank-padded eight-byte uppercase EBCDIC; address fields are resolved
by IEWL. The [Global Number Registry](global-number-registry.md)
remains the allocation authority, distinct from executable startup
registration.

## Approved decisions

| Item | Accepted version-1 design |
| --- | --- |
| **A — Trusted extents** | Mandatory, independently relocated begin/end symbols for registry and selected package descriptor data, plus source-controlled build/link verification; validate alignment, ordering and bounds before reading variable fields. Relocation alone cannot prove hostile pointers safe. |
| **B — Registry** | `BCRG` header of **28 bytes**; **8 bytes** per selected descriptor begin/end pair; **8 bytes** per application-required package ID; `28 + 8*N + 8*M` bytes. A no-extension application links a real 28-byte empty registry (`N=M=0`). Entries are dependency-first. |
| **C — Package descriptor** | `BCEX` header of **48 bytes**, **8 bytes** per exported (global,address) pair and **16 bytes** per dependency; `48 + 8*K + 16*D` bytes. Exact API major match; available API minor at least the required minor. One public dispatcher global per package by default; extra exports require documented exception. |
| **D — Dependencies and lifecycle** | Application and package requirements, transitive dependency checks before `START`, strict dependency-first registration, lazy initialization and no version-1 initializer hook. Finalizers once in reverse order before `BCPLIO.IOFIN` and `BCPLMEM.MEMDRAIN`. Failed validation publishes no optional globals. |
| **E — Global ownership** | Compose an effective application/BLIB/Core Runtime/optional-package owner ledger, including actual export trailers and the official Global Number Registry; reject unauthorized duplicate or conflicting optional exports before `START`. Preserve only *verified* historical precedence (notably conditional `G!76`); no new optional overwrites. Validate all selections transactionally. |
| **F — Finalizer ABI** | Conventional MVS linkage: R1 points to the public **8-byte** block (`+0` reason: 0 FINISH / 1 STOP; `+4` STOP code), R13 valid save area, R14 return, R15 entry address and returned status. Callee preserves R2–R12/R13. Nonzero returned status produces diagnostic; ordinary FINISH becomes RC=8, while STOP(n) retains n. Test-only extra trace and injected-error words are **not** public ABI. |
| **G — Defensive limits** | Explicit maxima for counts, tables and descriptors; safe arithmetic/bounds checks before variable reads; stable numeric diagnostic categories; negative tests for malformed data, overflow and invalid hooks. The three-package isolated fixture limit is **not** a production limit. **Exact maxima and numeric diagnostic values are still to be chosen, tested, and reviewed in R.0.** |
| **H — Core integration boundary** | One generic `BCPLMAIN` adaptation, fully validate before `START`, publish optional entries only after success, finalize before `IOFIN`/`MEMDRAIN`, retain existing BLIB/FINISH/STOP and stream behavior. No accepted runtime-object change in R.0. Actual core integration belongs to R.1, following the R.0 gate. |

## Fixed binary field positions adopted by B and C

`BCPLREG` fixed header:

| Byte offset | Length | Field |
| ---: | ---: | --- |
| 0 | 4 | EBCDIC `BCRG` |
| 4 | 4 | Layout version 1 |
| 8 | 4 | Header size 28 |
| 12 | 4 | Total table bytes |
| 16 | 4 | Selected descriptor count `N` |
| 20 | 4 | Application required-ID count `M` |
| 24 | 4 | Reserved zero |
| 28 | `8*N` | Begin/end fullword byte-address pairs |
| `28+8*N` | `8*M` | Required `CL8` package IDs |

`BCEX` package descriptor:

| Byte offset | Length | Field |
| ---: | ---: | --- |
| 0 | 4 | EBCDIC `BCEX` |
| 4 | 4 | Layout version 1 |
| 8 | 4 | Header size 48 |
| 12 | 4 | Total descriptor bytes |
| 16 | 8 | Package `CL8` identifier |
| 24 | 4 | API major |
| 28 | 4 | API minor |
| 32 | 4 | Export count `K` |
| 36 | 4 | Finalizer byte address, or zero |
| 40 | 4 | Dependency count `D` |
| 44 | 4 | Reserved zero |
| 48 | `8*K` | `(F'G_NUMBER', A(entry))` exports |
| `48+8*K` | `16*D` | `(CL8 required_ID, F'required_major', F'minimum_minor')` |

The older single-descriptor-pointer / 40-byte package-header
[proposal](runtime-extensions-r0-candidate-binary-abi-20261020.md)
is **superseded**; do not label both layouts version 1.

## What approval does not establish

- **Actual export ledger:** Decode current native CG370 application and
  installed BLIB object export-pair trailers and test documented legacy
  precedence. Source-declared BLIB names are only candidates, not evidence
  that those slots were installed. See the [ownership audit](runtime-extensions-r0-global-ownership-audit-20261021.md).
- **G's missing numeric values:** Choose and verify production maxima,
  size ceilings and stable diagnostic numbers. Explicitly cover empty
  lists, corrupt lengths/overflow and unexpected nonzero finalizer pointers.
- **Evidence and gate:** Preserve the [26 test-only outcomes](runtime-extensions-r0-batch-job-2195-evidence-20261021.md)
  without claiming they exercised a real `BCPLMAIN` registrar.
  Review bounded/trusted sources, compiler/BLIB overlap and R.0 acceptance
  evidence before closing R.0.
- **R.1 implementation:** Actual pre-`START` installation, optional
  collision rejection in `BCPLMAIN`, FINISH/STOP hook integration,
  save-area behavior and full runtime regression remain unimplemented
  integration/acceptance tasks. They are not retroactively proven by
  the simulated finalizer in JOB 2195.

**Current disposition:** Decisions **A–H approved**; **R.0 open**;
**R.1 not started**. No changes to compiler, assembler, runtime, JCL
or accepted PDS objects were authorized by this decision record.
