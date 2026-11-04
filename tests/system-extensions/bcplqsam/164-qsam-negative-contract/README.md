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
**Native verification — 29 October 2026: PASS.** Included in the
focused 163–170 run (8 PASS, 0 FAIL, 0 SKIP) and the complete
00–170 production panel (170 PASS, 0 FAIL, 1 expected SKIP 083;
TOTAL 171, runner RC=0). See the Q.2 closure record under
`packaging/qsam-q2-closure-20261029.md` for evidence and scope.
No permanent PDS writes or extension promotion.
