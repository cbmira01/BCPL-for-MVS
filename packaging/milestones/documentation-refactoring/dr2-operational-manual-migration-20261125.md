# DR.2 — Installation, operation and compilation manuals: migration and evidence

**Date:** 25 November 2026 EST  
**Baseline:** 8edb7dc3e1e7f5abcf552191cb3e1e97c9e20c51  
**Status:** Three substantive working drafts complete; all thirteen approved product manual drafts now exist. No march closure or normative authority transfer.

## Evidence alignment

Fifteen selected MR10 tracked files (ICINT19 assembler, five INTCODE decks, four suite/build JCL bodies, SCALVEC and separate-module sources/expected records) match RC4 frozen source e910de51c19c09698be139e33084a90401511cc9 by path/blob SHA. The RC4 companion and frozen manifest match publication tag commit 5fca3d6b83b7db6a29cd863e1c977c12a21876f2. Native regression 075 source, README and expected match CO.6 tested revision 216b6707c404a91c796ed8f1419a99ef172b184a. Source identity does not establish newly assembled binary identity.

The two companion JCL excerpts are exact. MRREGRES staging/C01A/G01A/R01 and R06 are exact source extracts; grouping a focused job and recipient namespace substitution are adaptations requiring separate execution. SCALVEC, separate module and native 075 source and expected extracts are exact. All original jobs/oracles remain intact.

## Migration ledger

| Existing source / authority | Destination | Reconciliation and remaining work |
| --- | --- | --- |
| RC4 companion, frozen manifest and TA.3/TA.7/TA.8 | Install 1–7; operate 1–5 | Media/ZIP/AWS identity, profile and DCB/namespace rules, tape bootstrap/installer decks, exact directory and functional scope; release companion remains controlling |
| TA.3 installer PROC design and result | Install 3–4,7 | BT0001/2 and eight installer members, site symbols, COPY from restored PDS, actual ten/nineteen IEBCOPY steps; no replay or alternate-site assurance |
| TA.4 automated acceptance, TA.5 revised scope, TA.7 | Install 5–7; operate 4–5; compile 1,7 | 80 supported functional cases/326 steps, independent golden comparison, isolated rebuild, native inventory-only, no independent IPL/site or new binary identity |
| MR10 suite and ICINT19 JCL READMEs, frozen JCL | Operate 2–8; compile 2–4,7 | Separate routine use from project installation/rebuild; stage five decks; step/record evidence; exact extracted examples and temporary lifetimes |
| MR10 compiler and library docs, canonical examples | Compile 1–4,8 | MR10 options, module combination, test-local G!180, native ABI distinction; link to reference rather than duplicate |
| Bootstrap guide, compile-mvs and production runner, case 075 | Compile 5–8 | Development-only textual CODE/IFOX/IEWL/GO, source/installed objects and actual output; note compile-mvs preview removes pre-existing output before show-jcl |
| Historical DIST.DOCS and retired trial controllers | Install 1,7; operate 8 | Preserve stale frozen notes, mandatory RC4 companion supersedes them; no retired live commands recommended |
| Existing runtime/extension/compiler manuals | Compile 1,6–8; operate 1,6 | Cross-reference ABI and restrictions; no new normative allocations or implementation claims |

## Outstanding reconciliation and limitations

- New focused JCL assembly from exact fragments, site substitutions and illustrative native compile invocation were not independently executed. Full original suite and native 075 evidence remain the basis; no new JES/IFOX/IEWL/GO submission.
- Raw owner-local sealed MVS receipts were not reopened. RC4 publication digest taken from accepted TA.8 and companion; no new asset download or tape rehash.
- Retain RC4 installation-only native boundary, alternate site/HLQ and independent IPL qualification, historical rights qualification, and prior reviewer/punch/semantic failure history. No frozen release bytes, source, JCL, registry or test oracle changed.
- Current project tools are separate from recipient MVS procedures. Preview output-path deletion is source-observed, not a new tested fix. DR.0 dependency audit qualification persists.
- All thirteen initial drafts are available; review completeness, cross-manual consistency and exact authority mappings before requesting DR.2 acceptance. Individual reference authority transfers require explicit owner approval.
