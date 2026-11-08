# Create tape

Producer-side source for AWS tape creation and validation.

- `jcl/`: MVS jobs for unloading distribution datasets to tape.
- `scripts/`: host-side orchestration and manifest-driven job generation.
- `tests/`: tape structure and read-back verification.

This side may use the project development environment (WSL, Python, Hercules, `dspal`). Writing tape or executing JES jobs requires explicit separate approval. No implementation is present yet.

## Manual scratch-PDS tape experiment (unverified on MVS)

Four independent JCL job bodies are in the jcl directory. They contain
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
   A secure host-JCL submission method remains to be designed.
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

No successful MVS execution or tape-restoration acceptance is claimed.
