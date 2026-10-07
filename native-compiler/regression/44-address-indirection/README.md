# 44 - address-of and monadic indirection

This regression isolates BCPL address-of (`@E`) and monadic indirection
(`!E`) on a local scalar.

Expected output:

```text
42
```

## Source shape

```bcpl
LET X = 17
LET P = @X

!P := !P + 25

DEBUGINT(X)
```

Earlier regressions already establish local scalar storage, ordinary assignment,
integer addition, DEBUGINT, and FINISH. Test 44 adds only address formation and
scalar indirection through the resulting BCPL pointer.

## Historical motivation

Address-of and monadic indirection are core BCPL operations in the historical
language definition. Compiler and systems code rely heavily on explicit
word-address manipulation, so this is documentation-driven coverage even where
the exact spelling is less frequent than vector-style `A!I`.

## Contract under test

The compiler must:

- form the BCPL word address of local X;
- store that pointer in local P;
- load X through `!P`;
- add 25;
- store the result back through `!P`; and
- allow an ordinary direct read of X to observe 42.

The generated assembler should make the BCPL pointer representation explicit.
Because BCPL pointers are word addresses while System/370 addresses are byte
addresses, the dump should show the conversion used by CG370 for `@X` and
`!P`.

## Acceptance criteria

A successful run must:

- compile through the resident Cambridge compiler and historical CG370;
- assemble, link-edit, and execute normally under MVS;
- emit exactly `42`;
- show explicit address formation for local X;
- show indirect load/store through P; and
- preserve the established BCPL word-pointer convention.

## Status

PENDING — ready for first native run.
