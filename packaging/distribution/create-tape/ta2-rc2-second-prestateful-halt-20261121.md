# TA.2 — Second BC0002 pre-stateful halt; physical VOL1 correction

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.2 — Manifest-Driven Tape Producer  
**Date:** 21 November 2026 EST  
**State:** **Second private producer invocation halted before media creation; incident investigation and code correction implemented; read-only MVS/Hercules verification pending.**

## Owner-reported MVS/Hercules result

On GitHub `main` `432eefdf66eaa36af605367a049057994fec8dbf`, after pulling the new Y/N prompt implementation, the owner invoked `ta2-rc2-produce-once --run` and reported:

```text
TA.2 RC2 AWS WRITE HALTED: HETMAP label contradicts physical VOL1 serial: HDR1
NO RETRY; preserve media, mount, attempt marker and evidence: workarea/ta2-rc2-production-operations/20261121T155143Z-26237
TA.2 RC2 build RC=2
```

The earlier `20261121T145906Z-26113` refusal was also displayed by the owner in the same message. These are **two separate pre-stateful runs**, not evidence of two image writes. The second failure originated during `existing_media()`, before the permanent attempt marker, HETINIT, mount, MVS catalog inquiry, or JES submission, based on the reviewed code path. The original private HETMAP reports have not been independently inspected by the assistant.

## Defect boundary and correction

The second guard incorrectly compared `HDR1` and `EOF1` data-set serial fields to `VOL1` as a precondition for checking **existing physical tape-volume VOLSER collisions**. `VOL1` identifies the physical volume; the `HDR1`/`EOF1` serial fields have separate data-set semantics, and an existing scratch image can contain different or dummy values. See IBM's documentation for the *standard volume label (VOL1)* and *standard data set label 1 (HDR1/EOV1/EOF1)*, and the Hercules HETMAP User Reference Guide.

The corrected collision guard identifies exactly one initial physical `VOL1` and requires its six-or-fewer-character serial, refusing missing, duplicate, or displaced `VOL1`. It does **not** interpret `HDR1` as another physical volume label. A `BC0002` in physical `VOL1` still refuses. Separate **new-candidate** independent HETMAP review continues to validate `HDR1`/`EOF1` DSN, sequence, VOLSER, physical-file structure and nonempty payloads. No stage data, tape image or release JCL is changed by this correction.

## Consolidated read-only review

`scripts/ta2-rc2-produce-once --inspect-media` is a new **read-only** path. It replays SHA256-sealed original reports and expected failure receipts from **both** owner-reported halted runs; checks the reserved candidate image and permanent no-retry marker are still absent; checks that the physical VOL1 of the original existing image agrees across the two reports and is not `BC0002`; queries all existing `.aws`/`.het` files through Hercules `hetmap -l` for true physical VOLSER collisions; and uses Hercules DEVLIST and guest MVS `D U,TAPE` to verify drive 0480 is empty and safe for a future separately authorized attempt. It writes sealed evidence only under `workarea/ta2-rc2-media-inspection/` and prints a compact PASS or refusal. **No MVS job, tape mount, initialization, image write, or restore is performed.**

Both original refusals and their evidence must remain intact. The old owner authorization applies only to the exhausted second invocation. The producer is now hard-gated by a **separate, not-yet-present** `ta2-rc2-after-second-halt-approval.json` before a third stateful invocation can even begin. No automatic retries or bypass if either incident/evidence goes missing.

**Assistant workspace:** Python AST checks and **82/82 combined focused rc2 offline tests PASS**, including inconsistent HDR1/data-set serial, true physical BC0002 collision, both sealed incident replays, tampering, absence of a marker/image, read-only inspection PASS and refusal paths. These tests are synthetic; actual owner-local reports and live MVS console results remain the next source of acceptance evidence.

**TA.2 — Manifest-Driven Tape Producer remains IN PROGRESS.** No publication, source-rights clearance, restore or clean-target installation is authorized.
