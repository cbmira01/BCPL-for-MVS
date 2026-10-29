# Native regression 167 — qsam-sixteen-stop

**Milestone QSAM — Q.2 — Fixed logical records.**

Sixteen-handle STOP lifecycle; deliberate native GO RC=0008.

The numbered `source.bcpl` is byte-identical to the canonical
`bootstrap-toolchain/extensions/bcplqsam/test-q1-stop.bcpl`.
The runner checks that identity before invoking the native compiler.

Run with `tools/bootstrap/run-production-regression 167`.
The established native runner compiles BCPL, assembles/link-edits on
MVS with IFOX/IEWL, submits JES JCL, verifies native steps and exact
application output in `expected.txt`, and preserves reports.

Original standalone verification: Q16STP; see Q.2 closure evidence.
The new numbered case itself requires a fresh native run.
No permanent PDS writes or extension promotion.
