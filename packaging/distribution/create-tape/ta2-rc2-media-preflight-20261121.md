# TA.2 — rc2 Hercules 0480 checkpoint and guarded read-only MVS preflight

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.2 — Manifest-Driven Tape Producer  
**Date:** 21 November 2026 EST  
**Status:** Hercules device observed, MVS unit/drive-readiness still pending fresh read-only verification. AWS writing NOT authorized.

## Owner-provided actual Hercules inquiry

After updating the local checkout from GitHub main, the owner ran:

    tools/mvs/mvs-console tape status 480

The console returned RC=0 and the single observed device row:

    13:23:32 HHC02279I 0:0480 3420 * IO[31] maxsize=0 eotmargin=128K deonirq=N

The project console client's existing TA.1 safety contract treats the 3420 \`*\` field as *no image mounted* at address 0480. This is **not** evidence of MVS guest allocation, a tape image/filename being unused, or current availability at a later instant. No media was initialized, mounted, unmounted, rewritten, or inspected by this command.

## New read-only rc2 preflight

\`scripts/ta2-rc2-media-preflight\` replays the current **BCPL-0.1.0-rc2** frozen-manifest/registry/source-selection checks using the existing rc2 preview and \`ta2-offline\` renderer. Its default mode makes no MVS inquiry. With \`--live\` it performs only two display commands, in sequence: Hercules \`tape status 480\` (DEVLIST) and MVS \`mvs tapes\` (D U,TAPE).

It refuses missing or conflicting device records, a mounted/busy Hercules drive, missing/ambiguous MVS unit 480/3400, guest state other than \`O\` or \`O-NRD\`, or MVS allocation/busy indicators. As in accepted TA.1 experiments, identical console echoes may be collapsed but conflicting records are not. It saves both original output streams and a SHA256-sealed receipt under a *new* directory within \`workarea/ta2-rc2-media-preflight/\`.

**Assistant-workspace verification:** AST/parse checks and **23/23 combined isolated offline tests PASS** across the rc2 producer preview (8 tests) and this media preflight (15 tests). Negative tests include loaded/busy/offline states, missing or conflicting rows, multiple nearby MVS device entries, unauthorized console command, and dry-run behavior. No actual MVS \`D U,TAPE\` result has yet been reported for this preflight.

**Authorization boundary:** A successful preflight is a read-only observation only. It is not a full media-file collision scan, source-/rights-certification result, write permission, complete AWS producer, or MVS label/readback acceptance. Reserved candidate VOLSER \`BC0002\` is unchanged, and BT0001–BT0021 remain accepted (qualified) staged release inputs. The earlier one-shot IEBCOPY staging operation must not be repeated.

Next: owner executes the single combined **read-only** MVS/Hercules preflight to capture the guest device state. A separately approved candidate tape-writing design and one-shot operational authorization are required before creating or mounting media. **TA.2 remains IN PROGRESS.**
