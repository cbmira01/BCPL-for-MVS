# Native BCPL ABI on System/370

## Purpose

This document records the native BCPL execution conventions recoverable from the surviving IBM/370 compiler source.

It is not yet a complete replacement for the missing historical `BCPLMAIN`. It is the minimum ABI baseline the native code generator should preserve.

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

## Register assignments

The later IBM/370 generator defines these integer-register roles:

```text
R1   K4    constant/base helper
R2   K8    constant/base helper
R3   K12   constant/base helper
R4   B     function/code address and section base role
R5   P     BCPL workspace/frame pointer
R6   L     link register for BCPL-to-BCPL calls
R7   A1    first argument / function result
R8   A2    second argument
R9   A3    third argument
R10  A4    fourth argument
R11  S     runtime/support base / return support register
R12  G     BCPL global-vector base
R13        used in generated section entry/save conventions
R14  A     auxiliary/runtime call link register
R15  W     new workspace/frame address during calls
```

The names above come from the historical generator and should be preserved in implementation notes and reconstructed source where practical.

---

## BCPL word and address model

The later compiler assumes:

```text
32-bit BCPL words
4 bytes per word
```

Workspace and global slot numbers are therefore translated to System/370 byte displacements by multiplying by four.

Examples from the generator include:

```text
local N  -> 4*N(R5)
global N -> 4*N(R12)
```

The native ABI therefore uses real byte addresses in System/370 registers while preserving BCPL's logical word indexing in compiler-generated offsets.

---

## Workspace pointer `P`

R5 (`R.P`) is the BCPL workspace/frame pointer.

The OCODE stack model and procedure protocol use numbered workspace words relative to `P`.

The later generator maintains a virtual stack and spills values into slots relative to R5.

A call computes the new workspace pointer from the caller's workspace and the OCODE frame offset `K`:

```text
R15 := R5 + 4*K
```

R15 is then available to the called routine as the new frame/workspace address.

---

## Procedure call convention

The later generator's `CGAPPLY` establishes the historical BCPL call protocol.

At a high level:

```text
caller:
    place first arguments in R7-R10 when possible
    place remaining arguments in the new workspace
    R15 := address of callee workspace
    R4  := function/routine address
    BALR R6,R4
```

The first four arguments map to:

```text
arg1 -> R7
arg2 -> R8
arg3 -> R9
arg4 -> R10
```

Additional arguments are stored in workspace words.

The code generator specifically avoids allocating R15 for unrelated expression work because `CGAPPLY` depends on it.

---

## Function result

For `FNAP`, the later generator treats R7 (`R.A1`) as the returned function value.

`FNRN` moves the expression result into R7 before returning.

Therefore:

```text
BCPL function result -> R7
```

A routine call (`RTAP`) has no required expression result.

---

## Procedure entry / SAVE

The later generator separates an `ENTRY` marker from `SAVE N`.

`ENTRY` establishes a generated procedure label and associated name/debug information.

`SAVE N` performs the concrete entry-frame setup. Without stack-checking enabled, the relevant behavior is:

```text
store incoming registers beginning with R4
R5 := R15
initialize compiler view of workspace size N
record register arguments into local workspace slots
```

The exact `STM` upper register depends on frame size, capped at R10.

This confirms that R15 carries the new frame address into the callee and R5 becomes the callee's active BCPL workspace pointer.

---

## Return convention

The generator emits procedure return as:

```text
BCR 15,R11
```

where R11 is named `R.S`.

This is important: BCPL-to-BCPL return does **not** simply branch through the `BALR` link in R6.

The missing runtime/startup machinery therefore has some responsibility for establishing the R11 support convention used by generated procedures.

This is one of the highest-priority runtime details to recover experimentally before complex native calls are trusted.

---

## Call link R6

BCPL calls use:

```text
BALR R6,R4
```

R6 receives the hardware return address.

The generated callee protocol and/or support base reached through R11 transforms this into the historical BCPL return mechanism.

The surviving generator is clear that R6 participates in calls, while R11 is used by `RTRN/FNRN` returns. The exact handoff between them is not completely reconstructable from the surviving generator alone because the machine-code runtime source is missing.

### Required experiment

The first reconstructed runtime shim should expose this mechanism with the smallest possible two-procedure native program and retain the listing/register reasoning as evidence.

---

## Global vector

R12 (`R.G`) is the BCPL global-vector base.

Generated global loads/stores are based on R12.

The later generator emits a global initialization structure containing global numbers and generated addresses. The compiler's in-memory `LOADCODE()` routine independently confirms the model by populating global-vector entries from generated pairs.

### Decision

Native modules continue to rendezvous through the BCPL GLOBAL vector. This is the native continuation of the linkage model already used successfully by separately compiled interpreted BCPL modules.

---

## Section entry

The generated section begins with code structurally like:

```text
STM 14,12,12(13)
L   R4,12(R15)
BCR 15,R4
<metadata / external address>
```

The surviving `bcplib/asm/program` module shows the same prologue pattern and an external reference to `BCPLMAIN`.

This means a generated BCPL section is not entered like a standalone conventional MVS assembler program. It expects a surrounding BCPL runtime/startup environment.

### Decision

Do not force each generated BCPL section to obey ordinary MVS program-entry linkage internally.

Construct an MVS-compatible outer shim that establishes the BCPL machine state, then let generated BCPL code use its historical ABI.

---

## `BCPLMAIN` external dependency

`CGSTART` creates an external reference named `BCPLMAIN`.

The historical build JCL states that the missing `BCPLMAIN` assembler source supplied the machine-code library and produced runtime pieces including:

```text
BCPLMAIN
$MAIN$
$BLOCK$
$LOAD$
$TPUT$
```

The generator and application sections therefore assume more than a single entry stub.

### Initial reconstruction policy

The first reconstructed `BCPLMAIN` should be deliberately minimal and should only implement services demonstrated as necessary by native acceptance tests.

Do not claim compatibility with the complete historical runtime until evidence supports it.

---

## Global-vector initialization

The later compiler's `LOADCODE()` provides valuable evidence for initialization semantics.

It:

1. establishes a global vector;
2. initializes otherwise-unset entries with recognizable sentinel values;
3. walks the generated global-definition table;
4. installs generated addresses into the corresponding global slots.

A linkable native implementation does not need to copy this exact in-memory loader algorithm, but it must reproduce the same resulting GLOBAL relationships.

---

## Base/address conventions

The generator names helper registers R1/R2/R3 as K4/K8/K12 and works within System/370 displacement constraints.

It also tracks per-procedure/section base information and enforces a code-size limit of approximately 4095 words.

### Initial policy

Preserve the historical base-management strategy while reviving the backend.

Do not optimize or redesign addressability until the historical generated code runs reliably.

---

## Byte access

The later generator's direct byte operations calculate a byte displacement from BCPL word address plus byte index and use `IC`/`STC`.

This confirms the expected native representation:

```text
BCPL word address -> System/370 byte address
byte index        -> byte displacement
```

The exact byte-order convention should continue to be validated against the working interpreted `GETBYTE`/`PUTBYTE` behavior.

---

## MVS boundary

The reconstructed runtime must bridge two conventions:

```text
MVS program linkage
        |
        v
reconstructed BCPL startup/runtime
        |
        v
historical BCPL/System-370 ABI
```

The outer MVS-facing code is free to use standard save areas, entry registers, GETMAIN, QSAM, and other services.

Generated BCPL procedures should not be rewritten to look like ordinary MVS assembler subroutines.

---

## ABI items considered established

The surviving generator strongly supports these points:

```text
word size                 32 bits
workspace pointer         R5
function/code address     R4 at call
call link                 BALR R6,R4
first four arguments      R7-R10
function result           R7
new frame/workspace       R15 before call, then R5 in callee
global-vector base        R12
BCPL return support       R11
word displacement scale   4 bytes
```

---

## ABI items still requiring runtime reconstruction

These are not fully determined from surviving source alone:

```text
exact startup register state supplied by BCPLMAIN
precise R6 -> R11 return-support mechanism
layout/ownership of root workspace
complete system-function dispatch
termination path
stack-limit/checking runtime protocol
exact runtime service table addressed through R11
MVS save-area interaction at outer boundary
full cross-module loader/segment conventions
```

These should be resolved in the acceptance order rather than speculated into existence.
