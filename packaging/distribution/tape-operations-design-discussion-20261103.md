# Design discussion — learning and testing MVS tape operations

**Date:** 2026-11-03  
**Status:** Research and proposed experiment; no authorized tape/JES activity or acceptance claim.  
**Scope:** Hercules virtual tape + MVS 3.8J; separate from production distribution creation.

## Question and finding

Can we practice tape attachment/detachment and tape writing/reading safely? **Yes, with a dedicated scratch virtual tape and a small controlled MVS experiment.** Distinguish three layers:

1. **Host image:** a file in `mvs-state/tape/` (AWS/HET formats and initialization must be selected and verified).
2. **Hercules drive/media:** a configured virtual tape unit, with a host file mounted through `devinit`. `attach`/`detach` change the *device configuration*; `devinit` changes mounted *media*. Ordinary media practice should use `devinit`, not device removal.
3. **MVS/JES allocation:** a JCL DD, VOLSER/labels, an MVS device assignment, operator messages, and normal completion/close. A Hercules mount does not itself allocate or close an MVS dataset.

The repository already has `tools/mvs/mvs-console` operations `tape list`, `tape files`, `tape status ADDRESS`, `--dry-run tape mount ADDRESS NAME`, `tape mount`, and `tape unmount`. The latter uses `devinit ADDRESS *`. Both operations check a fresh `devlist` response for a recognized non-busy tape unit, but cannot prove that MVS has released the allocation. The interface requires confirmation. **Use the observed device address, not a hard-coded example.** See `tools/mvs/mvs-console-README.md`.

## Proposed practice sequence and gates

| Stage | Experiment | Human review / expected evidence |
| --- | --- | --- |
| 0 | Inspect local commands and tape-unit inventory; use dry-run before any changes | Record live `tape list`, `tape status`, device model, and MVS tape status; distinguish an emulator state from MVS state |
| 1 | Choose a unique scratch image filename and unique six-character VOLSER; verify no existing media will be overwritten | Approve scratch path, device, label policy, and test datasets; never use an accepted distribution image |
| 2 | Initialize the image using the actual installed Hercules utilities (candidate: `hetinit`), and inspect its format/label | Record utility version/help, command outcome, and resulting file metadata. Do **not** assume a zero-byte file is a labeled tape |
| 3 | Mount via the repo tape interface, check drive status, then unmount while idle | Capture before/after Hercules inventory; do not remove a device configuration via `detach` |
| 4 | Remount and write a tiny **sequential** MVS dataset to a scratch tape file using a reviewed IEBGENER JCL job | Confirm MVS allocation, job completion, DCB/record attributes, label/VOLSER and file number; no existing target data overwritten |
| 5 | Close/free allocation, unmount, remount read-only where supported, and read the tape file back into a separate scratch DASD dataset | Use another IEBGENER job; independently compare record count, lengths and data, e.g. IEBCOMPR where suitable |
| 6 | Try **one small scratch PDS** through IEBCOPY unload to another tape file and reload into a *different* PDS | Compare member inventory and bytes; for object/load libraries specifically verify their usable member structure and build/link behavior |
| 7 | Explore a second tape file, filemarks, sequential file positions, an intentional nonmatching VOLSER, and read-only behavior | Negative tests only after the first round-trip passes; capture console messages without risking unrelated jobs |
| 8 | Close all files, confirm MVS unit is idle/free, unmount, preserve logs and retire scratch media | Never unmount an allocated/busy tape merely because Hercules accepts the command |

A preliminary **FB80 text dataset** is easier to audit than a binary object. Then add an exact-binary test and a PDS test. Avoid testing on permanent BCPL libraries. Inspect host-side tape structure independently in addition to MVS read-back; bytes in an AWS file are **not** simply a concatenation of logical records.

## Safety requirements

- Read-only discovery is distinct from mount, JCL submission, or MVS dataset mutation. All operational actions need separate operator approval.
- Never overwrite or append to an existing image without explicit authorization. Reserve scratch VOLSERs, temporary dataset names and a disposable tape-unit workflow.
- Check MVS allocation/JES status *and* Hercules device status before changing media. Prefer an explicit two-phase release protocol (job complete and allocation released; then devinit unmount).
- Review `LABEL`, `VOL=SER`, `DISP`, `UNIT`, `DCB`, tape file number and any `SYSUT*` temporary allocations in each JCL job. Exact MVS 3.8J syntax must be tested on TK5.
- Do not treat HTTP success, a zero return code from a launcher, or tape image existence as proof of complete MVS tape I/O.
- This is a proposed test design, not a demonstrated success under the current resident guest.

## References

- Repository: `tools/mvs/mvs-console-README.md`, `tools/mvs/mvs-console`, `tools/mvs/test_mvs_console.py`.
- Hercules operations: https://hercules-390.github.io/html/hercoper.html (attach/detach versus devinit).
- Hercules configuration: https://sdl-hercules-390.github.io/html/hercconf.html (`MOUNTED_TAPE_REINIT`, read-only/ring behavior).
- IBM *OS/VS2 MVS Utilities*, Release 3.8 (GC26-3902-1): https://bitsavers.org/pdf/ibm/370/OS_VS2/Release_3.8_1978/GC26-3902-1_OS_VS2_MVS_Utilities_Rel_3.8_Sep83.pdf (IEBGENER, IEBCOMPR, IEBCOPY).
