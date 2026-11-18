# TA.1 Track A — two-dataset round-trip acceptance candidate

**Project:** BCPL for MVS 3.8 Reconstruction
**Milestone:** Tape artifact release
**March:** TA.1 — Multi-Dataset Tape Mechanics
**Date:** 17 November 2026 local (MVS evidence directories dated 18 November UTC)
**Status:** Track A **PASS (qualified)**, including final saved-evidence physical-file review on 18 November 2026. TA.1 remains IN PROGRESS for Track B.

## Source and evidence quality

The owner ran the committed one-shot producer at GitHub main
0ba5ac4d3ee30970bdcb96936f4f6f4188feca68, then the readback at
de005c09aa443ba7f904215ad3eac804c71af046 against actual MVS 3.8J.
This record is based on the owner's console results, not on assistant
access to private JES printer/SYSPRINT or HETMAP files.

The source was read-only HERC02.BCPL.DIST.DOCS, PO/FB/80/800.
The NEW scratch image was mvs-state/tape/bcpl-ta1-a-20261117-01.aws,
VOLSER BTA101, Hercules 3420 address 0480, with uncataloged sequential
logical tape datasets BCPL.BT0001 and BCPL.BT0002. The restored NEW DASD
datasets are HERC02.BCPL.TA1A.FBREST (PS/FB/80/800) and
HERC02.BCPL.TA1A.PDSREST (PO/FB/80/800), cataloged on DASD only.

## Executed MVS work

| Job | Execution | Owner-reported result |
| --- | --- | --- |
| TA1AWRIT 9076 | BOOTSTRP IEBGENER, UNLOAD IEBCOPY | Both RC=0000; two standard-label datasets |
| TA1AR001 9084 | RESTORE IEBGENER | RC=0000; PS attributes checked |
| TA1AR002 9086 | RESTORE IEBCOPY | RC=0000; PO DCB and seven restored members checked |
| TA1ACOMP 9089 | CMPFB and CMPPDS IEBCOMPR | Both independent RC=0000 |

The owner-reported readback runner verified the original write receipt
and fresh read-only preflight, source-vs-restored attributes, full restored
PDS member inventory, required JES step summaries, and original-image
SHA-256 after every stage. No repeat tape write or image initialization
was reported.

**Image SHA-256 before and after readback, unchanged:**

d5900cbccaaa2f7eb1bcc59ae30847540e6911c577dafa5e131c0b3a9c8e3fe2

Original ignored write evidence:
workarea/ta1-operations/BTA101-track-a-execution-20261118T010626Z-5215/

Ignored readback evidence:
workarea/ta1-operations/BTA101-track-a-readback-20261118T020430Z-5920/

## Remaining evidence and acceptance boundary

The write runner saved actual hetmap --labels, --files and --all output,
original JES report and device-state observations. The owner did not initially paste the complete physical-file/block
table or SYSPRINT into the conversation. The later, separately reported
saved-evidence reviewer established the seven physical-file block counts
recorded below; raw private listings are still not present in this conversation.

The new read-only scripts/review-ta1-track-a verifies both retained
HETMAP file maps, seven expected physical file segments of an SL
two-dataset tape (with nonempty data files), both labeled dataset
sequences, the original image hash, original and restored job receipts,
two IEBCOMPR RC=0 steps, restored DCB and seven PDS members. This is
an audit of recorded MVS evidence, not another MVS job or tape action.
Unexpected filemark layout must be investigated, not waived.

Track A has now passed its bounded qualified acceptance conditions.
This does not close TA.1 or prove recipient installation or the RECFM=U
load-library path.
The separate Track B design is in
ta1-track-b-design-proposal-20261117.md.

The owner forbids cataloging distribution tapes on MVS. Tape data sets
remain uncataloged; new DASD restore targets only are cataloged.
Never overwrite or reinitialize BTA101, or automatically retry an
uncertain job.

## Final saved-evidence review — 18 November 2026

The owner ran the Git-controlled, strictly read-only
`packaging/distribution/create-tape/scripts/review-ta1-track-a` after
fast-forwarding GitHub `main` to
`4845be9db79ecaa6b8dd4e777ba32bbcf4983886`.
The reviewer rechecked the saved MVS/JES step summaries, physical-file
reports from `hetmap -f` and `hetmap -a`, both logical standard-label
datasets, restored DCB and member inventory, and the existing AWS checksum.
The owner supplied the reviewer PASS output; the private source reports
remain under ignored `workarea/` and have not been separately read by
the assistant.

**Track A saved-evidence review: PASS (qualified).**

| Hercules physical tape file | Blocks | Role inferred from verified SL layout |
| ---: | ---: | --- |
| 1 | 3 | `VOL1` and dataset 1 `HDR1/HDR2` |
| 2 | 3 | `BCPL.BT0001` FB80 data |
| 3 | 2 | Dataset 1 `EOF1/EOF2` |
| 4 | 2 | Dataset 2 `HDR1/HDR2` |
| 5 | 25 | `BCPL.BT0002` IEBCOPY unload data |
| 6 | 2 | Dataset 2 `EOF1/EOF2` |
| 7 | 0 | Terminal empty tape file |

The reviewer reported **seven physical files** with block counts
`3, 3, 2, 2, 25, 2, 0`, 28 payload-data blocks across the two
logical datasets. This is physical tape structure, **not** seven MVS
datasets or a claim of seven separately cataloged objects.

The verified original image SHA-256 remains
`d5900cbccaaa2f7eb1bcc59ae30847540e6911c577dafa5e131c0b3a9c8e3fe2`
after MVS JOBS 9076, 9084, 9086 and 9089. The reviewer also reported
both IEBCOMPR RC=0000, restored PS/PO FB80 attributes, and the exact
seven-member PDS inventory, without another MVS job or tape catalog
operation.

**Disposition:** Track A's bounded acceptance conditions have
passed on owner-supplied MVS/Hercules evidence. Track A is
**PASS (qualified)**, preserving the qualification that underlying
private JES/SYSPRINT and `hetmap` listings were reviewed by the
project runner rather than directly available to the assistant.
**TA.1 is still IN PROGRESS** because Track B's separate `RECFM=U`
load-library restore and actual `ICINT19` executable-use test have
not run. No Track B design approval, new tape initialization, mount,
write, or MVS execution is implied by this result.

