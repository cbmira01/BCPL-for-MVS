# 00 - Most degenerate BCPL program

This is the first native regression test.

The program defines only the required global `START` entry and immediately
executes the BCPL `FINISH` operation.

It is intended to prove only the minimum native lifecycle:

```text
generated module prefix
  -> BCPLMAIN
  -> installation of G!1 = START
  -> entry to START
  -> R11 system-vector FINISH service
  -> normal return to MVS
```

A failure here should be treated as a failure of basic generated-module /
BCPLMAIN rendezvous, global installation, initial runtime register state,
FINISH handling, or MVS return linkage.

No library output is expected.
