# TA.2 — Proposed independent MVS readback and restored-content verification

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.2 — Manifest-Driven Tape Producer  
**Date:** 21 November 2026 EST  
**Status:** **OWNER APPROVED DESIGN (21 November 2026); read-only JCL/preflight code implemented. Stateful readback and DASD allocation remain separately unauthorized.**

## Accepted starting point

The existing `BCPL-0.1.0-rc2` standard-labeled AWS image, VOLSER `BC0002`, is **qualified structurally accepted**: MVS JOB 9339 has 21 steps RC=0000, 21 ordered dataset labels, 64 physical files and reconciled 2,559 aggregate blocks. Frozen image SHA-256 is `123657b2feaeea739350853f8b8437ccb73b0e917442ddd3220589c7ae180375`. Source staged inputs remain `HERC02.BCPL.TA2STG.BT0001`–`BT0021` on `TSO002`; they must be opened **read-only** and must not be restaged.

The accepted TA.1 Track A jobs `TA1AR001.jcl`, `TA1AR002.jcl`, `TA1ACOMP.jcl` and Track B `TA1BREST.jcl` are the MVS precedent, **not** instructions to rerun TA.1. They demonstrate `IEBGENER` FB80 readback, `IEBCOPY` PDS unload restoration, `IEBCOMPR` for applicable record comparisons, and `IEHLIST`/bounded `ICINT19` execution qualification where binary equality was not directly proven.

## Recommended next design (owner decision required)

Perform one **separately authorized, guarded MVS readback** using the already mounted `BC0002` image, with **no tape write, HETINIT, automatic mounting, unmounting, or replacement**. MVS will necessarily control tape positioning while reading, so this is a state-changing device operation even though the AWS data are only read. All restored DASD targets must be newly allocated, collision-checked scratch datasets; never overwrite or recatalog development/source datasets.

1. **Before the write-protected read:** independently replay original sealed JOB 9339/structure evidence; verify SHA-256, volume serial, exact Hercules 0480 attachment and MVS readiness; inspect proposed scratch target absence, source DCBs and DASD free space. Abort on any drift or ambiguous device state.
2. **Read back all 21 logical tape datasets:** `IEBGENER` for `LABEL=(1,SL)` into a new PS FB/80/800 target; `IEBCOPY` `COPY` for `LABEL=(2,SL)` through `(21,SL)` into independent new PO datasets with manifest-matching DCBs. Preserve `RECFM=U, LRECL=0, BLKSIZE=6144` for the designated binary load library (manifest position **12**). Existing staged PDSes serve only as comparison sources. Tape DDs must be read-only.
3. **Verify MVS output:** require exact JES job and 21 step `IEF142I`/RC reports; independently query restored DCB and all 20 PDS directories; compare expected member sets from the frozen manifest, including the 4 installer members, the 127 selected historical/library items and 15 Cambridge source members.
4. **Compare actual content:** use independent `IEBCOMPR` or established record comparison for FB80 sequential/PDS data, with specific source-vs-restored dataset/member byte identity evidence where supported; handle `RECFM=U` through its own directory/IEWL/executable-use qualification and expressly distinguish that result from byte-for-byte binary equality if not demonstrated.
5. **Preserve artifacts:** verify the AWS SHA-256 before/after, save JES/SYSPRINT/LISTDS/IEHLIST/record-compare outputs and immutable attempt marker under `workarea/`, preserve the scratch targets for inspection; do not silently retry a partial MVS readback or delete evidence.

## Decisions to settle before implementing JCL

- **Scratch DASD volume/capacity and dataset naming:** propose new `HERC02.BCPL.TA2RB.BT0001`–`BT0021` on an independently checked owner-approved volume; do not assume `TSO002` has sufficient free extents simply because existing source staging succeeded.
- **Job shape and tape positioning:** recommend one strictly sequential, 21-read step job rather than manually repositioning the tape among 21 separate jobs; validate tape `LABEL=(n,SL)` behavior against TA.1 patterns and MVS before committing an executable deck.
- **Comparator scope:** treat `RECFM=U` restored-object verification separately from FB80 records. Avoid demanding unproven IBM IEBCOMPR binary identity; where necessary rely on actual IEHLIST and bounded execution evidence with a documented qualification.
- **Operator boundary:** one `[y/N]` confirmation immediately before the first MVS readback JES job, a permanent exclusive one-shot marker, no retries or automatic tape displacement, and explicit owner approval for each new MVS or DASD state change.

**Not part of this operation:** another tape production, rewriting the candidate AWS, public release, clean-target installation, historic-source rights clearance, or a claimed native-running Cambridge Compiler.

## Acceptance requirement

TA.2 cannot be formally closed solely on the present structural PASS. The independent tape-readback result must demonstrate the restored datasets, selected member inventory, applicable record/binary content checks and preserved AWS SHA. If a narrower first readback is chosen, document its scope and continue verification without representing a partial result as complete TA.2 acceptance.

**Await owner review of this design before implementing or submitting state-changing readback JCL.**

## Owner design approval and implementation checkpoint

The owner explicitly approved this design. [Implementation and test record](ta2-rc2-readback-design-implementation-20261121.md) documents the source-controlled JOB-less JCL and read-only MVS preflight. The suggested `TSO002` allocation and exact new 21-dataset track/extent budget are not yet approved; do not submit `TA2RC2RB` or attempt tape positioning until a separate owner decision. The accepted `BC0002` image, device and original SHA-256 remain unchanged.
