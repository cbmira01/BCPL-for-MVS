# TA.1 Track B — RECFM=U load-library tape mechanics: design proposal

**Project:** BCPL for MVS 3.8 Reconstruction
**Milestone:** Tape artifact release
**March:** TA.1 — Multi-Dataset Tape Mechanics
**Status:** DESIGN APPROVED BY OWNER 18 NOVEMBER 2026; JCL, generated-job contract and read-only MVS preflight implemented and offline-tested. **NO STATEFUL TAPE/MVS OPERATION AUTHORIZED.**

## Objective

Verify an actual IEBCOPY unload to standard-labeled AWS tape,
independent restoration to a new MVS load-library PDS, ICINT19 directory
and attributes, and real MVS execution with STEPLIB pointing ONLY to the
restored load library. TA.0 JOB 9060 observed the development ICINT19
directory (entry 000000, attributes 02E2), and JOB 9061 qualified the
eight-step development-load scalar/vector execution. Neither is restored
load-library evidence. Preserve those baselines.

This is a link-edited System/370 load module in an MVS load library,
NOT an FB80 relocatable object PDS, and NOT an MR10 INTCODE deck.

## Proposed scratch identities — NOT RESERVED

| Item | Proposal |
| --- | --- |
| Read-only source | HERC02.BCPL.MR10KIT.LOAD(ICINT19), PO/U/0/6144 |
| Fresh AWS file | mvs-state/tape/bcpl-ta1-b-20261117-01.aws |
| Fresh VOLSER | BTA102, subject to all-image/current-system uniqueness check |
| Hercules / MVS device | 0480 / 480, subject to release/availability |
| Uncataloged tape DSN | BCPL.BT0001, LABEL=(1,SL), on BTA102 only |
| Fresh restored DASD PDS | HERC02.BCPL.TA1B.LOAD, PO/U/0/6144 |
| Exact member | ICINT19, non-alias |

BT0001 is the first logical data set **on this separate diagnostic
scratch volume**, not the release bootstrap. A release tape's BT0001
must be readable FB80 bootstrap instructions. No catalog entry is
created for a tape DSN, even if it is reused on distinct scratch media.

## Proposed sequence

1. Read-only stat and IEHLIST directory preflight for the active
   development MR10_LOAD(ICINT19); verify source DCB, intended restore
   target absent, virgin image filename, candidate VOLSER uniqueness
   against every known image, Docker bind and idle tape unit.
2. Initialize BTA102 exactly once using installed hetinit -d -i, check
   VOL1, mount at verified idle 0480. A source-read-only IEBCOPY job
   unloads SELECT MEMBER=(ICINT19) to a single sequential SL tape
   data set; retain JOB, utility/label/filemark evidence and SHA-256.
   The IEBCOPY unload DCB is VS, distinct from source PO/U/0/6144.
3. After a separate safe device check, conditionally remount the same
   BTA102 image if MVS unloaded it; IEBCOPY from explicit
   VOL=SER=BTA102 and LABEL=(1,SL) to a new, cataloged
   HERC02.BCPL.TA1B.LOAD, DISP=(NEW,CATLG,DELETE), with verified
   PO/U/0/6144 DCB. Require source and restored IEHLIST FORMAT
   directory entries and matching non-alias ICINT19 metadata.
4. Derive the same eight validated scalar/vector MRREGRES case-01 steps
   from pinned mr10-kit-compiler/jcl/run-regression-tests.jcl:
   SSYNI STRNI SCGI SBLIBI SICLIB C01A G01A R01.
   Change ONLY the three ICINT19 STEPLIB DDs to
   DSN=HERC02.BCPL.TA1B.LOAD,DISP=SHR. Do not change canonical
   MRREGRES or source datasets. Require all eight step RC=0000 and
   successful IEF142I, interpreted CODE=0, and literal golden records
   RP: SCALAR 17 42 and RP: VECTOR 5 10 15 20.
5. Preserve original AWS SHA and all private JES/IEHLIST receipts under
   ignored workarea. Do not retry, overwrite, repack or reinitialize
   any image or source/target MVS dataset.

**Comparison limitation:** IBM cautions that IEBCOMPR should not
be used to compare load modules. Thus no IEBCOMPR load-module PASS or
byte-identical claim is part of this first design. An independent safe
raw binary equivalence method would require its own investigation.
Prove program fetch from the RESTORED STEPLIB and matching directory
attributes instead. Track A's FB80 IEBCOMPR does not prove this path.

## Approval gates and references

The owner approved the exact Track B scratch identity, selection,
restored-dataset and verification design on 18 November 2026. Source-controlled
JCL, generator, static and MVS read-only preflight, and offline safety tests
have now been implemented. Distinct authorization is still required
before any tape initialization/mount/write, MVS scratch allocation,
conditional remount, or executable smoke job. No producer/installer
release acceptance is implied.

Authorities: project TA.1 milestone/kickoff; TA.0 inventory member
MR10_LOAD(ICINT19), JOB 9060 IEHLIST and JOB 9061 executable-use
receipts; canonical MRREGRES source; accepted prior MVS IEBCOPY
experiments. MVS 3.8j IEBCOPY load-library examples:
https://www.jaymoseley.com/hercules/backup_restore/index.htm
IBM IEBCOMPR load-module caution:
https://www.ibm.com/docs/en/zos/2.5.0?topic=utilities-iebcompr-compare-data-sets-program

## Implementation checkpoint — 18 November 2026

See [Track B implementation and offline verification](ta1b-implementation-20261118.md). The two proposed JCL decks are `TA1BWRIT` and `TA1BREST`; `scripts/ta1b-contract` checks their safety contracts and derives source-pinned scalar/vector `TA1BGO` and IEHLIST FORMAT job bodies. `scripts/ta1b-preflight --live` gathers **read-only** live MVS catalog/DCB/member, Hercules tape image/VOLSER and unit evidence under `workarea/ta1b-operations/`. No execution of a Track B tape job, tape initialization or new DASD library has occurred, and no stateful operation is authorized by the design approval.

## Subsequent actual BTA102 write and separate readback gate (18 November 2026)

The owner subsequently approved and completed the one-shot scratch write.
`TA1BWRIT` JOB 9120 returned `IEBCOPY UNLOAD RC=0000`, and the
standard-labeled BTA102 AWS image was confirmed with four physical-file
block counts `3,8,2,0` and SHA-256
`c3b235ca78d221432199adcde1f7a83aead4f76bab0e0eaa19d77c81d9912210`.
The original no-stateful-operation description above documents the earlier
design-approval checkpoint and is superseded **only for the write stage**.
Restoration, any conditional remount, IEHLIST directory comparison and
restored executable GO remain separately gated; the owner has not approved
them by reporting the completed write. See
[the owner-reported write result](ta1b-write-evidence-and-readback-preparation-20261118.md).
