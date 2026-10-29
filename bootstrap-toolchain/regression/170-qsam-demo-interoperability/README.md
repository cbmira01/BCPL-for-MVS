# Native regression 170 — qsam-demo-interoperability

**Milestone QSAM — Q.2 — Fixed logical records.**

Combined G!200/G!203 dispatch with installed read-only BCPLDEMO, temporary BCPLQSAM and independent FB80 verification.

The numbered `source.bcpl` is byte-identical to the canonical
`bootstrap-toolchain/extensions/bcplqsam/test-q2-mix.bcpl`.
The runner checks that identity before invoking the native compiler.

Run with `tools/bootstrap/run-production-regression 170`.
The established native runner compiles BCPL, assembles/link-edits on
MVS with IFOX/IEWL, submits JES JCL, verifies native steps and exact
application output in `expected.txt`, and preserves reports.

Original standalone verification: Q2MIX; see Q.2 closure evidence.
The new numbered case itself requires a fresh native run.
No permanent PDS writes or extension promotion.
