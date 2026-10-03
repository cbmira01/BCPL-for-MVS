# Native compiler reconstruction

This directory is the working area for the transition from the proven INTCODE bootstrap to native System/370 BCPL compilation under MVS 3.8J.

The important readiness conclusion is that this project does **not** need to invent an IBM System/370 BCPL backend from scratch. The Richards transport material contains a substantial later System/370 code generator in:

```text
richards-bcpltape/bcplib/bcpl/cg
richards-bcpltape/bcplib/bcpl/cghdr
```

It includes System/370 instruction selection, register conventions, BCPL procedure-call generation, base/address management, switch generation, byte operations, floating-point support, global initialization data, relocations, a human-readable listing path, and an 80-column object-deck path.

At the same time, the compiler that currently runs under ICINT comes from the earlier MR10 kit:

```text
richards-bcpltape/mr10/bcplkit/syni
richards-bcpltape/mr10/bcplkit/trni
richards-bcpltape/mr10/bcplkit/cgi
```

The native compiler work therefore begins as a **bridge between two surviving lineages**:

```text
MR10 front end / OCODE semantics
             |
             v
compatibility and bootstrap adaptation
             |
             v
later IBM System/370 CG implementation
             |
             v
MVS object deck + listing
             |
             v
IEWL
             |
             v
native load module
```

The readiness research is split into:

- [`readiness-decisions.md`](readiness-decisions.md) — evidence, decisions, risks, and implementation order;
- [`ocode-contract.md`](ocode-contract.md) — OCODE compatibility surface between the working MR10 compiler and the later S/370 generator;
- [`native-abi.md`](native-abi.md) — the System/370 BCPL register, call-frame, global, and runtime conventions recoverable from surviving source;
- [`acceptance-plan.md`](acceptance-plan.md) — staged native-code acceptance tests and interpreted/native cross-checking.

## Primary historical evidence

The main files for this phase are:

```text
richards-bcpltape/INDEX
richards-bcpltape/mr10/bcplkit/cg
richards-bcpltape/bcplib/bcpl/bcpl
richards-bcpltape/bcplib/bcpl/cghdr
richards-bcpltape/bcplib/bcpl/cg
richards-bcpltape/bcplib/asm/program
richards-bcpltape/bcplib/jcl/makeobj
richards-bcpltape/bcplib/jcl/makelib
richards-bcpltape/sys1/userproc/bcplclg
```

A crucial absence is also evidence: the tape index identifies `BCPLIB.ASM(BCPLMAIN)` but the corresponding source is not present in the surviving repository. The native runtime boundary therefore still requires reconstruction.

## Current decision

The next implementation target is **not** the whole native compiler and **not** BCPLMAIN in full.

The next target is a bootstrap-capable native code-generation path that can consume OCODE produced by the already-working MR10 front end and produce linkable System/370 code while preserving as much of the surviving IBM/370 generator as practical.

Implementation should begin only after the contracts in this directory are kept synchronized with what experiments establish.
