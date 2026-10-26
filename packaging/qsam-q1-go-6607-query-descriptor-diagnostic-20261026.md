# Milestone QSAM — Q.1 three-DD diagnostic JOBs 6606–6607

**March:** Q.1 — Linkage & OPEN/CLOSE skeleton  
**Observed JES date:** 26 October 2026, 02:11:04–02:11:05  
**Disposition:** Diagnostic result, **native GO RC=0012**; Q.1 **OPEN**.

## Operator-supplied evidence

The operator updated GitHub `main` to
`acbef42b63566092e662f60c1eb7092bea8a6b47`. Before JES submission:
Q.1 source invariants passed; six `test_prepare_q1_3dd.py` tests and
three `test_q1_3dd_diag.py` tests passed; the temporary three-DD
2800-card JCL synthetic check passed. The demoted Cambridge compiler
running under ICINT19 returned **JOB 6606** with host compilation
RC=0 and wrote generated System/370 source only under ignored workarea.

The diagnostic `Q13DD` run was submitted as **JOB 6607**. All
nine prerequisite steps returned `RC=0000`:
`ASMWR`, `LKWR`, `ASMA`, `ASMN`, `ASMR`,
`ASMQ`, `ASMG`, `LKED`, and `WGO`.
The native `GO` step returned **RC=0012**.
Assembler statements flagged **0**, highest severity **0**,
JES result **FAILURE**. Host `job-summary --max-rc 0` returned
RC=1; JES report extraction returned RC=0.
The expected `BCPLQSAM Q1 THREE DD PASS` record was not found
in the GO suffix (record-check RC=1).

Following the last IEWL authorization boundary, the operator
observed exactly this leading BCPL diagnostic sequence:

```text
Q13D START
Q13D CALL 01 RC=6
Q13D CALL 02 RC=-1
Q13D ASSERT 01 BEFORE
Q13D CALL 03 RC=-3
Q13D CALL 04 RC=6
Q13D ASSERT 02 BEFORE
```

There was **no** `Q13D ASSERT 03 BEFORE`, unsupported-opcode,
or QSAM `OPEN` diagnostic. The original BCPL caller's next
executable conditional after `ASSERT 02 BEFORE` is:
`IF I!0 NE 1 | I!1 NE 1 | I!2 NE 0 DO STOP(8)`.
This isolates the failing interval to the descriptor-word check
(or an execution problem at that point), **before the first QSAM
OPEN**. The two vectors have different allocations in two
tested fixtures: native QUERY-only JOB 6603 used `I = VEC 6`
and passed; three-DD used `I = VEC 5`, which is still sized for
six words (`I!0..I!5`). That difference is **hypothesis material**,
not proof of out-of-bounds access or service corruption.

`QSAMSVC(0,I,6)` returning **6** does not prove the six copied
descriptor fields. Their actual values remain unknown.
Likewise, **GO RC=0012** is not established as the intended
BCPL `STOP(8)` result; do not infer a finalizer failure without
an executed finalizer diagnostic.

## Next minimal diagnostic

Leave production-candidate `bcplqsam.asm`, the original
`test-q1-3dd.bcpl`, Q.0 data writer, QSAM DCB ownership and
GO `REGION=256K` unchanged. Modify only
`test-q1-3dd-diag.bcpl` to emit `I!0` through `I!5`
immediately before the failed descriptor check, and a
`Q13D ASSERT 02 AFTER` marker on success. Preserve the existing
14 service calls, expected outcomes and 19 `STOP(8)` assertions.

Compile with the existing demoted Cambridge toolchain and reuse the
temporary three-DD JCL generator; the newly submitted diagnostic
JOB is tracked independently of JOBs 6605 and 6607. First establish
the exact descriptor mismatch (or lack thereof) before proposing
changes to the QSAM dispatcher, compiler, or ABI.

This is **diagnostic investigation**, not Q.1 gate acceptance.
