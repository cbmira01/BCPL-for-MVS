# Richards factorial demonstration

This directory contains a copy of the compact recursive factorial program used during the early BCPL-for-MVS compiler/bootstrap reconstruction.

The source is copied verbatim from:

```text
tests/03-compile-richards-factorial/richards-factorial-test.bcpl
```

The `tests/03-compile-richards-factorial/` copy remains the historical reconstruction probe and retains its saved OCODE/INTCODE evidence. This suite copy exists for a different purpose: it is a readable historical BCPL demonstration that can be run with the rest of the demo suite.

The program defines a local recursive factorial function:

```text
F(N) = N=0 -> 1, N*F(N-1)
```

and prints `F(1)` through `F(10)`.

Run from the repository root:

```bash
tools/compile-and-run --results \
    "$(tools/current-icint)" \
    suite/richards-factorial/richards-factorial.bcpl
```

The expected final value is:

```text
F(10), = 3628800
```

with interpreted `CODE = 0`.
