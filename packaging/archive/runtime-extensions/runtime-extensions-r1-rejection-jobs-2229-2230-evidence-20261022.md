# Milestone Runtime Extensions — R.1 rejection evidence: JOBs 2229/2230

**MVS execution date:** 22 October 2026.
**Disposition:** Diagnostic 1001 fired as specified; integrated negative
test **FAILED** because GO ended S322 rather than RC=0012.
The R.1 exit gate remains open. No accepted BOOT_OBJ promotion.

| Observation | JOB 2229 R1N1001 | JOB 2230 R1N1001 |
| --- | --- | --- |
| ASMA, ASMN, ASMR, ASMG, ASMD, ASMS | Each RC=0000 | Each RC=0000 |
| IEWL | RC=0000 | RC=0000 |
| WTO | BCPLREG 1001 INVALID REGISTRY EXTENT | Same |
| GO TIME limit | TIME=(,2) | TIME=(,30) |
| GO termination | S322 | S322 |
| GO CPU | 11.76 seconds | 32.95 seconds |
| Saved application PSW | 078D2000 000A71F6 | 078D2000 000A71F6 |

The recorded PSW maps to the instruction following the primary
QSAM CLOSE in BCPLIO.IOFIN. This is **consistent with** a CLOSE
operation not completing; it is not proof of the root cause.
The first error is emitted before START, and the dumped G!298 and
G!299 sentinels remained X'C7D3F4A8' and X'C7D3F4AC'.
No application output was expected on this rejection path.

The longer CPU limit did not fix the problem; increasing it further
is not a useful diagnostic. Do not count 1001 as passed, and do not
advance to 1002 until rejection termination has been corrected.

## Isolating the failure

Test an ordinary application that does enter START but calls FINISH
without WRITES, NEWLINE, or other output. Its empty BCPLREG uses the
same candidate startup and the same BCPLIO.IOINIT/IOFIN path.

- R1NOOUT GO RC=0000: ordinary no-output FINISH works; investigate
  the registration-rejection entry/cleanup path separately.
- R1NOOUT GO S322 at the same PSW: the problem is reproducible without
  rejection; focus on BCPLIO's empty-output CLOSE path.
- Any other result: diagnose using that job's complete JES/SYSUDUMP.

Only **after this comparison** assess an R.1 candidate that validates
registration before opening SYSPRINT. Preserve the approved rule that
finalizers run before IOFIN and MEMDRAIN. All changes remain candidate
objects until reviewed and accepted.
