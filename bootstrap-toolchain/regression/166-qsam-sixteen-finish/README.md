# Native regression 166 — qsam-sixteen-finish

**Milestone QSAM — Q.2 — Fixed logical records.**

Sixteen-handle FINISH lifecycle, 17th refusal, returned GO RC=0.

The numbered `source.bcpl` is byte-identical to the canonical
`bootstrap-toolchain/extensions/bcplqsam/test-q1-finish.bcpl`.
The runner checks that identity before invoking the native compiler.

Run with `tools/bootstrap/run-production-regression 166`.
The established native runner compiles BCPL, assembles/link-edits on
MVS with IFOX/IEWL, submits JES JCL, verifies native steps and exact
application output in `expected.txt`, and preserves reports.

Original standalone verification: Q16FIN; see Q.2 closure evidence.
**Native verification — 29 October 2026: PASS.** Included in the
focused 163–170 run (8 PASS, 0 FAIL, 0 SKIP) and the complete
00–170 production panel (170 PASS, 0 FAIL, 1 expected SKIP 083;
TOTAL 171, runner RC=0). See the Q.2 closure record under
`packaging/qsam-q2-closure-20261029.md` for evidence and scope.
No permanent PDS writes or extension promotion.
