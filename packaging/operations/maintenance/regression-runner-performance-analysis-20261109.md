# Project regression runner performance — initial source analysis and baseline

**Project:** BCPL for MVS 3.8 Reconstruction
**Date:** 9 November 2026 (US Eastern; execution-directory timestamp 10 November UTC)
**Status:** ANALYSIS OPEN; no runner/JCL/source changes proposed for implementation without owner review
**Input:** Owner-reported complete passing six-suite execution at GitHub HEAD `268600559e58defb410b7bb7719a66bc8e3c9a85`.

The clean-room batch-population optimization has a separate
[closure and evidence record](../../distribution/clean-room-batch-reconstruction-closure-20261109.md).
Do not conflate the reconstruction duration with regression duration.

## Measured full-run baseline

Executed with `tools/tests/run-project-regressions --run`, all six
suites, `--profile installed-r5-t1`, `--allow-device` and `--progress`.

- **Full coordinator wall-clock time:** **73 minutes 57 seconds = 4,437 seconds**.
- **Disposition:** **PASS**, shell RC=0, 194 PASS / 0 FAIL / 1 expected SKIP (083), 195 selected entries.
- **Native numbered cases:** 176 executed PASS among the 177 entries 00–176.
- **MR10 tests and accepted development probes:** 12 + 6 = 18 PASS.
- **Approximate run-wide average:** 4,437 / 194 = **22.9 seconds per executed case**. This includes shared setup, handoffs, validation, and final reporting; **it is not a measured mean or median of independently timed cases**. The SKIP contributes no separate test execution.

Evidence path, on the operator's WSL host:
`workarea/project-regressions/20261110T020053Z-70445-vk1narmi/summary.json`.
The user supplied full console pass counts and the elapsed shell timer.
The underlying native/JES log files and high-resolution per-case times
were **not independently inspected** for this analysis.

## Owner observation and measurement policy

The operator reports that individual tests **appear to take approximately
the same time regardless of suite**. This is plausible if repeated
external orchestration dominates compute time. It is **a working
hypothesis**, not proof that every case has equal execution duration.

**Do not begin by requiring per-suite timing measurements.** One overall
wall-clock baseline is already known. The next useful question is
**where the common per-case time is spent**; compare a small, deliberately
selected set of representative cases and phases before instrumenting
all 194 executions. Per-suite tables would not by themselves distinguish
JES startup/polling from real compiler, assembler, linkage and GO work.

## Confirmed source-level execution shape

### Native suite coordinator — repeated one-case launches

`tools/tests/run-project-regressions` launches each **suite**
sequentially; it stops launching further suites on FAIL/BLOCKED.
`tools/tests/run-suite` launches a **new installed-profile native
runner process for each numbered case**, captures an individual
`runner.log`, validates its footer and writes updated
`summary.json`. It does not run one shared native runner across the
entire suite.

For ordinary native numbered cases, the call path is:

```text
tools/tests/run-project-regressions
  -> tools/tests/run-suite
      -> tools/bootstrap/run-installed-r5-t1-regression (per case)
          -> tools/bootstrap/run-production-regression
              -> tools/bootstrap/run-regression (per case)
                  -> bootstrap-toolchain/regression/run-test-mvs.sh
                      -> bootstrap-toolchain/regression/run-test.sh
                          -> tools/bootstrap/compile-mvs
                          -> tools/mvs/submit-jcl
                          -> tools/mvs/job-summary
                          -> tools/mvs/dump-report-for-job
                          -> independent result/IEWL/output checks
```

QSAM cases 163–176 take the special
`tools/checks/run-q2-qsam-regression.py` branch from `run-test.sh`;
they still perform resident Cambridge compilation and native JCL
preparation/submission/validation.

### Common potentially expensive stages

1. **Resident Cambridge compilation:** `tools/bootstrap/compile-mvs`
   builds a compile deck and calls `dspal-core.submit_and_wait` to
   submit and await a separate MVS compiler job. The compiler executes
   as INTCODE under `ICINT19`, producing System/370 assembler.
2. **Native IFOX/IEWL/GO job:** `run-test.sh` then submits native
   JCL through `tools/mvs/submit-jcl`; it waits for a numbered
   JES start banner and then a complete job report. This is an
   additional JES job for ordinary native cases, and some cases may
   require more than one compiler or object unit.
3. **Repeated result retrieval and validation:** `submit-jcl` polls
   at 0.5-second intervals for job-start evidence. The ordinary native
   shell runner polls `job-summary` at 1-second intervals for job
   completion. The compiler-side DSPAL submitter polls at 0.5-second
   intervals. These are **code-path observations**; no portion of
   4,437 seconds has yet been attributed to polling.
4. **Per-case process/bootstrap overhead:** the suite launcher
   creates a new nested Python/shell process chain and scans the native
   test inventory for each case, then writes individual evidence. Its
   cost is unmeasured and should not be assumed dominant.
5. **MR10 regression and accepted probes:** their separate runners
   also execute cases serially and use `tools/mr10/compile-and-run`
   to submit and await real MVS jobs. The per-case number of JES
   operations is not assumed identical to the native path.

**Interpretation:** The common native case may pay for **at least two
serial MVS jobs** (resident compiler plus native assembler/link/GO),
plus repeated host wrappers, report reading and polling. This is a
strong initial explanation for broadly similar observed test durations
across simple native cases, but it is not a measured bottleneck
ranking and must not be extrapolated unchanged to every MR10/extended
case.

## First analysis actions — no implementation approval implied

1. **Use existing logs first.** Inspect a few straightforward native
   cases (e.g. 00, 01, 053), a more complex native case (e.g. 166),
   and an MR10 case. Determine the actual compiler-job and native-job
   IDs and JES elapsed times. Preserve any known differences.
2. **If existing evidence cannot separate time**, make a narrowly
   scoped **proposal** for monotonic host timing around existing
   compilation, submission/start, completion wait, report extraction
   and validation calls. Preserve each test's independent pass/fail
   assertions; do not change the output contract or force a new full
   74-minute run merely to instrument it.
3. **Quantify the common cost** from representative cases. If
   roughly uniform across simple cases, optimize shared per-case
   JES/host orchestration first. If compiler or IFOX/IEWL dominates,
   focus on the real source and JCL pipeline instead.
4. **Only after measurements**, consider design alternatives, such as
   grouping multiple independent compiler/JES operations into fewer
   jobs while retaining unambiguous per-case outputs, separate
   expected GO RCs, per-step JES/IFOX/IEWL proofs and strict failure
   attribution. This is **not an approved batch-regression design**:
   coalescing jobs may change isolation, temporary DD lifetimes,
   error-handling semantics and resource usage.
5. Evaluate any accepted change using focused native/MR10 tests,
   offline parser and JCL checks, and a later **entire independent
   six-suite regression** under the same profile/device authorization.

## Constraints that cannot be traded for speed

- Preserve the exact historical case IDs and independent suite
  identities; do not rename or renumber milestones or regressions.
- Preserve actual MVS compiler/JES execution, IFOX severity, IEWL
  result, expected GO return code, BCPL output, QSAM evidence and
  explicit class-B punch/printer opt-in.
- Keep case isolation, stop-on-failure policy and actionable
  per-case evidence. Do not treat a single job or suite RC=0 as
  proof of all tests.
- No unapproved parallel JES submissions against shared TK5 printer,
  punch queues, temporary dataset names or workarea paths.
- No new runner code, native JCL, installed dataset changes, or
  background jobs are authorized by this analysis. GitHub source
  remains authoritative; MVS and its tools remain the verification
  authority.

**Next design decision for the owner:** whether to add lightweight
phase timing for a handful of representative cases or use retained
MVS/JES report timestamps first. Both choices deliberately prioritize
**per-case shared overhead over per-suite measurements**.

## Initial native-case timing observations — operator report (10 November UTC)

After the 73m57s passing campaign, the operator inspected retained native
case log modification times and reported these approximate statistics
for **176 passing numbered native cases**:

| Observation | Approximate duration |
| --- | ---: |
| Minimum case | 11.9 s |
| Median case | 23.7 s |
| 90th percentile | 26.1 s |
| Maximum case | 40.9 s (case 168) |
| First 20 cases, median | 23.6 s |
| Last 20 cases, median | 26.1 s |
| Compilation phase, median | 11.9 s |
| Post-compilation phase, median | 11.7 s |

These values came from file modification times, **not** native
instrumentation. The compilation phase split was available only for
cases whose generated assembler file met the timestamp checks. The
first/last comparison also changes workload composition, so it cannot
prove that printer-log growth is the cause of the difference. The
near-constant total remains evidence for investigating shared
per-case costs rather than per-suite totals.

### Approved read-only trial

The owner authorized trial code and commits to study that common cost.
`tools/tests/profile-native-jes-overhead` is an **offline diagnostic**,
not a runner change. For ordinary numbered native cases (00–162),
it correlates retained per-case `JOB n` receipts with the last matching
`RGnnnC/L/R` printer sections in **one streaming printer pass**,
calculates their MVS-reported `IEF403I` to `IEF404I` durations, and
compares those with the case's approximate host wall time. It also
benchmarks the unchanged `tools/mvs/job-summary` implementation,
which currently reads and scans the complete printer log **on each poll**.

Run the unit test and inspect the sample:

```sh
python3 -B -m unittest discover -s tools/checks -p 'test_profile_native_jes_overhead.py' -v
tools/tests/profile-native-jes-overhead \
  --evidence workarea/project-regressions/20261110T020053Z-70445-vk1narmi
```

**Important qualifications:** `OTHER = host elapsed - summed MVS
job elapsed` is only an initial residual. It includes host work,
JES queue/submit/completion waits, log retrieval/validation, and MVS
timestamps rounded to whole seconds; a negative or implausible
residual signals clock or correlation uncertainty. Older/different
JES work can reuse the same job number/name, and later reruns can
replace the last matching printer occurrence. The tool validates the
retained numeric job identities but cannot prove that the latest
printer occurrence came from this exact campaign. QSAM 163–176 use
separate job naming and are deliberately excluded from this initial
trial. No full-suite rerun or JES submission is necessary.

**Decision remains pending** until the operator provides the diagnostic
results: if MVS step durations are small and `job-summary` scanning is
material, first consider a bounded, index-aware or offset-aware
read-only printer lookup. If the MVS compiler/IFOX stages dominate,
the design discussion must instead address separate JES job count and
test isolation. No producer/JCL changes or batch-regression
architecture have been approved.

## Printer-window trial — source implementation, live comparison pending

The operator's measured printer log was **776.7 MiB**. A normal
`job-summary` call took **8.486s median** (three runs), and the
diagnostic one-pass scan took **7.990s**. Selected ordinary native
cases 00, 01 and 053 each showed **0s** of reported MVS elapsed time
at whole-second granularity but approximately **21–23s** of host
elapsed time. Longer cases did have nonzero MVS durations, so actual
MVS processing is not assumed free.

With explicit owner approval, an [opt-in guarded printer-window
trial](jes-printer-window-opt-in-trial-20261110.md) now implements
capturing the printer byte offset before submission, validating the
file identity/short prefix digest, and scanning only records that
arrive afterward. The Cambridge compiler and ordinary native test
runner use it only when `BCPL_PRINTER_WINDOW_TRIAL=1`; default
behavior and validation contracts remain unchanged. The standalone
reader has passed host-only offline safety tests. Integrated JES
execution remains **unverified** until a separately authorized
focused test is performed.

The optimization decision is now concrete: determine whether a
focused case 00 run with the opt-in path retains identical JES/output
evidence and meaningfully reduces the **host-observed** duration.
No full regression acceptance or general default-on transition
is claimed.
