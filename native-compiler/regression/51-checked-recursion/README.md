# 51 - checked recursion

This regression executes repeated recursive calls with CG370 stack checking
enabled.

It deliberately reuses the non-tail-recursive source shape established by
Test 18:

```bcpl
LET DEPTH(N) = N=0 -> 37, DEPTH(N-1)+1
```

The recursion depth is five, so the run remains comfortably inside the current
static WIP workspace. The new condition is that every generated procedure uses
the checked-entry path.

The private Cambridge parameter record begins:

```text
/CN...
```

where second-phase `C` enables stack checking and `N` preserves bootstrap
suppression of the binary object-deck path.

## Contract under test

Tests 48-50 established:

- CG370 checked-entry emission;
- R5 establishment and inline-word skipping;
- runtime decoding of the inline frame size.

Test 51 composes those contracts with recursive workspace creation and unwind.

The generated module must contain at least two checked procedure entries,
covering START and DEPTH, and recursive code must form a new W from the current
P before an ordinary `BALR 6,4` call.

At each recursive DEPTH entry, `STKIMPL` must therefore:

1. receive the newly formed R15/W;
2. establish R5/P from it;
3. decode and validate that procedure's inline frame size;
4. resume after the inline fullword;
5. allow the normal system-vector return path to unwind to the caller.

## Acceptance criteria

A successful run must:

- compile with stack checking enabled;
- contain at least two checked-entry BAL/inline-size sequences;
- contain ordinary generated workspace advancement and BALR call linkage;
- assemble and link normally;
- execute five recursive levels and unwind normally;
- emit exactly:

  ```text
  42
  ```

No stack-end comparison or overflow behavior is introduced or claimed here.

## Status

PENDING native run.
