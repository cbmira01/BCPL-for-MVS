# DR.5 — Focused compiler input and option verification

Baseline `0de748ebef72965497dd1ac40330a99a33f56cae`. Three independent hypotheses, no changes to resident members, regular test numbering or suite oracles. Serial execution on the established corrected development installation.

| Probe | Input and prediction |
| --- | --- |
| MR10 nested GET | SYSIN GET DR5INC; outer header declares A, opens DR5NEST, then declares B and ends with period. Inner header declares C and ends at EOF. Require exact 17 5 20 42 output after both returns. |
| MR10 OPTIONS | L6000N should reprocess N after the decimal workspace argument, suppressing GET DR5MISS (no such DD allocated). Require option echo and exact 42 output. Does not measure actual workspace extent. |
| Cambridge CAMBPARM | J12Q/N/ slash-filled through column 80. Unknown first-phase J should warn and skip numeric suffix; Q should suppress ordinary phase diagnostics; second-phase N suppresses binary deck. GET LIBHDR supplies START/WRITEF and the three manifest values. Require warning, quiet diagnostics, zero ICINT CODE, IFOX/IEWL/native GO and exact 4 32 -1 output. No direct object-deck or native-running compiler claim. |

The separate [driver](../../../../../tools/checks/run-dr5-compiler-verification.py) uses existing MR10 and Cambridge host drivers, JES receipt checks and native object linkage. 904 is a private helper naming argument, not a new suite case. All three probes are expected to succeed; stop on first failure and retain private receipts. No automated retries, installations or full regression replay.

Offline Python compilation and fixture/oracle and option-record checks passed using a mocked shared helper. Actual MVS compilation, execution and diagnostic checks remain pending. Missing-input and nesting-overflow diagnostic paths are source-observed only; the MR10 suppressed-GET test deliberately avoids executing the unsafe unsuppressed missing-input path. No arbitrary nesting, all-option coverage, or malformed-input recovery certification.
