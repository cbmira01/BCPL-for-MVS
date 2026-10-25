# Milestone QSAM — Q.1 IFOX assembly evidence (JOB 6600)

**March:** Q.1 — Linkage & OPEN/CLOSE skeleton  
**Evidence date:** 25 October 2026, MVS JES date/time 23:30:48  
**Disposition:** IFOX-only assembly gate **PASS**; Q.1 **OPEN**.

## Operator-provided MVS evidence

From `python3 tools/mvs/job-summary 6600 --max-rc 0`:

| Field | Observed |
| --- | --- |
| JOB | `6600 Q1QSASM` |
| Job description | `Q1 IFOX` |
| Step | `ASMQ` |
| Program | `IFOX00` |
| Completion code | `RC=0000` |
| JES job result | `SUCCESS` |
| Highest step return code | `0000` |
| IFOX statements flagged | `0` |
| IFOX highest severity | `0` |
| Cards read | `797` |
| Assembler step REGION | `256K` |

The operator also supplied report excerpts showing `IEF142I` with
`COND CODE 0000`, `NO STATEMENTS FLAGGED IN THIS ASSEMBLY` and
`HIGHEST SEVERITY WAS 0`. The report was extracted locally into
`workarea/bcplqsam-q1/q1asm-report.txt`; that file and its full
listing were **not** submitted to GitHub in this evidence record.

**Proven:** The Q.1 assembler source in the `Q1QSASM` job passed
IFOX assembly, according to the supplied JES report and summary. The
original generator assembled BCPLQSAM with a test-only
`&&Q1QSOBJ` output, and did not install a permanent object.

**Not proven:** An IEWL MAP/XREF relocation result, BCEX/BCRG
registration, native BCPL use of `QSAMSVC:200`, QSAM OPEN/CLOSE
behavior, returned-CLOSE error handling, successful 16-handle
native GO at REGION=256K, or finalization on FINISH/STOP.

## Next bounded gate

Run the repository's `prepare-q1-link.py` job `Q1QSLNK`.
It assembles the same Q.1 source and feeds its **temporary** object
to IEWL. The linker writes only a temporary load module and does
**not execute** its descriptor entry. Require **ASMQ RC=0000**
and **LKED RC=0000**, then inspect the MAP/XREF for the Q.1
descriptor and assembler CSECTs. This is a *relocation/linkage*
gate, not the integrated native BCPL acceptance gate.

Maintain the approved temporary BCXCAT overlay and unchanged installed
runtime, extensions, BOOT_OBJ, BOOT_DEVOBJ and production catalog.
Returned-CLOSE fault tests and cleanup-error precedence remain
separate owner review questions.
