# 40 - STATIC scalar persistence/addressing

This regression isolates native storage and addressing for a BCPL STATIC scalar.

Expected output:

```text
42
```

## Source shape

The module declares:

```bcpl
STATIC $( COUNT = 17 $)
```

A separate procedure increments COUNT by 25. START then reads COUNT and reports
the result.

## Contract under test

Earlier regressions established:

- procedure linkage and return;
- mutable locals;
- ordinary arithmetic;
- global calls through G;
- DEBUGINT.

Test 40 adds only STATIC storage semantics.

The generated module must provide one persistent static cell initialized to 17.
BUMP must address and update that cell, and START must subsequently observe the
updated value 42.

This specifically tests that STATIC data is not allocated as an ephemeral local
workspace object and that generated references to the same static definition
resolve to one persistent module-relative storage location.

## Historical motivation

The Cambridge compiler master and historical CG370 source both use STATIC
declarations directly. This test therefore closes an observed compiler-corpus
gap rather than adding a synthetic language feature without provenance.

## Acceptance criteria

A successful run must:

- compile through the resident Cambridge compiler and historical CG370;
- assemble, link-edit, and execute normally under MVS;
- emit exactly `42`;
- show generated static initialization/storage associated with COUNT;
- show BUMP updating that persistent location; and
- show START re-reading the same location after BUMP returns.

The first successful run should be inspected to identify the exact CG370 static
layout/addressing convention.

## Observed generated convention

The first native run passed with output `42`.

CG370 emitted the STATIC cell as module-resident data:

```asm
L1 EQU *
 DC F'17'
```

BUMP addresses that same cell relative to its procedure base in R4:

```asm
 LA 7,25(0)
 A  7,0+L1-L2(4)
 ST 7,0+L1-L2(4)
```

START later reloads the same static cell relative to its own procedure base:

```asm
 L  7,0+L1-L5(4)
```

The assembler therefore resolves the same module label from different generated
procedure-base values. STATIC storage is persistent module data, not workspace
storage.

The callable address for BUMP is separately emitted as a fullword address
constant:

```asm
L3 EQU *
 DC A(0+L2)
```

This is useful evidence about the separation between static data and generated
procedure-entry constants in the module trailer/data area.

## Status

PASS — emitted `42` on 2026-10-07.
