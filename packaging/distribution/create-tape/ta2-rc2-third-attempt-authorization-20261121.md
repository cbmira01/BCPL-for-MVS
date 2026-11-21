# TA.2 — One owner-approved private BC0002 candidate production after two pre-stateful refusals

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.2 — Manifest-Driven Tape Producer  
**Date:** 21 November 2026 EST  
**State:** **ONE NEW PRIVATE WRITE ATTEMPT AUTHORIZED; LIVE MVS EXECUTION PENDING.**

## Owner decision

Following the actual owner-reported `--inspect-media` **PASS (RC=0)** on 21 November 2026, the owner explicitly authorized a **single** private `BCPL-0.1.0-rc2` candidate AWS production attempt. The preserved inspection evidence is `workarea/ta2-rc2-media-inspection/20261121T222712Z-26883`. That inspection replayed both original SHA256-sealed pre-stateful failures, checked five existing AWS/HET images without any `BC0002` physical `VOL1` collision, identified the prior scratch image as `BTO001`, and reported Hercules device `0480` empty.

This owner decision is embodied in the Git-committed **`ta2-rc2-after-second-halt-approval.json`**, which binds both original refusal evidence directories and the accepted inspection report. The producer verifies its exact approved fields, original unchanged Git file, accepted inspection SHA256SUMS and reports, absence of any previous candidate AWS or permanent write-attempt marker, and a **fresh** MVS/Hercules preflight before writing.

## Exact private write boundary

- Candidate: `BCPL-0.1.0-rc2`, reserved VOLSER `BC0002`.
- New image: `mvs-state/tape/bcpl-0.1.0-rc2-BC0002.aws`, Hercules drive `0480` (MVS unit 480).
- Immutable source input set: 21 accepted `HERC02.BCPL.TA2STG.BT0001` through `BT0021` staged datasets on `TSO002`, used read-only; no restaging.
- Exactly one `TA2RC2WR` JES job with 21 ordered `BCPL.BT0001`–`BCPL.BT0021` standard-labeled tape datasets: one IEBGENER, 20 IEBCOPY, 146 curated PDS member-selection cards.
- Approved **JOB-less** generated JCL SHA-256: `85eca6f3e1e83c2d0e476f24870a20664bde2a50e2de8653606bfa351af54b4f` (unchanged by this authorization).
- Operator decisions remain two simple **`[y/N]`** prompts: initialization/mount first, and one JES submission after mounting. Any answer other than `Y`/`y` declines.
- Permanent no-retry attempt marker is created **before** reserving/initializing a new AWS image. Never retry on stateful or ambiguous failure; preserve original media and evidence.

## Additional pre-production defect correction

While inspecting the complete write path, a further definite bug was found: the first media-inventory scan and the final post-confirmation scan called `existing_media` with the **same output names**, causing an `O_EXCL` failure on the second scan even when all volumes were safe. The amended producer uses phase-qualified original evidence names (`vol-initial-*.txt`, `vol-final-*.txt`, and `vol-inspection-*.txt`) and rejects a changed count before image initialization. The approved saved incident and inspection evidence is **not modified**. Original `workarea` evidence continues to use its preserved filenames and seals.

The committed producer also mandates replay of the accepted five-image `--inspect-media` receipt: it checks the SHA256-sealed `result.json`, five original HETMAP tape reports, both original incident identities, actual `BTO001` physical VOL1, and absence of any reported BC0002 collision. A fresh live existing-media scan and fresh MVS catalog/device preflight are still required immediately before the write.

## Verification and exclusions

In the assistant's separate repository-root workspace, **14/14** isolated executable Python negative/integration checks passed for the affected functions (two-phase evidence file uniqueness, the five saved HETMAP labels, BC0002 collisions, tamper rejection and receipt binding). The Git-controlled rc2 test suite is expanded with additional tests for these safeguards. These tests are **host-only** and are not a claim of actual 21-step MVS execution. The previously accepted TA.1 and source-staging operations are left untouched.

**Not authorized:** automatic retry, media overwrite, recovery after stateful failure, independent tape restore/installation, repository source modifications on the owner's WSL machine, release publication, unresolved redistribution-rights clearance or a claim that the native-running Cambridge Compiler exists. Further steps require actual MVS/JES and independent HETMAP evidence.

**TA.2 — Manifest-Driven Tape Producer remains IN PROGRESS** until the owner-reported private candidate is verified.

## Owner-reported single stateful invocation — 21 November 2026 EST

This authorization was **consumed** by one private candidate initialization/mount and the one `TA2RC2WR` job. The runner reported **RC=2** in the subsequent HETMAP physical-file number/block-count check, **after** its 21-step JES/IEF142I RC=0000 and standard-label checks. The exclusive permanent no-retry marker and image must remain untouched. Original saved evidence: `workarea/ta2-rc2-production-operations/20261121T231644Z-27163`. The [new post-write investigation](ta2-rc2-postwrite-physical-file-review-20261121.md) does **not** authorize repeat production, media movement or installation. The original qualified write evidence awaits independent read-only review.
