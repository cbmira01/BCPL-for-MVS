# 36 - Nested VALOF / RESULTIS

This regression extends VALOF/RESULTIS coverage to nested result continuations.

Expected output:

```text
42
```

## Sequence

START evaluates:

```bcpl
LET X = VALOF
$(2
    LET Y = VALOF
    $(3
        RESULTIS 17
    $)3

    RESULTIS Y + 25
$)2
```

The inner RESULTIS must exit only the inner VALOF and produce Y=17. Execution
must then continue inside the outer VALOF, compute Y+25, and execute the outer
RESULTIS to produce X=42.

START reports X through DEBUGINT and terminates normally.

## Contract under test

Tests 34 and 35 established single-level VALOF/RESULTIS result transfer and
multiple RESULTIS paths converging on one continuation.

Test 36 adds one semantic distinction:

- nested VALOF expressions must establish distinct continuations;
- the inner RESULTIS must target the inner continuation only;
- control must resume inside the outer VALOF after the inner expression;
- the outer RESULTIS must then target the outer continuation;
- values must survive both transfers through the ordinary expression/result
  path.

No function call, dynamic storage, loader behavior, or stream I/O is involved.

## Acceptance criteria

A successful run must:

- compile through the resident Cambridge compiler and historical CG370;
- assemble, link-edit, and execute normally under MVS;
- emit exactly `42`; and
- show generated S/370 with two distinct continuation labels, one for the inner
  VALOF and one for the outer VALOF.

The first successful run was inspected. CG370 emitted `RESULTIS 17` as an R7
load followed by an unconditional branch to inner continuation `L4`. At `L4`
the value is stored as Y, execution continues inside the outer VALOF, adds 25,
and the outer RESULTIS branches to distinct continuation `L3`. At `L3`, R7 is
stored as the value of the outer VALOF.

## Status

PASS — emitted `42` on 2026-10-07.
