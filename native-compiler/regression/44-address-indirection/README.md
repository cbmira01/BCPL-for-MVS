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

## Observed generated convention

The first native run passed with output `42`.

CG370 formed the BCPL pointer to local X by first taking its System/370 byte
address and then converting that byte address to a BCPL word address:

```asm
 LA 8,12(5)
 SRL 8,2(0)
 ST 8,16(5)
```

Thus local P contains `byte-address(X) / 4`, confirming the established BCPL
word-pointer representation.

For monadic indirection, CG370 loaded P and converted the BCPL word address back
to a byte address implicitly by using the same register as both base and index:

```asm
 AR 8,8
 L  9,0(8,8)
 ...
 ST 9,0(8,8)
```

After `AR 8,8`, R8 contains twice the word pointer. Address formation
`0(8,8)` adds R8 to itself again, producing four times the word pointer: the
original System/370 byte address.

The addition of 25 was emitted through CG370's halfword constant pool:

```asm
 AH 9,0+L997-L1(4)
...
L997 EQU * HALF WORD CONSTANTS
 DC H'25'
```

The final direct load of X:

```asm
 L 7,12(5)
```

observed the value written through P, proving that address-of and monadic
indirection designate the same local scalar storage.

## Status

PASS — emitted `42` on 2026-10-07.
