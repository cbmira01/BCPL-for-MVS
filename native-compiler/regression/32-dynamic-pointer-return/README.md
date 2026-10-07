# 32 - Dynamic pointer return

This regression composes dynamic allocation with the native BCPL function
result convention.

Expected output:

```text
42
```

## Sequence

START calls `MAKE()`.

MAKE:

1. obtains `V = GETVEC(2)`;
2. returns zero immediately if allocation fails;
3. stores 42 in `V!1`;
4. returns the BCPL word pointer V through the ordinary function-result path.

START stores the returned pointer in local P. If P is zero, the test emits 99.
Otherwise START dereferences `P!1`, reports the value through DEBUGINT, then
releases the same allocation with `FREEVEC(P)`.

## Contract under test

Test 20 established pointer return using a local vector. Tests 27-31 established
MVS-backed dynamic vectors and their behavior across ordinary procedure calls.

Test 32 combines those contracts and adds a lifetime property: a vector created
inside a callee must remain valid after that callee returns, because its storage
comes from GETVEC rather than the callee workspace.

The returned pointer must therefore:

- survive the function return unchanged;
- remain dereferenceable in the caller;
- still identify the original dynamic allocation; and
- remain acceptable to FREEVEC.

No BCPLMAIN change should be required.

## Acceptance criteria

A successful run must:

- compile through the resident Cambridge compiler and historical CG370;
- assemble, link-edit, and execute normally under MVS;
- emit exactly `42`;
- show MAKE returning the GETVEC pointer through the normal result convention;
- show START storing/reloading that returned pointer;
- show START dereferencing `P!1` after MAKE's frame is gone; and
- show FREEVEC receiving the same returned dynamic pointer.

Generated-code inspection should confirm the pointer result path.

## Scope

This is another composition/stability test. It does not introduce a new
allocator policy, loader feature, calling convention, or library service.

The current storage policy remains one MVS GETMAIN allocation per GETVEC and
one matching FREEMAIN per FREEVEC.

## Status

PENDING — ready for first native run.
