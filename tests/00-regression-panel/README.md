# Regression panel

This directory is the fast, deterministic canary for established BCPL-for-MVS behavior.

The regression panel is deliberately different from the other tests under `tests/` and from the programs under `suite/`:

- the panel asks **did an established contract break?**;
- the numbered reconstruction tests and probes ask **what does the historical system do, and what evidence supports the reconstruction?**;
- the demonstration suites provide readable examples of **what BCPL and the reconstructed runtime can do**.

Panel tests should be small, focused, deterministic, and have a mechanical pass/fail rubric. A failure should normally identify a narrow subsystem from the test name and category alone.

## Running the panel

From the repository root:

```bash
tools/run-regression-panel
```

The default interpreter is the promoted baseline named by `asm/CURRENT` and resolved by `tools/current-icint`.

A candidate interpreter can be tested without promoting it:

```bash
tools/run-regression-panel --icint asm/icintv19.asm
```

Useful selection options are:

```text
--list
--category NAME
--test NAME
--verbose
--stop-on-fail
```

`--category` and `--test` may be repeated.

Examples:

```bash
tools/run-regression-panel --category calculation
tools/run-regression-panel --category standard-library
tools/run-regression-panel --test basic-coroutine
tools/run-regression-panel --icint asm/icintv19.asm --stop-on-fail
```

## Manifest

`manifest.tsv` is the authoritative list of panel cases. It is tab-separated and has seven fields:

```text
name    category    source    extras    compile_args    expected    expected_code
```

All paths are repository-relative.

- `name` is the stable test identifier.
- `category` groups related contracts.
- `source` is the primary BCPL source passed to `tools/compile-and-run`.
- `extras` is a space-separated list of additional `+MODULE` arguments, such as a helper compilation unit or runtime library module.
- `compile_args` contains any additional arguments that must precede the interpreter argument to `compile-and-run`; it is normally empty.
- `expected` names the checked-in semantic-output file.
- `expected_code` is the required interpreted completion code.

The manifest, not the runner source, should grow as ordinary regression cases are added.

## Semantic-output contract

Regression programs emit stable semantic records beginning with:

```text
RP:
```

For example:

```text
RP: ARITH 22 12 85 3 2
```

The runner extracts only `RP:` records and compares them exactly, in order, against the corresponding `.expected` file. It separately extracts and verifies the interpreted `CODE` from ICINT's execution-completion record.

This intentionally ignores incidental data such as JES numbers, program size, cycle counts, printer spacing, and submission messages.

A test should expose useful values rather than merely print `PASS` when practical. A changed arithmetic result is more informative than a generic success flag.

## Initial categories

The starter panel establishes these categories:

- `data-movement` — scalar/vector movement and byte access;
- `calculation` — integer arithmetic;
- `control` — branches, loops, and dispatch;
- `calls` — argument passing, nested calls, and recursion;
- `modules` — separate compilation and GLOBAL-vector linkage;
- `standard-library` — stable library entry points intended for ordinary BCPL programs;
- `storage` — reconstructed allocation services;
- `coroutines` — reconstructed coroutine services.

Additional categories should be introduced when they represent a useful durable contract, not merely to classify every historical probe.

## Standard-library growth

The `standard-library` category is intentional. As the reconstructed BCPL standard library becomes a first-class project component, its supported routines should acquire small focused regression cases here.

Library tests should distinguish between:

1. the public BCPL-level contract, which belongs in this panel once considered stable; and
2. reconstruction experiments, ABI probes, historical comparisons, or implementation-specific diagnostics, which remain in the ordinary numbered test directories.

A library routine that becomes part of the supported programming environment should eventually have at least one narrow panel test for its durable behavior. Bugs discovered in library integration should be reduced to permanent regression cases when practical.

## Rules for adding cases

A panel test should normally satisfy all of the following:

- one narrow established contract per test;
- deterministic input and output;
- no dependency on another panel test;
- no dependency on transient JES job numbers;
- no timing-sensitive result;
- small output;
- exact checked-in expected output;
- explicit runtime/library dependencies in the manifest;
- no human judgment required to decide pass or fail.

When a bug is discovered elsewhere, add a reduced panel case if the bug represents behavior that should never regress again.

The panel should grow from real contracts and real failures rather than attempting to predict every possible future defect in advance.
