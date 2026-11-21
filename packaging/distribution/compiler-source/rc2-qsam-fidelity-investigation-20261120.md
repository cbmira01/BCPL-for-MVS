# TA.2 — Historical Cambridge source end-of-member record investigation

**Project:** BCPL for MVS 3.8 Reconstruction  
**March:** TA.2 — Manifest-Driven Tape Producer  
**Date:** 20 November 2026  
**Current status:** Source population accepted at directory level; binary/record fidelity pending direct MVS QSAM check.

## Observed MVS evidence

The owner returned the output of the saved readback diagnostic for
`BCPL-0.1.0-rc2` after the approved MVS source population in
JOBS **9325** and **9326**:

```text
TA.2 RC2 SAVED READBACK: 2/15 members examined; 1 mismatch(es)
  BCPL: MVS JOB 9328, normalized records PASS
  BLIB: MVS JOB 9329, MISMATCH
    type: missing-records-at-end
    first_different_record: 473
    expected_records: 474
    observed_records: 472
    expected_final_lf: True
    observed_final_lf: True
    expected_length: 0
    observed_length: None
```

The first 472 normalized `BLIB` records match the frozen Git source.
The frozen historical `BLIB` file contains **two empty final records**
(473–474). Separate GitHub inspection at frozen source commit
`78baec9a8546e4ab09caee779aa2b675379272f3` found one trailing
empty record each in `LIBHDR` and `TRNHDR`. The other 12 selected
members have no trailing fully blank records. The mismatch does **not**
establish whether the records are missing from the MVS PDS or lost
by the `dspal get` / IEBGENER / SYSOUT text path. Neither cause has
been assumed.

The original directory proof and population acceptance remain valid.
The independent `BT0021` staging data set is not yet accepted or written.
Do not rerun the one-shot population or overwrite previous evidence.

## Targeted MVS verification implementation

`rc2-qsam-fidelity.asm` adapts the project's established IFOX/QSAM
fixed-record GET pattern. A single temporary IFOX/IEWL build runs
15 individual read-only QSAM steps, one for each selected historical
PDS member. Each step reads all original **80-byte CP037/EBCDIC
records**, counting records and consecutive trailing all-blank
records, and calculating a 32-bit FNV-1a fingerprint and independent
32-bit additive checksum over the complete padded byte stream.
The hexadecimal output fits one 80-byte SYSOUT record per member.
No permanent load-module target, source write, IEBCOPY operation,
release tape write, or IBM utility self-test is included.

`rc2-qsam-fidelity.py --verify-mvs` checks the frozen canonical
selection, original source file Git contents, saved JOB 9325/9326
population and member-directory evidence, and effective managed
PDS mapping. It reproduces expected CP037 fixed-80-byte checksums
without trimming empty records, generates the in-memory authenticated
JCL, submits one bounded MVS verification job via the established
`dspal-core` interface, and retains its full job summary and print
report exclusively under
`workarea/ta2-rc2-cambsource-qsam-fidelity/`. It parses
15 unique member results, rejects any count/trailing-blank/checksum
mismatch, and does not repeat a prior submission or overwrite a
preexisting evidence directory. Any assembler or MVS failure must
be reviewed from retained evidence before deciding next actions.

**Scope:** This test checks actual FB80 record counts and two
independent byte fingerprints; these are diagnostics of binary
fidelity, not a mathematical proof of collision-free byte equality.
The previously successful normalized `BCPL` text readback adds a
separate logical-record check. A passing direct QSAM fingerprint
for a member is not equivalent to installing or executing a
native Cambridge Compiler.

## Pre-submission tests and release boundary

The assistant tested Python rendering, FB80 CP037 checksum reference
behavior, 80-byte assembler summary field sizes, fixed source-column
widths, exact 15-step JCL, parsing, and fail-closed cases in a separate
assistant workspace. **10/10 focused synthetic tests PASS**, plus
Python AST/assembler-card structure checks. Actual IFOX/IEWL/MVS
acceptance is pending owner execution; successful offline tests
must not be reported as MVS success.

`BCPL-0.1.0-rc2` / `BC0002` / 21 logical datasets are unchanged.
The first 20 staged inputs remain accepted and untouched; demoted
Cambridge development sources remain GitHub-only. Historical source
rights and final release verification remain independent open gates.
**TA.2 remains IN PROGRESS.**
