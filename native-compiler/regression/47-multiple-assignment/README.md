# 47 - multiple assignment

This regression isolates BCPL multiple assignment without depending on an
evaluation/assignment ordering that the historical language definition leaves
undefined.

Expected output:

```text
42
25
17
```

## Source shape

```bcpl
LET A = 0
LET B = 0

A,B := 25,17

DEBUGINT(A + B)
DEBUGINT(A)
DEBUGINT(B)
```

Earlier regressions already establish local scalar variables, ordinary
assignment, addition, DEBUGINT, and FINISH. Test 47 adds only multiple
assignment syntax and generation.

## Historical semantics

The original version of this regression used:

```bcpl
A,B := B,A
```

as a presumed simultaneous swap. That was too strong.

The 1979 proposed BCPL definition says that in a multiple assignment the
left- and right-hand expressions are evaluated and assigned in an undefined
order, and specifically allows some assignment to occur before all expressions
have been evaluated. Therefore `A,B := B,A` is not a portable swap idiom.

The Cambridge translator is consistent with that latitude. Its `ASSIGN`
routine recursively translates the left comma component and then the right
comma component:

```bcpl
ASSIGN(H2!X, H2!Y, N)
ASSIGN(H3!X, H3!Y, N)
```

The first native probe consequently generated two stores of the already-updated
value 25:

```asm
 ST 8,12(5)
 ST 8,16(5)
```

so the original swap expectation failed. That observation is retained as
evidence of this Cambridge implementation's ordering; it is not classified as
a compiler defect.

## Why the revised probe is valid

The revised assignment:

```bcpl
A,B := 25,17
```

has the same result under any permitted evaluation/assignment ordering because
neither right-hand expression depends on either destination.

The three reported values establish both assignments independently:

```text
A+B = 42
A   = 25
B   = 17
```

## Acceptance criteria

A successful run must:

- compile through the resident Cambridge compiler and historical CG370;
- assemble, link-edit, and execute normally under MVS;
- emit exactly:

  ```text
  42
  25
  17
  ```

- show both destination stores in generated code;
- require no new BCPLMAIN runtime service.

## Regression-harness incident

The first run of the original swap probe was incorrectly reported PASS because
the old output matcher searched the entire JES report and treated a multiline
expected file as alternative grep patterns. The line `25` matched unrelated
JCL text containing `REGION=256K`.

The harness was subsequently hardened so multiline expectations must occur as
one contiguous sequence and output matching is restricted to the report suffix
after the linkage editor's final `AUTHORIZATION CODE IS` marker.

A full 00-47 rerun under the corrected matcher passed Tests 00-46 and correctly
reported the original Test 47 swap expectation as a mismatch.

## Status

PENDING — revised order-independent multiple-assignment probe is ready to run.
