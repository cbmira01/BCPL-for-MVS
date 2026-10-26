# Milestone QSAM — Q.1 native QUERY-only evidence (JOBs 6602–6603)

**March:** Q.1 — Linkage & OPEN/CLOSE skeleton  
**MVS JES date:** 26 October 2026  
**Disposition:** Native QUERY-only registration/dispatcher/FINISH gate **PASS**; Q.1 **OPEN**.

## Operator-observed results

The operator updated GitHub `main` to `057b3999afe94b05c240676d7cc65d80e7ce43fe`.
After earlier missing-indentation generator correction, the source-invariant
check passed (181 labels, 123 branches, 16 slots, 32 DCBs). All **five**
`test_prepare_q1_query.py` tests passed. The synthetic
temporary IFOX/IEWL/GO deck passed its **2591-card** offline check.

`tools/bootstrap/compile-mvs` returned **JOB 6602** and successfully
saved the real CG370 System/370 assembler output to ignored
`workarea/bcplqsam-q1/query-generated.asm` (host compilation RC=0).
This is the **demoted Cambridge compiler under ICINT19** generating
native target code, *not* the separately reconstructed native compiler.

The operator then explicitly submitted the protected, temporary-only
`Q1QUERY` job and obtained **JOB 6603**. The supplied JES summary:

| Step | Program | Result |
| --- | --- | --- |
| ASMA | IFOX00 | RC=0000 |
| ASMN | IFOX00 | RC=0000 |
| ASMR | IFOX00 | RC=0000 |
| ASMQ | IFOX00 | RC=0000 |
| ASMG | IFOX00 | RC=0000 |
| LKED | IEWL | RC=0000 |
| GO | Native linked application | RC=0000 |

Other reported evidence:
- `JOB RESULT: SUCCESS`, `HIGHEST RC: 0000`.
- Assembler statements flagged **0**; highest severity **0**.
- `job-summary` command RC=0 and JES report extraction RC=0.
- Ordered logical output verification:
  `BCPLQSAM Q1 QUERY PASS` matched **once** after the link-edit
  authorization boundary; `check-combined-jes-records.py` returned
  success.
- **Explicit verifier limitation:** the combined report does *not*
  independently establish physical JES DD attribution.

## Proven scope and remaining gates

This integrated native BCPL result verifies that the selected temporary
`BCPLQSAM` BCEX descriptor and BCX/BCRG registration expose
`QSAMSVC:200`; the caller's QUERY capacity/sentinel checks,
unsupported READ/WRITE/unknown opcode responses, and FINISH with
**zero live QSAM handles** all completed on the observed GO path.
The native application was run under **GO REGION=256K**; this is not
a full 16-live-handle memory-budget result.

**Not established:** a successful returned QSAM OPEN or CLOSE, INFO of
a real opened DD, three live simultaneous handles, slot reuse/rollback,
returned-CLOSE quarantine, FINISH/STOP cleanup of *live* DCBs,
or the fully integrated 16-handle resource budget.

The follow-on Q.1 **three-DD** exercise should create three separate
temporary F1024 datasets, use the already reviewed native BCPL caller
`test-q1-3dd.bcpl`, and check OPEN/INFO/CLOSE/stale-handle behavior.
Use the existing Q.0 temporary writer precedent; don't OPEN uninitialized
new input datasets or change production catalog/BOOT_OBJ.
The owner-approved cleanup-error precedence and exceptional returned-CLOSE
fault-injection procedures remain separate explicit gates.
