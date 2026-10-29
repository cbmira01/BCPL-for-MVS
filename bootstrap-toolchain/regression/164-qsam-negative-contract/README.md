# Native regression 164 — qsam-negative-contract

**Milestone QSAM — Q.2 — Fixed logical records.**

Invalid DDNAME, missing DD, invalid modes, reserved fields and invalid handles.

The numbered `source.bcpl` is byte-identical to the canonical
`bootstrap-toolchain/extensions/bcplqsam/test-q1-negative.bcpl`.
The runner checks that identity before invoking the native compiler.

Run with `tools/bootstrap/run-production-regression 164`.
The established native runner compiles BCPL, assembles/link-edits on
MVS with IFOX/IEWL, submits JES JCL, verifies native steps and exact
application output in `expected.txt`, and preserves reports.

Original standalone verification: Q1NEG; see Q.2 closure evidence.
The new numbered case itself requires a fresh native run.
No permanent PDS writes or extension promotion.
