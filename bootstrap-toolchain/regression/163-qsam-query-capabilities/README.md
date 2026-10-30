# Native regression 163 — qsam-query-capabilities

**Milestone QSAM — Q.2 fixed records, extended for Q.3 variable records.**

QUERY v1 descriptor, opcode bitmap and argument/sentinel boundaries.
Q.3 extends the required capability bits to `QS_CAP_FIXED |
QS_CAP_VARIABLE = 3`, while the supported-opcode bitmap remains 31.
The numbered `source.bcpl` is byte-identical to
`bootstrap-toolchain/extensions/bcplqsam/test-q3-query.bcpl`,
not the preserved historical Q.2 query application.

Run with `tools/bootstrap/run-production-regression 163`.
The runner compiles with the resident demoted Cambridge compiler,
links temporary BCPLQSAM, and verifies real IFOX/IEWL/JES output.

**Historical Q.2 acceptance:** JOBs 6973–6974 and prior 163–170 panel
validated fixed-only capability 1 on the then-current source.
That historical evidence is retained in the Q.2 closure record and
`test-q2-query.bcpl`; it does not establish capability 3.
**Updated Q.3 numbered test: PENDING NATIVE EXECUTION.**
No permanent MVS dataset or object changes.
