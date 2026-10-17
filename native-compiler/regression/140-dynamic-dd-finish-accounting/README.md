# 140 — M4.3.2a terminal resource accounting

## Formal acceptance evidence — 2026-10-17

**M4.3 CLOSED, regression 140 PASS.**
Compiler JOB 7881; GO JOB 7882 (RG140R).
ASMAP IFOX00 RC0000; ASMFIO IFOX00 RC0000;
LKED IEWL RC0000; GO RC0000.
Job-level RESULT=SUCCESS; the regression runner reports PASS.
Only test-private BCPLIO was linked; no installed runtime was changed.
See `docs/Milestone-BCPLIO-dynamic-stream-M4.3-plan.md`.

Originally staged; now ACCEPTED after the 2026-10-17 operator run. Test-only BCPLIO asserts zero DHEAD/HHEAD and balanced 32/268/16-byte GETMAIN/FREEMAIN and dynamic QSAM OPEN/CLOSE counters after IODRAIN. On mismatch it intentionally executes an invalid opcode (S0C1), so normal completion is required for PASS. Reuses the proven logical program and expected output fixtures of regression 128. No runtime object installation or new BCPL global.

## First attempted run — source checker correction

The initial 2026-10-17 invocation did not reach this regression: a host-side assertion incorrectly expected eight BNE checks. The generated terminal instrumentation deliberately has two BNZ list checks and six BNE counter checks. The source checker was corrected; **this test has not yet run under MVS**.

## Accepted rerun (2026-10-17)

Operator-reported regression 140 PASS, part of 140..141: 2 PASS / 0 FAIL / 0 SKIP; source audit PASS. The private DRAINDN terminal assertions passed. The supplied summary did not expose new JES IDs or step condition codes. Counted synthetic failures remain untested.
