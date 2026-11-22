# TA.2 — BC0002 consolidated restore, installation and usage acceptance

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.2 — Manifest-Driven Tape Producer  
**Candidate:** `BCPL-0.1.0-rc2`; standard-label AWS `BC0002`  
**Status:** Implementation and local guards complete; actual MVS install not executed.

## Evidence and limits

The owner-reported `TA2RC2RB` JOB **9343** completed the 21 tape-to-TSO002 restoration steps at RC=0000. This establishes a qualified readback checkpoint, **not** independent installation, binary equality, semantic MR10 acceptance or publication. The original `BC0002` AWS, original staging and JOB 9343 data must remain unchanged. The new runner replays the saved immutable readback receipt; its read-only MVS preflight verifies all 21 restored DCBs and 21 absent installation targets with TSO `LISTDS LABEL`, retaining the complete JES report.

## One operator procedure

`packaging/distribution/install-from-tape/scripts/ta2-rc2-acceptance` uses exactly one entry point:

- Default: offline manifest/JCL preview and saved-readback evidence validation.
- `--live`: **one read-only** MVS `LISTDS LABEL` inquiry, no allocation or tape operation.
- `--run`: one owner-approved, guarded attempt, with a single interactive `[y/N]`. The operator's explicit `Y` is the stateful authorization; no separate Git approval file is needed. A refusal or any response other than `Y` does not consume the one-shot attempt.

For the proposed stateful operation, the runner creates **21 new** `HERC02.BCPL.TA2INS.*` datasets on `TSO002` from the already restored `HERC02.BCPL.TA2RB.BT0001`–`BT0021`: one `IEBGENER` PS copy and twenty `IEBCOPY` PDS copies. Destination names derive from the frozen release manifest. Every output uses `DISP=(NEW,CATLG,DELETE)`; `BT0012` preserves `PO/U/0/6144`. It then submits the original canonical 63-step `MRREGRES` JCL **retargeted exclusively to the new installed MR10 datasets**. The 12 interpreted `R01`–`R12` execution steps must be present at RC=0000. No existing development, staging, readback or installed dataset is an output; the runner never initializes, mounts, unmounts, positions or writes tape.

Each operation saves MVS JES reports and SHA-256-sealed evidence under `workarea/ta2-rc2-install-acceptance/`. A durable exclusive one-shot invocation marker is created **only after** the operator enters `Y` and before the first installation JCL submission; it prevents any unattended retry. The operator must preserve partial allocations and diagnostics after a failure and authorize any recovery separately.

## Acceptance semantics

**JES success is not BCPL semantic success.** A passing MRREGRES job proves the installed interpreter can fetch and run the compiler/runtime pipeline and the 12 cases reached their execution steps. The owner-approved `EXP:`/`RP:`/`CODE=` **human per-case review and sign-off** remain separate mandatory acceptance under TA.4 and TA.7. The current RC2 advertises `native_compiler: absent`; the Cambridge Compiler's distributed historical sources are **not** a working native source compiler. This procedure is an isolated installation *pilot* on the existing MVS, not yet the TA.3 fresh-recipient installation or TA.7 clean-target proof.

## Verification and authorization

Locally, `test_ta2_rc2_acceptance.py` passes **16/16 synthetic/negative tests** (37/37 across the install-from-tape suite) and the Python entry point compiles. The JCL planner was checked for 21 position mapping, unique new DSNs, 80-column cards/71-column operands, one RECFM=U load library, no input tape operations, and exactly 63 MRREGRES steps / 12 execution cases. There is no observed recipient MVS result from this new procedure yet. **The `--run` prompt expressly identifies the 21 new `TA2INS` datasets and one MRREGRES execution. An explicit `Y` authorizes that single installation-and-regression attempt; `N` leaves the installation unstarted and the one-shot marker absent.** No other scope or publication is implicitly authorized.

## Follow-up — blocked first invocation and operator-consent fix

The owner attempted the consolidated `--run` command and observed
`TA.2 RC2 acceptance REFUSED: --run CLOSED: separate owner approval for TA2INS allocations is missing`,
RC=2. This refusal occurred before any JES inquiry, MVS allocation,
installation or one-shot intent marker. The extra file gate was redundant
with the intended one-command, one-confirmation operator contract.

The revised runner retains a 42-dataset MVS LISTDS safety preflight and
the immutable JOB 9343 readback receipt, then prompts once. It writes the
exclusive no-retry intent marker **after an explicit Y**, just before
submitting `TA2INST`. The unchanged successful path remains 21 newly
allocated datasets and a single 63-step canonical MRREGRES job; accepted
outputs still require 12-case manual `EXP:/RP:/CODE=` review. The
37/37 local install-from-tape tests (16 in the acceptance module) passed;
new consent/decline and one-shot guards were exercised synthetically.
No claim of a new MVS JOB or semantic PASS is made by this fix.

## Owner-reported consolidated MVS outcome and saved semantic review

22 November 2026: the owner reported `--run` RC=0: JOB **9344** (21/21 restored DCBs; 21 new installation targets absent), **9345** (21 dataset installation copies successful), and **9346** (`MRREGRES`, installed MR10, 12/12 interpreted execution steps at MVS RC=0000). Evidence: `workarea/ta2-rc2-install-acceptance/20261122T133139Z-29894`. The results prove a qualified isolated installation-and-usage checkpoint; they do not themselves establish case-by-case BCPL result equality or all release requirements.

`--review`, on the **same** `ta2-rc2-acceptance` command, now reads and validates the original sealed evidence without touching MVS or repeating any job. Its ordered 12-case `TEST:`/`RP:` and interpreted `CODE=` comparison uses the canonical manifest, BCPL sources and `.expected` golden files. Output is a separate sealed JSON review record. This diagnostic check cannot replace the owner-approved `EXP:` + actual `RP:` display and human disposition: the present BCPL regression sources contain no `EXP:` lines. All 14 new synthetic reviewer tests passed; actual JOB 9346 semantics are pending review of its saved report. No publication or TA.3/TA.7 acceptance is implied.
