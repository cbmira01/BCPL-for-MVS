# 26 - Separately assembled native routine through G

This regression proves that generated BCPL can call a separately assembled
System/370 routine through the BCPL global vector.

The BCPL application declares but does not define `NATIVEADD`:

```bcpl
GLOBAL $( START:1; DEBUGINT:150; NATIVEADD:151 $)

LET START () BE
$(1
    LET X = NATIVEADD(17,25)

    DEBUGINT(X)
    FINISH
$)1
```

The assembler routine is built independently:

```asm
NATIVEAD CSECT
         STM   4,8,0(15)
         LR    5,15
         AR    8,7
         LR    7,8
         BCR   15,11
         END
```

Expected output:

```text
42
```

## Purpose

Test 25 crossed a BCPL compilation-unit boundary. Test 26 crosses the
language boundary between generated BCPL and application-written assembler.

The BCPL-generated application must still call only through G!151. Regression
scaffolding augments the generated module trailer with an external address for
`NATIVEAD`, and the assembler source is assembled in a separate IFOX step.
IEWL then resolves the external symbol when the two object decks are linked.

The intended path is:

```text
source.bcpl
   |
   v
Cambridge / CG370
   |
   v
BCPL object module ----+
                       |
native.asm -> IFOX ----+--> IEWL --> GO
                            |
                            v
                    G!151 -> NATIVEAD
                            |
                            v
                    BCPL call ABI
```

## Acceptance criteria

A successful run must:

- compile the application through Cambridge and CG370;
- assemble the BCPL/runtime source and `native.asm` in separate IFOX steps;
- have IEWL resolve `NATIVEAD` between those object modules;
- terminate normally under MVS;
- emit exactly `42`;
- show START loading G!151 at byte displacement 604 from R12;
- show the call occurring through the loaded global address;
- show G!151 initialized from external symbol `NATIVEAD`;
- show the native routine receiving arguments in R7/R8;
- show the native routine returning the result in R7 through the ordinary
  BCPL return trampoline.

## Scope

The trailer augmentation is regression scaffolding. This test does not claim
that the historical loader or a final application-facing mixed-language
interface has been reconstructed. It proves that the native calling convention
and ordinary MVS external linkage are sufficient to support such an interface.

## Status

PENDING.
