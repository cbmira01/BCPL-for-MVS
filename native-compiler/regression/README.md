# Native compiler regression panel

This directory is the durable home for BCPL source programs used to
regression-test the reconstructed native System/370 compiler/runtime path.

The panel is driven by BCPL behavior.  Each case should begin as a small BCPL
program chosen to exercise a specific language or runtime contract.  The
normal path under test is:

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

Assembler-only probes may still be used to diagnose a failing contract, but
they are not substitutes for panel cases.

## Intended layout

```text
native-compiler/regression/
    README.md
    cases/
        <case>.bcpl
    expected/
        <case>.txt
```

`cases/` contains the BCPL source inputs.

`expected/` is reserved for stable, human-readable expected results when a
case needs them.  Expected data should describe observable BCPL behavior, not
incidental JES job numbers, addresses, compiler cycle counts, or other
run-specific details.

Generated assembler, JCL, listings, load modules, and reports belong under
`workarea/`, not in this directory.

## Case design

A regression case should be:

- small enough that its generated code can be inspected when it fails;
- focused enough that a failure points at a reasonably narrow contract;
- written as BCPL source rather than as an assembler ABI probe;
- deterministic under MVS;
- retained after it passes, so later BCPLMAIN or compiler changes cannot
  silently break previously established behavior.

The panel should grow from the smallest native execution cases toward richer
runtime behavior.  The exact initial case set is intentionally not fixed here;
it should be chosen alongside the BCPLMAIN reconstruction so that each new
case proves a useful piece of the native contract.
