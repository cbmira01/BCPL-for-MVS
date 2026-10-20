# Milestone QSAM — Q.0 pending logical-record retry evidence (2026-10-20)

**March:** Q.0 — Reconnaissance & contract (remains open).
**Experiment:** standalone assembler FB80 logical-record staging;
**not** production BCPLQSAM and **not** the public `QSAMSVC:200` API.

## JOB 2174 — QS0RETRY

The owner executed the tracked
[`q0-qsam-retry-probes`](../bootstrap-toolchain/probes/q0-qsam-retry-probes/README.md)
generator and supplied the complete JES/IFOX/link-editor output,
dated 20 October 2026. `QS0RETRY` was assigned **JOB 2174**.

| Step | Program | Observed |
| --- | --- | --- |
| ASMWR | IFOX00 | RC=0000 |
| ASMRD | IFOX00 | RC=0000 |
| LKWR | IEWL | RC=0000 |
| LKRD | IEWL | RC=0000 |
| WGO | Temporary FB80 record writer | RC=0000 |
| RGO | Standalone staged reader | RC=0000 |

The reader wrote its success marker to `QOUT`:

```text
Q0 FB80 PENDING RETRIES 2 RECORDS PASS
```

The job used one temporary DASD dataset, `&&Q0RETRY`, allocated as
`RECFM=FB,LRECL=80,BLKSIZE=800` on `WORK04` (device 0293).
It was passed from writer to reader and deleted in the reader step.
No PDS objects were installed or modified.

## Tested state and sequence

The writer supplied two records with different eight-byte IDs and
known bytes, including `X'00'` and `X'FF'`. The reader staged each
logical record in a private static 80-byte buffer. It tested these
seven application-level requests:

| Request | Capacity | Simulated result | Length | GET attempts total |
| --- | ---: | --- | ---: | ---: |
| Record 1 | 7 | capacity error | 80 | 1 |
| Record 1 retry | 79 | capacity error | 80 | 1 |
| Record 1 retry | 80 | success | 80 | 1 |
| Record 2 | 0 | capacity error | 80 | 2 |
| Record 2 retry | 80 | success | 80 | 2 |
| Past final record | 80 | EOF | 0 | 3 (entered EODAD) |
| Repeat EOF | 80 | EOF | 0 | 3 (no new GET) |

The assembler compared the entire application destination against a
sentinel after each undersized read and at EOF. It checked exact
record order and data bytes after successful retries. It counted GET
attempts immediately before the QSAM `GET` macro, including the GET
that enters `EODAD`; therefore the final count of three is expected.

**Observed conclusion:** The tested QSAM FB80 reader can keep a
retrieved logical record pending across multiple insufficient-capacity
calls, return it intact on a sufficient retry without an extra GET,
and preserve EOF without repeated GET. A short READ need not lose or
skip a logical record when a private stage is used.

**Limits:** The private stage was **static** and there was **one input
handle**. No MVS `GETMAIN`/`FREEMAIN` allocation, real allocation
failure, simultaneous handles, resource accounting, BCPL byte-pointer
conversion, or `QSAMSVC` request/result vector was exercised. This
experiment does not establish a BCPLQSAM record-size ceiling or an
ability to recover from all QSAM abends.

March Q.0 remains open; Q.1 — Linkage & OPEN/CLOSE skeleton has not
started.
