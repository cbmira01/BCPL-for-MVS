# Native regression 175 — qsam-fb80-sysout-punch

**Milestone QSAM — Q.4 — SYSOUT devices.**

Uses the source-mode BCPLQSAM optional System Extension, production
`BOOT_OBJ` Core Runtime, the resident demoted Cambridge compiler, native
IFOX/IEWL and JES2 on MVS 3.8J.

BCPL writes three identical FB80 records to a temporary QSAM dataset and
`SYSPUNCH DD SYSOUT=B`. An independent IFOX verifier checks all 80
EBCDIC bytes, including trailing blanks/column 80, and exact EOF.

The runner additionally checks **new** class-B Hercules ASCII capture
against the accepted 172-byte three-card-plus-blank-separator image.
This proves observed ASCII device presentation, not independently preserved
physical EBCDIC trailing blanks. Missing/modified capture fails the case.

`source.bcpl` must be byte-identical to the canonical
`bootstrap-toolchain/extensions/bcplqsam/test-q4-punch.bcpl`.

Run: `tools/bootstrap/run-production-regression 175`. No installed
MVS object promotion or Hercules configuration changes.

**JES2 PUNCH1 operator prerequisite:** The punch writer may be
`PAUSED` with `P=Y`. The operator may choose
`Q4_PUNCH_RESUME=1 tools/bootstrap/run-production-regression 175`
to authorize one `$S PUN1` console command when the native steps
have passed and the expected punch capture remains unchanged.
This single operation may also release other queued class-B output.
The runner still verifies the actual new device bytes and records the
console reply under the attempt's `punch-writer-start.log`.
