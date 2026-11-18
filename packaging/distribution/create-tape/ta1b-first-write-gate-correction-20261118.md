# TA.1 — Track B first approved write invocation: read-only gate correction

**Project:** BCPL for MVS 3.8 Reconstruction
**Milestone:** Tape artifact release
**March:** TA.1 — Multi-Dataset Tape Mechanics
**Date:** 18 November 2026 (operator-local)
**Status:** First approved write invocation halted during read-only unit preflight; **no BTA102 media initialization or production JES submission observed**.

## Owner-provided evidence

The owner previously executed `ta1b-preflight --live` on GitHub
`eb0a26e489255e43a1bdc5089589dc53fa8347a0`; result PASS:
source `MR10_LOAD(ICINT19)` PO/U/0/6144 on TSO003;
BTA102 path absent and unused among four inspected tape images;
Hercules 0480 EMPTY; both proposed catalog names absent.

The owner then explicitly authorized exactly ONE fresh BTA102 image
initialization, mount on Hercules 0480, and `TA1BWRIT` IEBCOPY unload.
Invoking the guarded runner at GitHub
`51c56b326fc48a1f47d9e4b19101f0694f333387` produced:

    TA.1B WRITE HALTED: MVS tape unit 480 is not unambiguously online/ready
    Preserve media, dataset and receipts; do not retry, remount, overwrite or restore.
    Evidence: workarea/ta1b-operations/BTA102-track-b-write-20261118T205215Z-8283

No "fresh preflight PASS" or operator confirmation followed this.
The actual `D U,TAPE` row is in the owner's ignored private evidence
and was NOT supplied in the conversation.

## Root cause in reviewed source

`run-ta1-track-b-write` calls `unit_ready(..., mounted=False)`
in its FIRST read-only preflight; only after this first guard and a
second preflight does it call `take_attempt()`, `reserve_image()`,
`hetinit`, mount, then authenticated TA1BWRIT.

The original `ta1b-preflight.inspect_unit` accepts `O` or `O-NRD`
while the write runner required `O` exclusively on the EMPTY device.
IBM MVS `DISPLAY U` recognizes `NRD` as *not ready*, which can be
normal for an online tape unit without mounted media. The precise
owner-local status row remains unknown, so this is a code-supported
probable cause, **not an invented MVS observation**.

A strict fix distinguishes phases:

- BEFORE mount: require Hercules `0:0480 3420 *`, exactly one MVS
  unit 480/3400 status row, `O` or `O-NRD`, and no busy/allocated
  indication. Do not treat `O-NRD` as ready for tape I/O.
- AFTER mount: require the exact BTA102 image in Hercules, the
  single MVS row and **`O` only**. Refuse `O-NRD`, offline, unknown
  and allocated status. Never submit JES until this is satisfied.
- Preserve both live-preflight rounds before the attempt receipt;
  never overwrite an existing image, silently retry a stateful step,
  remount an old tape or catalog the logical tape dataset.
- If the actual guest status has some other meaning, the new guard
  prints the observed concise status row and stops before media changes.

The previous run reached neither `take_attempt()` nor
`reserve_image()`. Therefore it is safe to invoke the **corrected
guard** under the already-approved original operation scope, only
if its fresh no-marker/no-image and MVS/Hercules checks pass. This
does not permit repeating a real tape initialization or job attempt.

## Verification and next evidence

11 focused isolated test cases PASS for the exact amended
`unit_ready()` logic, including empty O-NRD acceptance, mounted O-NRD
rejection, foreign image rejection, offline/allocated/busy rejection,
duplicate/unknown status refusal, and both ordinary O cases. The
source-controlled writer regression suite has been extended from 27
to 32 cases; actual live execution remains the MVS authority.

The next permitted live stage is STILL ONLY virgin BTA102 creation,
mount on 0480 and one TA1BWRIT, followed by read-only JES/hetmap
inspection. No `TA1BREST`, `TA1BGO`, load-library catalog, remount
or release acceptance is authorized by this correction.
