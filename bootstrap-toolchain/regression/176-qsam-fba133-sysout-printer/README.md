# Native regression 176 — qsam-fba133-sysout-printer

**Milestone QSAM — Q.4 — SYSOUT devices.**

BCPL writes three complete FBA133 records, including the explicit ASA
control byte, to temporary QSAM and `Q4PRINT DD SYSOUT=A`.
`SYSPRINT` remains owned by the Core Runtime BCPLIO. The ASA characters
are EBCDIC blank (single space), `0` (double space), and `1`
(new page). An independent IFOX verifier checks all 133 EBCDIC bytes
and exact EOF from the passed temporary dataset.

The runner also examines **new** Hercules class-A ASCII output:
`Q4FBA001\n\nQ4FBA002` and `X\x0cQ4FBA003` must appear;
the three labels must be unique. This verifies observed JES2 carriage
presentation; the independent IFOX test verifies record bytes.

`source.bcpl` must be byte-identical to the canonical
`bootstrap-toolchain/extensions/bcplqsam/test-q4-fba.bcpl`.

Run: `tools/bootstrap/run-production-regression 176`.
No permanent MVS object or Hercules changes.
