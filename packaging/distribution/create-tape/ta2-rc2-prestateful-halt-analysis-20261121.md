# TA.2 — BC0002 existing-media preflight refusal and parser correction

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.2 — Manifest-Driven Tape Producer  
**Date:** 21 November 2026 EST  
**Disposition:** **Pre-stateful media preflight halted; no AWS candidate produced.**

## Owner-reported result

The approved private-build runner `scripts/ta2-rc2-produce-once --run` returned RC=2:

```text
TA.2 RC2 AWS WRITE HALTED: unrecognized/reused BC0002 volume in existing image: bcpl-objtest-20261108-01.aws
NO RETRY; preserve media, mount, attempt marker and evidence: workarea/ta2-rc2-production-operations/20261121T145906Z-26113
TA.2 RC2 private AWS build RC=2
```

The prior scratch image must remain untouched. The report identifies a **refusal**, not a verified reuse of BC0002. The owner's original HETMAP `vol-000.txt`, `failure.json` and SHA256SUMS are in the quoted private evidence directory; the assistant has not directly read those local bytes.

## Root cause in producer code

The old guard matched every `Volume Serial` in HETMAP output and required exactly one. A correctly standard-labeled tape repeats its VOLSER in `VOL1`, `HDR1` and `EOF1` records, often many times. The parser could therefore reject an unrelated, valid scratch tape.

The corrected guard locates the single initial **VOL1** label, extracts its one VOLSER, and checks other available label serials for consistency. It still refuses absent/duplicate VOL1, malformed serial fields, conflicting labels, a genuine BC0002 collision, unsafe media files or symlinks. The new code does not change the source manifests, JCL, accepted stage inputs, or earlier tapes.

The failure is in `existing_media()`, before any new candidate image creation, HETINIT, mount, permanent no-retry attempt marker, MVS catalog inquiry or JES submission. This describes the controlled execution path, not independent inspection of the owner's filesystem.

## Explicit gate after the halted invocation

A previous owner invocation terminated with NO RETRY. The updated producer therefore replays the exact original **SHA256-sealed** incident, verifies the old `vol-000.txt` reports a VOLSER other than BC0002, and checks that both the attempt marker and candidate AWS image are absent. A separate **new owner approval** must be committed as `ta2-rc2-prestateful-recovery-approval.json`, binding the incident, VOLSER, filename, and unchanged 21-dataset JCL SHA-256.

That new approval file is **intentionally absent**. Without it, the updated producer refuses any restart before performing new MVS/media operations. If the real original VOL1 serial is BC0002, or the evidence is malformed, the operation remains blocked regardless of approval.

**Assistant-workspace checks:** 73/73 isolated rc2 tests PASS, with Python AST checks. Negative tests cover invalid/duplicate VOL1, conflicting label fields, actual VOLSER reuse, sealed-evidence tampering, an existing marker and altered recovery approval. These are host-side tests, not new MVS execution.

The next owner decision is whether to authorize **one new guarded pre-stateful private BC0002 attempt**, contingent on the original evidence and fresh preflight passing. Rights, installation and publication remain outside scope. **TA.2 — Manifest-Driven Tape Producer remains IN PROGRESS.**
