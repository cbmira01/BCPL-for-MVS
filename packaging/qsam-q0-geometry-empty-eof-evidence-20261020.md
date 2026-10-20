# Milestone QSAM — Q.0 JFCB geometry and empty-EOF evidence (2026-10-20)

**March:** Q.0 — Reconnaissance & contract (**remains open**).
**Scope:** standalone IFOX/QSAM reconnaissance under MVS 3.8J / Hercules TK5.
**Status:** both jobs passed under MVS; no BCPLQSAM, Runtime Extensions,
native compiler, or accepted runtime changes.

**Primary evidence:** owner-supplied complete JES and IFOX/link-editor
reports for JOB 2172 (`QS0GEOM`) and JOB 2173 (`QS0EMPTY`), both
dated 20 October 2026. The exact generator and assembler sources are
tracked under
[`bootstrap-toolchain/probes/q0-qsam-followup-probes/`](../bootstrap-toolchain/probes/q0-qsam-followup-probes/README.md).
Full JES listings remain in the owner's TK5 printer spool and were not
committed; generated JCL is local to ignored `workarea/qsam-q0-followups/`
and may contain job-card credentials.

## JOB 2172 — QS0GEOM: RDJFCB non-opening geometry precheck

| Step | Program | Result |
| --- | --- | --- |
| ASM | IFOX00 | RC=0000 |
| LKED | IEWL | RC=0000 |
| GO | Q0GEOM | RC=0000 |

Reader/QOUT confirmation:

```text
Q0 JFCB FB80/800 OK FB80/801 REJECT PASS
```

The JCL created two **temporary** datasets: `QGOOD` with
`RECFM=FB,LRECL=80,BLKSIZE=800` (WORK04, device 0293), and `QBAD`
with `RECFM=FB,LRECL=80,BLKSIZE=801` (WORK02, device 0291).
Both allocations were deleted when GO ended.

The assembler issued `RDJFCB` separately for each unopened DCB and
required returned R15=0. The code then checked the corresponding JFCB
at `+100` for RECFM `X'90'` (FB), `+102` for BLKSIZE
(800 and 801 respectively), and `+104` for LRECL (80 in each).
For the invalid allocation it divided BLKSIZE by LRECL and required
a nonzero remainder. **Neither `QGOOD` nor `QBAD` was opened.**
The probe opened `QOUT` only to emit the success marker, and it
terminated normally.

**Narrow conclusion:** These JFCB fields and offsets work on both
tested FB DD allocations under this MVS 3.8J installation, and can
support a pre-OPEN FB blocking-relation guard. This is not proof that
all attribute variants or all potential OPEN failures can be
predicted. Compare the deliberately unrecovered FB80/801 OPEN
in [JOB 2171](qsam-q0-open-incompatible-evidence-20261020.md).

## JOB 2173 — QS0EMPTY: empty input and persistent EOF

| Step | Program | Result |
| --- | --- | --- |
| ASMWR | IFOX00 | RC=0000 |
| ASMRD | IFOX00 | RC=0000 |
| LKWR | IEWL | RC=0000 |
| LKRD | IEWL | RC=0000 |
| WGO | Q0EMW | RC=0000 |
| RGO | Q0EMR | RC=0000 |

Reader/QOUT confirmation:

```text
Q0 EMPTY FB EOF2 EODAD1 PASS
```

The WGO step opened and closed `&&Q0EMPTY` without a single PUT,
using FB80/BLKSIZE800 on WORK02 (device 0291). The RGO step
reopened the same temporary dataset as input. The independent reader
modeled two application read requests with a persistent `EOFLAG`:
the first request performed one QSAM `GET`, took `EODAD=ATEND`,
set the flag and returned EOF; the second request observed that flag
and returned EOF **without executing GET again**. The program required
`EOCOUNT=1` after each request and `RDCNT=2` after the second.
There were no data records; any ordinary GET return would have
taken the explicit failure path. The dataset was deleted by RGO.

**Narrow conclusion:** On the tested FB80 DASD path, empty-file
GET enters EODAD and the explicitly implemented sticky-EOF guard
supports repeated application-level EOF safely. The experiment
does **not** show how QSAM behaves if GET is called *again after*
EODAD; it deliberately avoids that potentially unsafe call. Nor
does it exercise the future BCPLQSAM request/result vectors.

## BCPLQSAM design consequences

1. Before opening an FB dataset, validate reliable JFCB attributes
   when available; reject invalid `BLKSIZE mod LRECL` geometry without
   invoking an OPEN likely to abend. A successful RDJFCB alone never
   guarantees OPEN will succeed, and a failed RDJFCB is not necessarily
   an unallocated DD.
2. Track EOF **per open handle** with an explicit persistent flag.
   Once EODAD is seen, later BCPLQSAM READ requests should report
   `QS_EOF` without reissuing GET until that handle is closed.
3. These tests are about EODAD and pre-OPEN checking only. They do not
   establish storage ceilings, a pending-record retry, complete INFO
   output, or recoverability of all MVS OPEN/GET/PUT/CLOSE errors.

**Q.0 remains open; Q.1 has not started.**
