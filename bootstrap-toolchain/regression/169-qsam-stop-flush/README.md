# Native regression 169 — qsam-stop-flush

**Milestone QSAM — Q.2 — Fixed logical records.**

STOP(8) FB80 finalizer flush and independent assembler exact readback.

The numbered `source.bcpl` is byte-identical to the canonical
`bootstrap-toolchain/extensions/bcplqsam/test-q2-stop-flush.bcpl`.
The runner checks that identity before invoking the native compiler.

Run with `tools/bootstrap/run-production-regression 169`.
The established native runner compiles BCPL, assembles/link-edits on
MVS with IFOX/IEWL, submits JES JCL, verifies native steps and exact
application output in `expected.txt`, and preserves reports.

Original standalone verification: Q2STOP; see Q.2 closure evidence.
The new numbered case itself requires a fresh native run.
No permanent PDS writes or extension promotion.
