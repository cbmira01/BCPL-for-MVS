# TA.2 — BT0021 read-only MVS preflight and encoding gate

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.2 — Manifest-Driven Tape Producer  
**Date:** 20 November 2026  
**Status:** Read-only tool implemented and locally tested; actual MVS read-only results pending. No staging/tape authorization.

## Accepted facts retained

- The canonical release is `BCPL-0.1.0-rc2`, VOLSER `BC0002`, 21 logical tape datasets; `BT0021` carries only 15 original historical Cambridge source members. `native_compiler: absent` remains true.
- The original `HERC02.BCPL.CAMBRIDG.SOURCE` PDS is accepted after MVS population JOBs **9325/9326**, directory verification and QSAM JOB **9330** (15/15 EBCDIC-reader-profile reconciled FB80 members, 6,577 records). Literal CP037 matches remain 7/15; the historical BCPL language's lexical encoding is not settled.
- `BT0001`–`BT0020` staging and MVS verification are accepted. Neither accepted staging nor the existing source PDS should be recreated.
- The proposed `BT0021` stage destination is **`HERC02.BCPL.TA2STG.BT0021`**, on **TSO002**. The approved release manifest has not yet been extended with an encoding policy, and this decision still requires owner review.

## Read-only preflight implementation

`rc2-bt0021-preflight.py --live`:

1. Reuses `rc2-cambsource-readiness.py` and `rc2-stage-draft.py` to validate frozen original source paths, source-only manifest selection, exact 15-member selective IEBCOPY stage layout and the `BC0002` reservation. The JCL stage draft is **not submitted**.
2. Replays the original JOB 9330 saved JES summary, complete job report and original failure receipt using the previously accepted QSAM and transport-reconciliation routines. Demands the existing, independently saved 15/15 reconciled source receipt, including 6,577 records, 7/15 CP037 and the three observed reader mappings. There is no repeat of the accepted source population or QSAM inquiry.
3. Submits **one read-only MVS LISTDS inquiry** and demands positive catalog absence for only the one `BT0021` DSN.
4. Submits **one read-only MVS IEHLIST LISTVTOC inquiry** for TSO002 and refuses any evidence of an uncataloged `BT0021` target; no numerical free-space acceptance is inferred from simply printing the VTOC.
5. Tries a **no-operand Hercules `codepage` operator-panel query** through the running emulator's existing localhost HTTP interface. Saves the actual response as received without inferring that it establishes a specific mapping. Failure of this supplementary query is recorded as *unavailable*, not silently reported as success, and does not nullify independently successful MVS checks.
6. Retains fresh original JES summaries and reports and a SHA-256-sealed receipt only in a new, exclusive run directory under `workarea/ta2-rc2-bt0021-preflight/`. Reports minimal console text and exact MVS job IDs. Any uncertain MVS result stops processing without retrying its job.

**Out of scope:** changing source bytes, CP037 normalization, Hercules codepage changes, creating `BT0021`, production of the AWS `BC0002` image, changing `BT0001`–`BT0020`, installing a compiler, rights approval, or source lexical correctness claims.

## Tests and next decision

**15/15 focused offline tests pass** in the assistant workspace. They cover the original evidence-identity guard, tampered receipt and encoding refusal, unsafe evidence paths, catalog absence/contradiction, 15 historical selected sources, two read-only MVS jobs with expected maximum RCs, evidence sealing/no overwrite and the Hercules diagnostic response and failure paths. Python syntax compilation also passes. These tests do not substitute for the upcoming **actual MVS** LISTDS/IEHLIST jobs or a live Hercules observation.

After actual live preflight results, review the exact MVS/VTOC evidence, then make the separate encoding-policy and one-shot `BT0021` staging decision. Preserve the accepted native MVS source records pending that decision; do not force CP037 merely to satisfy an earlier host comparison. Rights and public release remain independent, explicitly unresolved gates. **TA.2 IN PROGRESS.**
