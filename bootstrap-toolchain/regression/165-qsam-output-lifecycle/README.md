# Native regression 165 — qsam-output-lifecycle

**Milestone QSAM — Q.2 — Fixed logical records.**

OPEN/INFO/CLOSE and rejected null WRITE buffer.

The numbered `source.bcpl` is byte-identical to the canonical
`bootstrap-toolchain/extensions/bcplqsam/test-q1-output.bcpl`.
The runner checks that identity before invoking the native compiler.

Run with `tools/bootstrap/run-production-regression 165`.
The established native runner compiles BCPL, assembles/link-edits on
MVS with IFOX/IEWL, submits JES JCL, verifies native steps and exact
application output in `expected.txt`, and preserves reports.

Original standalone verification: Q1OUT; see Q.2 closure evidence.
The new numbered case itself requires a fresh native run.
No permanent PDS writes or extension promotion.
