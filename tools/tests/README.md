# Native suite coordinator (Stage 2B/2C)

`run-suite` reads `tests/suites/*.tsv`, validates their static case ownership,
and invokes existing `tools/bootstrap/run-production-regression` or
`tools/bootstrap/run-installed-r5-t1-regression` per selected native case.
It is a host-side selection/accounting adapter, not a replacement compiler,
JCL generator, MVS backend or MR10 runner. See [suite contract](../../tests/README.md).

Check offline with:

```sh
python3 -B -m unittest discover -s tools/checks -p 'test_stage2b_suite.py' -v
tools/tests/run-suite --check
tools/tests/run-suite --list
```

**`--run` submits JES jobs and requires separate authorization.**

## Stage 3 — independent coordinated regression

`run-project-regressions` coordinates the independent MR10 Regression Panel, six accepted MR10
Development Probes, and four native regression suites without replacing
their existing runners.

Host-only operations, requiring no MVS execution:

```sh
tools/tests/run-project-regressions --check
tools/tests/run-project-regressions --list
tools/tests/run-project-regressions --list --suite bcpltime
```

The following examples **execute tests** and require separate operator
authorization. Native execution submits JES jobs; MR10 execution invokes
the existing interpreter-hosted compile-and-run workflow.

```sh
tools/tests/run-project-regressions --run --suite mr10
tools/tests/run-project-regressions --run --suite bootstrap --profile production
tools/tests/run-project-regressions --run --suite mr10 --suite bcpltime --profile installed-r5-t1
# Console progress without showing verbose JES/compiler output:
tools/tests/run-project-regressions --run --suite mr10 --progress
# Explicitly authorized JES printer/punch tests (cases 175–176):
tools/tests/run-project-regressions --run --suite bcplqsam --profile installed-r5-t1 --allow-device
```

An executing command must explicitly select at least one suite.
Selected native suites require a common explicit profile:
`production` or `installed-r5-t1`.

The coordinator uses the existing MR10 panel/probe manifests and four
native suite manifests. It does not duplicate, renumber or relocate cases.
The eleven unverified MR10 Development Probes are excluded.

MR10 tests retain their `category/name` identities. Native cases retain
their established numeric IDs. Each suite keeps independent outcome
counts and records, without creating a combined acceptance total.

Execution creates a private directory under
`workarea/project-regressions/` containing `summary.json` and individual
suite logs. The native runner additionally retains its original
per-case JES evidence under `workarea/test-suites/`.

With `--run --progress`, each reported MR10 or native case result is
printed to the WSL console as it arrives (`PASS`, `FAIL`, `SKIP`, or
`BLOCKED`, with its original case ID). Full compiler/JES details still go
to the suite logs. Python child output is unbuffered in this mode to
make updates timely. Without `--progress`, only suite-level status is
shown. The flag is invalid with `--list` or `--check`; it neither
authorizes JES nor changes device opt-in. The project summary records
`progress` separately from `allow_device`.

The project summary distinguishes `PASS`, `FAIL`, `BLOCKED`,
`NOT_RUN` and `NOT_SELECTED`. The MR10 runner reports PASS and FAIL,
not SKIP/BLOCKED, so its unavailable categories remain `null`.

Execution stops before launching another suite when a selected suite
fails or is blocked. The coordinator strips inherited JES punch-resume
settings. By default, BCPLQSAM device cases 175–176 report BLOCKED.
Only an explicit `--run --suite bcplqsam --allow-device` authorizes
passing the flag to the native BCPLQSAM runner. The flag is rejected for
`--list`, `--check`, or runs not selecting BCPLQSAM. For case **175
only**, this opt-in also enables a **guarded single `$S PUN1`** when
`PUNCH1` is paused (`P=Y, Q=B`) and a fresh JES2 queue display shows
only the current case's `Q4PUNCH` job. Unrelated queued class-B work,
an unverified queue/device state, or a missing target job blocks the
writer start; the runner does not flush the queue or retry a failed
start. The exact new 172-byte image and target JES job receipt remain
mandatory. Case **176** never starts the punch writer. The project
summary records `allow_device`.

The coordinator does not check installed MVS objects or submit jobs
during `--check` or `--list`. A successful manifest check is not
evidence of native MVS execution.

The MR10 panel remains in `mr10-kit-compiler/tests/`.
Its established runner remains `tools/mr10/run-regression-panel`.

Host-only unit tests:

```sh
python3 -B -m unittest discover -s tools/checks -p 'test_stage3_coordinator.py' -v
python3 -B -m unittest discover -s tools/checks -p 'test_stage2b_suite.py' -v
python3 -B -m unittest discover -s tools/checks -p 'test_qsam_punch_writer_guard.py' -v
```

## Read-only JES overhead timing trial (10 November 2026)

`tools/tests/profile-native-jes-overhead` analyzes **existing**
`run-project-regressions` evidence and the Hercules printer file.
It does **not** submit JES, change installed MVS datasets, change runner
behavior or rerun tests. Host-only tests:

```sh
python3 -B -m unittest discover -s tools/checks -p 'test_profile_native_jes_overhead.py' -v
```

From the repository root, with the previously accepted 10 November
evidence still available in `workarea/`:

```sh
tools/tests/profile-native-jes-overhead \
  --evidence workarea/project-regressions/20261110T020053Z-70445-vk1narmi
```

The default sample is numbered native cases **00, 01, 053, 126, 141,
160**. Use repeated `--case N` to select other native cases 00–162,
or `--bench 0` to omit subprocess benchmarking. The prototype does
not yet handle BCPLQSAM 163–176, whose compiler and native logs use
different naming and evidence paths.

For each requested case, the trial correlates `JOB n` entries from
the retained native execution log with `RGnnnC/L/R` jobs in the printer
stream, then compares approximate host wall time (case log mtimes)
against the `IEF403I`/`IEF404I` MVS start/end difference. `OTHER`
is **not** a pure JES overhead measurement: it includes host preparation,
polling, report validation and whole-second MVS clock resolution.
The printer scan selects the **last matching job-number/name occurrence**,
which can be superseded by later JES activity; compare the job identities
before interpreting results. Missing or ambiguous durations are reported
as `n/a`. The optional benchmark times normal `job-summary` calls
against the current complete printer file; it does not change that tool.
This is diagnostic evidence, not regression acceptance.
