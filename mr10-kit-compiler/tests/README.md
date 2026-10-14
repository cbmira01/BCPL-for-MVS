# Tests

`tests/` contains durable regressions and reconstruction probes. The directories are numbered roughly in the order that capabilities were established; they are not all the same kind of test.

## Durable regression panel

`00-regression-panel/` is the fast exact-output contract suite. Run it with:

```sh
tools/run-regression-panel
```

Use this panel for behavior that should remain stable. See `00-regression-panel/README.md` for its manifest and output contract.

## Reconstruction tests and probes

- `01-echo-test` — basic INTCODE input/output through `SYSIN`;
- `02-honors-thesis-and-mapstore` — early interpreter workloads and map/store behavior;
- `03-compile-richards-factorial` — preserved compiler pipeline and saved OCODE/INTCODE evidence;
- `04-module-test` — separate BCPL compilation units and `GLOBAL`-vector linkage;
- `05-named-dd` — named DD discovery and compiler `GET` input;
- `06-dynamic-streams` — nested/dynamic stream handling;
- `07-many-streams` — twelve simultaneously live named input streams;
- `08-character-translation` — ASCII/EBCDIC/BCPL character translation, including historical backslash operator spellings;
- `09-multiple-assignment` — records the MR10 translator's sequential multiple-assignment semantics;
- `10-coroutines` — compiler frame probes and reconstructed coroutine behavior;
- `11-getvec-freevec` — allocator exercise for reconstructed `GETVEC`/`FREEVEC` support.

Several probe directories retain generated OCODE or INTCODE because those intermediates are evidence for calling conventions or compiler behavior, not disposable build output.

## Running individual workloads

Use `tools/run-intcode` for existing INTCODE and `tools/compile-and-run` for BCPL source. Prefer the promoted interpreter selected by `tools/current-icint` unless a test specifically documents an older milestone interpreter.

Examples:

```sh
tools/run-intcode --results \
    "$(tools/current-icint)" \
    tests/01-echo-test/echo-sysin.int \
    +intcode/blibi.int \
    +intcode/iclib.int
```

```sh
tools/compile-and-run --results \
    "$(tools/current-icint)" \
    tests/09-multiple-assignment/multiple-assignment.bcpl
```

Tests that require extra modules or DDs document their exact invocation in their local README or in the regression manifest.

## What belongs here

A narrow historical observation or reconstruction experiment belongs in a numbered probe directory. Once a behavior becomes a supported contract, reduce it to a deterministic case in `00-regression-panel/` when practical.