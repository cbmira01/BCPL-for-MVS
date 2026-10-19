# 48 - stack-check emission

This regression isolates CG370 stack-check **emission**, before changing
BCPLMAIN's stack-check implementation.

The BCPL source is deliberately the same minimal lifecycle shape as Test 00.
The only new condition is the private Cambridge bootstrap parameter record:

```text
/CN...
```

The leading slash enters the code-generator option phase. `C` enables
`STKCKING`; `N` retains the bootstrap requirement that suppresses binary
object-deck output.

## Expected generated contract

With stack checking disabled, CG370 procedure entry ordinarily establishes the
current workspace with:

```asm
LR    5,15
```

With `STKCKING` enabled, `CGSAVE` instead emits a BAL through system-vector
offset 60 followed by an inline fullword containing the generated procedure's
required stack-frame size:

```asm
BAL   14,60(11)
DC    A(Lnnn) STACK FRAME SIZE
```

CG370 later defines `Lnnn` as `BASEFRMSIZE*4`, so the inline value is a byte
count.

## Acceptance criteria

This is intentionally a compile-only regression. It must:

- compile through the resident Cambridge compiler and historical CG370;
- recover textual System/370 assembler;
- find a `BAL 14,60(11)` checked-entry call;
- find the immediately generated stack-frame-size fullword form;
- stop before IFOX/link/run, because BCPLMAIN's current `STKIMPL` is still a
  stub and is not yet expected to execute this contract.

No runtime behavior is claimed by this test.

## Status

PASS — native compile probe on 2026-10-07.

Observed generated entry:

```asm
STM 4,6,0(15)
BAL 14,60(11)
DC A(L994) STACK FRAME SIZE
BC 15,40(11)
L994 EQU 12 STACK FRAME SIZE
```

This proves the checked-entry call is emitted immediately after the generated
register save, that R14 links to the inline fullword, and that the minimal START
frame requires 12 bytes. It also confirms that the stack-check path replaces the
ordinary `LR 5,15` workspace-establishment instruction.
