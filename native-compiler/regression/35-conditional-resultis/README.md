# 35 - Conditional RESULTIS

This regression extends the minimal VALOF/RESULTIS coverage from Test 34 to
multiple control-flow paths that exit the same VALOF expression.

Expected output:

```text
42
```

## Sequence

START evaluates:

```bcpl
LET X = VALOF
$(2
    TEST 1 = 1
    THEN RESULTIS 42
    OR RESULTIS 99
$)2
```

The true branch must produce 42. The false branch exists so that two distinct
RESULTIS paths target the same enclosing VALOF continuation.

START then reports X through DEBUGINT and terminates normally.

## Contract under test

Test 34 established the degenerate one-path shape: RESULTIS evaluates its value
into the ordinary expression/result register and branches to the enclosing
VALOF continuation.

Test 35 adds one semantic distinction:

- two separate control-flow paths may each execute RESULTIS;
- both RESULTIS statements must target the same enclosing VALOF continuation;
- the selected path's value must survive that transfer and become the value of
  the VALOF expression.

No nested VALOF, function call, dynamic storage, loader behavior, or stream I/O
is involved.

## Acceptance criteria

A successful run must:

- compile through the resident Cambridge compiler and historical CG370;
- assemble, link-edit, and execute normally under MVS;
- emit exactly `42`; and
- show generated S/370 with distinct true/false RESULTIS paths converging on the
  same VALOF continuation.

The first successful run should be inspected once to characterize the exact
CG370 branch pattern.

## Status

PENDING — ready for first native run.
