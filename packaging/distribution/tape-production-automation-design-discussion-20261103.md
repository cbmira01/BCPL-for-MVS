# Design discussion — automation of distribution tape production

**Date:** 2026-11-03  
**Status:** Feasibility research and design options; no tape/JES execution, release, or new milestone authorized.

## Question and finding

Can creation of the Cambridge BCPL Programming System distribution tape be automated? **Yes, largely, after a verified single-PDS round trip establishes the MVS 3.8J tape/JCL contract.** Automate preparation, JCL generation, evidence capture and validation, while retaining operator gates for persistent or risky actions. Tape production is downstream of a separately accepted reconstruction; it should **not** quietly launch a destructive clean-room rebuild.

## Evidence and target architecture

- The repository already contains `packaging/distribution/{docs,manifest,create-tape,install-from-tape}`, `config/dspal.yaml`, and `tools/mvs/mvs-console`. The proposed media format is a **single AWS virtual tape** with multiple logical tape files; this is a design direction, not a verified tape image.
- IBM Release 3.8 IEBCOPY documentation explicitly supports unloading a PDS to a sequential tape dataset and subsequently loading it back; multiple PDSes require distinct sequential tape datasets on the volume. IEBGENER can copy sequential datasets. Preserve true unload formats, object libraries and load libraries; do not serialize PDS members into text as a substitute.
- Actual tape initialization utility, labels, device address, JCL file sequencing, `DISP`, and guest behavior are configuration-dependent and require a controlled test. Modern z/OS samples are not a substitute for the Release 3.8 manual and an actual TK5 job.

## Proposed production pipeline

| Stage | Action | Acceptance gate |
| --- | --- | --- |
| A. Freeze inputs | Pin Git SHA; record reconstruction evidence and accepted library inventories; identify explicitly included System Extensions and optional libraries | Owner reviews exact distribution scope; never include unaccepted candidates as production binaries |
| B. Build manifest | Derive MVS source DSNs from effective `dspal` config; record each logical tape file number, kind (IEBCOPY unload/sequential), DSN, DCB, members and release identity | Validate unique file numbers, names and required contents; use one inventory for producer and installer |
| C. Generate installer/bootstrap | Produce release-specific `docs` PDS members and MVS-only installation JCL from reviewed sources | Installer and readable instructions must be retrievable *before BCPL is installed*; bootstrap tape layout remains a design decision |
| D. Initialize scratch output tape | Create new, unique AWS image with a checked initialization/label policy | Explicit approval for disk-file creation/overwrite and target VOLSER; verify labels and file format |
| E. Mount & write | Mount on a verified idle drive; execute generated IEBCOPY jobs for PDSes, IEBGENER for sequential files | Approve JCL before JES submissions; validate payload job RCs, dataset/file counts, MVS allocation and clean CLOSE |
| F. Finalize and inspect | Confirm all allocations released; unmount; validate host image structural integrity/filemarks, label/VOLSER, ordering and checksums | Fail closed on missing/extra tape files; do not infer completeness from an AWS file's existence |
| G. Independent restoration | Restore the tape to a **separate, clean target MVS instance** using only tape-resident materials and ordinary MVS utilities | Independent member inventories, binary checks and compile/link/run smoke tests; include error cases and non-overwrite installation behavior |
| H. Publish | Generate immutable provenance receipt, SHA-256 checksum, annotated release tag and attached artifact | Explicit owner approval; GitHub source remains authoritative and release media is a derived artifact |

## Why a manifest-driven design

One canonical *release inventory* should drive tape file ordering, producer JCL, consumer JCL, `DATASETS`/`RELEASE` documentation and verification. It must be consistent with `config/dspal.yaml`, but differs in purpose: `dspal` describes managed MVS PDS content; the distribution manifest records **which installed artifacts actually ship and where on tape**.

Suggested manifest fields (not yet an approved schema): source commit, profile, VOLSER, tape-file sequence, file kind, input/output DSNs, record format/LRECL/BLKSIZE where relevant, member counts and hashes where measurable, accepted-object provenance, and validation policy. Avoid assuming every one of the 28 managed PDSes should appear in every end-user product profile. A full reconstruction archive and a smaller end-user compiler distribution can be separate explicit profiles.

## Control and failure handling

- Separate `plan` / `generate` (no system writes) from `produce` (MVS/tape writes) and `verify` (independent tape readback and/or new-target restore). Exact command names are provisional.
- Record each stage's identity, timestamps, input hashes, JCL decks, actual JES job IDs/step RCs, dataset inventory, tape mount state and final checksums.
- Treat incomplete/aborted output media as **invalid**, not resumable by appending without an explicit tape-position and dataset integrity design. Prefer recreate-from-scratch using a new scratch image. The [deferred multi-dataset/append experiment](multi-dataset-tape-and-append-experiment-20261108.md) must establish MVS 3.8J retention, label sequencing, positioning and readback before any producer append/recovery policy is implemented.
- Ensure an existing output tape is never modified by default. Preflight `MOUNTED_TAPE_REINIT`, image permissions and unique filenames; hardware detach/attach is not the normal mount procedure.
- Avoid hidden tape handling inside JES launcher code: keep operator-visible volume mount messages and deliberate checkpoint boundaries.
- Release creation, tag/push, permanent dataset overwrite, JES submission and tape mounting require explicit authorization beyond a repository commit.
- Distinguish successful *media creation* from proven *installation*. Tape is not releasable until independent restore is accepted.

## First bounded proof

1. Read-only inspect the emulator's configured tape drives and utility versions.
2. Create and mount a unique scratch image.
3. IEBCOPY-unload **one small disposable PDS**; close and unmount.
4. Remount and IEBCOPY-load into a different scratch PDS.
5. Compare directory/member contents and investigate tape image/filemark structure.
6. Once accepted, repeat with an object/load-library PDS and then two sequential tape files.

No tested full-distribution JCL, generated image, or production-ready installer is claimed here.

## References

- Repository: `packaging/distribution/README.md`, `config/dspal.yaml`, `tools/mvs/mvs-console-README.md`, `docs/Rebuild-BCPL-for-MVS-from-source.md`.
- IBM *OS/VS2 MVS Utilities*, Release 3.8 (GC26-3902-1), IEBCOPY examples 13–14 and IEBGENER: https://bitsavers.org/pdf/ibm/370/OS_VS2/Release_3.8_1978/GC26-3902-1_OS_VS2_MVS_Utilities_Rel_3.8_Sep83.pdf
- Hercules operations: https://hercules-390.github.io/html/hercoper.html
- Hercules mounted-media precautions: https://sdl-hercules-390.github.io/html/hercconf.html
- IBM modern IEBCOPY overview (corroboration, **not** the MVS 3.8 contract): https://www.ibm.com/docs/en/zos/2.5.0?topic=program-unloading-backing-up-data-sets

## Experiment status update (8 November 2026)

The "first bounded proof" step using a seven-member FB80 scratch PDS
has been **completed and accepted** on the target MVS system.
See [scratch PDS round-trip acceptance](create-tape/scratch-pds-roundtrip-acceptance-20261108.md).
This removes the particular feasibility question for single-file,
standard-labeled IEBCOPY unload/restore, but does not establish
automated tape creation or tape-resident installation. The future
distribution must still independently validate object and load
libraries, multifile sequencing, the readable first documentation
dataset, and clean-target installation. The existing Hercules
`hetmap` utility already provides tape label/file maps;
[inspection notes](tape-inspection-capabilities-20261108.md) record
what may require a project-specific read-only tool.
