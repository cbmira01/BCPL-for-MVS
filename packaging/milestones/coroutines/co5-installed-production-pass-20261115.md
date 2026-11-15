# CO.5 — Installed production coroutine verification PASS

**Project:** BCPL for MVS 3.8 Reconstruction
**Milestone:** Implement coroutine support for native compiler
**March:** CO.5 — Integration, Regression, and Release
**Tested GitHub revision:** `4bdf3509d99a82ee9784f5978bef0c6f2802829a`
**Operator date:** 15 November 2026 (MVS JES dates show 16 November)
**Status:** PRODUCTION INSTALLATION AND INSTALLED-LINK PASS;
CO.5 IN PROGRESS
**Evidence class:** OWNER-REPORTED MVS-TESTED, 252-line terminal transcript.
Full underlying operator-local JES spool and workarea receipts were
not independently reviewed.

## Source preflight and staged production inputs

A fast-forward to the tested source revision completed successfully.
Five host unit tests passed (5/5); production BCPL/header check and
installed-verifier preflight passed. Native manifest validation
reported 190 cases (00–189), 13 in the coroutines suite, and seven
project suites. These were host-only checks, not regression runs.

Resident Cambridge compiler JOB **5972** generated System/370 source
for `bootstrap-toolchain/library/coroutines.bcpl`; the production
preparation generated a **477-card independent IFOX library**.
The operator staged production source/header, the prepared IFOX
module and two JCL jobs into managed MVS datasets using seven
successful `dspal put` operations, JOBS **5973–5979**.
Production staging returned **RC=0**.

## MVS production installation and readback

| Payload job | Member or build | Zero-return evidence |
| ---: | --- | --- |
| **5981** | `BLDBMAIN` | Seven IFOX and seven object installs, all RC=0000; assembler severity 0 |
| **5983** | `BLDCORCO`: `BOOT_OBJ(BCPLCO)` | IFOX ASMCOR, PUT, readback and IEBCOMPR all RC=0000; severity 0 |
| **5985** | `BLDCORLB`: `BOOT_OBJ(COROUTIN)` | IFOX ASMCOLIB, PUT, readback and IEBCOMPR all RC=0000; severity 0 |

The final `HERC02.BCPL.BOOT.OBJ` listing shows **10 members**:
`BCPLAPT`, `BCPLBYTE`, `BCPLCO`, `BCPLIO`, `BCPLMAIN`,
`BCPLMEM`, `BCPLREG`, `BCPLRGS`, `BLIB`, `COROUTIN`.

## Installed-only application linkage and GO

`tools/coroutines/verify-installed-production.py --run` compiled
the accepted CO.3 deletion/reuse application in Cambridge
**JOB 5987**, then assembled and linked it against the **installed**
`BOOT_OBJ(BCPLMAIN)`, `BOOT_OBJ(BCPLCO)` and
`BOOT_OBJ(COROUTIN)` (plus the installed base objects).
Native **JOB 5988** reported IFOX/IEWL/GO all **RC=0000**,
accepted 21-record ordered `CO3BCPL` oracle, runner PASS.
Final **production installation/verification RC=0**.

**Operator-local evidence directory:**
`workarea/co5-installed-coroutines/20261115T233242Z-j41f2f9z`

## Explicit CO.5 qualifications

This verifies production installation and native use of the
two new relocatable object members, **not** the full post-promotion
regression suite. Run the relevant MR10/native suites again; the
13 source-selected coroutine cases 177–189 require fresh evidence.
Preserve the known MR10 legacy fixed-stack failure, expected
SKIP 083 and separately authorized BCPLQSAM device cases 175–176
without recategorization.

By explicit owner direction, `config/dspal.yaml` remains unchanged.
The promoted object members and staging sources therefore **would
not survive an unattended destructive clean-room reconstruction**.
The original clean-room PASS predates this installation and does not
prove reproducibility of the two new object members. The bounded
CO.4 contract and private descriptor caveats remain in force.
Formal CO.5 owner acceptance and release publication remain pending.

**Disposition:** Production-installed MVS PASS; CO.5 IN PROGRESS.
