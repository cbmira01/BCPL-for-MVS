# TA.1 Track A — two-dataset round-trip acceptance candidate

**Project:** BCPL for MVS 3.8 Reconstruction
**Milestone:** Tape artifact release
**March:** TA.1 — Multi-Dataset Tape Mechanics
**Date:** 17 November 2026 local (MVS evidence directories dated 18 November UTC)
**Status:** Operator-reported Track A write/restore/content compare PASS (qualified).
Physical-filemark review remains to be independently checked from the retained HETMAP reports. TA.1 remains IN PROGRESS for Track B.

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
original JES report and device-state observations. The owner did not
paste the complete physical-file/block table or SYSPRINT into the
conversation. We therefore do NOT invent the actual filemark counts.

The new read-only scripts/review-ta1-track-a verifies both retained
HETMAP file maps, seven expected physical file segments of an SL
two-dataset tape (with nonempty data files), both labeled dataset
sequences, the original image hash, original and restored job receipts,
two IEBCOMPR RC=0 steps, restored DCB and seven PDS members. This is
an audit of recorded MVS evidence, not another MVS job or tape action.
Unexpected filemark layout must be investigated, not waived.

Track A is a qualified acceptance candidate. It does not close
TA.1 or prove recipient installation or the RECFM=U load-library path.
The separate Track B design is in
ta1-track-b-design-proposal-20261117.md.

The owner forbids cataloging distribution tapes on MVS. Tape data sets
remain uncataloged; new DASD restore targets only are cataloged.
Never overwrite or reinitialize BTA101, or automatically retry an
uncertain job.
