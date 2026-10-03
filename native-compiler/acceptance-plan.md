# Native compiler acceptance corpus

## Purpose

This document defines the first native-code acceptance corpus for the reconstructed System/370 BCPL compiler.

The objective is not to demonstrate the whole language at once. The objective is to expose one compiler/runtime contract at a time and compare native behavior with the already-working interpreted path.

Each source program should be tiny, stable, and have exact expected output.

The preferred validation pattern is:

```text
same BCPL source
     |
     +--> current MR10 compiler --> CGI --> INTCODE --> ICINT
     |
     +--> current MR10 compiler --> saved OCODE --> CG370 --> IFOX --> IEWL --> native

compare semantic output
```

The interpreted path is the language-semantics reference. Native assembler listings and link maps are retained as target-code evidence.

---

## Corpus layout

Use:

```text
native-compiler/acceptance/
```

Each case should eventually contain:

```text
<name>.bcpl
<name>.expected
<name>.ocode          saved/canonical OCODE once captured
README.md             only when a case needs special explanation
```

Do not identify retained evidence by JES job number.

---

## A0 — minimal startup and finish

### Source intent

A `START` routine that performs no calculation and terminates normally.

Conceptually:

```bcpl
GLOBAL $( START:1 $)

LET START() BE FINISH
```

### What it proves

- generated section can be assembled by IFOX;
- object can be link-edited by IEWL;
- MVS startup shim can establish enough BCPL machine state to enter generated code;
- global slot 1 can resolve `START`;
- native termination works;
- no ordinary BCPL function call is required yet.

### Expected output

No semantic output is required. Native completion must be normal and deterministic.

This is the first test because it separates startup/linkage from expression and I/O semantics.

---

## A1 — constant and integer arithmetic

### Source intent

Compute a fixed expression from literals using only integer arithmetic, then report the result through the smallest available result/output mechanism.

Suggested semantic result:

```text
RP: ARITH 42
```

Exercise at least:

```text
LN
PLUS
MINUS
MULT
```

Division/remainder can be added after the basic accumulator/register path is working.

### What it proves

- literal loading;
- evaluation stack discipline;
- arithmetic instruction selection;
- result preservation;
- one minimal runtime/global call if output is used.

---

## A2 — local variables, comparison, branch, loop

### Source intent

Use local variables and a loop to compute a simple sum, for example `1+2+...+10`.

Expected semantic result:

```text
RP: LOOP 55
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

### Source intent

Define a small function such as:

```bcpl
LET ADD3(X) = X+3
```

and call it from `START`.

Expected semantic result:

```text
RP: CALL 10
```

### What it proves

This is the decisive ABI test.

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

The first successful run should be accompanied by a short register-by-register trace or annotated listing in the acceptance evidence.

Do not proceed to complicated native runtime work until this contract is understood.

---

## A4 — multiple arguments and routine call

### Source intent

Exercise two to four arguments and both function and routine application.

Example semantic output:

```text
RP: ARGS 10 20 30 40 100
```

### What it proves

- R7-R10 argument convention;
- argument-to-workspace save performed by `SAVE`;
- `FNAP` versus `RTAP` behavior;
- workspace offset `K` handling;
- caller/callee stack integrity.

A later variant should exercise a fifth argument so that at least one argument travels through workspace rather than only through argument registers.

---

## A5 — global vector load/store

### Source intent

Use a user global variable or global function so that generated code must load/store through R12.

Expected output should demonstrate both initial resolution and mutation, for example:

```text
RP: GLOBAL 17 18
```

### What it proves

- R12 global-vector base;
- `LG`, `SG`, and `LLG` as actually emitted;
- generated GLOBAL definition table;
- startup/runtime global initialization;
- correct distinction between BCPL GLOBAL linkage and MVS external symbols.

This is a prerequisite for useful library calls and separate modules.

---

## A6 — strings and bytes

### Source intent

Use one packed BCPL string and inspect a few bytes.

Expected output could be:

```text
RP: STRING 4 B C P L
```

### What it proves

- `LSTR` and generated static string data;
- label/address constants;
- BCPL packed string representation;
- byte-address calculation;
- either native byte operators or the runtime `GETBYTE` path, depending on what MR10 OCODE actually emits.

This test should be implemented only after saved OCODE confirms the relevant MR10 form.

---

## A7 — separate modules through GLOBAL

### Source intent

Compile a main module and a helper module separately, with the helper exported through a GLOBAL slot.

Expected output:

```text
RP: MODULE 42
```

### What it proves

- more than one generated native section/object;
- GLOBAL initialization from multiple modules;
- IEWL combination of native objects without replacing BCPL linkage semantics;
- cross-module code addresses;
- consistent ABI across separately generated modules.

This is the first strong indication that the native compiler is producing reusable BCPL objects rather than one-off standalone programs.

---

## A8 — minimal portable library call

After A7 is established, compile one already-tested portable library module alongside the main program.

A good early candidate is `library/integer-utils.bcpl`, because it does not require storage allocation, streams, coroutines, or host-dependent machinery.

Expected output should exercise one or two functions such as `ABS` and `GCD`.

### What it proves

- ordinary project library source can be compiled by the native path;
- project-local GLOBAL allocation convention survives native compilation;
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
expected semantic output
native assembler generated
native output
```

The OCODE inventory in `ocode-contract.md` should be updated from these observations.

---

# Pass criteria

A native acceptance case passes only when all applicable levels succeed:

1. MR10 source compilation succeeds.
2. Saved OCODE is parseable by CG370.
3. CG370 reports no unsupported operation.
4. Generated IFOX assembler assembles without errors.
5. IEWL links the generated object with the required runtime shim.
6. The native MVS program completes normally.
7. Semantic output matches the interpreted reference exactly, ignoring only deliberately documented presentation differences.

Warnings and nonzero assembler/link-editor condition codes must be explained rather than casually accepted.

---

# Recommended first implementation sequence

```text
A0 startup/finish
A1 integer expression
A2 locals/branch/loop
A3 function call/return
A4 arguments/routine call
A5 globals
A7 separate modules
A8 simple library
A6 strings/bytes
```

A6 is listed later than its number because byte/string behavior is less fundamental than establishing calls and GLOBAL linkage.

After these pass, the native backend is ready to begin compiling larger existing regression and language-suite programs.
