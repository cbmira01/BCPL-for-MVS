# Programmer orientation briefings

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
[current repository map](../packaging/repository-map.md).

## Source discipline

For original BCPL behavior prefer [historical BCPL source](../richards-bcpltape/)
and contemporary manuals. For MVS and System/370 behavior prefer IBM
manuals and observed TK5 behavior. The
[BCPL History Collection](https://softwarepreservation.computerhistory.org/BCPL/)
is a useful primary-source index.

Some briefings were drafted or edited with AI assistance. This does not
make them authoritative; verify consequential technical details against
primary documentation.
