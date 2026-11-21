# TA.2 — RC2 two-incident media inventory PASS (qualified)

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.2 — Manifest-Driven Tape Producer  
**Date:** 21 November 2026 EST (original private evidence timestamp 22:27:12 UTC)  
**Status:** **Read-only existing-media inventory PASS (qualified); private candidate AWS write NOT yet performed.**

## Owner-reported actual Hercules/MVS-facing result

The owner executed the committed read-only `scripts/ta2-rc2-produce-once --inspect-media` using GitHub `main` after the correction at `964f306555ffe780bf142029a60d3cc11c21a652`:

```text
TA.2 RC2 READ-ONLY MEDIA REVIEW PASS: 2 sealed preflight halts; original VOL1 BTO001; 5 existing images; drive 0480 empty.
Private evidence: workarea/ta2-rc2-media-inspection/20261121T222712Z-26883
No tape/media/JES changes; another private write needs separate owner approval.
TA.2 RC2 media inspection RC=0
```

The initial `TA.2 RC2 build RC=2` displayed just before this transcript refers to the earlier halted write invocation, not a new MVS tape-production attempt.

The reviewer executed **read-only** HETMAP `-l` on five existing images, replayed the original two SHA256-sealed pre-stateful refusal receipts, and queried the Hercules device state and MVS `D U,TAPE`. It reported that the physical `VOL1` of the previously troublesome `bcpl-objtest-20261108-01.aws` is **BTO001**, not the reserved production VOLSER **BC0002**. The owner-reported empty drive state is **0480**. The script required no candidate AWS file or permanent write-attempt marker to exist.

**Qualification:** The assistant has reviewed the committed verifier and the owner's exact terminal result, not the private HETMAP files, device reports, SHA256SUMS or result.json bytes. The evidence is owner-local under ignored `workarea/`. This PASS establishes the bounded read-only inventory gate at its execution time; it does **not** establish future drive availability, MVS catalog alias absence, 21-step write success, member-byte fidelity, or clean-target installation.

## Next controlled production gate

The original approved private release candidate is unchanged:

- Candidate `BCPL-0.1.0-rc2`, volume `BC0002`, image `mvs-state/tape/bcpl-0.1.0-rc2-BC0002.aws`, Hercules `0480`.
- Frozen JOB-less `TA2RC2WR` JCL SHA-256: `85eca6f3e1e83c2d0e476f24870a20664bde2a50e2de8653606bfa351af54b4f`.
- One `IEBGENER`, 20 `IEBCOPY` steps, 21 SL logical tape datasets, 146 selected PDS member cards, from the already accepted staged input PDSes and bootstrap source.
- Two separate `[y/N]` operator confirmations; exclusive no-retry intent marker before image creation; fresh HETMAP media collision, Hercules/MVS drive and MVS catalog absence checks; independent HETMAP and JES results after a write.

**A third private write invocation has NOT been owner-authorized.** The Git-committed writer deliberately refuses `--run` without the absent, incident-specific `packaging/distribution/create-tape/ta2-rc2-after-second-halt-approval.json`. Do not repurpose either prior approval, rerun the stage operations, or submit an MVS write merely because this read-only check passed. When the owner authorizes the exact third attempt, commit the new approval, rerun own-workspace focused tests, then perform the one guarded MVS-facing operation once.

**TA.2 — Manifest-Driven Tape Producer IN PROGRESS.** Publication, archive-source rights decisions, clean-target restore, and native Cambridge Compiler claims are outside this PASS.

## Subsequent owner approval and guarded production repair — 21 November 2026 EST

After accepting this **qualified read-only inspection PASS**, the owner authorized **one** new private `BC0002` production attempt. [The explicit third-attempt record](ta2-rc2-third-attempt-authorization-20261121.md) binds this sealed inspection evidence, both original pre-stateful failures and the frozen JCL hash to the new Git-committed authorization, without changing accepted source datasets or previous tapes. The producer's repeated-media-scan evidence collision was independently found and corrected before execution. The actual candidate write is still pending MVS/JES results.
