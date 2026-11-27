# Documentation

## Product manuals

### Tutorials

- [Tutorial on BCPL Programming](product/Tutorial-on-BCPL-Programming.md)

- [Tutorial on System Extensions](product/Tutorial-on-System-Extensions.md)

### How-to guides

- [How to Install BCPL from Tape](product/How-to-Install-BCPL-from-Tape.md)
- [How to Operate the BCPL Programming System](product/How-to-Operate-the-BCPL-Programming-System.md)
- [How to Compile and Run BCPL Programs](product/How-to-Compile-and-Run-BCPL-Programs.md)
- [How to Use System Extensions](product/How-to-Use-System-Extensions.md)

### Explanations

- [Explanation of BCPL Compilers](product/Explanation-of-BCPL-Compilers.md)

- [Explanation of the Cambridge Runtime and Libraries](product/Explanation-of-the-Cambridge-Runtime-and-Libraries.md)

- [Explanation of System Extensions](product/Explanation-of-System-Extensions.md)

### References

- [Reference for the BCPL Language](product/Reference-for-the-BCPL-Language.md) — normative for supported syntax and semantics.

- [Reference for BCPL Compilers](product/Reference-for-BCPL-Compilers.md) — normative for supported compiler interfaces.

- [Reference for the Cambridge Runtime and Libraries](product/Reference-for-the-Cambridge-Runtime-and-Libraries.md) — normative within the approved public native and MR10 contracts; detailed DEBUGINT verification pending.

- [Reference for System Extensions](product/Reference-for-System-Extensions.md) — normative for approved QUERY, registration/finalization and package APIs; selection-macro authority transfer pending.

## Project manuals

### How-to guides

- [How to Reconstruct BCPL from Source](project/How-to-Reconstruct-BCPL-from-Source.md) — reconciled procedure; existing reconstruction runbooks remain operative.
- [How to Develop and Test BCPL for MVS](project/How-to-Develop-and-Test-BCPL-for-MVS.md) — reconciled procedure; existing policies and test authorities retained.
- [How to Create a Release Candidate](project/How-to-Create-a-Release-Candidate.md) — reconciled review-oriented guide; [canonical execution guide](../tools/distribution/How-to-Create-a-Release-Candidate.md) remains operative.

### Explanations

- [Explanation of the MVS Programming Environment](project/Explanation-of-the-MVS-Programming-Environment.md) — explanatory guide; original briefings retained.

### References

- [Reference for Project Tools](project/Reference-for-Project-Tools.md) — normative for specified supported public host-tool interfaces.

## Subject index

- **BCPL language:** [Tutorial](product/Tutorial-on-BCPL-Programming.md), [language reference](product/Reference-for-the-BCPL-Language.md).

- **BCPL compilers:** [Explanation](product/Explanation-of-BCPL-Compilers.md), [compiler reference](product/Reference-for-BCPL-Compilers.md).

- **Runtime and libraries:** [Explanation](product/Explanation-of-the-Cambridge-Runtime-and-Libraries.md), [runtime and library reference](product/Reference-for-the-Cambridge-Runtime-and-Libraries.md).

- **System Extensions:** [Tutorial](product/Tutorial-on-System-Extensions.md), [how-to](product/How-to-Use-System-Extensions.md), [explanation](product/Explanation-of-System-Extensions.md), [reference](product/Reference-for-System-Extensions.md).

- **Installation and operation:** [Install from tape](product/How-to-Install-BCPL-from-Tape.md), [operate the system](product/How-to-Operate-the-BCPL-Programming-System.md), [compile and run programs](product/How-to-Compile-and-Run-BCPL-Programs.md).

- **Project reconstruction:** [Reconstruct from source](project/How-to-Reconstruct-BCPL-from-Source.md), [existing automated runbook](Rebuild-BCPL-for-MVS-from-source.md), [existing manual procedure](Manual-Rebuild-BCPL-for-MVS.md).

- **Project development and testing:** [Develop and test BCPL for MVS](project/How-to-Develop-and-Test-BCPL-for-MVS.md), [native suite contract](../tests/README.md), [test runner guide](../tools/tests/README.md).

- **Project tools:** [Reference for Project Tools](project/Reference-for-Project-Tools.md), [host tool directory](../tools/README.md).

- **Release creation:** [Release candidate review and gates](project/How-to-Create-a-Release-Candidate.md), [canonical execution guide](../tools/distribution/How-to-Create-a-Release-Candidate.md).

- **MVS programming environment:** [Consolidated explanation](project/Explanation-of-the-MVS-Programming-Environment.md), [original programmer orientation briefings](#programmer-orientation-briefings).

All thirteen approved product manuals and five approved project manuals are available. The five reference manuals have individual approved normative scopes; consult their status statements and the [Documentation Refactoring milestone](../packaging/milestones/documentation-refactoring/milestone-documentation-refactoring.md). Untransferred contracts, registry, configuration, manifests, independent oracles, canonical procedures and frozen release documentation retain their respective authority. Original engineering records and orientation briefings remain available. DR.5 verification and final closure remain pending.

## Programmer orientation briefings

This directory contains **human-readable educational briefings** on BCPL,
System/370, MVS 3.8J, Hercules, IFOX and JCL. They are explanatory notes,
not historical primary sources, formal runtime contracts or current
milestone trackers.

## BCPL and historical context

- [BCPL history and porting](BCPL-history-and-porting.md)
- [BCPL memory management](BCPL-memory-management.md)

## System/370 and IBM data

- [System/370 architecture](System_370-briefing.md)
- [IBM data representation](IBM-data-representation.md)
- [Object and load modules](S370-object-and-load-modules.md)

## MVS services and runtime environment

- [MVS 3.8J](MVS-3_8-briefing.md)
- [MVS access methods](MVS-access-methods.md)
- [MVS debugging](MVS-debugging.md)
- [MVS program execution](MVS-program-execution.md)
- [MVS storage and addressing](MVS-storage-and-addressing.md)
- [MVS system-programming interfaces](MVS-system-programming-interfaces.md)

## Development environment

- [Hercules](Hercules-briefing.md)
- [IFOX assembler toolchain](IFOX-assembler-toolchain-briefing.md)
- [JCL for the programmer](JCL-for-the-programmer.md)

For project architecture, build procedures, milestone decisions, audits
and runtime contracts, use the
[packaging documentation index](../packaging/README.md) and
[current repository map](../packaging/operations/repository-map.md).

## Source discipline

For original BCPL behavior prefer [historical BCPL source](../richards-bcpltape/)
and contemporary manuals. For MVS and System/370 behavior prefer IBM
manuals and observed TK5 behavior. The
[BCPL History Collection](https://softwarepreservation.computerhistory.org/BCPL/)
is a useful primary-source index.

Some briefings were drafted or edited with AI assistance. This does not
make them authoritative; verify consequential technical details against
primary documentation.
