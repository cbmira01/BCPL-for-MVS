# Cambridge Compiler — Assembler Sources

This folder holds the assembler sources for the native Cambridge compiler
runtime. The five `bcpl*.asm` files began as exact copies of the accepted
runtime modules in [`native-compiler/asm/`](../../native-compiler/asm/).
They are now separate working sources for the native Cambridge compiler.
Changing a file here does **not** change the interpreter-hosted bootstrap
toolchain or its accepted runtime objects.

## Folder contents

| File | Role | What it does |
| --- | --- | --- |
| [`bcplmain.asm`](bcplmain.asm) | Program startup and control | Enters a compiled BCPL program, allocates its global vector and stack, installs runtime services, starts the program, and handles return to MVS. Its current module setup imports the starting section and BLIB; the full compiler will need further section registration. |
| [`bcplmem.asm`](bcplmem.asm) | Heap storage | Implements `GETVEC` and `FREEVEC`, tracks live allocations, and releases leftover vectors during shutdown. |
| [`bcplbyte.asm`](bcplbyte.asm) | Byte access | Implements `GETBYTE` and `PUTBYTE` for bytes held in 32-bit BCPL words. |
| [`bcplapt.asm`](bcplapt.asm) | Temporary vectors | Implements `APTOVEC`: creates a vector in stack workspace, calls a BCPL routine, and checks the stack limit. |
| [`bcplio.asm`](bcplio.asm) | Stream I/O | Implements BCPL input and output on MVS QSAM records, including selected streams, DD-name lookup, dynamic stream handles, and cleanup. |
| [`program.asm`](program.asm) | Historical support module | Defines a 4,096-word module shaped like compiled BCPL. The original compiler can load it for the `LOADGO` option; it publishes global 100. It is **not** one of the five core runtime modules. |
| [`README.md`](README.md) | Folder guide | Describes the files and their roles. |

## Working rules

The five runtime files are **Cambridge-owned copies**, not a live mirror
of `native-compiler/asm/`. We can adapt them for the native compiler
without altering the accepted bootstrap runtime.

`program.asm` is kept as historical reference unless its original
loading behavior is needed. The presence of these source files does
not by itself mean that the full native Cambridge compiler has been
assembled, linked, or run.
