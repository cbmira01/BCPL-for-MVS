# Milestone QSAM — Q.1 consolidated JOB 6623–6631 corrective review

**March:** Q.1 — Linkage & OPEN/CLOSE skeleton. **Status:** OPEN, NOT ACCEPTED.
**Authority:** Native execution results supplied by the operator, with GitHub `main`
commit `9ec8e1b0d8fcea3697307d87a2cdc2a5686d9517` as the source baseline.
All proposed corrections are test-only; there is no production `bcplqsam.asm`
change, JES resubmission, installed-dataset mutation, or approval of Q.1 closure.

## Native observations from the single approved nine-job batch

| JOB | Identity | Evidence and disposition |
| --- | --- | --- |
| 6623–6626 | Four BCPL compilers | `COMP`/`SVCODE` RC=0000 in each. |
| 6627 | `Q16FIN` | All native steps RC=0000, application 16-handle PASS marker. Finalizer completion not proved: WTO absent from printer runtime section. |
| 6628 | `Q16STP` | GO RC=0008 as requested by `STOP(8)`; application 16-handle PASS marker. Finalizer completion not proved. |
| 6629 | `Q1NEG` | GO RC=0008 unexpectedly, no negative-case PASS marker. Failed assertion not identified by original caller. |
| 6630 | `Q1OUT` | Native steps RC=0000 and output OPEN/INFO/CLOSE PASS marker. |
| 6631 | `Q13DD` | `GO` abended **S322** (time limit); `Q00` `RDJFCB` and first `OBTAIN` returned R15=0 with raw DSCB data. No `Q01`/`Q02` result. |

Assembler/link steps completed RC=0000 with severity 0 in the native cases
that reached them. An assembled WTO string, or its printable representation
in a memory dump, is **not** execution-time finalizer evidence.

The raw Q00 DSCB from JOB 6631 is consistent with sequential F1024
(`DSORG=X'40'`, `RECFM=X'80'`, `BLKSIZE=1024`, `LRECL=1024`),
but those field-offset interpretations require independent validation
before production geometry recovery. S322 prevents successful test acceptance.

## Test-only corrections prepared for review

1. `prepare-q1-obtain.py`: after `BAL 14,QOBREAD`, execute
   `B QIDBACK` so the caller does not fall through into `QOBREAD` after
   its return. Add a structural regression test.
2. `test-q1-negative.bcpl`: preserve the seven original `QSAMSVC`
   requests/expected codes and emit a unique assertion number plus
   actual status on failure, before `STOP(8)`.
3. `check-q1-finalizer-console.py`: optionally inspect TK5/Hercules
   console evidence. A valid observation requires one `IEF403I` to
   `IEF404I` job-name interval and one genuine WTO within it, with no
   `BCPLREG 2001` or abnormal-termination record. Listing-only or
   ambiguous records fail closed. The integrated campaign checker accepts
   an explicitly supplied console log, but does not infer WTO from a
   successful application message or GO return code.

The compose bind mount for console/hardcopy files is `mvs-state/log/`.
A log with no identifiable bounded job interval is **NOT VERIFIED**,
not proof that the finalizer failed. The console-checker PASS is a
scoped observation, not acceptance of resource cleanup or Q.1 itself.

## Approval and gate boundaries

- Offline tests exercise emitted assembler-card structure, negative
  caller invariants, and synthetic evidence; they do not compile the
  corrected BCPL caller, assemble the corrected OBTAIN diagnostic, or
  execute MVS code.
- Preserve all evidence and the `.q1-consolidated-nine-submit-once`
  attempt directory. Do not delete its marker or resubmit original jobs.
- A separately approved GitHub commit is required to make corrections
  authoritative on `main`.
- Any corrected native compiler/JES attempts require separate explicit
  authorization with new immutable decks and a one-attempt marker.
- Returned-CLOSE fault injection and cleanup-error precedence remain
  under their separate owner design gate.
