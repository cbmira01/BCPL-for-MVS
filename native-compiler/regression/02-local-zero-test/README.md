# 02 - Local zero test

This test is the smallest intended increment over Test 01.

It introduces one local integer and one comparison with zero, while retaining
the same minimal FINISH-only termination path.

The program is intended to prove these additional contracts:

```text
START
  -> allocate/use local workspace
  -> store and reload a local integer
  -> compare the value with zero
  -> branch correctly
  -> FINISH
  -> normal MVS return
```

This test is especially relevant to the runtime invariant that R0 must contain
zero while generated BCPL code is executing.

The test deliberately avoids procedure arguments, recursion, strings, global
library calls, dynamic storage, and stream I/O.

A failure here, after Tests 00 and 01 pass, should focus attention on local
workspace layout, generated load/store addressing, condition-code generation,
branch masks, or the R0-zero invariant.
