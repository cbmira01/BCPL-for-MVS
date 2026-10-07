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

## Status

PENDING — ready for first native run.
