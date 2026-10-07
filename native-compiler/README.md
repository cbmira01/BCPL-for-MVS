# Native System/370 compiler work

The native target is built around the surviving BCPL kit compiler, not around a replacement front end.

The working bootstrap compiler remains the historical MR10-family pipeline:

```text
BCPL source -> SYN/TRN -> OCODE
```

The important change in direction is that a historical **System/370 code generator has been found** in the surviving BCPL material. The project therefore does not need to invent a System/370 backend from scratch. The current task is to make the historical generator runnable in the hosted environment, determine exactly which OCODE and runtime conventions it expects, adapt only what the MVS host requires, and use its output with IFOX and the MVS linkage editor.

## Architecture notes

- `cg370-architecture-notes.md` records the current understanding of OCODE versus INTCODE, the bootstrap-kit versus native-programming-system distinction, Cambridge `SECTION` handling, CG370's 16-KB section/base-addressing scheme, internal fixups, and object-deck generation.
- `kit-compiler-strategy.md` records the earlier investigation and should be read as design history where it conflicts with the current direction.

## What remains to be reconstructed

Finding the generator does not finish the native port. Work still includes:

- feeding known OCODE workloads to the historical S/370 generator and validating its assembler output;
- reconciling generator assumptions with the compiler kit that is actually runnable under ICINT;
- establishing the native BCPL calling convention and `GLOBAL`-vector layout used by generated code;
- reconstructing the necessary native runtime and MVS services, including the surviving `BCPLMAIN` contract;
- assembling and link-editing generated code under MVS 3.8J; and
- eventually compiling enough of the compiler itself to close the native bootstrap loop.

## Historical evidence

The executable bootstrap baseline is under:

- `richards-bcpltape/mr10/bcplkit/`

Useful contemporary documentation includes:

- `richards-bcpltape/mr10/print/manual` — the 1974 BCPL Programming Manual, including "Using BCPL on the 370";
- `richards-bcpltape/mr10/text/bstrbcpl` — bootstrap material;
- `richards-bcpltape/mr10/text/intcode` — INTCODE documentation.

Later Cambridge sources under `richards-bcpltape/bcplib/` remain valuable comparative evidence. They are not a prerequisite front end that must first be rebuilt before native code generation can proceed.

## Distant delivery question: BCPL/assembler interoperability

When the compiler and runtime are mature enough for application delivery, document and support an explicit interface between generated BCPL and separately assembled System/370 code.

The intended audience is an application programmer who wants to write a routine in assembler, assemble and link it with a BCPL program, and invoke it naturally from BCPL. This should eventually include worked templates rather than leaving programmers to reverse-engineer the compiler ABI.

Questions to settle before documenting the interface include:

- how a BCPL `GLOBAL` entry names or receives the address of an external assembler routine;
- the exact argument-register and return-value conventions, including more than four arguments if the language/runtime permits them;
- workspace, linkage, and base-register obligations across a BCPL-to-assembler call;
- which registers an assembler routine must preserve and which it may destroy;
- BCPL word-pointer versus native byte-address representation at the boundary;
- character, string, vector, and structure representation rules;
- how separately assembled object modules should be presented to the MVS linkage editor;
- how an assembler routine calls back into BCPL, if that direction is supported;
- how assembler code should call portable BCPL library services versus host-specific MVS services; and
- what error, storage, stream, and termination conventions are safe for application-written assembler.

A future delivery should ideally include at least:

```text
assembler-callable-from-bcpl.asm
bcpl-calls-assembler.bcpl
link-bcpl-and-assembler.jcl
```

plus a concise programmer-facing ABI reference.

This is intentionally deferred. The native regression panel should first establish the calling convention empirically and the runtime/library boundary should stabilize before the project promises an application-facing mixed-language interface.

## Working rule

Keep the runnable kit compiler as the reference path. Change historical code only when the MVS host, IFOX, or an observed incompatibility requires it, and preserve evidence for each such change.
