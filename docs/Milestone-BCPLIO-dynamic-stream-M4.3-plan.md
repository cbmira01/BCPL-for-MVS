# BCPLIO dynamic streams — M4.3 resource accountability

**Status: source-only accounting infrastructure and test 139 STAGED; no current IFOX/IEWL/GO result.**
Date: 2026-10-17

## Contract

M4.3 measures BCPLIO-owned dynamic resource lifetime, without modifying canonical BCPLIO or installing any MVS object. M4.2's narrower returned-error recovery contract remains accepted. A real MVS abend is not an accounting regression PASS.

Each ordinary dynamic stream owns a 32-byte descriptor and 268-byte record/DCB region. A separate 16-byte stable handle identity is retained after ENDREAD/ENDWRITE as a tombstone until IOFIN invokes IODRAIN. Private DQOPEN enters SVC19; private DQCLOSE enters SVC20. Bootstrap/static streams and all other runtime storage are excluded.

## Private counters

An isolated generated BCPLIO adds an internal assembler entry named `IOACCT` (R1 ID, R15 count; -1 for invalid ID). It does not add a production BCPL global.

| ID | Counter | Meaning |
|---|---|---|
| 0 | M43G32 | successful descriptor GETMAIN |
| 1 | M43F32 | returned descriptor FREEMAIN |
| 2 | M43G268 | successful region GETMAIN |
| 3 | M43F268 | returned region FREEMAIN |
| 4 | M43G16 | successful stable handle GETMAIN |
| 5 | M43F16 | returned stable handle FREEMAIN |
| 6 | M43OATT | dynamic SVC19 attempts |
| 7 | M43OSUC | post-SVC19 DCB observed open |
| 8 | M43CATT | dynamic SVC20 attempts |
| 9 | M43CRET | returned dynamic SVC20 |

A returned FREEMAIN call does not by itself prove physical MVS reclamation; nor does SVC20 returning establish every host CLOSE result. Counters reflect instrumented runtime control flow, with separate lifecycle and host-completion evidence.

## Staged acceptance gates

**M4.3.0:** Run the source-only audit `python3 tools/checks/check-bcplio-m43-account.py`. It validates the exact GETMAIN/FREEMAIN/SVC source sites and rejects source drift, repeat instrumentation and overwide IFOX cards. Only an observed PASS can accept this gate.

**M4.3.1:** Focused candidate-only compiled-BCPL test 139 uses existing regression G151 to call a separate test-only NATIVEAD assembler shim. It queries private IOACCT. Under MVS, ASMAP assembles the compiled BCPL program, ASMFIO assembles isolated BCPLIO, ASMNAT assembles NATIVEAD, and IEWL links both temporary objects with DEVOBJ(BCPLM6), without installed DEVOBJ(BCPLIO). GO asserts two live opens, duplicate FIND no extra OPEN, explicit ENDREAD releases descriptor/region but not the tombstone, fresh reopened identity, and three closes. It never reads the reopened instream DD DATA, avoiding an unfounded rewind guarantee. Marker: `M43 PRE-DRAIN COUNTS OK`.

**M4.3.2 (not implemented yet):** Add separately counted synthetic 32/268/16 and DQOPEN return-path failures and compare the count deltas to M4.1/M4.2 behavioral evidence. Add FINISH and STOP(8) termination checkpoints, including proof that IODRAIN leaves DHEAD and HHEAD empty and that G32=F32, G268=F268 and G16=F16, with open/close counts balanced on successful paths. Termination checks must execute *after* IODRAIN; pre-FINISH BCPL test 139 does not prove handle reclamation.

**M4.3 CLOSE:** Record the MVS job IDs, Cambridge/IFOX/IEWL/GO outcomes, generated object/link isolation and count observations, identify remaining host-level limitations, then accept only after all supported paths are proven. The owner's full regression deferral, M4.4 compatibility, M5 per-DD attribution and no OBJ promotion remain unchanged.

## First targeted operator check (no full regression)

```sh
cd ~/Source/Repos/BCPL-for-MVS
git pull --ff-only
python3 tools/checks/check-bcplio-m43-account.py
BCPL_RUNTIME_PDS=1 \
BCPL_RUNTIME_LIBRARY=DEVOBJ \
BCPL_RUNTIME_CANDIDATE=1 \
BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6 \
tools/native/run-regression 139 --show-output
```

DO NOT claim any PASS for 139 until the above actually executes under MVS.
