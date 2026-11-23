# TA.3 — RC4 tape-resident three-profile MVS recipient acceptance trial

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** **TA.3 — MVS Bootstrap and Installation**, IN PROGRESS  
**Candidate:** `BCPL-0.1.0-rc4` / VOLSER `BC0004`  
**Accepted owner-reported production SHA-256:**
`7cc5a1d61882bf88469fd9f9e38512f1976ef1a775e3095e12e3988600c57af1`

## Prerequisite (accepted, no replay)

Actual MVS 3.8J **JOBS 9393–9397 PASS**: 19 accepted RC3 source
PDSes; two new staged bootstrap/installer datasets; eight verified
installer members; and a **21-dataset standard-label / 64 physical
file** BC0004 AWS image. Evidence:
`workarea/ta3-rc4-production/20261123T130731Z-36363`.
No additional staging or tape-writing attempt is permitted.
The original BC0003 SHA-256
`6c54c4df2b75020a698110061c4f8003b09adbe21f738848dcaed3da495d81e1`
remains the immutable historical acceptance reference.

## What is being verified

The new
[one-shot MVS recipient runner](scripts/ta3-rc4-recipient)
uses only the accepted **BC0004** for release material. It performs
one read-only MVS LISTDS inquiry of all **42** new recipient PDSes
before requesting operator confirmation:

| Profile | Namespace | Tape-resident installer member | New PDSes including installer | Members |
| --- | --- | --- | ---: | ---: |
| MR10-only | `HERC02.BCPL.R4MR` | `BT0002(MR10)` | 11 | 94 |
| native-only | `HERC02.BCPL.R4NT` | `BT0002(NATIVE)` | 11 | 71 |
| combined | `HERC02.BCPL.R4CB` | `BT0002(COMBINED)` | 20 | 150 |
| **Total** | three isolated namespaces | three on-tape procedures | **42** | **315** |

The common BT0001 text is read using **MVS IEBGENER**; each
profile independently restores its eight-member
`BT0002` installer PDS with **MVS IEBCOPY**.
For every profile, the runner uses **MVS IEBGENER** to print
the *actual tape-restored* `MR10`, `NATIVE`, or `COMBINED`
member and the shared `COPY` member to JES SYSOUT.
Every printed JCL card must be reconstructed, in order, with exact
text matching the pinned RC4 candidate; a single missing or changed
card prevents submission.

**The executing profile job body comes from this MVS readback**, not
the old source-controlled external `TA3MR10`, `TA3NATV`,
or `TA3BOTH` jobs. The trusted offline generator is used only
as the expected full-byte candidate reference.
The operator's authorized JOB card is prepended to the restored
job body for submission to the actual MVS JES reader.
The profile's native `PROC` symbols select its fresh recipient
namespace, the original tape data positions and MVS
`BT0002(COPY)` IEBCOPY SYSIN. No Python or `dspal` is
required **within the MVS recipient procedure**; host software is
used to submit, print, capture and verify JES evidence.

JES/IEF142I procedure step results, full post-restore MVS LISTDS DCBs
and PDS directories are checked independently for all profiles.
The combined recipient then executes the actual restored
`MR10KIT.LOAD(ICINT19)` and installed `SCALVEC` source,
requiring `TEST:`/`EXP:`/`RP:`/`CODE=0` semantic PASS.

## Operational safeguards

- Verify both immutable image SHA-256 values before operations, and
  verify the **sealed accepted RC4 producer receipt** and one-shot
  marker. The production receipt identity pins MVS JOBS 9393–9397;
  no accepted process is repeated.
- Before one `[y/N]` approval, require **all 42 targets absent**
  in the MVS catalog and an idle tape unit 0480 holding either
  no media, the exact verified original BC0003, or the exact
  verified new BC0004.
- After approval, create a **new no-retry recipient marker**,
  mount only the accepted BC0004 on the same tape drive, and
  allocate only the new isolated recipient datasets.
- Never initialize/write a tape, delete a dataset, overwrite a
  previous installation, retry a partially executed operation
  or publish an unaccepted release.
- Save full JES, catalog, directory, on-tape JCL and semantic
  results under `workarea/ta3-rc4-recipient/` with SHA256SUMS.
  Keep WSL console output compact.

## Scope limitations

This is an MVS-native **installation/installed-use proof on the
existing MVS system**, with strictly isolated new dataset namespaces.
It does not independently prove a clean-IPL MVS system, full
TA.4 regression or native-runtime TA.5 link/execute outcomes.
The scoped RC4 candidate continues to declare
**`native_compiler: absent`**; `TA.6` is N/A, not PASS.

**Status: implementation committed; actual RC4 recipient MVS run
pending. TA.3 remains IN PROGRESS.**
