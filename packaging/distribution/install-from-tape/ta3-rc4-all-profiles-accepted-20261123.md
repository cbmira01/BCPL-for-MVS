# TA.3 — BC0004 tape-resident installation: three-profile MVS technical acceptance

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.3 — MVS Bootstrap and Installation  
**Candidate:** `BCPL-0.1.0-rc4` / volume `BC0004`  
**Date:** 23 November 2026 EST  
**Disposition:** **Technical TA.3 gate PASS (qualified, owner-reported actual MVS)**; formal owner closure decision separately required.

## Exact owner-reported MVS observations

The original one-shot `ta3-rc4-recipient --run` passed read-only
**JOB 9398**, verifying all 42 fresh target PDSes absent and the
unchanged `BC0004` volume. It later halted in a redundant
`IEBCOPY` program-name count applied to the compact JES summary:
the actual `IEF142I` ordered step/RC0000 checks had passed. Original
incident and consumed marker remain immutable at
`workarea/ta3-rc4-recipient/20261123T133542Z-36979`.
The owner did **not** repeat the original installation.

The separately approved, one-shot
`packaging/distribution/install-from-tape/scripts/ta3-rc4-continuation --run`
then reported:

```text
TA.3 RC4 RECOVERY PREFLIGHT PASS: JOB 9403; first MR10 11 PDS/94 members verified; native+combined 31 targets absent; drive EMPTY.
Install ONLY remaining NATIVE and COMBINED on-tape profiles ONCE? [y/N]: y
TA.3 RC4 NATIVE TAPE-RESIDENT PASS: 11 PDSes; 71 members; 10 MVS IEBCOPY steps.
TA.3 RC4 COMBINED TAPE-RESIDENT PASS: 20 PDSes; 150 members; 19 MVS IEBCOPY steps. SCALVEC TEST/EXP/RP/CODE PASS.
TA.3 RC4 ALL TAPE-RESIDENT PROFILES PASS: MR10 recovered without replay; NATIVE+COMBINED installed; BC0004 unchanged.
Evidence: workarea/ta3-rc4-continuation/20261123T163929Z-37828
```

The source-controlled continuation requires and records the full
actual MVS/JES evidence for the restored tape-resident `BT0002`
profiles, accepted original MR10, fresh MVS LISTDS/DCB and
PDS-directory/member results, and installed combined
`MR10KIT.LOAD(ICINT19)` SCALVEC `TEST:`, `EXP:`, `RP:`,
interpreter `CODE=0` semantic verification. It preserves
and verifies the original accepted media checksums.

| On-tape profile | Recipient namespace | Restored PDSes | Verified members | IEBCOPY evidence |
| --- | --- | ---: | ---: | --- |
| `MR10` | `HERC02.BCPL.R4MR` | 11 | 94 | First-profile `IEF142I` steps RC0000, recovered without re-execution |
| `NATIVE` | `HERC02.BCPL.R4NT` | 11 | 71 | 10 actual MVS steps, PASS |
| `COMBINED` | `HERC02.BCPL.R4CB` | 20 | 150 | 19 actual MVS steps, PASS; installed SCALVEC PASS |
| **Total** | Three disjoint targets | **42** | **315** | No duplicate MVS profile restore |

The new release candidate was previously produced and audited
under owner-authorized MVS **JOBS 9393–9397**, 21 standard-labeled
logical datasets and 64 AWS physical files. Immutable image:
`mvs-state/tape/bcpl-0.1.0-rc4-BC0004.aws`, SHA-256:
`7cc5a1d61882bf88469fd9f9e38512f1976ef1a775e3095e12e3988600c57af1`.
Original `BC0003` SHA-256:
`6c54c4df2b75020a698110061c4f8003b09adbe21f738848dcaed3da495d81e1`.

**Provenance qualification:** the user supplied the MVS runner output;
the private SHA256-sealed receipts and remaining JOB numbers are
retained under the owner's repository `workarea/` and were not
available to the assistant for direct opening. Do not infer additional
JES job numbers beyond **9398** and **9403** from this transcript.

## TA.3 acceptance mapping

1. `BT0001` human-readable MVS bootstrap was read from the new
   standard-labeled `BC0004` tape without running BCPL.
2. `BT0002` was restored with MVS IEBCOPY; the eight on-tape
   installer members include actual `MR10`, `NATIVE` and
   `COMBINED` executable MVS JCL profiles and shared `COPY`
   control input. They were recovered through MVS IEBGENER SYSOUT
   and verified card-for-card before execution. The profile JCL
   does not depend on Python, WSL, Git or `dspal` **within the
   recipient operating environment**.
3. Three target namespaces were distinct and initially uncataloged;
   the new-recipient procedure used `DISP=(NEW,CATLG,DELETE)`,
   actual MVS allocation, DCB/directory checks, no overwrite and
   separate approval/no-retry markers.
4. All three manifest-selected profiles installed correctly;
   the MR10 compiler environment and installed `SCALVEC` were
   demonstrated in actual MVS.

**Qualified limitations:** MVS site defaults `HERC02`/`TSO002`
were exercised; other site symbolic overrides were designed but not
empirically demonstrated. The same existing MVS 3.8J system, with
fresh recipient namespaces, was used; independent clean-system IPL
and integrated release acceptance are **TA.7**, not TA.3.
Complete MR10 11 language + 17 BCPL demonstrations, 12 individually
human-reviewed MR10 cases, and independent `ICINT19` rebuild remain
**TA.4**. Native runtime/BLIB/coroutine/extension link-edit and
execute acceptance remains **TA.5**. Source provenance, rights,
TA.8 audit and publication remain unresolved.

The candidate explicitly declares `native_compiler: absent`;
`TA.6` is **N/A** for this candidate, not PASS.

## No-replay and disposition

**Do not** repeat `ta3-rc4-production --run`,
`ta3-rc4-recipient --run`, or
`ta3-rc4-continuation --run`. All associated stateful markers are
consumed. Retain `BC0003`, `BC0004`, first-halt evidence,
continuation evidence and all accepted MVS datasets.

The **TA.3 technical installation gate is satisfied (qualified)**.
This file is the review-ready technical acceptance record;
a **formal owner-directed TA.3 closure and TA.4 kickoff** is a
separate project decision and is not implicitly authorized by
successful output alone.
