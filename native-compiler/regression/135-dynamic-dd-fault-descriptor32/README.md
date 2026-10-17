# 135 — M4.1 descriptor GETMAIN 32 deterministic failure

**Status: STAGED (MVS execution and acceptance pending).**

Candidate-only compiled BCPL against an **INLINE-assembled test-only
BCPLIO**, generated from canonical `native-compiler/asm/bcplio.asm`.
The unique marker `io-fault-mode.txt` enables the special job
builder. It does not alter installed `DEVOBJ(BCPLIO)`, production
`OBJ`, BCPLMAIN or any canonical runtime assembler source.

The private assembler generator patches the descriptor GETMAIN 32
request with a one-process-site counter. The **first call**
performs the real GETMAIN (DD01 opens and remains selected).
The **second call** skips the GETMAIN macro and synthesizes
a nonzero R15 (the DD02 FIND must return zero). The
**third call** invokes real GETMAIN again, and DD02 FIND
must now succeed. This is deterministic fault-path injection,
**not evidence of actual MVS storage exhaustion or allocator RC**.

The program verifies that failed FIND leaves DD01 selected and
its FB80 input cursor unchanged, that a subsequent FINDINPUT
for DD02 succeeds, and that both QSAM streams remain usable
and closable. Output marker: `BCPL FAULT 32 OK`; assertion failures
terminate via STOP(8).

For mode `descriptor32`, the injected branch is at `FI32`.
The 32-byte descriptor was never allocated on the failure path.
Exact SVC19/SVC20 and FREEMAIN accounting still belongs to
M4.3, and ordinary QSAM OPEN errors to M4.2.

```sh
cd ~/Source/Repos/BCPL-for-MVS
git pull --ff-only
BCPL_RUNTIME_PDS=1 \
BCPL_RUNTIME_LIBRARY=DEVOBJ \
BCPL_RUNTIME_CANDIDATE=1 \
BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6 \
tools/native/run-regression 135 --show-output
```

Expected: compiler and ASMAP/ASMFIO/LKED/GO succeed, output
`BCPL FAULT 32 OK`, and PASS 135. If this fails at assembler or link,
preserve the JES job report and investigate **the test-only
instrumentation**, not canonical BCPLIO, before modifying source.
