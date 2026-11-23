# TA.2 — Manifest-Driven Tape Producer: formal qualified closure and TA.3 transition

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.2 — Manifest-Driven Tape Producer  
**Owner decision:** **ACCEPTED AND CLOSED (qualified)**  
**Decision date:** 22 November 2026 EST / 23 November 2026 UTC  
**Authoritative source:** GitHub `main`  
**Next march:** **TA.3 — MVS Bootstrap and Installation: IN PROGRESS**

## Owner direction and scope

The owner explicitly directed: **"Right now: close TA2, move immediaterly to TA3. Give me a handoff prompt."** This is formal qualified closure of TA.2 based on the actual MVS/Hercules evidence below, and authorization to begin the **TA.3 — MVS Bootstrap and Installation** march. TA.2 is not to be reopened for procedural paperwork, repeated proof, or new administrative gates; reopen only on a demonstrated defect affecting the accepted tape producer or candidate.

TA.3 must prove a recipient can bootstrap and install the scoped **Cambridge BCPL Programming System for MVS 3.8J** using the published-on-tape MVS facilities, with no development-side Git/WSL/Python/`dspal` dependency. This transition does **not** itself authorize rewriting `BC0003`, overwriting existing recipient datasets, deleting evidence, publishing a release, or executing a newly destructive installation without appropriate operating safeguards.

## Accepted TA.2 candidate and original evidence

- **Candidate:** `BCPL-0.1.0-rc3`; VOLSER `BC0003`; immutable AWS `mvs-state/tape/bcpl-0.1.0-rc3-BC0003.aws`.
- **AWS SHA-256:** `6c54c4df2b75020a698110061c4f8003b09adbe21f738848dcaed3da495d81e1`.
- **Release manifest:** 21 contiguous logical standard-labeled `BCPL.BT0001`–`BCPL.BT0021` datasets; 146 selected PDS members; independent HETMAP audit found 21 label sets and 64 physical files.
- **Source revision:** `e910de51c19c09698be139e33084a90401511cc9`; manifest SHA-256 `b130e4a246cecb6d810f45febd945e3ed0e854164e83012899c86c730f365486`.
- **JOBS 9359/9360:** read-only source/target preflight PASS, then 21 new staging datasets plus 16 updated distribution members PASS (qualified).
- **JOB 9361:** 21-position AWS write and independent HETMAP verification PASS (qualified). MVS automatically demounted the volume after the final write, which caused a false alarm in the original runner, **not** a write failure.
- **JOBS 9362/9363:** recipient-absence preflight PASS followed by direct tape readback to 21 new `HERC02.BCPL.TA2R3I.*` datasets, all 21 IEBGENER/IEBCOPY steps RC=0000.
- **JOBS 9365/9366:** initial DCB investigation identified a verifier-only prefix collision (`BOOT` versus `BOOT.JCL`); actual `LISTDS MEMBERS` verified 146 selected PDS members across the 20 restored PDS directories.
- **JOBS 9367/9368:** corrected exact-dataset-name MVS `LISTDS LABEL` 21/21 DCB/volume PASS (including the actual PS bootstrap), and independent `LISTDS MEMBERS` 146/146 PASS.
- **JOB 9369:** installed MR10 `TA2R3MR` 63/63 ordered MVS JES/IEF142I steps RC0000, 12/12 printed `TEST:`, literal `EXP:`, computed `RP:`, interpreted `CODE=0` semantic comparisons PASS (qualified).

These statements are grounded in owner-supplied actual MVS runner output and tracked acceptance ledgers; private original JES reports have not been exported to the assistant. Immutable source evidence remains within the operator's repository `workarea/`:

- `workarea/ta2-rc3-consolidated/20261122T202323Z-30995`
- `workarea/ta2-rc3-restore-continuation/20261122T232532Z-31994`
- `workarea/ta2-rc3-recipient-diagnostic/20261122T234725Z-32362`
- `workarea/ta2-rc3-installed-mr10-continuation/20261123T000015Z-32502`

The production, restoration, and installed-regression one-shot markers are consumed. Preserve all accepted media, source datasets, recipients, receipts, and JES output; **do not rerun** their stateful operations.

## Human case-review observation and qualification

The owner subsequently displayed all 12 actual JOB 9369 test cases, entered `p` (PASS) for R01–R12, supplied reviewer identifier `cm`, and entered lowercase `sign`. The optional `ta2-rc3-human-review --signoff` helper erroneously rejected the lowercase confirmation, so **no sealed human sign-off receipt was produced by that invocation**. This operator-provided 12-case PASS transcript is preserved in the conversation; do not make the user repeat the review to close TA.2. The separate TA.4 human-review record and full TA.4 demonstration/rebuild gates remain governed by TA.4; they are **not** retroactive conditions on the TA.2 producer closure.

## Qualifications retained on closure

TA.2's producer, immutable tape structure and current-system MVS readback/installed-use evidence are accepted **qualified**. TA.2 closure does **not** establish:

- Independent **TA.3 — MVS Bootstrap and Installation** from `BT0001`/`BT0002` using MVS-only recipient procedures, site-specific HLQ, allocation/overwrite rules, and independently selectable profiles.
- Full **TA.4 — MR10 Kit Compiler Distribution and Verification**, including the 11 language demonstrations, 17 BCPL demonstrations, source rebuild, and any remaining formal human-evidence disposition.
- **TA.5 — Native Runtime, Libraries, and Extensions Distribution** source rebuild/link/execute and optional-link behavior from the release.
- **TA.7 — Clean-Target Integration and Release Acceptance** on an isolated clean system.
- Complete redistribution/provenance rights review or **TA.8 — Release Audit and Controlled Publication**.
- A runnable native Cambridge Compiler: the candidate declares `native_compiler: absent`; the corresponding TA.6 candidate gate is **N/A**, not PASS.

The current scoped release may omit the native Cambridge Compiler under the approved no-native-compiler release decision; never represent interpreter-hosted Cambridge sources or `CAMBCOMP` as a working native compiler.

## Formal disposition

**TA.2 — Manifest-Driven Tape Producer: CLOSED (qualified), by explicit owner direction.**

**TA.3 — MVS Bootstrap and Installation: IN PROGRESS.** Begin with the frozen `BC0003` artifact and approved manifest. Read the [TA.3 kickoff](ta3-kickoff-20261122.md) and original [milestone](milestone-tape-artifact-release.md) before changes. Orient work toward actual BCPL, IFOX, IEWL, IEBCOPY and MVS execution, minimizing host-side bureaucracy and avoiding redundant tests or owner confirmations.

No new branch, tape rewrite, deletion, destructive cleanup or release publication is approved by this record.
