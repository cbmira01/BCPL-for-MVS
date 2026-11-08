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
