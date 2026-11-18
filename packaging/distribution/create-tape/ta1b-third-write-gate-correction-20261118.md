# TA.1 Track B — third read-only unit-status guard correction

**Project:** BCPL for MVS 3.8 Reconstruction
**Milestone / march:** Tape artifact release / TA.1 — Multi-Dataset Tape Mechanics
**Date:** 18 November 2026 (operator-local)
**Disposition:** Pre-media, pre-JES halt. Corrected source/tests; actual Track B write pending.

## MVS observation

The owner executed the approved `run-ta1-track-b-write --run`
at GitHub `5bae753128c3f79f7e7cace74190c554a167a9a9`.
It returned `MVS tape unit 480 status row missing/ambiguous (matches=2)`,
and the bounded `observed=` diagnostic contained two exact copies of:

    23:36:00 / 480  3400 O-NRD              /REMOV 481  3400 OFFLINE

This is direct user-provided MVS output. Both copies identify
unit `480` as `O-NRD`; `481 OFFLINE` describes a *separate* unit.
The repeated line is a console/transport echo, not contradictory
unit-480 evidence.

Private local evidence remains at:
`workarea/ta1b-operations/BTA102-track-b-write-20261118T233538Z-9227/`.

## Source correction and safety

The writer stops during its FIRST read-only `unit_ready(mounted=False)`,
before operator prompts, `take_attempt`, `reserve_image`,
`hetinit`, mount or `TA1BWRIT` submission. This observed halt
did not create an AWS file or begin a stateful attempt.

The new parser collects *all* exact `480 3400` occurrences within
each guest output line. It forms a set of full raw line, occurrence
offset and status token, and requires precisely **one distinct record**.
Byte-identical echoed lines are accepted. Conflicting statuses,
different timestamps/prefixes, two entries on one line, offline and
allocated states remain hard failures with bounded diagnostics.
When 481 appears on the same physical console line, its allocation
flags are excluded from the 480 qualifier check.

Only an **empty Hercules 0:0480 3420** with MVS 480 `O` or
`O-NRD` is eligible for *initial mount*. The matching BTA102
image and `O` (not `O-NRD`) remain mandatory **after mount**.
No existing image is overwritten; the old BTA101 tape is untouched.
Any previous no-retry attempt marker or BTA102 AWS filename
must independently prevent reuse.

## Test evidence and next stage

An assistant-controlled workspace under
`BCPL-for-MVS/workarea/ta1b-unit-guard-review/`
ran **24/24 focused tests PASS** against the exact user status,
mount-stage readiness, conflicting echo/timestamps, two 480
entries, foreign media, busy/allocated, offline and unknown states,
and proper isolation of unit 481. The tracked runner regression
module was expanded from 41 to 50 test methods, including replacing
the former identical-echo rejection test. A full 50-case regression
PASS has not been claimed without running that full suite.

Owner approval already covered one virgin BTA102 initialization,
mount and selected-member IEBCOPY unload. Previous failures
reached no stateful operation. The corrected runner still performs
fresh MVS/Hercules/VOLSER/no-marker/no-file checks before any
irreversible action. If any such marker or image exists, do not retry.

**TA1BREST, restored ICINT19 GO and release acceptance are not authorized
or implied.** TA.1 remains IN PROGRESS.
