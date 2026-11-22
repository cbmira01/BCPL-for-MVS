# TA.2 — First 21-dataset readback preflight refusal: Hercules 0480 identity

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.2 — Manifest-Driven Tape Producer  
**Date:** 21 November 2026 EST / 22 November 2026 UTC  
**State:** **READ-ONLY PREFLIGHT REFUSED (RC=2), before LISTDS/IEHLIST and before tape or DASD changes; device-only investigation pending.**

## Actual owner-reported result

After pulling GitHub `main` `a34d309f4d950ac42984754b4afb9cb12df2fbe5`, the owner executed:

`scripts/ta2-rc2-readback-plan --volume TSO002 --live`

The console reported:

```text
TA.2 RC2 READBACK PREFLIGHT REFUSED: Hercules 0480 does not hold exact BC0002 candidate
Evidence: workarea/ta2-rc2-readback-preflight/20261122T005713Z-27881
TA.2 RC2 readback preflight RC=2
```

The committed control flow computes the canonical 21-dataset readback plan, revalidates the original `BC0002` image hash and sealed structural acceptance, and runs the Docker/bind preflight before requesting Hercules `tape status 0480`. That device-identity guard refused **before** the MVS `D U,TAPE` display, LISTDS inquiry job or IEHLIST VTOC job. The original status response was saved at `workarea/ta2-rc2-readback-preflight/20261122T005713Z-27881/mounted-hercules.txt` and SHA256-sealed with the refusal. The assistant has reviewed the code and owner-reported terminal output, not the private raw device report.

## Explanation and verification needed

The *original tape write* used `RETAIN` for all but its final output dataset; after the authorized 21-step `TA2RC2WR` JOB 9339 ended, release of the attached tape is therefore plausible. However, the current report does **not** prove whether unit 0480 is empty, has the expected image under a different display representation, or holds foreign media. The readback planner's original condition `IMAGE.name in device_line` was a fail-closed requirement, **not evidence of the actual mounted filename**. No mount or rewrite is justified without the original DEVLIST response.

## Safe diagnostic implementation

The existing `scripts/ta2-rc2-readback-plan` now offers `--inspect-drive`, using the same required `--volume` parameter but **without** either LISTDS or IEHLIST submission. It:

- Replays the exact original SHA256-sealed refusal and saved Hercules status line, without rewriting them.
- Revalidates the original 1,957,296-byte candidate's SHA-256 `123657b2feaeea739350853f8b8437ccb73b0e917442ddd3220589c7ae180375` and the original accepted postwrite receipt.
- Issues only two read-only device display inquiries: Hercules `tape status 0480` and MVS `D U,TAPE`.
- Recognizes exactly one DEVLIST `0480 3420` row and distinguishes `EMPTY`, exact `MOUNTED_BC0002`, `BUSY`, `FOREIGN_OR_UNRECOGNIZED`, and `UNVERIFIED`; a similar filename or unknown row never passes as the correct tape.
- Preserves raw responses, bounded original/fresh status lines, the diagnostics and SHA256SUMS under a **new** directory inside `workarea/ta2-rc2-readback-preflight/`. No `devinit`, HETINIT, mounting, rewinding, JES readback, DASD allocation, image mutation, or automatic retry.

The correction does **not** relax or bypass the original strict `--live` mounted-image guard. A future readback runner must be separately authorized for actual device positioning and new scratch DASD allocation; any mount of an empty unit will also require owner consent and must not displace foreign media.

## Validation

**18/18 focused synthetic offline tests PASS** for the updated readback-plan test module in the assistant's repository-root workspace, including the accepted manifest/JCL design, exact mounted image, empty/busy/foreign/ambiguous device output, tampered original failure receipt and sealed read-only report. Python AST passed. Exact Git blobs of the changed code and tests matched local `git hash-object` before the documentation commit.

**TA.2 remains IN PROGRESS.** The accepted `BC0002` AWS, original no-retry marker and prior reports are immutable. Neither a 21-step readback job nor additional MVS state change was authorized or executed.
