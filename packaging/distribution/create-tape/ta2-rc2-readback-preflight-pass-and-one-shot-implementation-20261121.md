# TA.2 — Readback preflight PASS and owner-gated one-shot MVS runner

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.2 — Manifest-Driven Tape Producer  
**Date:** 21 November 2026 EST / 22 November 2026 UTC  
**State:** **Read-only MVS catalog and VTOC preflight PASS (qualified); single-mount/21-step readback implementation and offline tests PASS. No MVS readback execution authorization exists.**

## Owner-reported actual MVS preflight

After GitHub `main` `7a620cd95fe4a1bf811fc98fda72f81c62c03aee` corrected the empty-drive check, the owner executed the approved read-only `ta2-rc2-readback-plan --volume TSO002 --live` and reported **RC=0**:

```text
TA.2 RC2 READBACK PREFLIGHT PASS: Hercules 0480 EMPTY, MVS O-NRD; 21 new targets absent; catalog JOB 9340, VTOC JOB 9341; IEHLIST reports 15335 free tracks.
Evidence: workarea/ta2-rc2-readback-preflight/20261122T010923Z-28068
No tape read/position, DASD allocation or readback job was performed.
TA.2 RC2 readback preflight RC=0
```

The preflight runner checks the accepted original `BCPL-0.1.0-rc2` AWS and SHA256SUMS-sealed postwrite acceptance, confirms the Docker tape bind and current Hercules/MVS device status, issues a combined `LISTDS LABEL` for all **21** missing `HERC02.BCPL.TA2RB.BT0001`–`BT0021` targets and all **21** accepted staged source datasets, and obtains an `IEHLIST LISTVTOC FORMAT` report for `TSO002`. Its accepted MVS jobs are **9340** (catalog/DCB) and **9341** (VTOC/free tracks), with a new private SHA256SUMS-sealed evidence folder at the path above. The assistant has inspected the source and owner-reported terminal result, **not** the private owner-local raw JES/IEHLIST bytes. The MVS/IEHLIST 15,335-track number is an allocation screening result, not evidence of sufficient contiguous extents for every allocation request.

The selected restore worksheet contains **770 primary + 81 secondary tracks**, plus **100 tracks** as the capacity screening margin: 15,335 reported free tracks exceeds that budget, without asserting a guaranteed future allocation.

## Completed guarded runner implementation

The new source-controlled `scripts/ta2-rc2-readback-once` reuses the canonical, already-approved `scripts/ta2-rc2-readback-plan` for manifest reconciliation, all 21 staged source contracts, **JOB-less MVS readback JCL**, and AWS SHA. It does not introduce a parallel manifest or modify the original AWS.

**Frozen proposed JCL SHA-256:** `226819ef3702234a1367c7a7df96399cf9fcaf32d99152061db1df98fed12e73` (315 MVS cards, derived from the current, Git-verified `ta2-rc2-readback-plan.render`, using `TSO002` and the approved-design staging worksheet). The independent accepted *write* JCL remains unchanged at `85eca6f3e1e83c2d0e476f24870a20664bde2a50e2de8653606bfa351af54b4f`.

The runner implements these separate safety stages:

1. **Refusal without a separately Git-committed owner execution approval.** Its `--run` path requires the exact `ta2-rc2-readback-execution-approval.json` committed **unchanged on GitHub main**. This file is **intentionally absent**. The JSON contract will bind `BC0002`, the existing AWS filename and SHA256, `TA2RC2RB`, the restored TSO002 namespace, the owner-reported jobs **9340/9341** and 15,335 free tracks, the SHA256-sealed accepted preflight directory, the exact readback JCL digest and a conditional one-time mount permission. No automatic retries, overwrites or publication are permitted.
2. **Original evidence replay:** the accepted postwrite, original no-retry write receipt and the exact SHA256-sealed 9340/9341 read-only preflight must still agree. A changed image, mismatched manifest, amended stage, inconsistent readback deck or changed preflight refuses.
3. **Fresh safety check before the one allowed operation:** a permanent **invocation-consumed marker** is written before the fresh read-only MVS inquiry; the candidate must be unchanged, the Docker tape binding valid, Hercules 0480 either **EMPTY/O-NRD** or exactly mounted `BC0002/O`, all new targets still absent and the 21 source DCBs unchanged. One MVS LISTDS job performs the new check; the already accepted VTOC inquiry need not be rerun without evidence of a defect.
4. **Exactly one operator `[y/N]` decision:** any response other than `Y`/`y` declines. The exclusive, irreversible **readback mount/JES intent marker** is created **before** any device mount. Only when 0480 is freshly verified **EMPTY** can the exact existing `BC0002` AWS filename be mounted with `mvs-console --yes tape mount`; foreign/busy/unrecognized media cause refusal, never displacement or automatic unmount.
5. **One actual 21-step MVS readback:** `R0001` IEBGENER restores the FB80 bootstrap PS, then `R0002`–`R0021` IEBCOPY restore unloads into **new** `HERC02.BCPL.TA2RB.BTnnnn` on `TSO002` with `DISP=(NEW,CATLG,DELETE)`. `BT0012` preserves `PO/U/0/6144`, all other PDS datasets `PO/FB/80/800`. Tape DDs are only `DISP=OLD`, standard label `LABEL=(n,SL)`, retained `BC0002` input media. The original 21 source PDS/PS datasets remain read-only.
6. **Qualified MVS result only:** original JES summary and `IEF142I` records must show all **21** ordered RC=0000 steps. Recheck the AWS hash after the job, save complete private MVS output and SHA256SUMS. Restored DCB/member inventory, record-level source/restored comparisons, `RECFM=U` load-member/executable qualification, provenance/release and clean recipient installation are **not claimed** by a 21-step RC=0000 alone.

## Offline verification and authorization boundary

The exact new runner and its 14 synthetic negative/positive tests passed in the assistant's separate repository-root workspace, alongside 23 existing source-controlled readback-plan tests: **37/37 PASS**, including missing authorization, original evidence drift, 21 MVS step/IEF142I mismatch, correct/foreign/empty device-state checks, exclusive marker creation, correct step ordering, input-only DDs and truthful separation of content-verification status. The script/test Git blobs were compared with the locally tested versions before committing.

**No new write/restore approval file is committed. No MVS mount, tape positioning, IEBGENER/IEBCOPY readback, new DASD allocation or source modification has been performed by this code work.** A separate affirmative owner decision for a single `BC0002` mount on **only an empty 0480** and single `TA2RC2RB` JES job on **TSO002** is required before creating the exact execution approval and giving any `--run` command. Do not rerun accepted tape production or modify the original image.

**TA.2 — Manifest-Driven Tape Producer remains IN PROGRESS.** TA.3 recipient installation and publication are separate marches.
