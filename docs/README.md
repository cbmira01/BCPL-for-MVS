# Programmer orientation notes

The files in this directory are working briefings for people developing or reviewing the BCPL reconstruction on System/370 and MVS 3.8J. They are secondary notes, not substitutes for contemporary IBM manuals or the historical BCPL sources.

## Main briefings

- `System_370-briefing.md` — System/370 architecture and instruction-level context
- `MVS-3_8-briefing.md` — MVS 3.8J services and execution environment
- `Hercules-briefing.md` — emulator configuration and operation
- `IFOX-assembler-toolchain-briefing.md` — Assembler F / IFOX workflow
- `JCL-for-the-programmer.md` — JCL needed for compile/link/run work
- `IBM-data-representation.md` — EBCDIC, integers, addresses, records, and representation issues
- `MVS-access-methods.md` — data-set and access-method concepts relevant to runtime work
- `MVS-debugging.md` — diagnostics available in the MVS 3.8 environment
- `MVS-program-execution.md` — loading, linkage, execution, and termination
- `MVS-storage-and-addressing.md` — storage management and addressability
- `MVS-system-programming-interfaces.md` — useful MVS service interfaces
- `S370-object-and-load-modules.md` — object modules and linkage-editor/load-module structure
- `BCPL-history-and-porting.md` — historical compiler/porting context
- `project-map.md` — repository and workflow map

## Source discipline

For questions about the historical BCPL implementation, prefer primary evidence in `richards-bcpltape/` and contemporary manuals. For MVS and System/370 behavior, prefer IBM documentation and observable TK5 behavior. These notes summarize and connect those sources for this project and may contain mistakes.

The Computer History Museum Software Preservation Group's [BCPL History Collection](https://softwarepreservation.computerhistory.org/BCPL/) is a useful index to historical manuals, papers, and source archives. Martin Richards' archive and Robert Nordier's Classic BCPL material are also important provenance sources.

Some briefings were drafted or edited with AI assistance. They have been kept because they are useful project notes, not because the drafting method gives them authority. Verify consequential details against primary documentation.