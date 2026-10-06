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
