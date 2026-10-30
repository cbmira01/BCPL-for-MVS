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
**Updated Q.3 numbered test: PASS, 30 October 2026.** The
owner-run focused 163–174 panel passed 12/12 and the complete production
00–174 panel passed with 174 PASS, 0 FAIL, one expected SKIP 083;
both runner RC=0. See the [Q.3 closure](../../../packaging/qsam-q3-closure-20261030.md).
No permanent MVS dataset or object changes.
