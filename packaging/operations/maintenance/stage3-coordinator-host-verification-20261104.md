# Stage 3 — independent coordinated regression

**Project:** BCPL for MVS 3.8 Reconstruction
**Date:** 4 November 2026
**Baseline:** `743c3840d7b192c5ede5ed422e77821d5b68c4c8`
**Status:** OWNER ACCEPTED — host and live integration verification PASSED.

Stage 3 is a repository maintenance work package, not a change to
an official milestone or march.

## Scope

A single project-level coordinator, `tools/tests/run-project-regressions`,
coordinates five independent suites:

| Suite | Tests | Execution authority |
| --- | ---: | --- |
| MR10 | 12 | Existing MR10 manifest/runner |
| Bootstrap | 146 | Existing native suite runner |
| Runtime Extensions | 13 | Existing native suite runner |
| BCPLTIME | 4 | Existing native suite runner |
| BCPLQSAM | 14 | Existing native suite runner |

There is no consolidated project acceptance total. MR10 names and native
numeric IDs remain independently defined and reported.

## Implementation boundaries

- `--list` and `--check` are host-only.
- `--run` requires explicit suite selection.
- Native runs require an explicit profile.
- Existing MR10 and native runners perform the actual test execution.
- Independent per-suite outcomes and evidence are preserved.
- Unselected suites are recorded as NOT_SELECTED.
- Selected suites not reached after failure are recorded as NOT_RUN.
- Failures and BLOCKED outcomes stop further suite execution.
- The coordinator strips inherited punch-resume environment variables.
- No project-level device opt-in is provided.
- Existing GitHub milestone and acceptance records are unchanged.

## Host verification

The operator executed eight isolated Stage 3 coordinator unit tests
using synthetic MR10/native runners, with all eight passing and RC=0.

The tests cover offline operations, CLI authorization checks, MR10
identity and independent accounting, mixed-suite reporting, failure
short-circuiting, BLOCKED short-circuiting, malformed native evidence,
and rejection of missing MR10 fixtures.

The real repository inventory check returned RC=0:

- MR10: 12
- Bootstrap: 146
- Runtime Extensions: 13
- BCPLTIME: 4
- BCPLQSAM: 14

These checks establish host-side coordination behavior only.
The synthetic runner outputs are not JES or interpreter execution
acceptance evidence.

## Verification boundary and next gate

The project coordinator has completed an authorized 16-case live
integration campaign. The remaining three suites were NOT_SELECTED;
their execution is not claimed as part of Stage 3 verification.

Full BCPLQSAM execution without explicit device authorization
will report BLOCKED for device cases 175–176. That status must not
be silently converted to SKIP or PASS.

Stage 3 was accepted by the project owner on 4 November 2026.
Further live-suite execution requires separate authorization.

## Live integration verification — 4 November 2026

### Initial campaign — failed host-side classification

Evidence: `workarea/project-regressions/20261104T135238Z-19669-j0gt52l9/`

The coordinator recorded MR10 as 0 PASS / 12 FAIL and stopped before
BCPLTIME. Investigation established that the MR10 `compile-and-run`
report extractor selected older printer reports when JES job numbers
were reused. JOB 9316 and 9317, for example, had earlier DSPALST
occurrences from 18 October 2026.

Independent read-only examination of all 12 original MVS jobs,
9316–9327, validated the interpreted completion codes and expected
BCPL output: **12/12 PASS**, with no job resubmission.

The initial coordinator result remains FAIL. Its evidence is preserved,
rather than retroactively modifying the recorded result.

### Corrective action

`tools/mr10/compile-and-run-core.py` was changed to select the latest
START occurrence for a reused JES job number and require its matching
END occurrence. It does not fall back to a completed older occurrence.

Six permanent host-side regression tests were added in
`tools/checks/test_mr10_job_number_reuse.py`: **6/6 PASS**.

The separate Stage 3 coordinator tests also passed: **8/8**.

### Fresh authorized campaign — PASS

Evidence: `workarea/project-regressions/20261104T150057Z-20210-4ej4rzal/`

Git baseline: `743c3840d7b192c5ede5ed422e77821d5b68c4c8`

- MR10 interpreted regression: 12/12 PASS.
- BCPLTIME native regression: 4/4 PASS.
- Native execution profile: `installed-r5-t1`.
- Coordinator overall result: PASS, RC=0.
- Independent evidence verification: PASS, RC=0.
- Transcript capture: RC=0.
- Bootstrap, Runtime Extensions and BCPLQSAM: NOT_SELECTED.

The campaign demonstrates a successful MR10-to-native suite transition,
preserving independent suite reports and evidence. It does not
constitute a full execution of all five suites.

The coordinator and extractor source SHA-256 values were captured
in the fresh campaign transcript and verified during this documentation
update.

**Stage 3 live integration gate: SATISFIED.**

**Owner acceptance:** Stage 3 — Independent Coordinated Regression
accepted on 4 November 2026. The accepted live campaign covers
MR10 and BCPLTIME; the other three suites remain NOT_SELECTED.
