# TA.2 — Actual RC2 empty-tape-drive diagnosis and revised read-only preflight

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.2 — Manifest-Driven Tape Producer  
**Date:** 21 November 2026 EST / 22 November 2026 UTC  
**Disposition:** **Hercules 0480 confirmed EMPTY in both preserved and fresh reports, MVS 480 O-NRD; read-only preflight can now proceed without mounting. State-changing readback NOT authorized.**

## Owner-reported actual Hercules and MVS evidence

The owner ran the source-controlled `ta2-rc2-readback-plan --volume TSO002 --inspect-drive` after committing the bounded device diagnostic, and reported **RC=0**:

```text
TA.2 RC2 READBACK DEVICE DIAGNOSTIC: original=EMPTY; fresh=EMPTY; MVS 480=O-NRD
Original 0480: 00:57:14 HHC02279I 0:0480 3420 * IO[3171] maxsize=0 eotmargin=128K deonirq=N
Fresh 0480: 01:04:14 HHC02279I 0:0480 3420 * IO[3171] maxsize=0 eotmargin=128K deonirq=N
Evidence: workarea/ta2-rc2-readback-preflight/20261122T010414Z-27961
No tape movement/mount, readback job, or DASD allocation.
TA.2 RC2 device diagnostic RC=0
```

The script replayed the original failed preflight's SHA256-sealed report at `workarea/ta2-rc2-readback-preflight/20261122T005713Z-27881`, recomputed the accepted existing `BC0002` AWS SHA256 and replayed the accepted sealed structural receipt. Fresh Hercules/MVS display inquiries confirmed that **0480 has no image mounted** and the guest device state is **O-NRD**. The assistant reviewed the Git-controlled source and the owner's exact terminal report, not private files directly. The original `TA2RC2WR` write did not request `RETAIN` on the final output; the empty post-job drive is consistent with release, but the exact release mechanism is not independently proven here.

## Targeted preflight correction

The earlier `--live` planner incorrectly treated the **presence of an already mounted tape** as a prerequisite to **read-only DASD catalog and VTOC inquiries**, causing RC=2 before their MVS submission. The corrected `ta2-rc2-readback-plan --volume <DASD_VOLSER> --live` now explicitly separates read-only DASD preflight from a future tape read:

- Requires exactly one Hercules 0480/3420 row reporting either `EMPTY` (literal `*`) or exact `MOUNTED_BC0002`, never foreign/busy/ambiguous media.
- Requires MVS device **O-NRD** when empty or **O** when the expected image is mounted; contradictory drive states fail closed.
- In either accepted state, verifies the **existing candidate AWS file/hash**, original staged source contracts and readback JCL selection, Docker tape bind, then performs a read-only MVS LISTDS inquiry for all **21 proposed new readback target absences** plus accepted staged-source DCBs, followed by read-only formatted IEHLIST VTOC/capacity inquiry.
- Saves original query reports, device state, JCL digest, candidate DASD volume and a SHA256SUMS-sealed receipt under `workarea/ta2-rc2-readback-preflight/`. IEHLIST's free-track total is a screening value and does not by itself prove a future allocation can obtain all needed extents.
- **Does not mount, initialize, read, position or modify the tape**, allocate/overwrite a DASD dataset or submit the actual `TA2RC2RB` job. No stateful readback option or automatic retry exists.

The owner-approved readback *design* remains unchanged: 21 new `HERC02.BCPL.TA2RB.BTnnnn` datasets, `R0001` IEBGENER followed by 20 IEBCOPY steps, `BT0012` `PO/U/0/6144`, with proposed 770 primary + 81 secondary tracks. `TSO002` remains a **candidate** readback volume, not a newly approved permanent allocation target.

**Assistant-workspace verification:** Python AST for both modified files PASS; **23/23** focused executable offline checks PASS, including exact empty/mounted classifications, MVS device-state conflicts, foreign and busy media, prior failure replay, unchanged candidate image, and preservation of read-only inquiry paths. GitHub upload blobs match the byte-for-byte locally tested files.

## Next gate

Perform exactly one fresh **read-only** `--volume TSO002 --live` inquiry. If it passes, inspect MVS LISTDS/IEHLIST and the new SHA256SUMS evidence; then decide whether to approve the scratch DASD volume, controlled exact-image mount on empty 0480, and one-shot 21-step MVS readback. **None of those state changes are authorized by this evidence or code revision.**

**TA.2 — Manifest-Driven Tape Producer IN PROGRESS.** The original production no-retry marker and accepted AWS image remain immutable; no new release publication or clean recipient installation claim is made.

## Subsequent owner-reported successful read-only MVS preflight

The owner executed `ta2-rc2-readback-plan --volume TSO002 --live`, now reporting **RC=0**: Hercules 0480 EMPTY, MVS O-NRD, **21** new target dataset absences, **catalog JOB 9340**, **VTOC JOB 9341** and **15,335** reported free tracks. Original receipt: `workarea/ta2-rc2-readback-preflight/20261122T010923Z-28068`. See the [accepted read-only preflight and owner-gated runner record](ta2-rc2-readback-preflight-pass-and-one-shot-implementation-20261121.md). The earlier device refusal and its evidence remain preserved. Actual mount and 21-step MVS readback are not yet authorized.
