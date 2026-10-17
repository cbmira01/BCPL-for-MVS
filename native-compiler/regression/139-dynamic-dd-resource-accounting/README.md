# 139 — dynamic DD resource accounting (isolated test-only BCPLIO)

**M4.3.1 ACCEPTED 2026-10-17: corrected regression 139 PASS.** Requires BCPL_RUNTIME_PDS=1, BCPL_RUNTIME_LIBRARY=DEVOBJ, BCPL_RUNTIME_CANDIDATE=1 and BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6.

Compiles a normal BCPL application. G151 points only in this test to separately assembled NATIVEAD, which calls private test-only BCPLIO entry IOACCT. Checks exact dynamic GETMAIN/FREEMAIN and SVC19/SVC20 counts, duplicate FIND, ENDREAD, stale handle, and fresh DD02 identity after reopen. The installed candidate runtime modules are not changed.

Expected marker: M43 PRE-DRAIN COUNTS OK.

This test does not prove post-IOFIN 16-byte tombstone reclamation, real MVS free semantics, or system abend recovery. Consult docs/Milestone-BCPLIO-dynamic-stream-M4.3-plan.md for further gates.

## First MVS evidence — 2026-10-17

- Host source checker: PASS.
- Cambridge compilation: JOB 7877 produced generated CODE.
- JOB 7878 (RG139R): ASMAP IFOX00 RC=0000; ASMFIO IFOX00 RC=0000; ASMNAT IFOX00 RC=0008. IEWL LKED and GO bypassed by their condition checks.
- ASMNAT diagnostic: IFO209, statement 9, `L 15,=V(IOACCT)`; no base register was established for the V-type literal.
- Corrective action: `native.asm` uses `BALR 10,0` / `USING *,10` before the V literal and `DROP 10` after the return path. The later rerun passed.
- Canonical BCPLIO and production or development installed PDS members were not changed.


## Accepted rerun — 2026-10-17

The operator reports the corrected helper source audit **PASS**
and focused native **139 PASS (1 pass, 0 fails, 0 skips)**.
The current supplied output does not enumerate the rerun's MVS
job IDs or individual step codes. Accepted scope is the compiled
BCPL pre-drain assertions only; IOFIN/IODRAIN after-termination
accounting and fault paths remain open.
