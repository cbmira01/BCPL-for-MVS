# TA.1 — Track A first multi-dataset scratch tape write — owner-provided execution evidence

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.1 — Multi-Dataset Tape Mechanics  
**Date:** 17 November 2026, Louisville local; evidence directory timestamp 18 November 2026 UTC  
**Status:** Write stage completed; independent restoration and comparison PENDING

## Exact observed run

The owner authorized initialization of one new image, mount at 0480,
one TA1AWRIT submission, and post-write inspection. The owner ran
`packaging/distribution/create-tape/scripts/run-ta1-track-a --run`
from GitHub main at commit `0ba5ac4d3ee30970bdcb96936f4f6f4188feca68`.
The console transcript supplied to the project reports:

- Fresh live preflight PASS before image creation.
- Created `mvs-state/tape/bcpl-ta1-a-20261117-01.aws`, initialized
  as standard-labeled VOLSER `BTA101` and mounted on Hercules `0480`.
- Submitted the approved two-step `TA1AWRIT` exactly once as MVS JOB **9076**;
  the helper reported RC=0. The runner contains checks that BOOTSTRP and
  UNLOAD each appear in the JES job summary with RC=0000. The complete
  JES report itself was not included in the conversation excerpt.
- The runner reported its expected two ordered standard-label groups
  for `BCPL.BT0001` and `BCPL.BT0002`, and ran read-only hetmap
  label/file/all inspections. The full label and physical-filemark listings
  are saved locally, not yet independently reviewed in the conversation.
- The runner printed SHA-256:
  `d5900cbccaaa2f7eb1bcc59ae30847540e6911c577dafa5e131c0b3a9c8e3fe2`.
- Preserved ignored evidence directory:
  `workarea/ta1-operations/BTA101-track-a-execution-20261118T010626Z-5215/`.

The full SYSOUT, step-level messages, exact physical filemark/block counts
and final device mount/demount state were NOT supplied to this conversation.
Do not fabricate those details or promote this report to full acceptance.

## Boundary and next step

This is a successful operator-reported first two-dataset MVS write stage;
**not** a completed TA.1 Track A round-trip, clean-target installation,
release image or publication approval.

The remaining approved design (but **not yet separately authorized live
operation**) is to restore `BCPL.BT0001` via IEBGENER to a NEW cataloged DASD
`HERC02.BCPL.TA1A.FBREST`, restore `BCPL.BT0002` via IEBCOPY to a
NEW cataloged DASD `HERC02.BCPL.TA1A.PDSREST`, then independently compare
FB80 records and all PDS members using IEBCOMPR TYPORG=PS and TYPORG=PO.

The Track A readback entry point `scripts/run-ta1-track-a-readback`
performs read-only preflight by default. Its `--run` is separately gated,
checks the original write evidence and immutable image checksum before and
after all operations, selectively remounts the SAME existing image only
when 0480 is empty, protects the new DASD targets, and refuses all retries.
It MUST NOT be invoked with `--run` without new explicit owner approval.

**Owner direction:** NEVER catalog any distribution-tape datasets on MVS;
temporary new DASD restore targets may be cataloged.

**Unresolved TA.1:** independent restored content evidence and the Track B
PO/U/0/6144 `MR10_LOAD(ICINT19)` executable round trip.


## Subsequent restoration checkpoint (17 November 2026)

The owner subsequently completed the separately authorized readback:
TA1AR001 JOB 9084 RC=0000; TA1AR002 JOB 9086 RC=0000;
TA1ACOMP JOB 9089 with both independent IEBCOMPR steps RC=0000.
The original BTA101 image SHA-256 was unchanged.
See [the Track A round-trip record](ta1-track-a-roundtrip-review-20261117.md).
Earlier write-stage PENDING statements are historical and superseded.
