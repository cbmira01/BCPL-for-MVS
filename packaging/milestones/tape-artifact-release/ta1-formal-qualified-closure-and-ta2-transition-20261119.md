# TA.1 — Multi-Dataset Tape Mechanics: formal qualified closure and TA.2 transition

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.1 — Multi-Dataset Tape Mechanics  
**Owner decision:** **ACCEPTED AND CLOSED (qualified)**  
**Decision date:** 19 November 2026  
**Evidence/source checkpoint:** GitHub `main` `99290fba45c6c51d31720d2b49b993ced5e66722`  
**Next march:** TA.2 — Manifest-Driven Tape Producer (**READY FOR DESIGN AND READ-ONLY PREFLIGHT ONLY**)

## Owner direction and authority

The owner directed: **“Move to TA.1 closure without delay. Give me a
handoff prompt for TA.2.”** This authorizes formal **TA.1 CLOSED
(qualified)**, based on the accepted actual MVS/Hercules two-track
evidence, and advances the project to TA.2 for initial design
and read-only preflight. This does not authorize a producer
tape write, permanent dataset change, candidate identity or
VOLSER reservation, release installation or publication.

## Accepted Track A — two ordered standard-label datasets

- BTA101, separate scratch AWS image, logical `BCPL.BT0001`
  FB80 and `BCPL.BT0002` IEBCOPY-PDS unload.
- **TA1AWRIT JOB 9076** wrote both datasets, RC=0000.
- Independent restore **JOBS 9084 and 9086** RC=0000 and
  **IEBCOMPR JOB 9089** both steps RC=0000; confirmed source/
  restored DCBs, selected FB80 data and seven-member PDS inventory.
- Saved tape structure review accepted seven physical tape files
  with block counts `3,3,2,2,25,2,0`, not seven logical datasets.
- Preserved BTA101 SHA-256:
  `d5900cbccaaa2f7eb1bcc59ae30847540e6911c577dafa5e131c0b3a9c8e3fe2`.

**Disposition:** Track A PASS (qualified), per
[round-trip and physical-file review](../../distribution/create-tape/ta1-track-a-roundtrip-review-20261117.md).

## Accepted Track B — RECFM=U restored load library

- BTA102 distinct scratch AWS, selective IEBCOPY **UNLOAD**
  `TA1BWRIT` **JOB 9120**, RC=0000, single logical SL
  dataset and physical block counts `3,8,2,0`.
- Independent IEBCOPY **RESTORE**
  `TA1BREST` **JOB 9136** RC=0000:
  `HERC02.BCPL.TA1B.LOAD(ICINT19)` on **TSO002**,
  `PO/U/0/6144`. Original development source load
  PDS remained separately on TSO003.
- Original/restored IEHLIST `LISTPDS FORMAT`
  `TA1BSRC` **JOB 9151** and `TA1BDST`
  **JOB 9152** both RC=0000, exact matching member
  `ICINT19`, entry point `000000`, attributes `02E2`.
- Actual independent tape-restored `STEPLIB` execution:
  `TA1BGO` **JOB 9165** ran the pinned
  **eight-step MRREGRES scalar/vector** case, all
  RC=0000, three `ICINT19` invocations using restored
  `HERC02.BCPL.TA1B.LOAD`, and correct
  `RP: SCALAR 17 42` and
  `RP: VECTOR 5 10 15 20` records. The runner
  also checked interpreted `CODE=0` and MVS IEF142I.
- Preserved BTA102 SHA-256:
  `c3b235ca78d221432199adcde1f7a83aead4f76bab0e0eaa19d77c81d9912210`.

**Disposition:** Track B PASS (qualified), per
[restored GO MVS acceptance](../../distribution/create-tape/ta1b-restored-go-evidence-20261119.md).

## Evidence provenance and retained qualifications

The results are actual **owner-observed MVS 3.8J/JES/IEBCOPY/
IEHLIST/ICINT19/Hercules** runner output. The assistant reviewed
the Git-controlled tools and supplied outputs, **not** the raw
ignored JES/SYSPRINT/HETMAP bytes directly.
Private original evidence remains under `workarea/ta1-operations/`
and `workarea/ta1b-operations/`; tracked acceptance detail is
in the [qualified acceptance matrix](ta1-qualified-acceptance-candidate-20261119.md).

- No byte-for-byte `RECFM=U` source/restored
  load-module identity was demonstrated. Directory metadata match
  plus successful bounded execution are accepted for this march,
  not a blanket binary equality assertion.
- BTA101 and BTA102 are **immutable scratch experiment evidence**,
  not distributable candidate media. Never reinitialize, append,
  overwrite, relabel or reuse their identities.
- No complete recipient installation, multi-PDS distribution,
  source-to-resident-binary provenance, redistribution rights
  sign-off, native Cambridge Compiler self-compilation,
  complete MR10 `MRREGRES` panel, or public release is
  accepted by TA.1.
- Historical guard halts and unverified positioning/demount
  causes remain documented; do not extrapolate beyond the
  observed tape operations.
- **Do not reopen TA.1 without a demonstrated regression or
  specific defect.**

## Formal transition

TA.1 is **CLOSED (qualified)**.

TA.2 — **Manifest-Driven Tape Producer** is **READY FOR
DESIGN AND READ-ONLY PREFLIGHT**. Its objective is a
**new** immutable AWS candidate from a frozen Git-controlled
manifest and verified MVS data sources, with generated JCL,
contiguous logical `BCPL.BTnnnn` aliases, independent label/
filemark/readback and restored-content verification, SHA-256,
and provenance/registry tracking. This is a new march, not
permission to perform those stateful production steps.

[TA.2 kickoff](ta2-kickoff-20261119.md) is the governing
handoff for initial scope and design decisions. Major
producer/registry/verification choices require owner review
before implementation, and any actual fresh tape production,
MVS persistent dataset modification or release publication
requires separate explicit authorization.
