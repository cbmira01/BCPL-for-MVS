# 01 - One procedure call

This test is the smallest intended increment over Test 00.

It adds one ordinary BCPL procedure call and return before executing
`FINISH`.

The program is intended to prove this additional contract:

```text
START
  -> establish caller workspace
  -> call NOP
  -> NOP establishes callee workspace
  -> procedure return through the R11 return path
  -> resume START
  -> FINISH
  -> normal MVS return
```

The test deliberately avoids strings, arithmetic, recursion, global library
calls, dynamic storage, and stream I/O.

A failure here, after Test 00 passes, should focus attention on generated
procedure entry, R5/R15 workspace handling, R6 linkage, saved-register layout,
or the procedure-return service reached through R11.

The exact generated assembler should remain inspectable as part of diagnosis,
but the regression case itself is the BCPL source program.


## Status

PASS.

First successful end-to-end native run: JES Job 950 on 2026-10-06.

Observed result:

```text
ASM   IFOX00   RC=0000
LKED  IEWL     RC=0000
GO              RC=0000
```

This provides the first native validation of the ordinary generated BCPL
procedure-call/return path used by this test, including caller/callee
workspace handling, R6 linkage, and the current R11 return trampoline:

```asm
RETIMPL  LM    4,6,0(5)
         BCR   15,6
```

This is evidence for that minimal call/return contract only; it does not yet
establish argument passing, recursion, deeper stack behavior, or all generated
procedure shapes.
