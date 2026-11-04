# 24 - Callable global through G

This regression proves that a user-defined BCPL function exported through
the global vector can be called through G rather than by a local
section-relative address.

The program is deliberately minimal:

```bcpl
GLOBAL $( START:1; DEBUGINT:150; ADD:151 $)

LET ADD(A,B) = A+B

LET START () BE
$(1
    LET X = ADD(17,25)

    DEBUGINT(X)
    FINISH
$)1
```

Expected output:

```text
42
```

## Purpose

Earlier tests proved local generated calls, function results, and user global
data. Test 24 combines those ideas by making ADD itself a user global.

The defining path is:

```text
module trailer exports ADD as G!151
BCPLMAIN installs G!151
START loads ADD through R12/G
START calls the loaded address
ADD receives 17 and 25
ADD returns 42 in R7
START passes 42 to DEBUGINT
```

Since each global slot occupies four bytes, G!151 is expected at byte
displacement 604 from R12.

## Acceptance criteria

A successful run must:

- compile through the Cambridge compiler and historical CG370;
- assemble and link with no errors;
- terminate normally under MVS;
- emit exactly `42`;
- show the generated module trailer exporting ADD as global 151;
- show START loading the callable ADD address from `604(R12)`;
- show the call using that loaded address rather than a local
  section-relative callee address;
- show ADD returning 42 through the ordinary R7 function-result convention.

Generated-code inspection is part of the proof.

## BCPLMAIN relevance

This test directly exercises the global-vector callable linkage used by
runtime and library functions. It validates not only CG370's call sequence
but also BCPLMAIN's trailer decoding and installation of a user-defined
callable global beyond FIRSTFREEGLOBAL.

## Scope

This test does not introduce BLIB or a separately linked library module.
ADD is defined in the same generated section but is exported and reached
through G.

## Status

PASS.

Job 1014 on 2026-10-06 assembled, link-edited, and executed successfully:

```text
ASM   RC=0000
LKED  RC=0000
GO    RC=0000
```

The native program emitted:

```text
42
```

Generated-code inspection confirms callable linkage through G.

START loads ADD from G!151 at byte displacement 604 from R12:

```asm
LA 8,25(0)
LA 7,17(0)
LA 15,12(5)
L  4,604(12)
BALR 6,4
ST 7,12(5)
```

This is a true global-vector call. The caller does not use a local
section-relative address for ADD.

ADD itself receives its two arguments in R7/R8 and returns the sum in R7:

```asm
STM 4,8,0(15)
LR 5,15
AR 8,7
LR 7,8
BCR 15,11
```

The generated trailer also exports ADD as global 151:

```asm
DC F'604'
DC F'0'
DC F'604'
DC A(0+L1)
DC F'4'
DC A(0+L3)
```

The `604` entry identifies G!151, while the associated address points at
ADD's generated entry L1.


## Contract established

Test 24 establishes the callable-global path through the BCPL global vector:

- a generated user function may be exported in the module trailer;
- BCPLMAIN installs the exported function address into G;
- generated callers load the function address through R12/G;
- the loaded address is called with BALR;
- ordinary BCPL argument registers and the R7 function-result convention
  remain unchanged across the G-mediated call.

This directly validates the mechanism that future runtime and library
routines will use when reached as BCPL globals.
