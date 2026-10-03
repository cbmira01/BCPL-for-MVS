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
reconstructed CG370 using later IBM/370 algorithms
             |
             v
IFOX assembler source
             |
             v
IFOX00 + IEWL
             |
             v
native load module
```

The historical direct object-deck generator remains important evidence and a later compatibility target, but the first reconstruction emits IFOX source so generated instructions, symbols, addressability, and relocation can be inspected directly.

The readiness research is split into:

- [`readiness-decisions.md`](readiness-decisions.md) — evidence, decisions, risks, and implementation order;
- [`ocode-contract.md`](ocode-contract.md) — OCODE instruction/semantics inventory and compatibility surface;
- [`native-abi.md`](native-abi.md) — the System/370 BCPL register, call-frame, GLOBAL, startup, and runtime contract;
- [`acceptance-plan.md`](acceptance-plan.md) — staged native-code acceptance gates and interpreted/native cross-checking;
- [`acceptance/README.md`](acceptance/README.md) — the actual small BCPL acceptance corpus.

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

## Current decisions

The next implementation target is **not** the whole native compiler and **not** BCPLMAIN in full.

It is a bootstrap-capable CG370 path that:

1. consumes OCODE produced by the already-working MR10 front end;
2. adapts the surviving later S/370 instruction-selection and ABI logic;
3. emits inspectable IFOX assembler;
4. links against a deliberately minimal reconstructed runtime/startup shim;
5. advances through the acceptance corpus one contract at a time.

The first acceptance sequence is:

```text
A0 startup/FINISH
A1 arithmetic
A2 locals/branch/loop
A3 function call/return
A4 multi-argument call
A5 GLOBAL vector
```

Only after these are understood should implementation expand toward separate modules, ordinary libraries, strings/bytes, and eventually compiler self-hosting.

The contracts in this directory are living reconstruction documents. Update them when experiments establish details more precisely than the surviving source alone can.
