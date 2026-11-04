# 42 - MANIFEST constant expression

This regression isolates compile-time MANIFEST constant evaluation.

Expected output:

```text
42
```

## Source shape

```bcpl
MANIFEST $( LEFT=17; RIGHT=25; ANSWER=LEFT+RIGHT $)
...
DEBUGINT(ANSWER)
```

Earlier regressions already establish DEBUGINT, integer values, ordinary calls,
and FINISH. Test 42 adds only MANIFEST binding and compile-time expression
evaluation.

## Historical motivation

The Cambridge compiler master and historical CG370 contain MANIFEST
declarations, and TRN has explicit translation paths for MANIFEST definitions.
The historical language definition treats MANIFEST names as compile-time
constants.

The Cambridge master includes examples such as:

```bcpl
MANIFEST $( S.NAME=2 $)
```

and:

```bcpl
MANIFEST $( GLOBWORD=#XC7D3F000
            H1=0; H2=1 $)
```

This regression goes one step beyond literal binding by requiring the compiler
to evaluate one MANIFEST constant from two previously declared MANIFEST names.

## Contract under test

The compiler must evaluate:

```text
LEFT   = 17
RIGHT  = 25
ANSWER = LEFT + RIGHT = 42
```

at compile time.

The generated System/370 should therefore contain no runtime storage object for
LEFT, RIGHT, or ANSWER and no runtime addition needed to obtain ANSWER. The
DEBUGINT argument should be materialized directly as constant 42, subject to
CG370's normal constant-generation strategy.

## Acceptance criteria

A successful run must:

- compile through the resident Cambridge compiler and historical CG370;
- assemble, link-edit, and execute normally under MVS;
- emit exactly `42`;
- show no module-resident variable storage corresponding to the MANIFEST names;
- show ANSWER folded to a generated constant value rather than computed by a
  runtime add.

## Observed generated convention

The first native run passed with output `42`.

CG370 emitted the manifest-derived value directly:

```asm
 LA 7,42(0)
```

There is no generated module storage for LEFT, RIGHT, or ANSWER, and there is no
runtime addition corresponding to `LEFT+RIGHT`.

This is direct evidence that the compiler evaluated the MANIFEST expression at
compile time and substituted the resulting value into generated code.

The result is stronger than proving literal MANIFEST binding alone: ANSWER
depends on two previously declared MANIFEST names and an arithmetic expression.

## Status

PASS — emitted `42` on 2026-10-07.
