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

DEFINED. Not yet run.
