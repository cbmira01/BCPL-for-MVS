# Native regression 170 — qsam-demo-interoperability

**Milestone QSAM — Q.4 capability acceptance update.**

Combined `QSAMSVC:200` and installed read-only `DEMOSVC:203`,
interleaved calls, temporary FB80 binary output and independent IFOX
readback. QUERY now requires F/FB, V/VB and verified FBA carriage
capability bits `7`; the opcode bitmap remains `31`.

The numbered `source.bcpl` must be byte-identical to
`bootstrap-toolchain/extensions/bcplqsam/test-q4-mix.bcpl`.
Historical Q.3 source remains retained. Test still expects the
same two native Q2 MIX messages and STOP(8) finalizer behavior.

Run: `tools/bootstrap/run-production-regression 170`.
