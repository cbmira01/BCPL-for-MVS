# 50 - stack frame size

This regression proves that checked procedure entry carries a materially sized
inline frame requirement and that BCPLMAIN now reads and structurally validates
that value before continuing.

The source uses a local `VEC 31`, stores 17 and 25 at opposite ends, and emits
their sum. Earlier vector regressions already establish local-vector addressing;
the new behavior here is the much larger checked frame.

The Cambridge bootstrap parameter record begins:

```text
/CN...
```

so second-phase `C` enables stack checking and `N` continues to suppress the
bootstrap binary object-deck path.

## Runtime change under test

`STKIMPL` now reads the inline fullword through R14:

```asm
STKIMPL  LR    5,15
         L     4,0(14)
         LTR   4,4
         BC    12,STKFORM
         TM    3(14),X'03'
         BC    7,STKFORM
         L     4,0(15)
         LA    14,4(14)
         BR    14
```

R4 is safe as a temporary because CG370 has already saved R4-R6 at 0(R15)
before entering the stack-check service. The original R4 is restored before
generated code resumes.

The structural checks require the generated frame size to be positive and
word aligned. This is deliberately not yet a stack-overflow check: the value is
not compared with WORKEND.

## Acceptance criteria

A successful run must:

- compile with stack checking enabled;
- emit the checked-entry BAL plus inline frame-size word;
- define a frame size of at least three decimal digits, materially larger than
  Test 49's 44-byte frame;
- assemble, link-edit, and execute normally;
- emit exactly:

  ```text
  42
  ```

## Status

PASS — native run on 2026-10-07; emitted `42`.

Observed generated checked entry and frame definition:

```asm
BAL 14,60(11)
DC A(L994) STACK FRAME SIZE
...
L994 EQU 172 STACK FRAME SIZE
```

The 172-byte value was accepted by the runtime's positive/alignment checks,
R4 was restored from the saved frame, execution resumed after the inline
fullword, and the local vector produced the expected result. This establishes
frame-size decoding only; no stack-end comparison or overflow detection is
claimed.
