# Create tape

Producer-side source for AWS tape creation and validation.

- `jcl/`: MVS jobs for unloading distribution datasets to tape.
- `scripts/`: host-side orchestration and manifest-driven job generation.
- `tests/`: tape structure and read-back verification.

This side may use the project development environment (WSL, Python, Hercules, `dspal`). Writing tape or executing JES jobs requires explicit separate approval. An initial manual job submission helper is implemented; no end-to-end tape producer exists. The [approved distribution design](../native-cambridge-compiler-distribution-decisions-20261108.md) makes the release manifest authoritative for `BCPL.BTnnnn` logical tape dataset order and producer/consumer JCL generation; the accepted one-dataset scratch tests below predate that naming convention.

## Manual scratch-PDS tape experiment (accepted on MVS 8 November 2026)

Four independent JCL job bodies are in the jcl directory. All four
completed RC=0000 in the recorded experiment (JOBS 2469, 2472, 2474,
2477); rerunning still requires fresh scratch state and approval. They contain
no JOB card or credentials. MVS execution, image creation, mounting,
and dataset changes require separate operational approval.

| Job | Proposed action |
| --- | --- |
| TP01PRE | Copy DIST.DOCS into a new scratch source PDS |
| TP02UNLD | IEBCOPY unload the scratch PDS to tape dataset 1 |
| TP03REST | Restore the tape unload into a different new PDS |
| TP04COMP | Compare original and restored PDSes with IEBCOMPR |

Input PDS: HERC02.BCPL.DIST.DOCS (read-only).
Scratch PDSes: HERC02.BCPL.TPTEST.SRC and
HERC02.BCPL.TPTEST.RESTORE, both must not exist before creation.
Tape dataset: HERC02.BCTP01, VOLSER BTP001, LABEL=(1,SL),
observed Hercules 3420 at address 0480.

Media is a NEW uncompressed AWS file, proposed name
mvs-state/tape/bcpl-pdstest-20261108-01.aws. The existing bcpl01.aws
must remain untouched. Both mvs-state (except .gitkeep) and workarea
are Git-ignored: never place tape binaries in source-controlled folders.

**Operating gates before any authorized execution:**

1. Reconfirm Git revision, effective MVS identity, tape unit and status.
   Refuse existing scratch PDSes, existing tape filenames and reused VOLSERs.
2. Confirm the installed hetinit options before initializing a NEW image.
3. Review the full authenticated JES job deck and submit one job at a time.
   The project dspal submit command requires a previously installed managed
   JCL PDS member: it cannot directly submit a host-side JCL file.
   Use scripts/submit-scratch-job to preview and, after confirmation, submit one host-side JCL body with existing dspal authentication.
4. Check actual payload JES job IDs, step RCs, IEBCOPY/IEBCOMPR output,
   tape label handling, and MVS device-allocation messages.
5. Before unmounting, ensure MVS has released the tape. Hercules devinit
   does not itself release an MVS allocation.
6. Compare all seven restored member names and records, and confirm the
   restored DCB. Check AWS structure and filemarks separately.
7. On failure, stop; do not append to or overwrite the existing image.

This scratch tape does NOT define the eventual distribution tape layout.
The first dataset on a release tape must provide simple human-readable
bootstrap, offload and installation instructions.

The JCL is based on IBM OS/VS2 MVS Utilities Release 3.8
(GC26-3902-1), IEBCOPY examples 13/14 and IEBCOMPR TYPORG=PO.

Offline checks (do not submit JES or mount tapes):

    python3 -m unittest discover -s packaging/distribution/create-tape/tests -p 'test_*.py' -v

The bounded real-MVS experiment was accepted after IEBCOMPR RC=0000. See [the full receipt](scratch-pds-roundtrip-acceptance-20261108.md). No end-to-end distribution tape or installer is accepted.

## Operator-controlled manual scratch job submission

From the repository root, preview the full deck with its password redacted:

    packaging/distribution/create-tape/scripts/submit-scratch-job TP01PRE

Default mode never contacts JES. Only the four scratch jobs are accepted.
Since the JCL uses fixed HERC02 dataset names, an alternate effective
MVS HLQ is rejected.

After reviewing prerequisites and the deck, submit ONE job interactively:

    packaging/distribution/create-tape/scripts/submit-scratch-job TP01PRE --run

A typed SUBMIT TP01PRE confirmation is mandatory. No unattended mode exists.
The helper uses the existing dspal submit-and-wait mechanism and requires
JES RC=0. The authenticated deck exists only in a private temporary file
outside Git, which the existing tool removes afterward. The password is
read from the ignored config/dspal.local.yaml and is never stored in the
tracked job bodies. Treat JES printer output as sensitive evidence.

Before TP01PRE: verify the scratch PDS HERC02.BCPL.TPTEST.SRC does not
exist; inspect the seven members of HERC02.BCPL.DIST.DOCS. The original
PDS is opened read-only. Before TP02UNLD: verify the new tape image was
initialized once, its VOLSER is BTP001 and device 0480 is correctly
mounted and released by MVS. The helper checks that the image file
exists, but it cannot verify its labels, mount, allocation or position.
Check the actual installed hetinit -h before creating any new tape.

Before TP03REST: do NOT reinitialize the tape image. Confirm the
restore PDS is absent and the correct tape is mounted. After every job,
inspect its JES number, step RC, relevant utility messages, and dataset
inventory. Only run TP04COMP after verifying the restored PDS.

Offline checks, with no JES/tape changes:

    python3 -B -m unittest discover \
        -s packaging/distribution/create-tape/tests -p 'test_*.py' -v

Keep all AWS images under Git-ignored mvs-state/tape, and any local
reports under Git-ignored workarea. Never commit tape media.

The existing Hercules `hetmap` tool can inspect tape labels and file
structure without a JES job. See [tape inspection](../tape-inspection-capabilities-20261108.md).

## Object-library tape experiment (accepted 8 November 2026)

The separate **TO01PRE–TO04COMP** jobs test binary FB80
`HERC02.BCPL.BOOT.OBJ` -> new scratch PDS -> new BTO001 AWS tape ->
new restored scratch PDS -> IEBCOMPR. The **TO05LINK** stage uses native
bootstrap regressions 00 and 03, with an *explicitly gated* restored
PDS selection in the existing JCL generator. No approved release is
inferred from a scratch experiment.

See [object-library tape test plan](object-library-tape-test-plan-20261108.md)
for the original design and [accepted MVS evidence](object-library-tape-roundtrip-acceptance-20261108.md)
for JOBS 2483/2486/2488/2491, tape labels and SHA-256, IEBCOMPR,
and both restored-library native regression results.

Preview all new jobs with `scripts/submit-scratch-job TO01PRE` (similarly
TO02UNLD, TO03REST, TO04COMP). Submissions, mounts and image creation
remain separately authorized operator actions.

Offline checks: `python3 -B -m unittest discover -s packaging/distribution/create-tape/tests -p 'test_*.py' -v`.

## TA.1 Track A (design approved; live media not authorized)

See [TA.1 Track A preflight](ta1-track-a-preflight-20261117.md).
The four TA1A JCL bodies are staged with a read-only ta1-preflight checker,
14 offline JCL/negative tests, and a separately tested one-shot authenticated
submit-ta1-job helper (7 offline tests). Its default mode makes no JES calls;
its --run mode is subject to independent, explicit stateful owner approval.
No image, mount, restore or MVS-write acceptance follows from this design.

### Owner-authorized TA.1 Track A single-run entry point

Use `scripts/run-ta1-track-a --run` from the repository root after GitHub
main is updated. This single command combines fresh read-only catalog,
device and media collision checks, exclusive AWS initialization, mount,
once-only authenticated TA1AWRIT submission, then saved JES/hetmap evidence.
It requires a terminal and typed confirmations; it never retries and never
restores or catalogs tape datasets. On any failure, preserve media and
`workarea/ta1-operations/` evidence and report the result. See the
TA.1 Track A preflight document for the exact approval boundary.

## TA.1 Track A operator write completed; readback not yet authorized

The owner-provided 17 November 2026 transcript shows TA1AWRIT JOB 9076
ran on newly initialized, standard-labeled scratch BTA101 image, with
two ordered BCPL.BT0001 / BCPL.BT0002 label sequences and SHA-256
d5900cbccaaa2f7eb1bcc59ae30847540e6911c577dafa5e131c0b3a9c8e3fe2.
See [the write-stage evidence](ta1-track-a-write-evidence-20261117.md).

A separate `scripts/run-ta1-track-a-readback` entry point has been
prepared and offline-tested for one-shot IEBGENER/IEBCOPY restore and
independent IEBCOMPR TYPORG=PS/PO. Its default mode is READ-ONLY;
its `--run` mode (including selective remount and new DASD allocation)
requires separate owner approval. The program requires the original
JOB 9076 receipt, matching original image SHA-256 and clean scratch
target catalog; any ambiguous result halts without retry. Tape datasets
remain uncataloged throughout.


## Track A complete two-dataset round-trip: qualified owner-reported PASS

The separate readback restored both datasets on MVS and ran both
IEBCOMPR comparison steps RC=0000: JOB 9084 (PS restore), JOB 9086
(PDS restore), JOB 9089 (two comparisons). The original JOB 9076
image SHA-256 remained unchanged. See
[the bounded Track A round-trip record](ta1-track-a-roundtrip-review-20261117.md).

A strictly **read-only** saved-evidence/filemark checker is
scripts/review-ta1-track-a. It checks the original private JES summaries,
Hercules physical-file output, both standard-label datasets, restored
DCBs and PDS members, and the immutable original AWS SHA. It creates
no files, submits no JES, and changes no mounted tape or MVS dataset.
13/13 synthetic/negative tests PASS; actual physical-file counts must
come from owner-local HETMAP output before final filemark acceptance.

[Track B RECFM=U load library design](ta1-track-b-design-proposal-20261117.md)
is proposed for owner review. No Track B stateful operation is authorized.

## Track A final saved-evidence review — 18 November 2026

The owner ran the non-submitting `scripts/review-ta1-track-a`; result
`TA.1 TRACK A: saved MVS evidence PASS (qualified)`. The physical
standard-labeled AWS layout has seven file segments containing
`3, 3, 2, 2, 25, 2, 0` blocks. Source/restored MVS checks show
JOBS 9076, 9084, 9086 and 9089 at required RC=0000; restored PS/PO
attributes, seven PDS members and unchanged BTA101 SHA-256
`d5900cbccaaa2f7eb1bcc59ae30847540e6911c577dafa5e131c0b3a9c8e3fe2`.
See [Track A acceptance evidence](ta1-track-a-roundtrip-review-20261117.md)
for physical file roles and evidence qualifications.

**Track A PASS (qualified); TA.1 IN PROGRESS** pending the separately
designed `RECFM=U` Track B test. No new tape job, MVS state change,
or tape catalog operation is authorized by this record.

## TA.1 Track B: approved design and static implementation (18 November 2026)

The owner approved the [Track B RECFM=U design](ta1-track-b-design-proposal-20261117.md). Tracked fixed JCL `jcl/TA1BWRIT.jcl` and `jcl/TA1BREST.jcl` operate on a **proposed new** standard-label BTA102 AWS scratch tape and source-read-only `HERC02.BCPL.MR10KIT.LOAD(ICINT19)`; only the separate new DASD target `HERC02.BCPL.TA1B.LOAD` may eventually be cataloged. `scripts/ta1b-contract` validates fixed card/dataset/label/disposition contracts, generates a read-only IEHLIST FORMAT body and extracts eight pinned MRREGRES steps with exactly three restored-STEPLIB substitutions.

`scripts/ta1b-preflight --live` is a compact **read-only MVS-facing** source, catalog, VOLSER, tape-inventory and device check, using existing MVS LISTDS inquiries and Hercules inspection. It saves private evidence under ignored `workarea/ta1b-operations/` and does not initialize, mount, unload, restore or execute programs. The [implementation checkpoint](ta1b-implementation-20261118.md) records 44/44 dedicated offline tests passing. **Separate owner authorization for BTA102 initialization, MVS unload, restore, remount and GO is still required.**

## Track B live read-only preflight PASS; one-shot write runner awaiting approval

The owner reported `ta1b-preflight --live` PASS (18 November 2026):
source `MR10_LOAD(ICINT19)` PO/U/0/6144 on `TSO003`, BTA102 absent
among four inspected AWS images, new filename absent, Hercules 0480
empty, and scratch tape DSN/restore target uncataloged/absent.
See [the source-constrained evidence and write gate](ta1b-readonly-preflight-and-write-gate-20261118.md).

`scripts/run-ta1-track-b-write` is inert by default. Its `--run`
mode will demand **separate explicit media-write authorization**,
repeat the actual MVS/Hercules/VOLSER/source checks, exclusively create
the new AWS file, submit `TA1BWRIT` once, capture JES/hetmap labels
and filemarks, and record SHA-256. No automatic retry, remount,
restoration, restored ICINT19 execution, or tape cataloging.
Its **27/27** isolated negative/synthetic tests PASS; no BTA102 image
has been initialized or written by this checkpoint.
