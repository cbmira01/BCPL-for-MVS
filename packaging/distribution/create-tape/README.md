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

## TA.1B first approved invocation — preflight-only halt

The owner authorized the first BTA102 scratch write but the invocation
on GitHub `51c56b326fc48a1f47d9e4b19101f0694f333387` stopped
during the first guest unit-status check, before any media creation,
attempt marker, mount or production JES submission.
A narrowly corrected `scripts/run-ta1-track-b-write` now accepts
MVS `O-NRD` **only for a verified EMPTY Hercules 0480**, while
requiring MVS `O` after mount. Ambiguous, foreign-media,
offline or allocated conditions remain blocked. See
[TA.1B unit gate correction](ta1b-first-write-gate-correction-20261118.md).
The original media-write authorization scope is unchanged and the
one-shot runner refuses a previous stateful attempt if one exists.

## TA.1B second first-guard halt — prefix-aware MVS status check

A further invocation at `efab256a987512b9e524557293faff99f206fac2`
failed during the FIRST read-only writer readiness check (before media
creation or an attempt receipt), because the writer insisted that the
MVS unit status row begin at column 1. The original read-only preflight
passed using an in-line lookup. The updated writer now searches within
each console line while strictly requiring one unit row and checking
`O` / `O-NRD` by mount phase. On a future mismatch it supplies a
bounded status-line excerpt rather than another opaque failure.
See [second write-gate correction](ta1b-second-write-gate-correction-20261118.md).
No fresh media initialization, remount, JES unload, DASD restoration,
or GO execution is claimed.

## Track B: exact duplicate MVS unit line (third gate correction)

The owner reported two identical status records,
`23:36:00 / 480  3400 O-NRD /REMOV 481  3400 OFFLINE`,
during the first read-only `run-ta1-track-b-write` guard.
This was before any attempt marker, image, tape mount or production JES job.
The writer now deduplicates **only byte-identical** unit 480 records,
rejects conflicting observations and requires MVS `O` after mounting.
The change is limited to console parsing and diagnostics; the
original authorization and no-retry media safeguards remain intact.
See [third gate evidence](ta1b-third-write-gate-correction-20261118.md).

## Track B successful BTA102 unload and guarded restore preflight (18 November 2026)

The owner reported MVS `TA1BWRIT` JOB **9120**, IEBCOPY UNLOAD
RC=0000, with a complete standard-label single-dataset AWS tape
(layout `3,8,2,0`) and immutable BTA102 SHA-256
`c3b235ca78d221432199adcde1f7a83aead4f76bab0e0eaa19d77c81d9912210`.
Original evidence is retained in ignored
`workarea/ta1b-operations/BTA102-track-b-write-20261118T235204Z-9548/`.

The new `scripts/run-ta1-track-b-restore` defaults to read-only live
MVS/Hercules preflight, including strict source, target-absence,
original JES, label/filemark, full inventory, checksum and tape unit
checks. Under **separate owner authorization only**, `--run` can
conditionally mount the *same* BTA102 AWS image and submit one
`TA1BREST` job to new DASD `HERC02.BCPL.TA1B.LOAD`.
It does not create/reinitialize/overwrite the AWS tape, catalog
a tape dataset, or run the MR10 `ICINT19` GO. The script retains
private receipts and enforces a durable no-retry marker before any
stateful action. Its **26 isolated synthetic tests PASS**.
See [Track B write evidence and readback gate](ta1b-write-evidence-and-readback-preparation-20261118.md).

**Status:** TA.1 Track B WRITE PASS (qualified); independent restoration,
IEHLIST directory comparison and executable GO still pending separate
approval and actual MVS verification.

## TA.1B independent restore preflight: live PASS (18 November 2026)

The owner executed `scripts/run-ta1-track-b-restore` in default
read-only mode at `52c128ca4dac2b82549114976f4f4eee807aa9d6`.
The verified original JOB 9120 BTA102 receipt and AWS SHA-256 were
unchanged, 0480 was EMPTY, and the new target
`HERC02.BCPL.TA1B.LOAD` did not exist. The MVS-facing run saved
private evidence at
`workarea/ta1b-operations/BTA102-track-b-restore-20261119T002435Z-10407/`.
See [the read-only preflight record](ta1b-restore-readonly-preflight-20261118.md).
No remount, PDS creation, restore, IEHLIST or GO occurred. A
one-shot `TA1BREST` will require **separate explicit owner
stateful authorization**; the exact-image conditional mount and
no-retry refusal are already controlled by the committed runner.

## TA.1B independent IEBCOPY restore PASS and directory comparison gate

The owner authorized the independent restore, and `TA1BREST` JOB
**9136** completed IEBCOPY RESTORE **RC=0000**, creating
`HERC02.BCPL.TA1B.LOAD(ICINT19)` on DASD **TSO002**, `PO/U/0/6144`.
BTA102 retained original AWS SHA-256
`c3b235ca78d221432199adcde1f7a83aead4f76bab0e0eaa19d77c81d9912210`.
Original private MVS evidence:
`workarea/ta1b-operations/BTA102-track-b-restore-20261119T021135Z-10863/`.

The new `scripts/run-ta1-track-b-directory` defaults to read-only
live `dspal stat/ls` MVS inquiries and checks saved JOB 9136 evidence
and immutable BTA102. Only after **separate owner approval** may
`--run` submit exactly two one-shot `IEHLIST LISTPDS FORMAT` jobs:
source TSO003 and restored TSO002. It verifies job RC=0000,
IEF142I and matching nonalias `ICINT19` entry `000000`/attrs `02E2`.
It never initializes, mounts or rewrites tape, modifies an existing
load library, or executes the restored module. **35/35 offline tests
PASS** across the extended standalone checks and the tracked contract
module. Source/target IEHLIST and actual restored-STEPLIB GO remain
unexecuted and separately authorized. See
[the restore and directory-stage record](ta1b-restore-evidence-and-directory-gate-20261118.md).

## TA.1B source/restored directory read-only preflight PASS

The owner executed `scripts/run-ta1-track-b-directory` without
`--run` on GitHub `main` `58f98db10dd5b790ea52c488070c6de2a98b98d5`.
The MVS-facing preflight returned PASS: source MR10_LOAD TSO003
and restored HERC02.BCPL.TA1B.LOAD TSO002 both PO/U/0/6144,
with BTA102 SHA-256 and JOB 9136 receipt validated. Evidence:
`workarea/ta1b-operations/BTA102-track-b-directory-20261119T023717Z-11735/`.
No IEHLIST JES jobs or executable GO occurred. The separately
authorized next stage, **not approved by this PASS**, is the guarded
one-shot submission of `TA1BSRC` and `TA1BDST` for source/restored
ICINT19 directory attributes. See
[the live read-only preflight](ta1b-directory-readonly-preflight-20261118.md).

## TA.1B IEHLIST directory match PASS and restored ICINT19 GO preflight

The owner executed the approved pair of read-only IEHLIST jobs:
`TA1BSRC` **JOB 9151** for source TSO003 and
`TA1BDST` **JOB 9152** for restored TSO002.
Both reported `DIRLIST IEHLIST RC=0000`; nonalias `ICINT19`
entry `000000` and attrs `02E2` matched.
The original BTA102 SHA-256 stayed
`c3b235ca78d221432199adcde1f7a83aead4f76bab0e0eaa19d77c81d9912210`.
Evidence:
`workarea/ta1b-operations/BTA102-track-b-directory-20261119T024927Z-11906/`.

The new `scripts/run-ta1-track-b-go` defaults to **read-only MVS
source/restored inquiry**. It validates actual saved IEHLIST jobs
9151/9152 from raw JES reports, original restored-load JOB 9136,
BTA102 SHA, exact source TSO003/restored TSO002 PO/U/0/6144,
and the pinned canonical MRREGRES scalar/vector JCL.
**32 isolated tests PASS**, including altered evidence, source
STEPLIB drift, report tampering, and the one-shot no-retry guard.

A separately owner-authorized `--run` can submit **one** authenticated
`TA1BGO` eight-step MR10 scalar/vector job, with all three `STEPLIB`
DDs pointing at restored `HERC02.BCPL.TA1B.LOAD`, and only temporary
`&&` outputs. It would require all steps RC=0000, corresponding
IEF142I messages, interpreted CODE=0 and exact scalar/vector RP
records. No tape operations or persistent MVS dataset modification
occur in default mode, and actual GO remains **not yet authorized**.
See [directory PASS and GO preflight design](ta1b-directory-match-and-go-preparation-20261118.md).

## TA.1B restored-STEPLIB GO live read-only preflight PASS — 19 November 2026

The owner ran the committed `scripts/run-ta1-track-b-go` in default
read-only mode on GitHub main `acae8bd36b222bc4e3ef7ac5bee57ea482c1dcf3`.
The actual guest checks reported IEHLIST jobs 9151/9152 accepted
(entry `000000`, attrs `02E2`), source PDS TSO003 and restored
PDS TSO002 both PO/U/0/6144, and original BTA102 SHA-256 unchanged.
Private evidence: `workarea/ta1b-operations/BTA102-track-b-go-20261119T114903Z-13321/`.
There was **no ICINT19 GO JES submission or MVS/tape modification**.
The separate owner authorization for a single `TA1BGO` remains
pending. See [the live restored-GO preflight record](ta1b-go-readonly-preflight-20261119.md).

## TA.1B actual tape-restored ICINT19 executable-use PASS — 19 November 2026

On separately authorized `run-ta1-track-b-go --run`, the owner
reported MVS **TA1BGO JOB 9165**: all eight original scalar/vector
MRREGRES steps RC=0000, three interpreter `ICINT19` invocations,
and exact scalar/vector `RP:` output PASS from the
`HERC02.BCPL.TA1B.LOAD` restored `STEPLIB`. The runner checks
three interpreted `CODE=0` outcomes and eight `IEF142I`
success confirmations as part of PASS. Original BTA102 SHA-256
`c3b235ca78d221432199adcde1f7a83aead4f76bab0e0eaa19d77c81d9912210`
remained unchanged. Actual private evidence:
`workarea/ta1b-operations/BTA102-track-b-go-20261119T121015Z-13509/`.

**Track B PASS (qualified)** now includes IEBCOPY unload JOB 9120,
independent restore JOB 9136, matching source/restored directory
IEHLIST JOBS 9151/9152 (entry `000000`, attrs `02E2`),
and restored executable-use JOB 9165.
Track A previously passed its two-dataset SL tape round-trip.
The [TA.1 formal qualified acceptance candidate](../../milestones/tape-artifact-release/ta1-qualified-acceptance-candidate-20261119.md)
is ready for owner review; TA.1 is **not formally closed**
without approval. No byte-identical load module or public release
acceptance is claimed. The next march, **TA.2 — Manifest-Driven Tape
Producer**, remains separately scoped and unauthorized for stateful
production. See [GO evidence](ta1b-restored-go-evidence-20261119.md).

## TA.1 formally closed (qualified) and TA.2 transition — 19 November 2026

The owner accepted **TA.1 — Multi-Dataset Tape Mechanics CLOSED
(qualified)** after Track A's BTA101 two-logical-dataset
standard-label round trip and Track B's BTA102 IEBCOPY
load-module unload/restore, source/restored IEHLIST comparison
and **TA1BGO JOB 9165** restored-`ICINT19` execution.
The original experimental tapes must not be overwritten or
repurposed as a release candidate. See
[formal TA.1 closure](../../milestones/tape-artifact-release/ta1-formal-qualified-closure-and-ta2-transition-20261119.md).

**TA.2 — Manifest-Driven Tape Producer** is ready for **design and
read-only preflight only**. The proposed 20-position TA.0 design
inventory is not a frozen candidate, and the native compiler's
absence remains explicitly disclosed in any scoped release.
No new AWS volume, VOLSER, source freeze, installation or
publication is authorized by this transition. See
[TA.2 kickoff](../../milestones/tape-artifact-release/ta2-kickoff-20261119.md).

## TA.2 — Initial offline manifest producer and validation

The reviewed first TA.2 implementation is `scripts/ta2-offline` with tests
`tests/test_ta2_offline.py` and details in
[TA.2 offline implementation](ta2-offline-producer-implementation-20261119.md).
The default mode accepts only the design stage as a concise, read-only
inventory review. `--candidate` is a strict, separately authorized frozen
manifest/registry/evidence gate. `--emit-jcl` only renders a validated JOB-less
JCL body; it never submits it. There is no candidate manifest, registry
reservation, tape write, full producer, or TA.2 acceptance yet.

### TA.2 read-only MVS source inventory collector

After separate approval of **read-only MVS inquiries**, invoke
`scripts/ta2-source-preflight --live` from the repository root.
This collects one `dspal stat` and `dspal ls` per selected development
PDS (18 each), checks DCBs and selected member presence against the
canonical design manifest, and stores SHA-256-pinned private records under
`workarea/ta2-source-preflight/`. Unselected development members are
reported but never selected for release. This is neither a candidate
staging operation nor an MVS content comparison; it does not write DASD/tape.
Offline parser/safety tests: `tests/test_ta2_source_preflight.py`.

### TA.2 independent saved-source-evidence review

`scripts/ta2-source-review --evidence workarea/ta2-source-preflight/<run-id>`
performs a **host-only, read-only** independent recheck of a completed
`ta2-source-preflight --live` MVS inquiry run. It verifies SHA-256 checksums,
success RC and original MVS dataset/member listings against the single TA.0
manifest, and refuses changed or incomplete evidence. The reviewer neither
submits an MVS job nor modifies the source evidence. The 19 November MVS
source-inventory checkpoint is recorded in the
[TA.2 implementation record](ta2-offline-producer-implementation-20261119.md).
It does not substitute for the future isolated staging inventory or source
byte/provenance verification.

### TA.2 read-only source-capacity inquiry (MVS IEHLIST)

`scripts/ta2-capacity-preflight --live --source-evidence <saved-run>`
first independently audits the saved 18-source DCB/member inventory and then
uses the existing **read-only** `tools/datasets/dspal stat` all-datasets
LISTDS/IEHLIST query to record source track allocation, high-water and
directory-block capacity. It rejects missing/ambiguous metadata, preserves
private SHA-256-pinned evidence under `workarea/ta2-capacity-preflight/`,
and does **not** allocate or copy MVS datasets, mount tapes, or reserve
candidate identities. Source PDS high-water figures are only conservative
staging-planning evidence, not exact curated payload sizing.
See [the capacity-preflight design and evidence contract](ta2-capacity-preflight-20261119.md).

### TA.2 staging worksheet (read-only MVS recheck)

`scripts/ta2-stage-plan --live --source-evidence <saved-source-run>
--capacity-evidence <saved-capacity-run>` independently replays the
checksum-pinned source and capacity inquiries, and **then** performs a
fresh, read-only MVS `dspal stat`/IEHLIST observation. An exact 18-PDS
source-capacity match produces a private checksum-pinned worksheet under
`workarea/ta2-stage-plan/`; destination DSNs and `SPACE` values remain
**unset**. No stage allocation/IEBCOPY/tape or candidate identity is performed.
See [the staging-plan evidence contract](ta2-stage-plan-20261119.md).

### TA.2 selective IEBCOPY staging-deck proposal (offline only)

`scripts/ta2-stage-jcl` independently replays the saved stage-plan,
capacity and 127-member source evidence, and derives **18 selective
IEBCOPY stages** from the one TA.0 manifest. Without an explicit separate
staging namespace/volume/SPACE allocation proposal it is a non-mutating
source-selection check. With such a proposal it emits **only a new private
JOB-less draft** under `workarea/`, never submits MVS, touches DASD, or
assigns release media. No staging parameters or authorization exist yet.
See the [design and exact remaining gates](ta2-selective-staging-deck-20261119.md).

### TA.2 owner-approved namespace and read-only target probe

The **approved** staging namespace is
`HERC02.BCPL.TA2STG.BT0003`–`BT0020`; the approved future
production tape VOLSER format is `BCnnnn` (`BC0001`–`BC9999`),
**without any current VOLSER reservation**.

`scripts/ta2-target-preflight --stage-evidence <run> --volume TSO002 --live`
independently replays the original source/capacity/stage receipt and
performs two **read-only MVS JES** inquiries: exact TSO LISTDS catalog
absence for all 18 staging names, followed by a raw IEHLIST VTOC
observation of the *proposed* volume. No allocation, copy or tape I/O
is performed. Its compact result and original JES evidence are private
under `workarea/ta2-target-preflight/`. Raw VTOC free-space and
uncataloged-collision interpretation still require follow-up review;
`TSO002` is only a proposed volume for the read-only inquiry. See
[the target safety contract](ta2-namespace-volser-and-target-preflight-20261119.md).

### TA.2 saved target/VTOC evidence review (read-only)

`scripts/ta2-target-review --target-evidence <saved-target-run> --live`
checks the complete saved TSO LISTDS/IEHLIST evidence and chained
source/capacity/staging receipts, and **then** performs a new read-only
MVS catalog and VTOC recheck, retaining full JES records under
`workarea/ta2-target-review/`. It records the source allocated-space
totals and, *only if MVS provides an unambiguous volume summary*, the
volume-reported empty tracks. It never computes an approved per-PDS
staging `SPACE` or submits state-changing JCL. See the
[TA.2 saved-VTOC evidence contract](ta2-target-saved-vtoc-review-20261119.md).
