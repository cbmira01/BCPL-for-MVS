# JES printer-window reader — opt-in performance trial

**Project:** BCPL for MVS 3.8 Reconstruction
**Date:** 10 November 2026 UTC (9 November US Eastern)
**Status:** TRIAL CODE — offline helper tests passed; live MVS validation and performance comparison pending
**Authority:** [Regressions performance analysis](regression-runner-performance-analysis-20261109.md); GitHub `main` is source authority. Actual JES and program execution remain the acceptance authority.

## Motivation and measured baseline

The previously accepted six-suite regression took **73m57s** at source
revision `268600559e58defb410b7bb7719a66bc8e3c9a85`:
194 PASS, 0 FAIL, 1 expected SKIP (083). A representative native-case
sample showed **23.7s median** host elapsed. The owner's real 10 November
profiling run found:

- Hercules printer `mvs-state/prt/prt00e.txt`: **776.7 MiB**.
- One `job-summary` invocation: **8.486s median** over three runs.
- One-pass full printer scan: **7.990s**.
- Sample ordinary native cases: MVS-reported job execution between
  **0 and 5s summed**, versus **20.8–28.4s** host-observed time.
  MVS timestamps have whole-second resolution; the host residual
  includes both JES and unrelated host overhead. No claim of zero MVS
  execution time is justified.

The existing completion monitor `tools/mvs/job-summary` reads
the whole printer stream for every poll. Normal regressions submit at
least one separate compiler and one native IFOX/IEWL/GO job per
ordinary case, so full-file scans are expensive and repeated.

## Trial mechanism and scope

`tools/mvs/printer-window.py` captures a printer-file cursor
**before** the associated JES reader submission. The cursor contains
the file's device/inode, byte offset, an SHA-256 digest of the last
up to 64 bytes, and whether the snapshot ended inside a partial line.
The cursor is written atomically and mode 0600.

Subsequent reads check the file identity, that it has not shrunk
below the recorded offset, and that the protected prefix bytes are
unchanged. When an earlier line was partial, its continuation is
discarded; only newly completed records are eligible. A replaced,
truncated or inconsistent printer file **fails closed**: it never
silently falls back to stale complete jobs. The hash is a safety
check against likely rewrites, not a cryptographic provenance
guarantee for the complete printer file.

Opt-in support was added without changing the existing default
behavior of:

- `tools/mvs/submit-jcl --cursor-file FILE`: capture before socket
  submission; poll new bytes for job-start identification.
- `tools/mvs/job-summary JOB --cursor-file FILE`: check only new
  output, preserving job-number-reuse, step return-code, assembler
  and abend parsing.
- `tools/mvs/dump-report-for-job JOB --cursor-file FILE`: retain
  existing awk job extraction, but run it on the validated window.
- `tools/datasets/dspal-core.py`: optional cursor argument on
  `submit_and_wait` and `job_report`.
- `tools/bootstrap/compile-mvs`: optional cursor for Cambridge
  compile job, including both completion and assembler-text recovery.
- `bootstrap-toolchain/regression/run-test.sh`: optional cursor for
  the independent native assemble/link/GO job, including GO result
  and output extraction.

The trial is enabled **only** by an explicit
`BCPL_PRINTER_WINDOW_TRIAL=1` environment variable. It applies
fully to ordinary native numbered cases **00–162**. BCPLQSAM
163–176 use `tools/checks/run-q2-qsam-regression.py` for their
native multi-step job and remain on that reader's established
report path (their Cambridge compilation may use the cursor).
The MR10 panel and development probes likewise retain their
existing independent reader paths.

A job-number reuse *after the captured cursor* is still handled by
the existing latest-start/latest-END job summary logic. The cursor
also excludes historical completed jobs with matching numbers.
Host-only tests cover rotation, truncation, partial lines, recent
incomplete jobs, reuse, output parity with the legacy path, and
nonmutation. Running a JES job is **not** part of those tests.

## Required offline validation

From a checkout at the trial commit:

```sh
python3 -B -m unittest discover -s tools/checks \
  -p 'test_printer_window*.py' -v
python3 -B -m unittest discover -s tools/checks \
  -p 'test_profile_native_jes_overhead.py' -v
tools/tests/run-project-regressions --check
```

None of these operations submits JES or modifies MVS datasets.
Do not confuse this test coverage with native MVS acceptance.

## Controlled live comparison (requires separate operator authorization)

When the owner separately approves an actual regression job, compare
ordinary native **case 00** with the existing installed-profile
baseline (historically approximately **21s**), while explicitly
enabling the environment variable only for that invocation:

```sh
BCPL_PRINTER_WINDOW_TRIAL=1 tools/tests/run-suite \
  bootstrap --run --case 0 --profile installed-r5-t1
```

This is **an MVS submission command, not an offline validation**.
It must **not** be executed until the operator separately authorizes
JES submissions and confirms a suitable idle/resident target state.
Keep the resulting JES job IDs, compiler/assembler/link/GO codes,
generated code and per-case logs. Verify against the previous
accepted test behavior and explicitly compare elapsed host time.
A successful process RC without complete JES evidence is insufficient.

If successful, choose a small number of additional representative
cases, including separate BCPL library compilation. A later
fully independent six-suite regression remains required before
making the new reader the default.

## Boundaries

- No MVS source, JCL deck structure, canonical BCPL compiler or
  installed object/dataset contents are changed by this trial code.
- No job submissions, permanent-object installation, release or
  baseline tagging are authorized by the commit.
- Errors do **not** fall back to full scans; a failed or ambiguous
  submission must be investigated before any retry.
- Do not extend the opt-in to parallel JES submissions without
  separate dataset/printer/device isolation analysis.
- Verify the installed profile, QSAM 163–176 and MR10 paths separately
  before considering default-on activation. The accepted unoptimized
  behavior remains available by leaving the environment variable unset.
