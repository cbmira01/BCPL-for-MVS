# 41 - TABLE constant vector

This regression isolates native representation and addressing for a BCPL TABLE
expression.

Expected output:

```text
42
```

## Source shape

```bcpl
LET T = TABLE 17,25
DEBUGINT(T!0 + T!1)
```

Earlier regressions already establish local variables, vector indexing, integer
addition, DEBUGINT, and normal FINISH. Test 41 adds only TABLE construction and
addressing.

## Historical motivation

The Cambridge compiler corpus uses TABLE directly in the compiler master, TRN,
and CG370. The 1979 BCPL definition describes TABLE as an initialized static
vector expression. This is therefore both corpus-driven and documentation-driven
coverage.

## Contract under test

The generated module should contain persistent initialized words representing
the TABLE values 17 and 25, and the expression result should evaluate to 42.

The first successful assembler dump should be inspected for:

- the emitted static TABLE data;
- the value returned for the TABLE expression;
- how the generated code turns that value into BCPL vector addressing; and
- whether TABLE data shares the same general module-relative storage convention
  observed for STATIC in Test 40.

## Acceptance criteria

A successful run must:

- compile through the resident Cambridge compiler and historical CG370;
- assemble, link-edit, and execute normally under MVS;
- emit exactly `42`; and
- show both initialized TABLE elements in generated static/module data.

## Observed generated convention

The first native run passed with output `42`.

CG370 emitted the TABLE as contiguous initialized module data:

```asm
L3 EQU *
 DC F'17'
 DC F'25'
```

START materializes the TABLE value as a BCPL word pointer to that data:

```asm
 LA 7,0+L3-L1(4)
 SRL 7,2(0)
 ST 7,12(5)
```

This is direct evidence that a TABLE expression denotes statically allocated
module data and yields its BCPL word address.

The subsequent indexing follows the established BCPL word-pointer convention:

```asm
 AR 7,7
 L  8,0(7,7)
 A  8,4(7,7)
```

After doubling R7 twice through the effective-address form, the code reads the
first and second fullwords at byte displacements 0 and 4, producing 17+25=42.

TABLE therefore shares the same broad module-resident storage model seen for
STATIC in Test 40, but differs in expression semantics: the generated code
constructs and returns a BCPL pointer to the first table element.

## Status

PASS — emitted `42` on 2026-10-07.
