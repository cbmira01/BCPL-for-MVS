# 34 - VALOF / RESULTIS

This regression introduces the minimal BCPL `VALOF ... RESULTIS ...` expression
form.

Expected output:

```text
42
```

## Sequence

START evaluates:

```bcpl
LET X = VALOF
$(2
    RESULTIS 42
$)2
```

The RESULTIS value must become the value of the enclosing VALOF expression.
START then reports X through DEBUGINT and terminates normally.

## Contract under test

This test isolates one language/code-generation contract:

- VALOF establishes a local expression-result continuation;
- RESULTIS evaluates its operand;
- RESULTIS transfers control to the matching enclosing VALOF;
- the resulting value remains available as the value of that expression.

No function call, GETVEC/FREEVEC activity, nested VALOF, conditional RESULTIS,
loader behavior, or stream I/O is involved.

## Acceptance criteria

A successful run must:

- compile through the resident Cambridge compiler and historical CG370;
- assemble, link-edit, and execute normally under MVS;
- emit exactly `42`; and
- show generated S/370 in which RESULTIS transfers control to the correct
  VALOF continuation while preserving the result value.

The first successful run was inspected. CG370 evaluated `RESULTIS 42` into R7,
then emitted an unconditional R4-relative branch to the VALOF continuation; the
continuation stored R7 as the value of the VALOF expression.

## Scope

This is the smallest possible native regression for VALOF/RESULTIS. Conditional
and nested RESULTIS cases belong in later tests.

## Status

PASS — emitted `42` on 2026-10-07.
