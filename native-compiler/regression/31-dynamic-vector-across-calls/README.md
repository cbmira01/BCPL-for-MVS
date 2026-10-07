# 31 - Dynamic vector across a procedure call

This regression composes the native GETVEC/FREEVEC contract with the ordinary
BCPL pointer and procedure-linkage contract already established by earlier
tests.

Expected output:

```text
42
```

## Sequence

START obtains a three-word BCPL payload with `GETVEC(2)`. If allocation
unexpectedly fails, the test emits 99 and terminates normally.

On the successful path START:

1. stores 17 in `V!1`;
2. passes the dynamically allocated BCPL word pointer to `SETVALUE`;
3. SETVALUE stores 42 through that pointer;
4. START independently reloads `V!1` after the call;
5. reports the reloaded value through DEBUGINT;
6. releases the same vector with `FREEVEC(V)`.

## Contract under test

Tests 11 and 12 established read/write aliasing through a procedure call using
a local `VEC`. Tests 27-30 established the MVS-backed GETVEC/FREEVEC
mechanism.

Test 31 combines those contracts. A dynamically allocated vector must behave
like an ordinary BCPL pointer across generated procedure linkage, remain valid
until explicitly released, and remain acceptable to FREEVEC after the call.

No BCPLMAIN change should be required.

## Acceptance criteria

A successful run must:

- compile through the resident Cambridge compiler and historical CG370;
- assemble, link-edit, and execute normally under MVS;
- emit exactly `42`;
- show the GETVEC result passed to SETVALUE through ordinary BCPL linkage;
- show SETVALUE storing 42 through the received pointer;
- show START reloading and dereferencing V after SETVALUE returns; and
- release that same dynamic vector through FREEVEC.

Generated-code inspection should confirm the pointer path, but the primary
regression result is the end-to-end runtime behavior.

## Scope

This is deliberately a composition test. It does not add a new allocator
feature, heap architecture, calling convention, or library service.

The current storage policy remains one MVS GETMAIN allocation per GETVEC and
one matching FREEMAIN per FREEVEC.

## Status

PASS — validated in the full 00..32 native regression panel on 2026-10-07.
