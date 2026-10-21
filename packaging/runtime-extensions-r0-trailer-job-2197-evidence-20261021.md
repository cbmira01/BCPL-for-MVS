# Milestone Runtime Extensions — R.0 actual export trailers, JOB 2197

**March:** R.0 — Evidence and contract (**open**). **MVS/JES job
calendar date:** 21 October 2026. **Git source revision for the probe:**
`a7a16cfb9968e51da5b1a1946c5bed703948d779`.
**Evidence status:** actual MVS operator-reported execution; installed
object build provenance remains unverified. No R.1 work was performed.

## Reproduction and MVS results

The operator pulled the [tracked export-trailer
probe](../bootstrap-toolchain/probes/r0-export-trailer-probe/README.md)
and ran `bash bootstrap-toolchain/probes/r0-export-trailer-probe/run.sh`.
Its 12 host Python tests passed. JOB **2196** (`R0TRCMP`) compiled a
small native CG370 application using the installed interpreter-hosted
**demoted Cambridge compiler**, and saved
`workarea/runtime-extensions-r0-trailers/app.s370.asm`.
The generated assembler SHA-256 was
`805526d354cc672f21b1aa1fb217c7497a65e74e079fc016fdfb2edaa5fc51bd`.

JOB **2197** (`R0TRAIL`), 21 OCT 26 01:07:42–01:07:42,
assembled the separate observer and application, link-edited a temporary
module against installed `BOOT_OBJ`, and executed the **observer**, not
`R0APP`/`BLIB`/`BCPLMAIN`.

| Step | Program | Observed result |
| --- | --- | --- |
| ASMT | IFOX00 | RC=0000 |
| ASMA | IFOX00 | RC=0000 |
| LKED | IEWL | RC=0000 |
| GO | Temporary load module | RC=0000 |

Highest RC 0000, zero IFOX statements flagged, highest assembler
severity 0; 239 JCL cards, 681 SYSOUT records. The owner-provided IEWL
listing showed explicit `INCLUDE OBJ(BCPLMAIN,BCPLIO,BCPLMEM,BCPLBYTE,
BCPLAPT,BLIB)` (individual `INCLUDE` cards), `ENTRY R0TRACE`, and
`NAME R0TRAIL(R)`. Its map placed the following separate CSECTs:

| CSECT | Relative address | Length |
| --- | ---: | ---: |
| `R0TRACE` | `000000` | `000534` |
| `R0APP` | `000538` | `000050` |
| `BLIB` | `003488` | `001BB0` |

`R0APP` and `BLIB` were resolved external references for the observer.
The actual GO/QOUT region contains the installed BLIB's 21 exported
records followed by `R0TR PASS APP AND INSTALLED BLIB`. The report
parser required the sentinel, count, offset alignment and GO marker;
no PASS was inferred from IFOX source constants.

## Exact exported globals from relocated loaded modules

| Origin | G! numbers | Count |
| --- | --- | ---: |
| Application `R0APP` | **1** (START) | 1 |
| Installed `BOOT_OBJ(BLIB)` | **3, 4, 5, 56, 58, 59, 60, 62, 63, 64, 65, 66, 67, 68, 69, 70, 74, 75, 76, 77, 78** | 21 |

There are **no application/BLIB overlaps** and no overlaps between the
application's exports and source-derived direct native stores. The only
intersection of the observed BLIB exports with the *source-derived*
Core Runtime direct-write inventory is **G!76**. The observer measured
BLIB's relocated G!76 entry as `000A95FC` in this one run. This address
is not a stable API or reproducible absolute address across link-edits.

The 21 actual BLIB exported slots match the 21 names in the earlier
[source inventory](runtime-extensions-r0-global-ownership-audit-20261021.md).
The observation independently confirms the installed linked object's
*slot set*, but it does not establish that the object was rebuilt from a
particular source revision.

## Evidence limits and next gate

- The observer deliberately does **not run `BCPLMAIN`**, so a BLIB G!76
  export is **not itself a test** that the Core Runtime preserves WRITEF.
  The next [separate G!76 precedence probe](../bootstrap-toolchain/probes/r0-g76-precedence-probe/README.md)
  tests that condition using the actual installed runtime at START.
- A one-export application does not establish noncollision for every
  application or compiler program; dynamic ownership is per executable.
- The full runtime effective ownership ledger still needs any indirect
  binder behavior reviewed and historical precedence validated.
- The installed `BOOT_OBJ(BLIB)` member's *build provenance* is not
  proved by JOB 2197 or by the host-generated CG370 assembler digest.
- No optional-package transactionality, pre-START collision checking,
  descriptor hardening or finalizer integration has been implemented.
- Decision G's numeric limits and diagnostic codes and the final R.0
  acceptance review remain open. R.1 — Generic registration foundation
  has not started.

Operator-retained host files (ignored, not committed):
`workarea/runtime-extensions-r0-trailers/job-2197.txt`,
`ledger-job-2197.json`, `ledger-job-2197.tsv`, and
`source-provenance.txt`.
