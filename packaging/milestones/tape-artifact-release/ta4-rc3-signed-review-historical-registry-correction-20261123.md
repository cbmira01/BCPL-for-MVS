# TA.4 — RC3 signed-review historical registry compatibility correction

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.4 — MR10 Kit Compiler Distribution and Verification  
**Date:** 23 November 2026 EST  
**Status:** Tested source correction; human sign-off still **PENDING**  
**Predecessor:** RC4 TA.4 MVS rebuild, SCALVEC, 11 language and 17 BCPL demos PASS (qualified)  
**Preserved MVS regression:** RC3 **JOB 9369**, 63 steps, 12 cases `TEST:/EXP:/RP:/CODE=0` PASS

## Owner-reported pre-signature refusal

```text
RC3 HUMAN REVIEW REFUSED: RC3 registry reservation or manifest checksum changed
```

This occurred **before** the reviewer displayed the twelve cases or asked
for an identified signature. No new signed receipt was reported. The
original installed-job evidence, `BC0003` and `BC0004` remain accepted
and must not be replayed or overwritten for administrative sign-off.

## Diagnosis

The existing `ta2-rc3-human-review.accepted()` called the historical
tape **producer's** `ta2-rc3-consolidated.plan()` solely to reconstruct
the 12-case source selection and `MRREGRES` JCL. That original producer
requires `len(registry.candidates) == 3` and RC3 to be the last registry
entry. The current authoritative append-only release registry correctly
contains four candidates: RC1, RC2, RC3 and the later accepted RC4.
Consequently, historical sign-off was refused by a legitimate registry
extension, **not by demonstrated corruption**.

GitHub `main` manifest content was independently SHA-256 checked before
this correction. RC3 registered/actual digest:
`b130e4a246cecb6d810f45febd945e3ed0e854164e83012899c86c730f365486`.
RC4 registered/actual digest:
`72c241201a95953546923f62ea6bfb43fcf56349c5ec7618671d7802d2ee6c1a`.

## Narrow correction

The signed-review script now uses a dedicated **read-only**
`historical_regression_plan()` that reconstructs the original canonical
12-source `MRREGRES` job body without invoking the production plan.
It requires:

- Exact original RC2→RC3 manifest identity, 21-dataset selection,
  candidate source-commit and `BC0003` identity.
- Exact **third registry entry** for RC3, including the recomputed
  original RC3 manifest SHA-256, plus unique candidate IDs and VOLSERs.
- Later entries only **after** RC3, with separate verified manifest
  SHA-256, candidate ID, version, source-commit, VOLSER and reservation.
- Twelve canonical BCPL source selections and precisely retargeted
  installed `MRREGRES` JCL using the original builder.
- The original unchanged acceptance checks: sealed saved MVS JES/semantic
  reports, exact JOB 9369 63-step `IEF142I`, full 12-case
  `TEST:/EXP:/RP:/CODE=0`, preserved AWS SHA-256 and original one-shot
  marker, followed by explicit identified human verdicts and literal `SIGN`.

The legacy **RC3 production planner is unchanged** and retains its own
strict one-shot reservation checks. The compact one-response
sign-off remains optional, and the previous per-case mode is unchanged.

## Local verification

The assistant performed **7/7 focused Python execution tests**
against an isolated in-repository fixture: existing RC3/RC4 append
acceptance and legacy three-entry acceptance passed; deliberate
RC3 manifest-checksum alteration, RC4 manifest alteration,
duplicate `BC0003` VOLSER, RC3 dataset drift and missing RC4
manifest all refused as required. The updated tracked regression test
module also covers these cases. No user checkout, MVS job, AWS image,
accepted PDS, historical seal or existing sign-off was modified.

## Acceptance boundary

This commit is a **reviewer repair**, not a human signature and
not formal TA.4 closure. The signed 12-case human receipt must still
be produced by an identified reviewer and reported for formal
owner acceptance. A human FAIL blocks the release; publication
authorization remains false. No accepted MVS execution is to be repeated.
