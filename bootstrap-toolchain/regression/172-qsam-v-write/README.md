# Native regression 172 — qsam-v-write

**Milestone QSAM — Q.3 — Variable logical records.**

RECFM=V, effective DCB LRECL=1024, BLKSIZE=1028.
Private BCPLQSAM logical stage 1024 bytes including four-byte RDW,
so maximum BCPL payload is 1020 bytes; QSAM owns physical blocking
and any BDW. The BCPL application uses `QSAMSVC:200` directly.

Coverage: RDW construction; 0, 1, 12 and 1,020-byte payloads; rejected oversize/negative WRITE; independent IFOX RDW/binary/EOF verification.

The numbered `source.bcpl` must be byte-identical to
`bootstrap-toolchain/extensions/bcplqsam/test-q3-limit-write.bcpl`.
The established QSAM native regression runner enforces that identity,
uses the existing Q.3 limit JCL generator, links a temporary source-mode
BCPLQSAM, and verifies every IFOX/IEWL/application step and the exact
`expected.txt` output records. An independent IFOX reader validates RDWs and every payload byte.

Standalone acceptance campaign: JOB 7348 Q3VLWRT, all ten steps RC=0000,
native output PASS, as reported by the operator on MVS 3.8J.
**Numbered regression status: PENDING NEW EXECUTION**. The earlier
standalone job is not evidence that numbered case 172 has run.

Run with `tools/bootstrap/run-production-regression 172`.
No permanent MVS dataset writes or BCPLQSAM object promotion.
