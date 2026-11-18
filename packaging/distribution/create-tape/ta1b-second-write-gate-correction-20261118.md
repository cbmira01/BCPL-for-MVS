# TA.1 — Track B: second read-only tape-unit parsing failure

**Project:** BCPL for MVS 3.8 Reconstruction
**Milestone / march:** Tape artifact release / TA.1 — Multi-Dataset Tape Mechanics
**Date:** 18 November 2026, local
**Status:** Read-only guard failure; corrective source and isolated tests. No tape write evidence.

## Actual operator-supplied execution

On GitHub main `efab256a987512b9e524557293faff99f206fac2`,
the owner invoked `scripts/run-ta1-track-b-write --run` and received:

    TA.1B WRITE HALTED: MVS tape unit 480 status row missing/ambiguous
    Preserve media, dataset and receipts; do not retry, remount, overwrite or restore.
    Evidence: workarea/ta1b-operations/BTA102-track-b-write-20261118T232154Z-8887

There was no "fresh preflight PASS" or typed operator approval in
this invocation. According to the committed control flow this halt
is reached during the FIRST `unit_ready(preflight, first,
mounted=False)` check — strictly before `take_attempt()`,
`reserve_image()`, `hetinit`, mount and `submit_once()`. Thus no
new stateful BTA102 action is indicated by this transcript.
The MVS `D U,TAPE` raw output remains private in the ignored
evidence folder and has not been shared or independently read here.

## Source-supported cause

The original and previously successful `ta1b-preflight.inspect_unit`
uses `re.search` for unit `480 3400 O` or `O-NRD`
anywhere in the MVS console reply. After the first failure, the
writer's `unit_ready` check was tightened to `re.match` with
`^\s*480\s+3400`, requiring the device status to begin at the
left margin. The second owner-provided failure is consistent with
a system-message or timestamp prefix; the actual prefix and
exact observed status are NOT claimed without the private log.

The narrow correction searches *within each line* for the exact
unit `480`, device class `3400` and its status token; it counts
all matching rows and refuses none/more than one. It never scans
across newlines. Unknown/offline/allocated statuses still fail.
Before mounting it accepts `O` or `O-NRD` only when Hercules
reports empty `0:0480 3420 *`. After a confirmed BTA102 mount it
requires `O`, never `O-NRD`. Foreign media, duplicate rows
and Hercules busy status remain prohibited.

A third unknown device format will produce a bounded diagnostic
containing up to two nearby MVS unit lines (160 characters each).
Raw private console output remains in `workarea/`.

## Testing and authorization boundary

15 synthetic isolated checks executed in the assistant workspace,
including prefixed `O`/`O-NRD` rows, mounted-ready requirement,
duplicate/offline/allocated/busy refusal, foreign media and bounded
diagnostics: **15/15 PASS**. The tracked regression module is
extended by nine status-format tests (32 to 41 cases). This is NOT
live MVS verification; the next actual MVS result is authoritative.

The original owner authorization covered one new BTA102
initialization, mount and single `TA1BWRIT` IEBCOPY selected-member
unload. Both previous invocations halted before any such stateful
action; a new invocation of the corrected safety gate remains within
that scope **only if** the new AWS filename and no-retry marker
are still absent. The runner enforces these checks.

Do not auto-retry, reinitialize, remount, rewrite or restore after
an ambiguous stateful outcome. No `TA1BREST`, `TA1BGO`, cataloging
of tape datasets, or milestone acceptance is authorized or implied.
