# 137 — M4.1 stable-handle GETMAIN 16 deterministic failure

**Status: STAGED (MVS execution and acceptance pending).**

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
