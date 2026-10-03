# Native compiler acceptance corpus

## Purpose

This document defines the first native-code acceptance corpus for the reconstructed System/370 BCPL compiler.

The objective is not to demonstrate the whole language at once. The objective is to expose one compiler/runtime contract at a time and compare native behavior with the already-working interpreted path.

Each source program is intentionally tiny and stable.

The preferred validation pattern is:

```text
same BCPL source
     |
     +--> current MR10 compiler --> CGI --> INTCODE --> ICINT
     |
     +--> current MR10 compiler --> saved OCODE --> CG370 --> IFOX --> IEWL --> native

compare semantic result
```

For the earliest native cases, semantic results are written into test-only GLOBAL mailbox slots rather than through formatted I/O. This prevents `WRITEF` and stream reconstruction from becoming prerequisites for validating arithmetic, control flow, calls, and GLOBAL-vector semantics.

The interpreted path remains the language-semantics reference. Native assembler listings and link maps are retained as target-code evidence.

---

## Corpus layout

The actual sources live in:

```text
native-compiler/acceptance/
```

Each case contains:

```text
<name>.bcpl
<name>.expected
<name>.ocode          saved/canonical OCODE once captured
```

The acceptance-directory README documents the test-only GLOBAL convention.

Do not identify retained evidence by JES job number.

---

## Test-only result globals

The early corpus reserves:

```text
NATIVE_COUNTER:399
NATIVE_RESULT:400
```

These are outside the project general-purpose library range 96..159 and remain within ICINT V17's current 0..400 GLOBAL capacity.

They are **not production ABI assignments**.

The native test shim may inspect these slots after `FINISH` or as part of its termination path.

Expected files use notation such as:

```text
GLOBAL 400 = 42
```

---

## A0 — minimal startup and finish

Source:

```text
acceptance/a0-finish.bcpl
```

### What it proves

- generated section assembles under IFOX;
- object link-edits under IEWL;
- MVS startup shim establishes enough BCPL state to enter generated code;
- global slot 1 resolves `START`;
- native `FINISH`/termination works;
- no ordinary BCPL function call is required yet.

### Expected result

```text
NORMAL COMPLETION
```

This separates startup/linkage from expression and I/O semantics.

---

## A1 — constant and integer arithmetic

Source:

```text
acceptance/a1-arithmetic.bcpl
```

Computes:

```text
(7+5)*4-6 = 42
```

Expected result:

```text
GLOBAL 400 = 42
```

Likely OCODE coverage includes:

```text
LN
PLUS
MULT
MINUS
SG
FINISH
```

### What it proves

- literal loading;
- evaluation-stack discipline;
- arithmetic instruction selection;
- result preservation;
- first generated GLOBAL store.

---

## A2 — local variables, comparison, branch, loop

Source:

```text
acceptance/a2-loop.bcpl
```

Computes the sum `1+2+...+10`.

Expected result:

```text
GLOBAL 400 = 55
```

Likely OCODE surface includes:

```text
LP
SP
LN
PLUS
LE or LS
JT/JF
JUMP
LAB
STACK/STORE as generated
```

### What it proves

- local workspace addressing through R5;
- store/load consistency;
- integer comparison;
- condition-code generation;
- forward/backward labels;
- control-flow joins;
- base/address reachability for ordinary code.

---

## A3 — BCPL function call and return value

Source:

```text
acceptance/a3-function-call.bcpl
```

Defines `ADD3(X)` and calls it with 7.

Expected result:

```text
GLOBAL 400 = 10
```

### What it proves

This is the decisive first ABI test.

It must exercise and verify:

```text
R4   callee address
R15  new workspace address
R6   BALR call link
R5   callee P/workspace
R7   first argument and function result
R11  native BCPL return-support convention
ENTRY / SAVE / FNAP / FNRN
```

The first successful run should retain an annotated listing/register trace around caller and callee.

---

## A4 — five arguments

Source:

```text
acceptance/a4-arguments.bcpl
```

Calls `SUM5(10,20,30,40,50)`.

Expected result:

```text
GLOBAL 400 = 150
```

### What it proves

- R7-R10 argument convention for the first four arguments;
- fifth argument through workspace;
- argument-to-workspace save performed by `SAVE`;
- workspace offset `K` handling;
- caller/callee stack integrity.

A separate RTAP-specific case can be added after this function-call path is established.

---

## A5 — GLOBAL vector load/store

Source:

```text
acceptance/a5-global.bcpl
```

Uses two GLOBAL slots and mutates one of them.

Expected result:

```text
GLOBAL 399 = 18
GLOBAL 400 = 1718
```

### What it proves

- R12 global-vector base;
- `LG`, `SG`, and possibly `LLG` as actually emitted;
- generated GLOBAL definition table;
- startup/runtime global initialization;
- independent GLOBAL slot state;
- correct distinction between BCPL GLOBAL linkage and MVS external symbols.

This is a prerequisite for useful library calls and separate modules.

---

## A6 — strings and bytes

Not yet instantiated as source.

It should use one packed BCPL string and inspect a few bytes only after saved OCODE confirms whether current MR10 output uses global runtime calls or dedicated byte-oriented OCODE.

### What it should prove

- `LSTR` and generated static string data;
- label/address constants;
- BCPL packed string representation;
- byte-address calculation;
- native byte behavior matching ICINT.

---

## A7 — separate modules through GLOBAL

Not yet instantiated as source.

Compile a main module and helper module separately, with the helper exported through a GLOBAL slot.

### What it should prove

- more than one generated native section/object;
- GLOBAL initialization from multiple modules;
- IEWL combination of native objects without replacing BCPL linkage semantics;
- cross-module code addresses;
- consistent ABI across separately generated modules.

---

## A8 — minimal portable library call

Not yet instantiated as source.

A good early candidate is `library/integer-utils.bcpl`, because it does not require storage allocation, streams, coroutines, or host-dependent machinery.

### What it should prove

- ordinary project library source compiles through the native path;
- project-local GLOBAL allocation survives native compilation;
- generated code is compatible across nontrivial BCPL modules.

---

# Corpus intentionally deferred

Do not require these before the integer/native ABI path is stable:

```text
GETVEC/FREEVEC
coroutines / CHANGECO
named MVS streams
READLINE
floating point
LOADSEG / UNLOADSEG
compiler phases themselves
```

They are later native milestones with additional runtime requirements.

---

# OCODE capture requirement

Before implementing each test beyond A0, save its OCODE through the working MR10 compiler.

For each accepted case record:

```text
source path
exact command used to save OCODE
OCODE file
set of OCODE operations observed
expected mailbox/result state
native assembler generated
native result
```

Update the coverage table in `ocode-contract.md` from observed OCODE rather than manifest membership alone.

---

# Pass criteria

A native acceptance case passes only when all applicable levels succeed:

1. MR10 source compilation succeeds.
2. Saved OCODE is parseable by CG370.
3. CG370 reports no unsupported operation.
4. Generated IFOX assembler assembles without errors.
5. IEWL links the generated object with the required runtime shim.
6. The native MVS program completes normally.
7. Test GLOBAL state or later semantic output matches the expected result exactly.

Warnings and nonzero assembler/link-editor condition codes must be explained rather than casually accepted.

---

# Recommended first implementation sequence

```text
A0 startup/finish
A1 integer expression
A2 locals/branch/loop
A3 function call/return
A4 five arguments
A5 globals
A7 separate modules
A8 simple library
A6 strings/bytes
```

After A0-A5 pass, the fundamental native ABI and integer compiler path should be stable enough to begin broader language-suite coverage.
