# 137 — M4.1 stable-handle GETMAIN 16 deterministic failure

**Status: ACCEPTED — targeted MVS regression 137 PASS (2026-10-17).**

Operator fast-forwarded `main` from `831ee82` to `ccb0f1b`
and executed `tools/native/run-regression 137 --show-output`
with `BCPL_RUNTIME_PDS=1`, `BCPL_RUNTIME_LIBRARY=DEVOBJ`,
`BCPL_RUNTIME_CANDIDATE=1`,
`BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6`. Console outcome:
**PASS 137; PASS 1 / FAIL 0 / SKIP 0 / TOTAL 1**.
The single-case runner passed with the inline-assembled,
test-only BCPLIO linked to the unchanged development runtime;
the supplied excerpt does not include JES job IDs or separately
enumerate assembler/link/GO condition codes.

Accepted scope: a synthetic HNEW second-visit 16-byte GETMAIN
failure **after QSAM OPEN**, followed by zero-valued FINDINPUT,
preservation of a live input handle/cursor, a successful DD02
retry, and ordinary read/close behavior. Source-level control
flow requires `DQCLOSE` then `DREL` on this branch; this
regression is **not** an independent count of CLOSE/FREEMAIN,
a real MVS storage-exhaustion test, or an OPEN-error test.
Production and installed development object PDS members
remain unchanged.

Candidate-only compiled BCPL against an **INLINE-assembled test-only
BCPLIO**, generated from canonical `native-compiler/asm/bcplio.asm`.
The unique marker `io-fault-mode.txt` enables the special job
builder. It does not alter installed `DEVOBJ(BCPLIO)`, production
`OBJ`, BCPLMAIN or any canonical runtime assembler source.

The private assembler generator patches the HNEW 16-byte GETMAIN
request with a one-process-site counter. The **first call**
performs real GETMAIN (DD01 opens and remains selected).
The **second call** skips the macro and synthesizes
a nonzero R15 (DD02 FIND must return zero).
The **third call** invokes real GETMAIN again; DD02 FIND
must succeed. This is deterministic fault-path injection,
**not evidence of actual MVS storage exhaustion**.

This tests the cleanup path after successful QSAM OPEN but failed
stable-handle creation: DIFIND should DQCLOSE and DREL its partially
created stream, preserve DD01's selected handle/cursor, and
permit fresh DD02 opening. All tests assert zero on failure
and recovery with live input records. Primary success marker:
`BCPL FAULT 16 OK`.

Exact SVC19/SVC20 and FREEMAIN accounting remains M4.3,
and true QSAM OPEN failure remains M4.2.

```sh
cd ~/Source/Repos/BCPL-for-MVS
git pull --ff-only
BCPL_RUNTIME_PDS=1 \
BCPL_RUNTIME_LIBRARY=DEVOBJ \
BCPL_RUNTIME_CANDIDATE=1 \
BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6 \
tools/native/run-regression 137 --show-output
```

Expect ASMAP/ASMFIO/LKED/GO RC0000 and PASS 137. If assembly
or link fails, inspect the test-only instrumentation first.
