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
- `--run`: one owner-approved, guarded attempt, with a single interactive `[y/N]`; refuses without a separate exact Git-committed `ta2-rc2-install-execution-approval.json`. **This execution approval has not yet been given or committed.**

For the proposed stateful operation, the runner creates **21 new** `HERC02.BCPL.TA2INS.*` datasets on `TSO002` from the already restored `HERC02.BCPL.TA2RB.BT0001`–`BT0021`: one `IEBGENER` PS copy and twenty `IEBCOPY` PDS copies. Destination names derive from the frozen release manifest. Every output uses `DISP=(NEW,CATLG,DELETE)`; `BT0012` preserves `PO/U/0/6144`. It then submits the original canonical 63-step `MRREGRES` JCL **retargeted exclusively to the new installed MR10 datasets**. The 12 interpreted `R01`–`R12` execution steps must be present at RC=0000. No existing development, staging, readback or installed dataset is an output; the runner never initializes, mounts, unmounts, positions or writes tape.

Each operation saves MVS JES reports and SHA-256-sealed evidence under `workarea/ta2-rc2-install-acceptance/`. A durable exclusive invocation marker prevents an unattended retry. The operator must preserve partial allocations and diagnostics after a failure and authorize any recovery separately.

## Acceptance semantics

**JES success is not BCPL semantic success.** A passing MRREGRES job proves the installed interpreter can fetch and run the compiler/runtime pipeline and the 12 cases reached their execution steps. The owner-approved `EXP:`/`RP:`/`CODE=` **human per-case review and sign-off** remain separate mandatory acceptance under TA.4 and TA.7. The current RC2 advertises `native_compiler: absent`; the Cambridge Compiler's distributed historical sources are **not** a working native source compiler. This procedure is an isolated installation *pilot* on the existing MVS, not yet the TA.3 fresh-recipient installation or TA.7 clean-target proof.

## Verification and authorization

Locally, `test_ta2_rc2_acceptance.py` passes **14/14 synthetic/negative tests** and the Python entry point compiles. The JCL planner was checked for 21 position mapping, unique new DSNs, 80-column cards/71-column operands, one RECFM=U load library, no input tape operations, and exactly 63 MRREGRES steps / 12 execution cases. There is no observed recipient MVS result from this new procedure yet. **Before enabling `--run`, obtain a separate owner authorization for the exact `TA2INS` namespace, DASD TSO002 allocations, one `TA2INST` job, and one `TA2MR10` job.** No other scope or publication is implicitly authorized.
