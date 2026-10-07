# 32 - Dynamic pointer return

This regression composes dynamic allocation with the already-proven native BCPL
function-result convention.

Expected output:

```text
42
```

## Sequence

START calls `MAKE()`.

MAKE consists only of:

```bcpl
LET MAKE() = GETVEC(2)
```

The GETVEC result therefore becomes the ordinary BCPL function result directly.
START stores that returned pointer in local P. If P is zero, the test emits 99.
Otherwise START stores 42 in `P!1`, reloads and reports that value through
DEBUGINT, then releases the same allocation with `FREEVEC(P)`.

## Contract under test

Test 20 established pointer return. Tests 27-31 established MVS-backed dynamic
vectors and their behavior across ordinary calls.

Test 32 now isolates exactly one composition question: can a GETVEC result
created in a callee be returned through the normal function-result path and
remain valid in the caller after the callee workspace is gone?

The returned pointer must therefore:

- survive function return unchanged;
- remain writable and readable in the caller;
- still identify the original dynamic allocation; and
- remain acceptable to FREEVEC.

No BCPLMAIN change should be required.

## Why VALOF/RESULTIS was removed

The first version of Test 32 used `VALOF ... RESULTIS ...` inside MAKE and
also initialized the dynamic vector before returning it. That introduced an
additional, previously unisolated language/code-generation construct into a
test whose intended subject was dynamic-pointer return.

Its first native run compiled, assembled, and linked successfully but ABENDed
S0C4 in generated MAKE before the caller-side lifetime contract could be
established.

The narrowed test deliberately removes VALOF/RESULTIS and callee-side vector
access. Those semantics belong in a separate regression after this pointer
return contract is settled.

## Acceptance criteria

A successful run must:

- compile through the resident Cambridge compiler and historical CG370;
- assemble, link-edit, and execute normally under MVS;
- emit exactly `42`;
- show MAKE returning the GETVEC result through the ordinary R7 result path;
- show START storing/reloading that returned pointer;
- show START writing and reading `P!1` after MAKE has returned; and
- show FREEVEC receiving the same returned dynamic pointer.

## Scope

This is a composition/stability test. It introduces no new allocator policy,
loader feature, calling convention, or runtime service.

The current storage policy remains one MVS GETMAIN allocation per GETVEC and
one matching FREEMAIN per FREEVEC.

## Status

PENDING — narrowed after the first S0C4 run and ready for retest.
