# TA.1 Track A — approved design and pre-execution contract

**Project:** BCPL for MVS 3.8 Reconstruction
**Milestone:** Tape artifact release
**March:** TA.1 — Multi-Dataset Tape Mechanics
**Design decision:** Track A design approved by the owner, 17 November 2026
**Authority:** GitHub main, following TA.0 CLOSED (qualified)
**Execution status:** PREFLIGHT ONLY — NO TAPE INITIALIZATION, MOUNT, WRITE, RESTORE OR MVS DATASET CHANGE AUTHORIZED

## Track A identity and fixture

- Fresh proposed image: mvs-state/tape/bcpl-ta1-a-20261117-01.aws
- Proposed unique six-character scratch VOLSER: BTA101 (not yet live-verified unused or reserved)
- Historically observed Hercules 3420 device 0480; MVS unit 480 (not live-verified now)
- Read-only fixture source: HERC02.BCPL.DIST.DOCS (PO/FB/80/800)
- Logical tape dataset 1: BCPL.BT0001, LABEL=(1,SL), IEBGENER from DIST.DOCS(README), PS/FB/80/800
- Logical tape dataset 2: BCPL.BT0002, LABEL=(2,SL), IEBCOPY unload of DIST.DOCS, unload DCB to be observed rather than guessed
- Fresh DASD restore targets: HERC02.BCPL.TA1A.FBREST (PS/FB/80/800), HERC02.BCPL.TA1A.PDSREST (PO/FB/80/800)

BT0002 is a mechanical documentation-PDS unload fixture, not an operable installer. No production object, source or load library is a write target. The two dataset aliases are logical MVS dataset sequence, not Hercules physical tape file numbers. No release manifest or VOLSER reservation is created by the scratch plan.

## Source and operation sequence

Tracked, reviewable, JOB-card-free JCL bodies:

- jcl/TA1AWRIT.jcl — one two-step IEBGENER then IEBCOPY job; VOLUME RETAIN in first allocation, explicit labels 1 and 2, separate DSNs, second step conditional on first RC=0
- jcl/TA1AR001.jcl — separate IEBGENER read of logical dataset 1 into a new PS
- jcl/TA1AR002.jcl — separate IEBCOPY read of logical dataset 2 into a new PDS
- jcl/TA1ACOMP.jcl — two independent IEBCOMPR checks, TYPORG=PS and TYPORG=PO

The retained first volume may still be unloaded or repositioned by MVS/operator action. KEEP preserves dataset disposition, not an unconditional mount guarantee. Correct positioning and survival of both datasets are required observations, NOT assumptions from JCL syntax.

The repository script scripts/ta1-preflight is a READ-ONLY STATIC gate. It validates expected JCL steps, exact dataset names, tape unit, labels, VOLSER, retention, condition, DCB, read-only sources, new-only scratch restore targets, and the unused proposed image path. It never creates or mounts media, runs Docker, inspects live MVS catalog, or submits JES.

## Required live preflight, before separate stateful authorization

1. Verify source PDS, README member and its actual DCB from MVS.
2. Verify source/target uniqueness on MVS and that both scratch DASD output names are absent. Check that neither tape dataset name is an already protected production tape catalog entry.
3. Confirm image path is UNUSED, including symlink checks; check ALL known physical AWS/registry VOLSERs for BTA101 uniqueness, not just filename absence. Never overwrite another medium.
4. Inspect actual Hercules tape drive 0480, current mount/busy state, MVS D U,TAPE allocation and all operator prompts. Stop on ambiguity.
5. Inspect installed hetinit/hetmap syntax and initialize exactly once as the actual Hercules runtime user only AFTER separate explicit authorization.
6. Mount only after confirmation of idle/unallocated drive and correct media. Check Hercules and MVS independently.

After permission, submit TA1AWRIT once. Capture each JES JOB/step, utility message and RC, device state and any removal/retention event. Stop if first step fails or if the second step's position is doubtful. Inspect the written, quiescent image with hetmap labels/all/files/datasets and enumerate physical filemarks and blocks; record SHA-256, exact VOLSER, and both HDR/EOF sequences. NEVER reinitialize, retry or resume a possibly written image. On any failure/timeout/ambiguity preserve media and reports, then require a new owner decision.

Only after a separate approved safe readback: explicitly remount the same written image if needed; submit each restore job once against the absent target; inspect DCBs and PDS inventory; compare PS and PDS independently by IEBCOMPR, with both RC=0 and content/member evidence. Preserve real MVS/JES/Hercules observations in ignored workarea/ta1-*, never as fabricated Git acceptance evidence.

## Validation and acceptance

In the assistant's isolated workspace on 17 November 2026, 14/14 offline structural and negative tests passed. The static preflight reported STATIC_ONLY_PASS for its local image path. This does NOT establish the user's live image absence, VOLSER uniqueness, MVS catalog/DCB, drive availability, positioning, standard-label sequence, two restored datasets, record comparisons or release acceptance.

Track A PASS requires actual live MVS/Hercules two-dataset tape structure and restored compare evidence. Track B independently requires PO/U/0/6144 MR10_LOAD(ICINT19) unload/restore, directory/content checks and successful execution with STEPLIB selecting RESTORED ICINT19. Development JOB 9061 is only a baseline.

TA.0 remains CLOSED (qualified). TA.1 remains in preflight, NOT accepted. Publication and candidate manifest identity belong to later gates.

## One-shot authenticated Track A submission helper

The Git-controlled scripts/submit-ta1-job entry point reuses the existing
submit-scratch-job authenticated JOB-card construction and dspal-core submission.
Default execution only validates and previews. --show-deck prints a redacted
review copy. --run requires a real initialized image, an interactive exact
SUBMIT <job> BTA101 confirmation, and independent prior operator approval.
The helper writes a unique durable per-job attempt marker under
workarea/ta1-operations/ *before* transmitting JES and refuses any repeat of
that stage even following failure or ambiguous completion. It isolates the
printer window with a cursor, redirects temporary authenticated decks into
workarea/ (not /tmp), and caps user-facing summary output. These protections
do not verify tape position, volume identity, catalog collision, MVS allocation,
or mount/demount status and are NOT substitutes for the live preflight.

Do not invoke --run solely because the design is approved. Obtain explicit
permission for the exact media initialization, mount, one write job, later
restore jobs and any remount/unmount; preserve all results without retry.

## Owner-supplied live preflight observations (17 November 2026)

This record reflects console and utility output provided by the owner, NOT
execution by this change. No image creation, device mount, JES write job,
restore, or comparison was reported. Evidence here establishes only the
inquiries actually shown.

- GitHub main was fast-forwarded to 671242045694faab2d169986fd218ab50664650a.
- Hercules devlist reported 0:0480 as an unmounted 3420 (shown as '*').
  MVS D U,TAPE listed 480 online ('O') with /REMOV and no active VOLSER.
- dspal stat DIST_DOCS returned JOB 9062 and confirmed
  HERC02.BCPL.DIST.DOCS on TSO002, PO/FB/80/800, with COMPILE, DATASETS,
  INSTALL, LICENSE, README, RELEASE and VERIFY.
- Four independent dspal stat catalog inquiries reported 'data set not
  found': HERC02.BCPL.TA1A.FBREST, HERC02.BCPL.TA1A.PDSREST,
  BCPL.BT0001 and BCPL.BT0002.
- The observed tape directory contained only .gitkeep, bcpl01.aws,
  bcpl-pdstest-20261108-01.aws and bcpl-objtest-20261108-01.aws; proposed
  bcpl-ta1-a-20261117-01.aws was absent in that listing.
- Owner-supplied hetmap --labels inspection identified existing volume
  serials BCPL01, BTP001 and BTO001 respectively. Neither reported BTA101.
  The old bcpl01.aws contains an anomalous placeholder HDR1; it must not
  be treated as a scratch candidate.
- This proves no BTA101 collision within the three inspected images;
  it does NOT verify every external image, operator reservation or future
  filesystem state. Revalidate absence and idle state immediately before
  separately authorized initialization.

**Owner direction: never catalog the distribution tape datasets on MVS.**
The approved tape writer uses DISP=(NEW,KEEP,KEEP), not CATLG, and tape
readers explicitly specify UNIT=480, VOL=SER=BTA101 and LABEL=(n,SL).
Cataloging the newly allocated, disposable DASD restoration targets is
distinct and acceptable. No installation design may rely on a tape catalog.

**Status:** TRACK A LIVE READ-ONLY PREFLIGHT EVIDENCE RECORDED;
MEDIA INITIALIZATION / MOUNT / WRITING STILL REQUIRE DISTINCT EXPLICIT
OWNER AUTHORIZATION. TA.1 acceptance is not implied.

## Owner-authorized stateful TA.1 Track A execution

**Authorization received 17 November 2026:** initialize exactly one NEW
`mvs-state/tape/bcpl-ta1-a-20261117-01.aws` as uncompressed SL AWS tape,
VOLSER `BTA101`; mount it at Hercules device `0480`; submit the single
two-step `TA1AWRIT` job once; inspect MVS/JES and final AWS labels/filemarks.
This authorizes NO restoration, remount after failure, retry, modification
of any existing image, catalog of tape datasets, or release publication.

Use `scripts/run-ta1-track-a --run` from repository root after pulling the
commit containing this section. It performs fresh live MVS source/collision,
Hercules device, Docker bind/user and all existing AWS VOLSER checks before
a typed confirmation. It uses exclusive-create records under
`workarea/ta1-operations/` and exclusive creation of the new tape image;
once an attempt begins, it cannot be repeated. The image initialization
is `hetinit -d -i`, followed by VOL1 verification, mount/ready verification,
the separately confirmed authenticated `submit-ta1-job TA1AWRIT --run`,
then job summary, JES report, final `hetmap` -l/-f/-a and SHA-256 evidence.
Full host output is saved privately in unique ignored `workarea/` evidence,
not dumped into WSL. A failure never triggers automatic recovery.

**Validation:** 27/27 isolated offline tests passed for the new runner and
existing static JCL gate; no live MVS initialization or job execution is
claimed by these tests. The owner-provided old VOLSER reports remain
read-only preflight evidence; a new current VOLSER scan is required.

MVS disposition policy remains unchanged: tape datasets are uncataloged;
only independent fresh DASD restore targets may be cataloged in a later
separately authorized step. TA.1 is NOT accepted until live write and
independent restored-dataset evidence have been reviewed.
