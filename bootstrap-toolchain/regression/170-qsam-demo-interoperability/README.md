# Native regression 170 — qsam-demo-interoperability

**Milestone QSAM — Q.2 interoperability, QUERY expectation updated for Q.3.**

Combined `QSAMSVC:200` and installed read-only BCPLDEMO
`DEMOSVC:203`, interleaved calls, temporary FB80 data and
independent IFOX readback. The current QUERY must report
`QS_CAP_FIXED | QS_CAP_VARIABLE = 3` (opcode bitmap 31).
The numbered `source.bcpl` is byte-identical to the Q.3-aware
`bootstrap-toolchain/extensions/bcplqsam/test-q3-mix.bcpl`.
The historical `test-q2-mix.bcpl` is unchanged.

Run with `tools/bootstrap/run-production-regression 170`.
The established native runner verifies the assembler/linker steps,
BCEX descriptors, 60-byte BCPLREG, independent FB80 readback,
and exact application output. The original Q2MIX and 163–170
production panel passed on 29 October 2026 with QUERY capability 1;
that remains historical evidence, not Q.3 capability-3 validation.
**Updated Q.3 numbered test: PENDING NATIVE EXECUTION.**
No permanent MVS dataset writes or optional object promotion.
