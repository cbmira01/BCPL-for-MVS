# Native BCPL compiler for MVS

## Change of approach

The native-compiler effort has been reset.

The project is no longer attempting to use the surviving MR10 bootstrap compiler as a stepping stone to rebuild the much later Cambridge compiler before native code generation can begin. Instead, the surviving MR10 BCPL kit is now the compiler baseline.

The immediate goal is:

> Build a native System/370 implementation of the surviving MR10-family BCPL compiler for MVS 3.8J.

In practical terms, the existing MR10 SYN and TRN phases remain the language front end. A new System/370 code generator will consume their OCODE and emit assembler suitable for the MVS assembler/link-edit toolchain. A native MVS BCPL runtime will support the generated programs.

This is intentionally an early-BCPL implementation. Later Cambridge language facilities may be added incrementally, but they are no longer prerequisites for a successful compiler.

See [`kit-compiler-strategy.md`](kit-compiler-strategy.md) for the historical reasoning, the lessons from the Cambridge bootstrap experiment, the language-scope decision, programmer-documentation plans, and the initial implementation direction.

## Historical sources

The principal surviving compiler baseline is under:

- `richards-bcpltape/mr10/bcplkit/`

Important contemporary documentation also survives in the tape image, notably:

- `richards-bcpltape/mr10/print/manual` — *The BCPL Programming Manual*, M. Richards, November 1974; includes the language definition, runtime library, and a section specifically titled **Using BCPL on the 370**.
- `richards-bcpltape/mr10/text/bstrbcpl` — bootstrap material.
- `richards-bcpltape/mr10/text/intcode` — INTCODE documentation.

The later Cambridge sources remain under `richards-bcpltape/bcplib/` as historical and design evidence. They are not the baseline source language for the new native compiler effort.

## Working principle

First produce a small, sound, documented native BCPL for MVS from the compiler we actually possess and can execute. Improvements can then be made forward from that known working point.
