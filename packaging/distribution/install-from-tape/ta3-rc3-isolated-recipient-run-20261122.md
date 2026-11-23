# TA.3 — BC0003 isolated MVS recipient run preparation

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.3 — MVS Bootstrap and Installation — IN PROGRESS  
**Date:** 22 November 2026 EST / 23 November 2026 UTC  
**Authority:** owner approval to proceed with one guarded isolated-recipient MVS operation.

## Fixed candidate and isolated recipient

Use the original `BCPL-0.1.0-rc3` / `BC0003` AWS image,
SHA-256 `6c54c4df2b75020a698110061c4f8003b09adbe21f738848dcaed3da495d81e1`.
Do not change the tape or rerun TA.2 JOBS 9361, 9363, 9367, 9368, 9369.

The first TA.3 proof targets **new** `HERC02.BCPL.TA3N1.*` PDSes on
DASD `TSO002` through `SYSDA`. This is an isolated namespace on the
existing MVS 3.8J system, **not** an independent newly IPL'd MVS system.
It tests ordinary recipient JCL and separately allocated inputs without
replacing the existing developer or accepted TA.2 recipients.

## Execution path

The source-controlled `scripts/ta3-rc3-recipient --run` performs one
operator-approved MVS-facing operation using the already accepted
JES/Hercules tools for job submission and evidence collection.
Only the MVS resident IEBGENER, IEBCOPY, TSO LISTDS, and interpreter
executable `ICINT19` are needed by the actual JCL job streams.

1. Check original AWS SHA-256, live tape drive 0480 empty, source job bodies,
   candidate mapping, and all **11** recipient target datasets absent
   through a fresh MVS LISTDS catalog inquiry.
2. Require one `Y` response before a durable no-retry marker is written.
3. Mount the **existing** BC0003 image, execute `TA3BOOT` to read
   `BCPL.BT0001` with IEBGENER and inspect printed bootstrap identity.
4. Execute `TA3BT2` to restore `BCPL.BT0002` into
   `HERC02.BCPL.TA3N1.DIST.INST` and `TA3VIEW` to print its four
   installed members: INSTALL, DATASETS, RELEASE, RESTORE.
5. Execute `TA3MR10` once: 10 IEBCOPY restores (BT0003 common docs,
   BT0004–BT0012 MR10 source, assembler, JCL, library, demonstrations,
   tests, relocatable object and ICINT19 load module).
6. Require fresh MVS DCB/volume identity and independent member-directory
   results for 11 installed PDSes / 90 members.
7. Execute `TA3GO` from source-controlled MVS JCL, staging the five
   interpreted compiler/library inputs, compiling SCALVEC with SYNI/TRNI,
   generating INTCODE through CGI, and running it through the
   **recipient STEPLIB** `HERC02.BCPL.TA3N1.MR10KIT.LOAD`. Demand all
   eight JES/IEF142I RC0000 steps and the actual TEST:/EXP:/RP:/CODE=0
   semantic comparison.
8. Recheck original AWS SHA-256 and preserve the MVS evidence under
   `workarea/ta3-rc3-recipient/`. Console output stays compact.

The JCL bodies contain no destructive `DISP=MOD`, replacement, scratch,
or restart path; installation PDSes use `DISP=(NEW,CATLG,DELETE)`.
The tape uses standard-label `LABEL=(n,SL)` and
`VOL=(PRIVATE,RETAIN,SER=BC0003)`. A demounted but otherwise unchanged
original tape may be remounted between jobs. No tape write, `hetinit`,
source staging or TA.2 replay takes place.

## Preparation and acceptance boundary

**Local checks:** Python syntax passed; five focused synthetic/refusal
tests passed; source-controlled JCL site substitution, card widths and
expected active steps passed for TA3BOOT, TA3BT2, TA3VIEW, TA3MR10 and TA3GO.
The GitHub runner bytes were compared with the locally tested source.

**No TA.3 MVS execution result is claimed until the owner runs the
single operation and supplies its actual MVS console summary.**
A stateful failure consumes the marker; do not blindly rerun or replace
partially created datasets. Its saved reports, JCL and failure record
are the basis of the next MVS-guided correction.

MR10-only success would prove a bounded isolated-namespace demonstration,
not complete TA.3 closure: the native-component-only and combined paths
also require real recipient trials, and an independently bootstrapped
system remains a later acceptance obligation. The immutable tape still
contains the original inert 19-step installer `RESTORE` template; the
new source-controlled profile decks are external to that frozen image.
If tape-resident selectable JCL is required for release, it belongs in
a **new separately authorized candidate**, not in-place BC0003 changes.

The scoped image declares `native_compiler: absent`; it contains the
MR10 Kit Compiler, accepted native runtime/library/extension components,
and unfinished Cambridge Compiler source, **not** a runnable native
Cambridge Compiler. TA.4, TA.5, TA.7 and TA.8 remain separately open.
