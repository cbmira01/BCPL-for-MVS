# System/370 assembler sources

This directory contains project-written/reconstructed assembler for MVS 3.8J, most importantly the hosted INTCODE interpreter.

## ICINT line

The current promoted interpreter is selected by `config/CURRENT`; `tools/current-icint` resolves that selection for scripts and users. At the time of this README the promoted source is `asm/icintv17.asm`.

The numbered ICINT files are retained because each is a useful reconstruction milestone rather than an arbitrary backup:

- V12 established the main historical instruction model and basic execution path;
- V13 added map/store work used by later diagnostics;
- V14/V14-trace developed tracing and reporting;
- V15 expanded hosted stream support;
- V16 moved generic streams to dynamic MVS-managed storage and established character translation behavior;
- V17 is the current baseline, retaining the V16 stream work while adding recent-instruction diagnostics and guarded store handling.

The interpreter is based closely on `richards-bcpltape/mr10/bcplkit/icint`. The reconstruction rule is to stay close to that historical implementation and depart only where MVS hosting, diagnostics, or demonstrated correctness requires it.

## Building

For direct assembler work, generate a self-contained IFOX job with:

```sh
tools/make-asm-job asm/program.asm --output-dir jcl --listing heavy
```

For ICINT workloads, use `tools/run-intcode` or `tools/compile-and-run`; they generate the necessary assembly/link/run jobs automatically.

`hello-world.asm` is a small IFOX example retained as a toolchain sanity check.

## Native direction

ICINT is the bootstrap host, not the end product. The native compiler work now starts from a surviving historical System/370 BCPL code generator. The assembler work ahead is therefore centered on validating generated S/370 code and reconstructing the native runtime/MVS service layer, not on inventing a backend without historical reference.

`bcplmain-wip.asm` is the working native-runtime reconstruction. It separates experimentally established CG370/BCPLMAIN contracts from provisional implementations and explicit stubs for unresolved runtime services.\n\nSee `native-compiler/README.md` for the current compiler direction and `THIRD-PARTY-NOTICES.md` for historical provenance.