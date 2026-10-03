# OCODE contract for the native compiler

## Purpose

This document defines the OCODE surface that the first native System/370 compiler should support.

The working bootstrap compiler comes from `richards-bcpltape/mr10/bcplkit/`. The surviving IBM/370 backend comes from `richards-bcpltape/bcplib/bcpl/`. Their OCODE vocabularies overlap substantially but are not identical.

The first native compiler should therefore target the **OCODE actually emitted by the working MR10 compiler**, while borrowing target-machine implementation from the later System/370 CG.

---

## MR10 operator set

The MR10 code generator defines these OCODE operators:

```text
TRUE FALSE
RV FNAP
MULT DIV REM PLUS MINUS QUERY NEG
EQ NE LS GR LE GE
NOT LSHIFT RSHIFT LOGAND LOGOR EQV NEQV COND
LP LG LN LSTR LL LLP LLG LLL
RTAP GOTO RETURN FINISH SWITCHON GLOBAL
SP SG SL STIND
JUMP JT JF
LAB STACK STORE RSTACK ENTRY SAVE FNRN RTRN RES RESLAB
DATALAB ITEML ITEMN ENDPROC END CHAR DEBUG
```

Not every manifest name necessarily appears in every emitted program. The implementation should be driven by captured OCODE from the regression suite.

---

## Later System/370 operator set

The later native generator recognizes the same broad core, plus later extensions including:

```text
NEEDS SECTION
FIX ABS
SLCTAP SLCTST
STARTBLOCK ENDBLOCK
MOD MODSLCT
GETBYTE PUTBYTE
floating-point arithmetic/comparisons
FLOAT
```

The later generator does not present the MR10 vocabulary in exactly the same form. In particular, MR10-era names such as `QUERY`, `COND`, `RETURN`, `RESLAB`, and `CHAR` need to be checked against the actual OCODE emitted by the working front end before assuming they require new backend code.

---

## Compatibility classes

### Class A: direct semantic matches

These have clear counterparts in the later System/370 generator and should be implemented by adapting the surviving code:

```text
TRUE FALSE
RV FNAP RTAP
MULT DIV REM PLUS MINUS NEG
EQ NE LS GR LE GE
NOT LSHIFT RSHIFT LOGAND LOGOR EQV NEQV
LP LG LN LSTR LL
LLP LLG LLL
SP SG SL STIND
GOTO JUMP JT JF LAB
STACK STORE RSTACK
ENTRY SAVE FNRN RTRN RES
FINISH SWITCHON GLOBAL
DATALAB ITEML ITEMN ENDPROC END
```

### Class B: MR10 names requiring evidence before implementation

```text
QUERY
COND
RETURN
RESLAB
CHAR
DEBUG
```

For these, the correct first question is not “how should CG370 implement this?” but “does current TRNI emit it for any accepted source program?”

If an operator is never emitted by the current compiler path, it is not a readiness blocker.

### Class C: later extensions, deferred initially

```text
NEEDS SECTION
FIX ABS
SLCTAP SLCTST
STARTBLOCK ENDBLOCK
MOD MODSLCT
GETBYTE PUTBYTE
floating-point family
FLOAT
```

Some of these may become desirable very early, especially `GETBYTE`/`PUTBYTE`, but they should not be required merely because the later compiler supports them.

---

## Operand-reading conventions

The MR10 generator parses textual OCODE. Examples of operand forms include:

```text
LP n
LG n
LN n
LL Ln
LLP n
LLG n
LLL Ln
SP n
SG n
SL Ln
LAB Ln
STACK n
ENTRY <name data> Ln
SAVE n
FNAP n
RTAP n
RES Ln
SWITCHON n ...
GLOBAL n ...
```

The later compiler stores OCODE in a compact byte-coded representation and reads it through `READOP`, `READN`, `READL`, and `READGN`.

### Decision

The first bootstrap native generator should not depend on the later compact OCODE encoding unless that proves advantageous.

A clean first adaptation is allowed to consume the textual OCODE already producible/savable by the current pipeline, provided semantics are preserved.

This separates two problems:

```text
OCODE semantics
    versus
historical OCODE storage encoding
```

The storage encoding can be reconciled later if necessary for self-hosting the later compiler source directly.

---

## Stack-machine model

Both generators treat OCODE as operations over a conceptual BCPL evaluation stack/workspace.

Important recurring concepts are:

- local/workspace slot (`LP`, `SP`, `LLP`);
- global slot (`LG`, `SG`, `LLG`);
- literal number (`LN`);
- label/code address (`LL`, `LLL`);
- value-at-address (`RV`);
- indirect store (`STIND`);
- procedure call (`FNAP`, `RTAP`);
- procedure frame management (`ENTRY`, `SAVE`, `STACK`, `RSTACK`, return operations).

The later S/370 generator keeps a virtual description of the top of the BCPL stack in registers and spills it to workspace as required. That optimization can be preserved, but the semantic contract is independent of the optimization.

---

## Global-vector semantics

`LG n` and `SG n` access BCPL global slot `n` through the global-vector base register in the native ABI.

`GLOBAL` terminates a generated section with initialization information associating global numbers with generated addresses.

This mechanism is fundamental and must be preserved even if MVS linkage-editing is used for the surrounding load module.

---

## Calls

`FNAP k` and `RTAP k` invoke a function/routine using a workspace offset/frame boundary `k`.

The later System/370 generator maps these to its recovered native convention:

- create the new workspace pointer from current `P + 4*k`;
- marshal initial arguments into R7-R10 where applicable;
- spill remaining arguments to the workspace;
- load function address into R4;
- call with `BALR R6,R4`;
- return a function result in R7.

The exact MR10 `k` interpretation must be verified with saved OCODE examples, but the structural correspondence is strong.

---

## Procedure entry and return

The later generator handles:

```text
ENTRY
SAVE
FNRN
RTRN
```

as the core procedure protocol.

The first native generator should preserve this protocol rather than translating BCPL procedures into conventional OS linkage frames.

MVS-standard linkage belongs only at the outer runtime boundary.

---

## Data and strings

The common operators:

```text
LSTR
DATALAB
ITEML
ITEMN
GLOBAL
```

are enough to represent literal strings, static data, label references, numeric data, and global initialization.

The later generator already maintains separate lists for strings, fullword constants, halfword constants, data labels, and relocations. Those mechanisms should be reused where possible.

---

## Byte operations

The later generator has native `GETBYTE` and `PUTBYTE` OCODE operations. The MR10 kit historically exposes byte operations as runtime/system functions in some contexts.

### Decision

Do not assume byte access must initially be a dedicated OCODE operator.

Use whatever form the current MR10 compiler actually emits. If ordinary source using `GETBYTE`/`PUTBYTE` compiles into global calls, support those calls first. If the current pipeline emits byte operators, adapt `CGBYTEAP` from the later generator.

---

## Floating point

The later System/370 generator contains substantial floating-point support.

### Decision

Floating point is explicitly outside the first native acceptance milestone.

The code should remain recoverable and documented, but not required before integer/system-programming workloads run natively.

---

## Required readiness experiment

Before implementation expands beyond the first few operators, save OCODE for the acceptance corpus using the existing compiler pipeline.

For each program, record:

```text
source file
exact compile-and-run command used to save OCODE
saved OCODE artifact
set of operators observed
```

Then maintain a table of:

```text
operator
observed in current compiler output?
later CG implementation location
native implementation status
regression that exercises it
```

This table should become the authoritative scope tracker for the bootstrap CG.

---

## Rule for unsupported OCODE

During native-CG development, an unimplemented OCODE operation must fail explicitly with:

```text
operator number/name
input position if available
current procedure/section if available
```

Do not silently approximate an unsupported operation.

The native generator is easier to trust if missing coverage is loud and local.
