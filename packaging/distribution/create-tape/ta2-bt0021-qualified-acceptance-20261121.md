# TA.2 — BT0021 historical-source staging: qualified MVS acceptance

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.2 — Manifest-Driven Tape Producer  
**Date:** 21 November 2026 EST  
**Status:** **BT0021 staged PDS directory/DCB ACCEPTED (qualified)**; no AWS production authorized.

## Owner-provided actual MVS execution

The owner ran the committed one-shot `rc2-bt0021-stage-once.py --run` on the resident MVS 3.8J. The runner repeated LISTDS/IEHLIST and reported **15,375 free tracks** on TSO002 immediately before staging. The owner typed the requested confirmation exactly once.

The runner reported **TA2C21ST JOB 9335, IEBCOPY step S0021 RC=0000**, with overall runner RC=0, and saved private JES/receipt evidence under:

`workarea/ta2-rc2-bt0021-stage-operations/20261121T124159Z-25452`

An independent owner-executed read-only `dspal stat <DSN> --raw` and `dspal ls <DSN> --raw` followed. Both inquiry commands returned RC=0. The supplied original LISTDS LABEL excerpt shows **JOB 9336**, `IEF142I DSPALST STAT ... COND CODE 0000`, `RECFM=FB`, `LRECL=80`, `BLKSIZE=800`, `DSORG=PO` and **VOLSER TSO002** for **HERC02.BCPL.TA2STG.BT0021**.

The independent `LISTDS MEMBERS` excerpt contains exactly 15 members: `BCPL`, `BLIB`, `CG`, `CGHDR`, `EDITMAIN`, `IOS`, `LIBHDR`, `MAKELIB`, `MAKEOBJ`, `PM`, `PROGRAM`, `SYN`, `SYNHDR`, `TRN`, `TRNHDR`. This set exactly matches `BCPL-0.1.0-rc2.yaml` sequence 21. No members are absent or extra. The LISTDS MEMBERS job number is not in the supplied excerpt; it is recoverable from the original private JES report without repeating an inquiry.

Saved original independent MVS output, inquiry return codes and SHA256SUMS:

`workarea/ta2-rc2-bt0021-verification/20261121T130011Z-23628`

**Evidence boundary:** This acceptance is based on the owner-provided real MVS outputs quoted above. This assistant did not directly open the private owner-local JES reports in its workspace; the preserved reports remain the full evidence authority. IEBCOPY RC=0000 plus exact MVS directory/DCB is sufficient for the **stage-input acceptance**; it does not certify all original member bytes a second time. The existing JOB 9330 record reconciliation remains the accepted 15/15, 6,577-record Hercules-translated FB80 source-fidelity result.

## Acceptance and boundaries

- **BT0021 accepted (qualified)** as the new historical-only MVS stage input for **BCPL-0.1.0-rc2**, VOLSER **BC0002** reserved.
- Existing **BT0001–BT0020 remain previously accepted**; no source PDS was rewritten, no earlier input was restaged and no re-execution of the one-shot runner is permitted.
- The committed preservation policy retains the **Hercules-translated FB80 bytes**, not literal CP037 equivalence. Historical Cambridge lexical compatibility remains unproven.
- Historical-source redistribution rights remain unresolved. The rc2 candidate contains **historical source only**, not a native-running Cambridge Compiler.
- No **AWS tape initialization, mount, write, readback, clean-target installation, publication or legal clearance** is implied or approved.

**TA.2 remains IN PROGRESS.** The next work is host-only candidate tape-producer preparation with the accepted 21-position manifest, independent AWS verification design, and a separately authorized, guarded candidate-media operation when the release gates are resolved.
