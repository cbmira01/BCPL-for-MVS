# 49 - checked procedure entry

This regression executes the non-overflowing CG370 stack-check entry path.

It reuses behavior already established by Test 06: a mutable local is changed
from 17 to 42, WRCH consumes the ordinary first-argument register, and
DEBUGINT then receives X from the procedure workspace. The only new condition
is Cambridge code-generator option `C`.

The private bootstrap parameter record begins:

```text
/CN...
```

where second-phase `C` enables `STKCKING` and `N` continues to suppress
the unsupported binary object-deck path.

## Runtime change under test

Test 48 proved that checked procedure entry emits:

```asm
BAL   14,60(11)
DC    A(Lnnn) STACK FRAME SIZE
```

instead of the ordinary unchecked `LR 5,15`.

BCPLMAIN now implements the minimum non-overflowing entry contract:

```asm
STKIMPL  LR    5,15
         LA    14,4(14)
         BR    14
```

This deliberately does not inspect the inline frame size or perform a stack
limit comparison. Those semantics belong to later tests.

## Acceptance criteria

A successful run must:

- compile with stack checking enabled;
- retain the checked-entry BAL plus inline frame-size word in generated code;
- assemble, link-edit, and execute normally;
- emit exactly:

  ```text
  X42
  ```

The output establishes that checked entry resumes after the inline fullword and
that R5 is correctly established as the current workspace, because X must be
reloaded after WRCH.

## Status

PASS — native run on 2026-10-07; emitted `X42`.

Observed checked entry:

```asm
STM 4,6,0(15)
BAL 14,60(11)
DC A(L994) STACK FRAME SIZE
...
L994 EQU 44 STACK FRAME SIZE
```

The run assembled, link-edited, and executed normally. Because WRCH consumes the
ordinary first-argument register and DEBUGINT subsequently receives X from
`12(R5)`, the observed `X42` proves that checked entry established R5 from
R15 and resumed after the inline fullword correctly.
