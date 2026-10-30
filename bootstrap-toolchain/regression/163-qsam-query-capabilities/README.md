# Native regression 163 — qsam-query-capabilities

**Milestone QSAM — Q.4 capability acceptance update.**

Reassert the QUERY v1 descriptor, operation bitmap (31) and sentinel
boundaries, with `QS_CAP_FIXED | QS_CAP_VARIABLE | QS_CAP_CARRIAGE = 7`
for verified F/FB, V/VB and FBA output carriage semantics.
This does **not** claim VBA support. Historical Q.3 sources remain in
`bootstrap-toolchain/extensions/bcplqsam/test-q3-query.bcpl`.

The numbered `source.bcpl` must be byte-identical to
`bootstrap-toolchain/extensions/bcplqsam/test-q4-query.bcpl`.
Run: `tools/bootstrap/run-production-regression 163`.
