# TA.2 — Stage/source/build-chain reconciliation

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.2 — Manifest-Driven Tape Producer  
**Date:** 20 November 2026  
**Status:** Read-only reconciliation implemented and offline-tested; **no new MVS execution, release-rights approval or tape production**.

## Grounded checkpoint

Owner-reported actual MVS staging and directory/DCB verification accepted **all 20** logical producer inputs on TSO002 (JOBS 9310–9312 and 9317–9319). The frozen Git tree check independently found **110/110** selected Git-backed members unchanged at approved source SHA `146ae09a58398c9b4d685500760f85592e770e1e`. The reserved candidate is `BCPL-0.1.0-rc1`; VOLSER `BC0001` is reserved but not used to write a release image.

Earlier accepted TA.0 build-chain research already identifies **15 selected object/load members** produced by **eight** build-job contracts. Its MVS retained-evidence intake requires actual operator-retained JES reports and inventories; these are not held in this conversation or GitHub as approved candidate-specific receipts. Its requirement is not a reason to repeat successful staging or reimplement IFOX/IEWL.

## Implemented bridge to existing authoritative tools

New read-only `scripts/ta2-build-chain-reconcile` joins three existing validated views:

1. `ta2-complete-stage-inputs.evaluate()`: exact 20-input staging acceptance, MVS job IDs, source DSNs and member lists.
2. `ta2-source-lineage.evaluate()`: the same 127 selected payload members, frozen Git source identities and explicitly unreviewed redistribution status.
3. The existing TA.0 `audit-binary-build-chain.build_plan()` after canonical TA.0 manifest validation: accepted source-chain requirements, actual selected JCL paths, and IFOX/IEWL step contracts for 15 object/load targets.

It requires a single approved candidate/manifest SHA, **110 Git-backed + 2 generated + 15 resident binaries**, exact member identity and presence in the accepted MVS staging inventory. It refuses missing/extra binary targets, nonselected source dependencies, wrong staging identity, inserted rights approvals, synthetic MVS receipts and contradictory compiler/rebuild claims. Its default output is two compact lines, or `--output workarea/<new-file>.json` writes an exclusive **derived** private review queue without changing manifests, Git, MVS or tape.

The joined build plan contains eight jobs: `IC19BLD`, `BLDBMAIN`, `BLIBBLD`, `BLDCORCO`, `BLDCORLB`, `BCPLDEMO`, `BCPLTIME`, and `BCPLQSAM`. The `BLIBBLD` development job is **not shipped** in the candidate; that does not invalidate its already accepted resident object but prevents claiming a self-contained BCPL-source rebuild. `BOOT_ASM(COROUTIN)` is generated from maintained Coroutine Support Library source; `BOOT_SOURCE(BLIB)` is historical Base Library work. These generated inputs and their object builders remain distinct. A no-native-compiler release must not claim the native-running Cambridge Compiler or native BCPL-source compilation.

## Checks and remaining decisions

**19/19** focused synthetic local tests and Python syntax checks **PASS**, including generated/relocatable build dependency separation, actual selected source references, 8 builder contracts, the one unshipped job, rights-approval refusal, no-receipt substitution, fixed candidate identity, no-overwrite output and no MVS/tape actions. GitHub-committed source/test blob hashes are checked against the locally tested files. The combined tool has not been executed against the user's private MVS evidence; only the owner-reported accepted original MVS results support those claims.

Nothing is automatically authorized for redistribution. `LICENSE.md`, `THIRD-PARTY-NOTICES.md`, and `PUBLIC-RELEASE-AUDIT.md` distinguish original MIT-licensed project files from historical BCPL source and derived reconstructions. A **source-family redistribution policy** requires owner review; archival publication does not silently confer separate tape rights. Likewise, a build-job JCL contract is **not** a candidate-specific JES receipt, generated-source derivation receipt, member byte hash or executable GO result.

Next: inventory and review existing retained BCPL/IFOX/IEWL evidence for the eight builder contracts without rebuilding everything merely to satisfy paperwork, and decide how to handle historical/derivative redistribution. Once evidence is actually accepted, update the single candidate manifest and registry together under controlled review. The existing strict `ta2-offline --candidate` gate stays authoritative and closed until its requirements are met.

**TA.2 remains IN PROGRESS.** TA.0/TA.1 qualified closures remain unchanged. No `BC0001` AWS tape, recipient restore or TA.3 installation is authorized or accepted.
