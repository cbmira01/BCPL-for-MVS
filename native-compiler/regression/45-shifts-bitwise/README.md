# 45 - shifts and bitwise operators

This regression isolates native generation for BCPL shifts and bitwise/logical
operators.

Expected output:

```text
42
```

## Source shape

```bcpl
LET A = 3 << 4
LET B = A >> 1
LET C = B | 2
LET D = C & 7
LET E = D EQV 5
LET F = E NEQV 0

DEBUGINT((F & 1) + 41)
```

Earlier regressions already establish local scalars, assignment, integer
addition, DEBUGINT, and FINISH. Test 45 adds:

- left shift;
- right shift;
- bitwise OR;
- bitwise AND;
- EQV;
- NEQV.

## Expected evaluation

The intended value flow is:

```text
A = 3 << 4      = 48
B = A >> 1      = 24
C = B | 2       = 26
D = C & 7       = 2
E = D EQV 5
F = E NEQV 0
```

The final expression masks F with 1 and adds 41 so that the native execution
result is expected to be 42 if the operators follow the historical BCPL
truth/bitwise conventions implemented by the Cambridge compiler.

## Historical motivation

The historical BCPL language definition includes shifts, AND, OR, EQV, and
NEQV as core operators. The Cambridge code generator corpus also contains
direct handling for these operations, making this both documentation-driven and
corpus-driven coverage.

## What to inspect in generated assembler

The generated System/370 should reveal CG370's chosen instruction sequences for:

- logical left shift;
- logical/arithmetic right shift as defined by this compiler;
- AND;
- OR;
- equivalence;
- non-equivalence.

Particular attention should be paid to whether EQV/NEQV are emitted through
exclusive-OR/complement sequences, constants, or branch-based normalization.

## Acceptance criteria

A successful run must:

- compile through the resident Cambridge compiler and historical CG370;
- assemble, link-edit, and execute normally under MVS;
- emit exactly `42`;
- show native code corresponding to the shift and bitwise operations;
- require no new BCPLMAIN runtime service.

## Status

PENDING — ready for first native run.
