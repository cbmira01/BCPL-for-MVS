# 136 — M4.1 buffer/DCB GETMAIN 268 deterministic failure

**Status: ACCEPTED — targeted MVS regression 136 PASS against the
isolated test-only BCPLIO on DEVOBJ (2026-10-17 project record).**

The operator pulled `main` from `175fc2e` through `831ee82` and
ran `tools/native/run-regression 136 --show-output` with
`BCPL_RUNTIME_PDS=1 BCPL_RUNTIME_LIBRARY=DEVOBJ
BCPL_RUNTIME_CANDIDATE=1 BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6`.
The result was `PASS 136`, with **PASS 1 / FAIL 0 / SKIP 0 /
TOTAL 1**. No individual JES job number or step return-code report
was supplied; the successful regression runner result is the
observable acceptance evidence.

This proves synthetic failure-path behavior and recovery after the
268-byte QSAM region allocation is denied on its second invocation:
the FIND returns zero, live DD01 remains selected with its input
cursor preserved, a subsequent DD02 FIND succeeds, and both streams
remain readable and closable. Source inspection identifies the
`DALNOMEM` 32-byte FREEMAIN branch, but this result does **not**
independently count successful FREEMAIN operations or demonstrate
genuine MVS low-storage exhaustion. Production `OBJ` and installed
`DEVOBJ` objects were not changed.

Candidate-only compiled BCPL against an **INLINE-assembled test-only
BCPLIO**, generated from canonical `native-compiler/asm/bcplio.asm`.
The unique marker `io-fault-mode.txt` enables the special job
builder. It does not alter installed `DEVOBJ(BCPLIO)`, production
`OBJ`, BCPLMAIN or any canonical runtime assembler source.

The private assembler generator patches the buffer/DCB GETMAIN 268
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
and closable. Output marker: `BCPL FAULT 268 OK`; assertion failures
terminate via STOP(8).

For mode `buffer268`, the injected branch is at `FI268`.
The failing 268-byte request must release the already acquired 32-byte descriptor through DALNOMEM.
Exact SVC19/SVC20 and FREEMAIN accounting still belongs to
M4.3, and ordinary QSAM OPEN errors to M4.2.

```sh
cd ~/Source/Repos/BCPL-for-MVS
git pull --ff-only
BCPL_RUNTIME_PDS=1 \
BCPL_RUNTIME_LIBRARY=DEVOBJ \
BCPL_RUNTIME_CANDIDATE=1 \
BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6 \
tools/native/run-regression 136 --show-output
```

Expected: compiler and ASMAP/ASMFIO/LKED/GO succeed, output
`BCPL FAULT 268 OK`, and PASS 136. If this fails at assembler or link,
preserve the JES job report and investigate **the test-only
instrumentation**, not canonical BCPLIO, before modifying source.
