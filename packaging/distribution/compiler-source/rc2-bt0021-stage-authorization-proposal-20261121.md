# TA.2 — BT0021 MVS preflight acceptance and owner-gated one-shot staging implementation

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.2 — Manifest-Driven Tape Producer  
**Date:** 21 November 2026 EST  
**State:** MVS read-only BT0021 preflight PASS; separately approved IEBCOPY staging NOT YET AUTHORIZED.

## Actual MVS result from owner

At GitHub main commit `83ef858ce26ef346a2b89275eeff831d85d86b45`, the owner executed:

`python3 -B packaging/distribution/compiler-source/rc2-bt0021-preflight.py --live`

The reported result was:

```text
TA.2 BT0021 READ-ONLY MVS PREFLIGHT PASS: target catalog-absent; TSO002 VTOC observed.
MVS JOBS: LISTDS 9331, IEHLIST 9332.
Hercules CODEPAGE query: response-captured-unparsed.
Original source JOB 9330: 15/15 transport-encoded members, 6577 FB80 records.
Staging NOT authorized; source encoding and rights remain qualified.
Private evidence: workarea/ta2-rc2-bt0021-preflight/20261121T051500Z-24489
TA.2 BT0021 preflight RC=0
```

The original read-only JES summaries and reports, the unparsed Hercules response and `SHA256SUMS` remain in the owner's private repository `workarea`. This report is evidence of a successful **bounded target-absence/VTOC observation**, not proof of full free space, a declared historical EBCDIC lexical contract or allocation permission. There is **no** new IEBCOPY dataset.

JOB 9330, original CAMB_SOURCE JOBS 9325/9326, BT0001–BT0020's MVS staging and inspection, the 21-dataset `BCPL-0.1.0-rc2` manifest, and the reserved `BC0002` VOLSER are unchanged.

## One-shot staging code

`rc2-bt0021-stage-once.py` implements the next stateful step but is **blocked until explicit, separately committed owner approval**. The approval file `rc2-bt0021-stage-approval.json` is intentionally absent.

The guarded runner:

1. Refuses noninteractive or modified local `main`, missing owner-approved source-byte policy or any earlier BT0021 attempt.
2. Replays the **original SHA-256-sealed JOB 9331/9332** catalog and VTOC reports, verifies exact MVS job numbers and source identities, independently replays the saved JOB 9330 source-fidelity reconciliation, and validates the exact 15-member historical-only `rc2-stage-draft.py` IEBCOPY JCL.
3. Demands a separate committed approval bound to `BCPL-0.1.0-rc2`, `BC0002`, TSO002, exactly one new `HERC02.BCPL.TA2STG.BT0021` PDS, 15 historical source members, 6,577 records, **archive-only preservation of the observed Hercules-translated FB80 bytes**, and no tape/media permission or retry. This explicitly leaves the historical Cambridge lexer byte convention unresolved and does not force CP037.
4. **Only if approved**, performs fresh read-only MVS LISTDS and IEHLIST immediately before a possible write, independently parses the bounded TSO002 free-track observation (40+10 staged-track proposal), and requires an interactive operator confirmation.
5. Writes a permanent exclusive **no-retry submission-intent marker before JES submission**, executes **one** selected-member IEBCOPY job (step `S0021`), requires exact real MVS `RC=0000`, `IEF142I` and no ABEND, then preserves the original JES reports. Any ambiguous submission or failure must be investigated without automatic resubmission. Raw authenticated JCL is never saved.
6. Distinguishes *staging-job success* from independent **new staged-PDS directory/DCB inspection** and from the later tape producer's AWS label/readback/installation gates.

All evidence remains within `workarea/ta2-rc2-bt0021-stage-operations/`; tracked source, tests, this note and milestone stay under `packaging/`.

**Assistant-workspace verification:** Python syntax compile and **16/16 focused offline unittest cases PASS** for exact original evidence identity/seal, tampering, source/owner policy, no tape permission, one-shot marker refusal, single-target JCL, exact MVS job/RC/IEF142I parsing, and denial of a stateful run without a committed approval. No actual staging JES job has been run, and synthetic tests are not represented as MVS proof.

## Explicit owner decision still required

**Proposal, NOT APPROVED:** For the **source-only archival rc2 payload**, retain the verified FB80 bytes already held in the MVS `CAMB_SOURCE` PDS, without re-translating or rewriting them, and document their observed Hercules reader mapping. The original MR10 `EBCDIC CHARACTER SET` and System/370 BCPL manual show a different historical punctuation convention; the source-only archival choice must not be misrepresented as proven lexical compatibility with a future native Cambridge Compiler.

A second, separate choice is whether to authorize **exactly one** IEBCOPY stage from `HERC02.BCPL.CAMBRIDG.SOURCE` to the otherwise absent `HERC02.BCPL.TA2STG.BT0021` on **TSO002**. The requested operation changes no other staging dataset. It does **not** authorize a tape write, release publication, source-byte rewrite, compiler execution or redistribution-rights approval. The latter remain separate unresolved release gates.

Until the owner explicitly chooses both source-byte policy and the new staging operation, the approval file is absent and the runner **must refuse `--run`**.

**TA.2 IN PROGRESS.**
