# Native compiler readiness decisions

## Scope

This document records the decisions made before beginning native System/370 compiler implementation.

The decisions are based primarily on surviving source in `richards-bcpltape/`, especially the MR10 kit and the later IBM/370 compiler. Where the evidence is incomplete, the uncertainty is stated explicitly.

---

## Finding 1: a System/370 backend already survives

The later compiler source in:

```text
richards-bcpltape/bcplib/bcpl/cghdr
richards-bcpltape/bcplib/bcpl/cg
```

is already an IBM System/370 backend.

Evidence includes:

- `CG370` as the main code-generator entry;
- explicit System/370 register assignments;
- explicit IBM/370 opcodes such as `BALR`, `BCR`, `STM`, `LM`, `L`, `ST`, `AR`, `SR`, `MR`, `DR`, shifts, byte operations, and floating-point instructions;
- System/370 procedure entry/call generation;
- base/address management;
- switch generation;
- string/data generation;
- relocation lists;
- object-deck generation;
- external symbol processing;
- a human-readable listing path.

### Decision

**Do not design a new System/370 backend from first principles.**

The project should reconstruct/adapt the surviving backend unless experiments show a specific part is unusable.

---

## Finding 2: the working bootstrap and the surviving native backend are from different compiler lineages

The currently executable compiler is the MR10 INTCODE kit:

```text
SYNI
TRNI
CGI
```

Its BCPL source counterpart is under:

```text
richards-bcpltape/mr10/bcplkit/
```

The surviving native IBM/370 generator is from the later compiler under:

```text
richards-bcpltape/bcplib/bcpl/
```

The OCODE vocabularies overlap heavily but are not identical. The later compiler adds operations and conventions absent from the MR10 code generator.

### Decision

Treat the two lineages differently:

```text
MR10 compiler
    = source-language and current OCODE reference

later IBM/370 compiler
    = target-machine implementation reference
```

The first native bootstrap generator should implement the OCODE actually emitted by the working MR10 compiler, using the later S/370 CG as the source of target-machine algorithms and ABI conventions.

Do not require the complete later OCODE language before the first native program can run.

---

## Finding 3: the historical backend emitted both listings and linkable object decks

The later generator contains both readable listing and binary/deck paths. `CGSTART` records an external dependency on `BCPLMAIN`. `CGEND` performs relocation fixups and calls `DECKOUT()` when binary output is enabled.

The surviving historical procedure `BCPLCLG` ran:

```text
BCPL compiler
    |
    v
SYSGO object deck
    |
    v
IEWL linkage editor
    |
    v
load module
```

That historical object-deck path is valuable evidence and should ultimately be recoverable.

### Decision for reconstruction

**The first reconstructed CG370 will emit IFOX assembler source.**

The reasons are practical and diagnostic:

- generated code is directly readable;
- IFOX validates instruction forms and addressability;
- assembler listings expose generated addresses, symbols, constants, and base-register choices;
- assembler errors localize code-generator defects much better than malformed object cards;
- IEWL maps and relocation information remain available after assembly;
- the project already has a reliable assemble-link-run workflow under MVS;
- it separates semantic/code-generation reconstruction from historical object-deck encoding.

The initial native path is therefore:

```text
MR10 OCODE
    |
    v
reconstructed CG370
    |
    v
IFOX assembler source
    |
    v
IFOX00
    |
    v
System/370 object module
    |
    v
IEWL
    |
    v
native load module
```

### Deferred compatibility target

The original relocatable object-deck generator is **not discarded**. Once the native ABI and instruction selection are established, the historical `DECKOUT`/relocation path can be revived as a later compatibility and efficiency milestone.

This is a deliberate reconstruction choice, not a claim that the historical compiler itself primarily emitted assembler source.

---

## Finding 4: the later compiler already defines a BCPL/System/370 calling convention

The surviving generator assigns:

```text
R.B  = 4
R.P  = 5
R.L  = 6
R.A1 = 7
R.A2 = 8
R.A3 = 9
R.A4 = 10
R.S  = 11
R.G  = 12
R.A  = 14
R.W  = 15
```

`CGAPPLY` uses R7-R10 for the first four arguments when possible, R15 as the new workspace/frame address, R4 for the function address, and `BALR R6,R4` for the call.

`CGSAVE` establishes the callee frame and stores incoming register state. Function results are returned in R7 (`R.A1`). Returns branch through R11 (`R.S`).

### Decision

**Adopt the recovered historical System/370 BCPL call convention as the native ABI baseline.**

Do not invent a new linkage convention merely to resemble conventional MVS assembler linkage.

The BCPL-to-BCPL ABI may be unconventional by MVS standards; MVS compatibility belongs at the runtime boundary.

See `native-abi.md`.

---

## Finding 5: `BCPLMAIN` is fundamental but missing

The tape index explicitly lists:

```text
BCPLIB.ASM(BCPLMAIN)    -
BCPLIB.OBJ(BCPLMAIN)    -
```

The source and object are absent from the surviving repository.

The surviving build JCL says `BCPLMAIN` contained the entire machine-code library and was processed and assembled to supply runtime members including:

```text
$MAIN$
BCPLMAIN
$BLOCK$
$LOAD$
$TPUT$
```

The generator itself emits an external reference to `BCPLMAIN`.

### Decision

Do **not** block code-generator reconstruction until the complete historical `BCPLMAIN` has been recreated.

Instead reconstruct the runtime boundary incrementally, beginning with the smallest startup/runtime shim required to link and execute the first generated program.

The full runtime contract should be recovered from generated code and surviving library/compiler use as native coverage expands.

---

## Finding 6: generated code assumes a BCPL global vector, not ordinary external linkage for every routine

The later generator emits a global initialization table at the end of a section. Globals are addressed through R12 (`R.G`).

The compiler's `LOADCODE()` routine also shows the expected model: initialize the global vector, then populate global entries from generated `(global-number,address)` pairs.

This matches the portable BCPL model already established under ICINT.

### Decision

Keep the **BCPL GLOBAL vector as the primary cross-module/runtime rendezvous mechanism**.

Use the MVS linkage editor mainly for section/module placement and true external runtime dependencies, not to replace BCPL GLOBAL semantics.

---

## Finding 7: generated sections were designed around a bounded code region

The generator reports:

```text
Code exceeds 4K words - section must be split
```

and `CGEND` checks whether generated text exceeds `4*4095` bytes.

This is consistent with the backend's base-register/addressing strategy and with System/370 displacement limits.

### Decision

Preserve the historical section-size constraint during initial reconstruction.

Do not redesign the backend for arbitrary-size sections before the historical path works.

Large compiler components can continue to use multiple sections/modules as the original system intended.

---

## Finding 8: we already possess a reference execution path

The MR10 front end and INTCODE generator run successfully through ICINT V17. This gives the project an executable semantic reference for ordinary BCPL source.

### Decision

Native development will use **differential validation**:

```text
same BCPL source
     |
     +--> CGI --> INTCODE --> ICINT
     |
     +--> CG370 --> IFOX assembler --> IFOX --> IEWL --> native execution

compare observable behavior
```

The interpreted result is not assumed to prove every historical native ABI detail, but it is the best available reference for language semantics and library-visible behavior.

---

# Implementation order

The recommended implementation sequence is:

1. **OCODE capture and compatibility probe**
   - save OCODE for the native acceptance corpus;
   - inventory every operator observed;
   - map each operator to surviving later-CG handling or mark it for adaptation.

2. **Extract a bootstrap S/370 generator**
   - reuse later target algorithms;
   - initially support only the MR10 OCODE subset required by the acceptance ladder;
   - emit readable IFOX assembler;
   - keep unsupported operators explicit and fatal.

3. **Provide minimal native runtime/startup**
   - establish R12 global vector;
   - establish BCPL workspace/frame state;
   - provide the minimum termination/result-reporting support needed by acceptance tests;
   - reconstruct only the BCPLMAIN behavior demonstrated as necessary.

4. **Assemble and link with the normal MVS toolchain**
   - IFOX00 assembles generated source;
   - IEWL produces the load module;
   - retain assembler listing and link map as evidence.

5. **Run the acceptance ladder**
   - constants/arithmetic;
   - branches/loops;
   - procedure call/value return;
   - globals;
   - separate modules;
   - then bytes/strings and selected runtime/library calls.

6. **Expand toward compiler self-hosting**
   - implement remaining MR10 OCODE operations as encountered;
   - compile portable library components;
   - compile the compiler phases;
   - only then broaden toward later compiler extensions if useful.

7. **Revisit historical object-deck emission**
   - once semantics and ABI are stable;
   - use surviving relocation/deck code as the reference;
   - validate generated decks against IFOX-produced object behavior.

---

# Work explicitly deferred

These are not prerequisites for starting native compiler implementation:

- complete reconstruction of historical BCPLMAIN;
- native coroutines;
- production-quality `GETVEC/FREEVEC` integration with MVS storage;
- LOADSEG/UNLOADSEG;
- floating-point support;
- full later-compiler OCODE extensions;
- historical direct object-deck output;
- removal of the historical 4K-word section limit;
- polished installation/distribution media.

They should be introduced when a concrete native workload requires them.

---

# Readiness verdict

The project is ready to begin native code-generator implementation.

The remaining uncertainty is no longer primarily architectural. The critical unknowns are now best resolved by constructing and running the first native generated programs.

The key constraints are:

- preserve the recovered historical BCPL/System-370 ABI where evidence is strong;
- use the working MR10 compiler as the OCODE semantic reference;
- adapt the surviving later S/370 generator rather than inventing instruction selection from scratch;
- emit IFOX assembler first so every generated instruction is inspectable;
- add native acceptance tests before expanding toward self-hosting.
