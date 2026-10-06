# Native compiler regression panel

This directory is the durable regression panel for the reconstructed native
System/370 BCPL compiler/runtime path.

The panel is driven by BCPL behavior.  Tests are deliberately ordered from the
smallest possible native BCPL program upward through progressively larger parts
of the compiler and BCPLMAIN contract.

The normal path under test is:

```text
BCPL source
  -> Cambridge SYN/LEX/TRN
  -> OCODE
  -> historical CG370
  -> System/370 assembler
  -> IFOX / linkage editor
  -> asm/bcplmain-wip.asm
  -> execution under MVS 3.8J
```

Assembler-only probes may diagnose a failing contract, but they are not panel
tests.

## Test layout

Each regression test has its own numbered directory:

```text
native-compiler/regression/
    README.md
    00-most-degenerate-bcpl-program/
        source.bcpl
        README.md
    01-...
    02-...
```

The numeric prefix is part of the test identity.  It records the intended
progression through the native execution contract.

Generated assembler, JCL, listings, load modules, and printer reports belong
under `workarea/`, not in the regression directories.

## Test design rule

A test should introduce as little new behavior as possible beyond all earlier
tests.  When a test fails, the difference between it and the preceding passing
tests should point toward a reasonably narrow compiler/runtime contract.

Tests should therefore be:

- BCPL source programs, not assembler ABI probes;
- small enough that generated S/370 code can be inspected directly;
- deterministic under MVS;
- retained permanently after they pass;
- ordered so that later tests build on contracts already established by
  earlier tests.

## Test 00

`00-most-degenerate-bcpl-program` is intentionally almost empty.  Its only
job is to establish the minimum native BCPL lifecycle:

```text
compiled module entry
  -> BCPLMAIN
  -> global 1 / START
  -> FINISH
  -> normal MVS return
```

It should not depend on WRITEF, strings, arithmetic, procedure calls,
recursion, dynamic storage, stream I/O, or other library services.

The remaining tests should be chosen one at a time as the BCPLMAIN contract is
reconstructed.
