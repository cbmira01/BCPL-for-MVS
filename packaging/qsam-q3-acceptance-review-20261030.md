# Milestone QSAM — Q.3 acceptance review (30 October 2026)

**Project:** BCPL for MVS 3.8 Reconstruction
**March:** **Q.3 — Variable logical records**
**Disposition:** **IN PROGRESS — numbered and full native regression gate PENDING.**
**Source baseline entering integration:** GitHub `main` at
`aa53ffb16f16c5c4bb906cb55061f9201fa60be2`, followed by
the owner-approved Q.3 regression/QUERY integration commit.

## Native System/370 / MVS 3.8J evidence already observed

The owner supplied actual JES/IFOX/IEWL/QSAM output for these temporary
source-mode jobs. The jobs do not imply production object installation.

| JOB | Operation | Native results and observations |
| --- | --- | --- |
| 7340 | RECFM=V READ, LRECL=100 | Six logical records, RDW stripping, repeated capacity retry, valid zero-length record, EOF; native PASS |
| 7344 | RECFM=V WRITE, LRECL=100 | Six records, independent IFOX RDW and binary verification; ten steps RC=0000. Corrected System/370 R0 addressing defect in `LA 0,4(0)` |
| 7347 Q3VLRED | V READ, LRECL=1024/BLKSIZE=1028 | Seven records including two successive 1020-byte payloads; IFOX writer, BCPL reader; 10 steps RC=0000; marker PASS |
| 7348 Q3VLWRT | V WRITE, LRECL=1024/BLKSIZE=1028 | BCPL writer plus independent IFOX RDW/binary verifier; 10 steps RC=0000; both markers PASS |
| 7349 Q3VBRED | VB READ, LRECL=1024/BLKSIZE=2052 | QSAM deblocking, BCPL RDW isolation, full payload/EOF/retry; 10 steps RC=0000; marker PASS |
| 7350 Q3VBWRT | VB WRITE, LRECL=1024/BLKSIZE=2052 | QSAM blocking, independent IFOX RDW/binary readback; 10 steps RC=0000; both markers PASS |

For 7347–7350 the reported assembler severity and flagged statements
were both zero; each job's highest RC was 0000. Existing generated
JCL, compiler output, summaries, reports and attempt markers remain in
the operator's local `workarea/bcplqsam-q3/`, not in tracked Git
artifacts. The MVS results prove the tested behavior, not an
unlimited record-size capability.

## Accepted public interface and tested implementation

- One optional `BCPLQSAM` System Extension at `QSAMSVC:200` with
  existing 4-word request and 8-word result vectors and opcodes 0–5.
- F/FB (Q.2) and V/VB (Q.3) share the same dispatcher ABI.
- For V/VB the 1024-byte private per-handle stage includes a four-byte
  RDW; 1020 is the maximum application payload. Zero payload is not
  EOF. No RDW or physical BDW is exposed to BCPL.
- READ preserves the pending record after `QS_ERR_CAPACITY=-1`,
  gives exact required data length, does not overwrite the caller's
  buffer, and supports repeated EOF. WRITE validates the data length
  before constructing its internal RDW.
- MVS QSAM retains ownership of physical blocking/deblocking.
- QUERY reports opcode bitmap 31; `info!5` is updated to 3:
  `QS_CAP_FIXED | QS_CAP_VARIABLE`. No carriage-control support is
  claimed during Q.3.

## Permanent native regression integration — awaiting execution

The owner approved four new regression identities:

| Case | Purpose | Earlier standalone evidence |
| --- | --- | --- |
| 171 | RECFM=V READ, 1024-stage boundary | JOB 7347 |
| 172 | RECFM=V WRITE and independent IFOX readback | JOB 7348 |
| 173 | RECFM=VB READ, 1024-stage boundary | JOB 7349 |
| 174 | RECFM=VB WRITE and independent IFOX readback | JOB 7350 |

Existing case 163 QUERY and case 170 BCPLQSAM/BCPLDEMO both
previously expected fixed capability 1. Their new fixtures require
capability 3. Historical `test-q2-query.bcpl` and
`test-q2-mix.bcpl` and the Q.2 closure evidence remain unchanged.

Run source-mode native regressions through the existing
`tools/bootstrap/run-production-regression` entry point:

1. Focused 163–174: 12 native cases; require **12 PASS, 0 FAIL,
   0 SKIP**, runner RC=0.
2. Full 00–174: 175 total cases; with the historically expected
   SKIP 083, target **174 PASS, 0 FAIL, 1 SKIP**, runner RC=0.
   Counts are expectations, **not** recorded execution results.

The focused run must pass before the full one. Actual per-case
compiler/JES IDs, summaries, reports, final counts and any unresolved
failures must be recorded before changing the disposition to CLOSED.
JES submissions are operator-controlled; no installed MVS PDS may be
modified or BCPLQSAM promoted under this work.

## Retained deferrals and next march

Q.1 returned-CLOSE fault injection and STOP cleanup details, broader
OPEN failure/geometry handling, full resource accounting, production
object promotion, clean-room rebuild and comprehensive regression
hardening remain recorded for Q.5 — Hardening & release as applicable.
Q.4 — SYSOUT devices is **NOT STARTED**. Its printer/punch and
carriage-control work is not implied by successful Q.3 V/VB tests.

**Owner authorization:** The project owner requested permanent Q.3
native regressions, regression-163 capability correction, and closure
of Q.3. Closure is contingent on the focused and full native panel
passing; this document does not claim either panel has run.
