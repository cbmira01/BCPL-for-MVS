# Milestone QSAM — Q.0 standalone QSAM FB80 evidence

**Observed MVS job date:** October 20, 2026 (JES clock; local host request
occurred October 19). **Result:** PASS, JOB 2159. **Scope:** Standalone
System/370 assembler QSAM move-mode I/O, not BCPLQSAM or Q.1.

## Evidence received from owner

| Sequence | JOB | Observation |
|---|---|---|
| First FB80 job | 2158 | JES JCL rejection, `IEF652I`/`IEF605I`; nothing executed |
| Corrected FB80 job | 2159 | ASM IFOX00 RC=0000; LKED IEWL RC=0000; GO RC=0000 |

JOB 2159 reported zero assembler statements flagged and severity 0.
Its job report showed `OPEN (INDCB,(INPUT))`,
`OPEN (OUTDCB,(OUTPUT))`, `GET INDCB,RECAREA`,
`PUT OUTDCB,RECAREA`, `CLOSE` for both DCBs, and an EODAD path.
The assembly source checks exactly two records, both 80 bytes long:

- `Q0FIX001` followed by 71 blanks and an `X` in byte/column 80.
- `Q0FIX002` followed by 71 blanks and a `Y` in byte/column 80.

The recorded `QOUT` SYSOUT contains both complete records, and GO
returned RC=0000 after following the expected EOF path.

## Distinguish proof from uncertainty

This **proves** a working standalone QSAM assembly/link and sequential
logical-record transfer on the TK5 MVS system, including successful
MVS OPEN, GET, PUT, EODAD and CLOSE, for those particular JCL DDs.
`QOUT` explicitly requested `RECFM=FB,LRECL=80,BLKSIZE=800`.
The input `QIN DD DATA,DLM=QZ` no longer specified explicit DCB
parameters after the JCL fix. Its effective physical RECFM and BLKSIZE
were **not checked**. `QOUT SYSOUT` was not a blocked DASD dataset.
Therefore JOB 2159 is **not** evidence that an FB dataset spanning
physical disk blocks was read/deblocked.

## Correction retained in Git

The test-only generator at
[`bootstrap-toolchain/probes/q0-qsam-fb80-probe/make-job.py`](../bootstrap-toolchain/probes/q0-qsam-fb80-probe/make-job.py)
now emits `//QIN DD DATA,DLM=QZ` with no DD DATA DCB override and
`//QOUT DD SYSOUT=*,` followed by the FB80 DCB continuation. This is
exactly the local correction that produced JOB 2159.

The follow-on [DASD QSAM probes](../bootstrap-toolchain/probes/q0-qsam-dasd-probes/README.md)
exercise genuinely blocked fixed-format records and V/VB behavior.
Those probes were **not yet executed when this earlier record was written**;
they later passed in JOBs 2160–2162. See the separate
[Q.0 DASD evidence](qsam-q0-dasd-evidence-20261020.md).

**Q.0 — Reconnaissance & contract remains open.** The global-vector
registrar, error semantics, V/VB edge cases, buffer retry staging and
other Q.0 acceptance conditions are not established by this result.
