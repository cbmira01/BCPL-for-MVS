# Native BCPL ABI on System/370

## Purpose

This document records the native BCPL execution conventions recoverable from the surviving IBM/370 compiler source and turns them into the runtime contract for the first reconstructed native compiler.

It is **not** yet a complete replacement for the missing historical `BCPLMAIN`. It defines what generated native BCPL code may assume, what the reconstructed runtime shim must establish, and which details remain experimental.

Primary evidence:

```text
richards-bcpltape/bcplib/bcpl/cghdr
richards-bcpltape/bcplib/bcpl/cg
richards-bcpltape/bcplib/bcpl/bcpl
richards-bcpltape/bcplib/asm/program
richards-bcpltape/bcplib/jcl/makeobj
richards-bcpltape/bcplib/jcl/makelib
```

---

# 1. Established machine model

## BCPL word

```text
word size             32 bits
bytes per word        4
native address unit   byte
BCPL logical indexing word-oriented
```

Generated workspace/global offsets therefore use:

```text
BCPL slot n -> byte displacement 4*n
```

No 24-bit BCPL word model is implied merely because the target is classic System/370; BCPL values are full 32-bit words in the surviving generator.

---

# 2. Register contract

The recovered register assignments are:

```text
R1   K4    constant/base helper
R2   K8    constant/base helper
R3   K12   constant/base helper
R4   B     code/function address; code-base role
R5   P     current BCPL workspace/frame pointer
R6   L     hardware link register for BCPL call
R7   A1    argument 1 / function result
R8   A2    argument 2
R9   A3    argument 3
R10  A4    argument 4
R11  S     BCPL runtime/support base and return-support register
R12  G     BCPL GLOBAL-vector base
R13        outer/generated-entry save-area interaction
R14  A     auxiliary/runtime-call link
R15  W     new workspace address during BCPL calls
```

### Contract

Generated BCPL-to-BCPL code may rely on these assignments.

The MVS-facing startup shim may use conventional linkage on entry, but it must establish the BCPL register state before entering generated code.

Do not redesign this map to resemble ordinary OS assembler linkage.

---

# 3. Workspace/frame contract

R5 (`P`) points to the current BCPL workspace.

Generated local accesses use:

```text
P[n] == fullword at 4*n(R5)
```

The OCODE/call convention reserves low workspace slots for procedure linkage and argument preservation. The later CG's `SAVE` logic maps incoming argument registers into workspace beginning at the historical local-slot convention used by the compiler.

For the first reconstructed runtime we do **not** need a general MVS stack abstraction. We need a contiguous writable BCPL workspace large enough for the accepted program and runtime frames.

### Root-frame requirement

Before first BCPL procedure entry, the runtime must provide:

- a valid writable root workspace;
- R5/R15 values consistent with entering the first generated procedure;
- sufficient storage to prevent accepted test programs from colliding with runtime state;
- deterministic failure if the provisional workspace is exhausted.

Exact production stack-growth policy is deferred.

---

# 4. Procedure call contract

The surviving `CGAPPLY` provides the baseline.

For a call with OCODE frame/workspace offset `K`:

```text
R15 := R5 + 4*K
R4  := callee address
R7  := argument 1, when present
R8  := argument 2, when present
R9  := argument 3, when present
R10 := argument 4, when present
additional arguments -> new workspace
BALR R6,R4
```

The code generator may have to spill/reload values before this sequence; those are implementation details, not ABI changes.

### Function versus routine

```text
FNAP  expects result in R7
RTAP  has no expression result
```

### Contract

The reconstructed CG370 must preserve the historical `K`-based workspace calculation rather than introduce a new caller-allocated MVS save-area frame.

---

# 5. Procedure entry / SAVE contract

`ENTRY` identifies and labels a generated BCPL procedure.

`SAVE N` establishes the concrete callee frame.

The later CG shows this sequence in substance:

```text
store incoming BCPL registers needed by frame
R5 := R15
materialize register arguments in expected workspace slots
initialize procedure workspace depth N
```

The exact `STM` range depends on the frame/argument requirement and is capped at the argument-register range.

### Contract

For the first native CG, generated procedure entry must remain structurally compatible with the later generator. Optimization may come later.

---

# 6. Function result contract

A BCPL function returns its value in:

```text
R7 (A1)
```

`FNRN` moves the result expression into R7 before return.

The caller's `FNAP` path then treats R7 as the pushed result value.

This is established strongly enough to use in the first call acceptance test.

---

# 7. Return-support contract and unresolved R6/R11 handoff

Calls use:

```text
BALR R6,R4
```

but generated `FNRN` / `RTRN` returns use:

```text
BCR 15,R11
```

This means R11 is not merely an arbitrary preserved register. It participates in the historical BCPL return/runtime support mechanism.

The missing `BCPLMAIN` source prevents a complete static reconstruction of how the R6 hardware return address is transformed into or serviced through R11.

### Decision

The first runtime shim must implement **only enough R11 support to make A3 (single BCPL function call) correct and explainable**.

Do not hard-code a guessed full historical support-vector layout before that experiment.

### Required evidence

When A3 first passes, retain:

- generated IFOX source;
- assembler listing around caller and callee;
- startup/runtime shim source;
- a written register trace showing R4/R5/R6/R7/R11/R15 across call and return.

That experiment promotes the return mechanism from “inferred” to “established for reconstruction.”

---

# 8. GLOBAL-vector contract

R12 (`G`) is the BCPL GLOBAL-vector base.

Generated operations use:

```text
LG n -> load 4*n(R12)
SG n -> store 4*n(R12)
LLG n -> address 4*n(R12)
```

Generated modules also emit GLOBAL-definition information associating global numbers with generated addresses.

The later compiler's `LOADCODE()` independently demonstrates the intended result: initialize the vector, then install addresses from the module's global-definition table.

### Contract

The reconstructed runtime/startup must provide one GLOBAL vector shared by all linked BCPL modules in the load module.

MVS external linkage does not replace this mechanism.

### Initial global-vector policy

For acceptance work:

- allocate a fixed-size vector comfortably above the highest global used by the test;
- initialize unused entries deterministically, preferably with an unmistakable invalid/sentinel value;
- install module definitions before invoking `START`;
- fail loudly on an out-of-range global definition.

Production sizing can be revisited later.

---

# 9. Program entry contract

Generated sections are **not** ordinary standalone MVS main programs.

Surviving generated/handwritten section entry has the characteristic form:

```text
STM   14,12,12(13)
L     R4,12(R15)
BCR   15,R4
... metadata / external address ...
```

`bcplib/asm/program` also declares `EXTRN BCPLMAIN` and follows this pattern.

### Contract

The reconstructed system has two distinct boundaries:

```text
MVS entry linkage
      |
      v
minimal BCPL startup/runtime shim
      |
      v
historical BCPL/System-370 procedure ABI
```

Only the outer shim must look conventional to MVS.

---

# 10. Minimal reconstructed runtime contract

The first runtime shim is intentionally smaller than historical `BCPLMAIN`.

For acceptance cases A0-A5 it must provide, at minimum:

## Startup

- preserve/restore MVS caller state sufficiently for normal program return;
- obtain or reserve BCPL workspace storage;
- reserve GLOBAL-vector storage;
- initialize R12 to the GLOBAL vector;
- initialize root BCPL workspace state;
- install generated GLOBAL definitions;
- identify global 1 / `START` entry and invoke it using the native BCPL ABI.

## Return support

- establish the R11 convention needed by generated BCPL returns;
- make nested BCPL calls work by A3/A4;
- preserve caller workspace and return address according to the recovered ABI.

## Termination

- provide the support path used by generated `FINISH`;
- return to MVS normally for success;
- provide a deterministic non-success path for runtime fatal errors.

## Minimal result/output support

For early semantic tests, choose one of these in order of preference:

1. a tiny runtime routine callable through a known GLOBAL slot that writes a deterministic line to `SYSPRINT`;
2. an even smaller test-only result mailbox inspected by the MVS wrapper, if formatted output would distract from ABI work.

The acceptance corpus should not require full historical `WRITEF` before arithmetic/call/global semantics are proven.

---

# 11. Runtime services explicitly not required initially

A0-A5 do not require the full historical machine-code library.

Defer until demanded by native tests:

```text
full stream subsystem
FINDINPUT/FINDOUTPUT
GETVEC/FREEVEC production integration
LOADSEG/UNLOADSEG
coroutines/CHANGECO
postmortem/debugger services
stack-check/counting services
floating point
TPUT/terminal support
complete historical system-function dispatcher
```

---

# 12. Static data and relocation contract

Because the initial reconstructed CG emits IFOX assembler, relocation is initially delegated to IFOX/IEWL.

CG370 must emit assembler expressions/symbol references for:

- procedure labels;
- string/static data labels;
- global-definition addresses;
- runtime external symbols where truly required.

This avoids reconstructing object-card relocation simultaneously with code semantics.

The historical relocation/deck machinery remains the compatibility reference for later direct-object emission.

---

# 13. Base/addressability contract

System/370 RX-format displacements are limited to 12 bits.

The later CG explicitly manages bases and limits generated section size to roughly 4095 words.

### Initial decision

Preserve bounded sections and explicit base management.

For IFOX output, generated source must include a clear base-register plan and `USING`/`DROP` directives or equivalent generated address forms sufficient for IFOX to diagnose reachability.

Do not solve arbitrary-size code before the historical section model works.

---

# 14. Byte representation contract

Native BCPL word addresses become System/370 byte addresses. Byte access in the later generator uses `IC` and `STC` after scaling/index calculation.

The exact packed-string/byte ordering must match the already-working interpreted `GETBYTE`/`PUTBYTE` behavior.

### Rule

Do not declare byte semantics established solely from reading the later CG. A6 must compare native results with ICINT for the same string source.

---

# 15. MVS-facing contract

The runtime shim may use ordinary MVS facilities internally:

- standard entry/save-area conventions;
- GETMAIN/FREEMAIN;
- QSAM or existing project stream machinery;
- normal MVS return codes and ABEND handling.

But these choices must terminate at the runtime boundary. Generated BCPL-to-BCPL calls retain the historical ABI.

---

# 16. Established versus provisional ABI

## Established strongly enough to implement

```text
32-bit word
4-byte slot scale
R4  callee/code address
R5  current P/workspace
R6  BALR call link
R7-R10 first four arguments
R7  function result
R12 global-vector base
R15 new frame/workspace address
P-relative locals
G-relative globals
GLOBAL-vector cross-module linkage
```

## Strong evidence, but first native experiment must confirm exact runtime behavior

```text
R11 return/support mechanism
root frame layout
START invocation details
FINISH support entry
module GLOBAL-definition installation sequence
```

## Deferred/unknown

```text
complete historical BCPLMAIN service table
full system-function dispatch
stack-check/counting protocol
segment loader ABI
postmortem runtime layout
complete overlay conventions
```

---

# 17. Acceptance gates for this contract

The ABI is considered sufficiently established for further compiler expansion when:

```text
A0 proves startup/FINISH
A3 proves one nested function call and return
A4 proves argument registers/workspace overflow arguments
A5 proves GLOBAL vector initialization and mutation
A7 proves the same ABI across separately generated modules
```

Each gate should update this document when experiment reveals a detail more precise than the current source-derived contract.
