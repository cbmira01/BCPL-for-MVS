# TA.2 — Guarded 21-dataset rc2 private AWS producer and independent review

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.2 — Manifest-Driven Tape Producer  
**Date:** 21 November 2026 EST  
**Status:** **Implementation and offline tests PASS; no AWS candidate created or authorized.**

## Accepted actual MVS evidence

The owner ran `scripts/ta2-rc2-media-preflight --live` from GitHub `main`. Reported output was exactly:

```text
TA.2 RC2 DRIVE PREFLIGHT PASS: Hercules 0480 empty; MVS 480 O-NRD.
Private evidence: workarea/ta2-rc2-media-preflight/20261121T133703Z-25915
No media, MVS datasets, or JES jobs changed; AWS production still unauthorized.
TA.2 RC2 drive preflight RC=0
```

This accepted checkpoint supplements the previous qualified MVS acceptance of the exact **21** staging input datasets `HERC02.BCPL.TA2STG.BT0001` through `BT0021` on `TSO002`. It does not establish future unit availability or permit AWS writing. Earlier IEBCOPY staging operations remain immutable and must not be repeated.

## Consolidated implementation

The new `scripts/ta2-rc2-produce-once`:

- Uses the existing **canonical** `BCPL-0.1.0-rc2` release manifest, reserved VOLSER `BC0002`, `compiler-source/successor-contract.py` and `scripts/ta2-offline` JCL renderer. No independent release manifest is introduced.
- Replays the original SHA256-sealed accepted MVS stage receipts for BT0001–BT0020 and BT0021, including the preserved independent BT0021 LISTDS DCB and 15-member directory, without additional staging or MVS inquiry in the default mode.
- Proposes one JOB-less body with **T0001 IEBGENER**, **T0002–T0021 IEBCOPY**, 21 ordered `BCPL.BTnnnn` standard-label tape datasets, and **146 SELECT MEMBER cards**. These are physical tape unloads of the accepted staged inputs; the native-running Cambridge Compiler is **absent**.
- Has a permanently closed **media-write gate**: the exact Git-tracked `ta2-rc2-media-write-approval.json` must be separately owner approved and committed before `--run` can perform *any* media operation. It is **not present** in this commit. Merely running `--run` without it refuses.
- Once separately authorized, checks clean `main`, original stage seals, running Docker/bind and host identity, installed HETINIT support, absence of proposed filename, standard-label VOLSER collision across local media, fresh Hercules/MVS device state, and absence of all 21 logical tape DSNs from MVS catalog. It obtains two explicit operator confirmations, creates an irreversible no-retry attempt marker **before** media creation, reserves the new image exclusively, initializes/mounts the private candidate, and submits exactly one authenticated 21-step JES job. On any failure it does not retry, overwrite, remount, or automatically clean up state.
- Verifies the actual JES job summary and distinct IEF142I entries with 21 expected RC=0000 results. Captures private MVS/Hercules output and calculates the image SHA-256. No credentials are intentionally persisted in tracked files. The candidate is **private, not published**.

The new independent `scripts/ta2-rc2-aws-review` uses saved HETMAP reports or a fresh **read-only** HETMAP examination of an existing exact candidate image. It checks one VOL1, ordered HDR1/HDR2/EOF1/EOF2 for each of 21 datasets, matching sequence/name/VOLSER in HDR1 and EOF1, and **64** physical files (21 header, 21 data, 21 trailer, 1 terminal empty). Each dataset's payload file must contain blocks. It preserves SHA256-sealed reports under ignored `workarea/`. This is structure verification, **not byte-for-byte member identity, IEBCOPY restore, or clean-target installation**.

## Assistant-workspace testing and open gate

Python syntax/AST checks and the complete **60/60 rc2 focused tests** passed in the assistant workspace, including previous manifest/drive tests, new 21-step JES acceptance/refusal tests, approval/marker/exclusivity/receipt checks, and 15 independent AWS positive/corrupt-label/filemark tests. No live 21-dataset MVS job or AWS candidate media was produced by these synthetic tests.

One proposed private image filename is `mvs-state/tape/bcpl-0.1.0-rc2-BC0002.aws`, to be reviewed with the owner before an exact write authorization is committed. Even if authorized and successfully written, the candidate will still require separate MVS tape readback, independent restore/functional regression, installer verification, provenance/redistribution review, and publication approval. The archival Cambridge source-byte policy remains the Hercules-translated FB80 records; native lexical semantics remain unresolved.

**Next decision:** whether to authorize **one private, guarded** standard-labeled AWS candidate build for `BCPL-0.1.0-rc2` / `BC0002`, device `0480`, exact 21 staged inputs, filename above, with **no publication or automatic retry**. No approval or writer WSL command is included in this implementation record. TA.2 remains IN PROGRESS.
