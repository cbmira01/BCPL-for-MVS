# 33 - Caller base after function return

This regression permanently guards the reconstructed native BCPL procedure-return
contract exposed by Test 32.

Expected output:

```text
42
```

## Sequence

START calls `VALUE()`, which simply returns 17.

Immediately after the generated function return, START tests the returned value.
The source is deliberately shaped so that the caller must continue through its
own generated control flow after the call rather than merely consume R7 in a
straight-line expression.

If the returned value is 17, START reports 42. Otherwise it reports 99.

## Contract under test

Generated procedure entry saves R4..R6 in the callee workspace and sets R5 to
that workspace. The reconstructed return trampoline must restore:

- R6 from 8(current P), the caller return linkage;
- R5 from 4(current P), the caller workspace pointer;
- R4 from 0(restored caller P), the caller's generated-code base.

The former reconstruction used:

```asm
LM 4,6,0(5)
BCR 15,6
```

which restored R4 from the callee frame. Test 32 exposed that this can leave the
caller using the callee's base for subsequent R4-relative branches.

The corrected trampoline is:

```asm
L   6,8(5)
L   5,4(5)
L   4,0(5)
BCR 15,6
```

## Acceptance criteria

A successful run must:

- compile through the resident Cambridge compiler and historical CG370;
- assemble, link-edit, and execute normally under MVS;
- emit exactly `42`;
- show VALUE returning through the ordinary R7 function-result path; and
- show START executing caller-relative control flow correctly after VALUE
  returns.

Generated S/370 should be inspected on the first successful run to confirm that
the post-call TEST actually uses an R4-relative branch. If this source shape
does not force that form, the test should be adjusted before being considered
fully established.

## Scope

This is a foundation regression for the native calling convention. It does not
exercise GETVEC, FREEVEC, VALOF/RESULTIS, loader behavior, stream I/O, or any
new runtime service.

## Status

PASS — emitted `42` on 2026-10-07.
