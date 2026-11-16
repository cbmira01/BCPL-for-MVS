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

`run-project-regressions` coordinates the independent MR10 Regression Panel, eleven accepted MR10
Development Probes, and five native regression suites without replacing
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
The six still-unverified MR10 Development Probes are excluded.

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

## Native regression printer-window default

The [10 November six-suite verification](../../packaging/operations/maintenance/jes-printer-window-six-suite-verification-20261110.md)
records 194 PASS, zero FAIL, one expected SKIP (083), and 9m17s
wall time with the offset-based reader explicitly enabled. The
[owner-directed default decision](../../packaging/operations/maintenance/jes-printer-window-default-decision-20261110.md)
promotes that already-tested reader to the **default for numbered native
regressions 00–176**, without changing the generic JES tooling defaults.

- Unset `BCPL_PRINTER_WINDOW_TRIAL` (or set it to `1`): use the
  pre-submission byte-offset reader for Cambridge compilation and native
  IFOX/IEWL/GO JES verification.
- Set `BCPL_PRINTER_WINDOW_TRIAL=0`: explicitly request the legacy
  full-printer-file reader for a native regression.
- Both profiles and direct numbered-regression harness calls follow this
  default; independently invoked `tools/bootstrap/compile-mvs` and generic
  `tools/mvs` utilities retain their established defaults.
- BCPLQSAM cases 163–176 use a bounded native-job report cursor; their
  physical Hercules punch/printer capture checks retain separate offsets.
  MR10 and MR10 probes retain their independent readers.
- Invalid/rotated cursors still fail closed, without legacy fallback.
  The default **does not grant** device authorization; cases 175–176
  still require `--allow-device` through the suite coordinator.

Host-only checks (no JES submission):

```sh
python3 -B -m unittest discover -s tools/checks -p 'test_printer_window*.py' -v
tools/tests/run-project-regressions --check
```

## CO.5 — native coroutine suite

`coroutines` owns test IDs 177–189 with private source-selected CO.2–CO.4
candidate assemblies and BCPL library. Exact oracles and each individual
Cambridge/IFOX/IEWL/GO/JES receipt are checked by the native coordinator.
The `--suite coroutines` project selection runs 13 independent cases without
assigning public globals, modifying installed BOOT_OBJ or changing existing
suite identities. An actual JES run and acceptance remain separate evidence.

## CO.6 — Interpreted/native coroutine comparison

The additional project suite selector `mr10-coroutines` runs the five original owner-accepted `10-coroutines/` MR10 Development Probes via the existing interpreted runner with their unchanged goldens and JES checks. It does **not** duplicate or renumber the 11-case `mr10-probes` selection, the ordinary 12-case `mr10` panel, or the 13-case native `coroutines` suite (177–189).

The original `10-coroutines/fixed-stack-producer-consumer` is a genuine, known interpreted `CODE=-1` FAIL under canonical COBOOT first-activation semantics. It remains FAIL, not an expected PASS, SKIP or XFAIL, so `mr10-coroutines` currently cannot truthfully report all-PASS. The project coordinator stops at that failure; execute the native `coroutines` selection separately to collect its independent MVS receipts. Cross-compiler equivalence is not proved by running the two suites without matched source/oracles. See [CO.6 common contract](../../packaging/milestones/coroutines/co6-common-coroutine-contract-20261116.md).

Host-only contracts: `tools/tests/run-project-regressions --check` and `python3 -B -m unittest discover -s tools/checks -p 'test_co6_coroutine_suite.py' -v`. MVS runs require `--run`, and native `coroutines` additionally requires `--profile production` or `--profile installed-r5-t1`.

### CO.6 known first-activation failure evidence collection

Only the `mr10-coroutines` coordinator selection opts in to
`--continue-known-fixed-stack-failure`. The MR10 runner may continue to later
cases only if the original fixed-stack case has the exact known
interpreted `CODE=-1` diagnostic, compiler/runner RC=0 and a unique
JES job ID. The fixed-stack case and **entire suite remain FAIL**.
All other failures are fail-stop, and the eleven-case
`mr10-probes` selection retains its existing default. This makes
`resumeco-chain` and `create-delete-static-pool` observable in the
same new-suite campaign without hiding the original exception.

## CO.6 paired interpreted/native application candidate

`tools/coroutines/run-co6-pair.py --run` submits independent interpreted
MR10 and native Cambridge/IFOX/IEWL/GO paths, using
`packaging/milestones/coroutines/candidates/co6-pair/` and one exact
11-record oracle. Its `--check` mode is host-only. The native
linker path reuses the accepted CO.3 deletion adapter with pinned source
inputs and does not install or overwrite BOOT_OBJ. Full logs and
structured results go under `workarea/co6-pair/`; normal console output
is limited to per-engine status and evidence location. Both engines must
PASS for an overall PASS; an MR10 failure never suppresses the native
submission. The `co6-pair` and `co6-nested` fixtures each have an owner-reported independent MVS PASS. They are now promoted into the `coroutine-contract` regular project suite, whose own new coordinator run remains pending MVS verification.

## CO.6 — second paired nested coroutine MVS candidate

`tools/coroutines/run-co6-nested.py --check` validates source/oracle
contracts without contacting MVS. `--run` executes both interpreted
MR10 and native System/370 independently, retaining exact records,
zero-return-code job steps and source evidence in
`workarea/co6-nested/`. The separate paired contract uses 18 ordered
`CO6NEST` records and exercises two-worker nested suspension,
busy-target refusal, RESUMECO parent transfer, deletion and reuse.
The tool reuses the verified first-pair driver without editing it or
writing installed MVS objects. Source inputs and host tests are
verified; **actual MVS execution remains outstanding**.

## CO.6 regular cross-compiler regression suite

The newly registered `coroutine-contract` project suite contains exactly two source-pinned paired cases: **`co6-pair`** (11 output records, single-worker re-entry) and **`co6-nested`** (18 output records, two-worker parent-chain, nested continuations and delete/reuse). It dispatches the accepted `tools/coroutines/run-co6-pair.py` and `run-co6-nested.py` unchanged through `tools/coroutines/run-co6-contract-regressions.py`.

The manifest `tests/suites/coroutine-contract.tsv` pins both case identities, source runners and oracles. `tools/tests/run-project-regressions --check` validates the paired sources without JES work. `--run --suite coroutine-contract` submits MVS work (MR10 plus Cambridge/IFOX/IEWL/GO per case), validates complete separate receipts, and provides case names with `--progress`. This suite **does not need** the native-only `--profile` option, because each paired candidate already owns its proven native compilation/linkage profile. Failure stops later cases and returns nonzero. The original `mr10-coroutines` suite continues to report the qualified manual-frame FAIL and cannot be hidden by the new green-contract suite. The first integrated MVS coordinator run is still pending.

## CO.6 supported versus historical MR10 coroutine selections

`mr10-coroutines-supported` selects five **valid-domain** interpreted
MR10 cases. The first four use the existing accepted
`run-dev-probes` strict golden/JES verifier; the fifth compiles
`fixed-stack-co0-candidate.bcpl` under canonical ICINT19 and verifies
its independent exact ten-record oracle, ten zero-RC JES steps and
three zero-valued compiler/generator/RUN completion codes. The supported
manifest is kept separately at
`mr10-kit-compiler/tests/10-coroutines/supported-manifest.tsv`.
The suite retains evidence in `workarea/mr10-supported-coroutines/`
and its accepted subreceipt in `workarea/mr10-probes/`.
Use `--suite mr10-coroutines-supported` to select it in
`tools/tests/run-project-regressions`. Its integrated MVS PASS remains
pending on this newly committed version.

`mr10-coroutines` still selects the **five original historical**
coroutine probes and retains the original fixed-stack failure as
**one genuine FAIL**; no source/golden or status was changed.
The six regular project suites and `coroutine-contract` also remain
unchanged. Never combine historical diagnostic FAIL outcomes into the
regular PASS total without explicitly distinguishing the separate
execution groups.
