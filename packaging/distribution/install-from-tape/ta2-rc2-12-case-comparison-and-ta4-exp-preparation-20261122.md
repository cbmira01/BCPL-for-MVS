# TA.2 — BC0002 installed MR10 results and TA.4 EXP source preparation

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**Current march:** TA.2 — Manifest-Driven Tape Producer (IN PROGRESS)  
**Subsequent applicable acceptance:** TA.4 — MR10 Kit Compiler Distribution and Verification  
**Date:** 22 November 2026  
**Status:** Recorded owner-reported MVS success; proposed source enhancement validated offline; MVS retest of enhancement pending.

## Real MVS checkpoint

The owner reported a single successful consolidated **BCPL-0.1.0-rc2 / BC0002** install-and-use operation:

- Readback: **JOB 9343** restored all 21 standard-label logical datasets, 21/21 RC=0000; original AWS SHA unchanged.
- Preflight: **JOB 9344** passed 21/21 restored DCBs and observed 21 installation targets absent.
- Installation: **JOB 9345** created 21 new `HERC02.BCPL.TA2INS.*` datasets on TSO002.
- Installed MR10 regression: **JOB 9346** completed the 63-step compilation/generation/execution JCL, with all 12 `R01`–`R12` MVS steps RC=0000.
- Saved-report semantic review: each **R01–R12 GOLDEN/CODE MATCH**, every case's `RP:` values matched tracked golden records in order and each interpreted completion was `CODE=0`. The reviewer reported **EXP ABSENT** in all 12 cases, `GOLDEN_RP_CODE_MATCH_EXP_REQUIRED`, **RC=0**. **This is a successful diagnostic RP/CODE comparison, not TA.4 sign-off.**

Original private evidence (unmodified):

- `workarea/ta2-rc2-install-acceptance/20261122T133139Z-29894`
- `workarea/ta2-rc2-install-acceptance/review-20261122T134121Z-30250`

These paths were reported by the owner; this record does not claim independent access to that WSL evidence.

## Approved TA.4 display contract implemented in canonical BCPL source

The 16 November 2026 owner-approved `EXP:` / human-inspection contract requires fixed, predetermined expected output **in the BCPL program's own MVS report**, distinct from its computed `RP:` lines, with a reviewer-signed disposition for every case. No MVS-resident automatic semantic comparator is required.

This change adds **23 literal `WRITEF("EXP: ...*N")` lines across the existing 12 canonical regression BCPL programs**, immediately following their `TEST:` line and before the original evaluated output. The new text is derived verbatim from the separately maintained `.expected` golden records, changing only the `RP:` prefix to `EXP:`. It contains no BCPL expressions or format placeholders. It does **not** change the `RP:` computations, test cases, manifest, golden files, standard `MRREGRES` JCL, or WSL `run-regression-panel` comparison logic.

The new read-only `packaging/distribution/install-from-tape/scripts/mr10-exp-source-check` enforces this mapping, 12-case MVS JCL order, `CODE=0` manifest expectations, and FB80 source-card limits. Isolated test/negative checks were run in the assistant's repository workspace. **Actual BCPL compile-and-run verification of these modifications is still required.**

## Release boundary and next acceptance

**BC0002 and its installed datasets contain the previous sources without `EXP:`.** Editing GitHub source does not retroactively change the frozen, checksummed AWS image, staging datasets, restored datasets or MVS JOB 9346. Do not rerun the one-shot readback or installation, modify the media, or relabel the candidate as `EXP:`-compliant.

The next controlled MVS-facing verification is to run the existing 12-case WSL `tools/mr10/run-regression-panel` against these new Git-controlled BCPL sources, expecting 12 automatic `RP:`/`CODE=0` PASS. A subsequent separately governed producer/recipient candidate must include the new source bytes and produce all 12 `TEST:`/`EXP:`/`RP:`/`CODE=` records on recipient MVS; that is when human per-case review and final TA.4/TA.7 acceptance can be considered. No new candidate identifier, VOLSER, tape-write operation, installation attempt or publication is authorized by this record.

**TA.2 remains IN PROGRESS, and TA.3–TA.8 remain governed by their original acceptance gates.**
