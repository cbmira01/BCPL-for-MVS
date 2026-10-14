# Regression panel

This directory is the fast deterministic canary for established BCPL-for-MVS behavior. It is intentionally different from the numbered reconstruction probes and from the readable programs under `suite/`.

Run the complete panel with:

```sh
tools/run-regression-panel
```

The default interpreter is the promoted baseline named by `config/CURRENT` and resolved by `tools/current-icint`.

A candidate interpreter can be tested without promoting it:

```sh
tools/run-regression-panel --icint PATH
```

Useful selectors include:

```text
--list
--category NAME
--test NAME
--verbose
--stop-on-fail
```

`--category` and `--test` may be repeated.

## Manifest

`manifest.tsv` is the authoritative list of cases. It has seven tab-separated fields:

```text
name    category    source    extras    compile_args    expected    expected_code
```

The manifest describes the primary BCPL source, extra compilation units/runtime modules, additional compiler arguments, exact expected semantic output, and required interpreted completion code.

## Semantic-output contract

Regression programs emit stable records beginning with `RP:`. The runner extracts only those semantic records and compares them exactly, in order, with the corresponding `.expected` file. It separately checks the interpreted completion code.

Incidental values such as JES numbers, program size, cycle counts, printer spacing, and submission messages are deliberately ignored.

Tests should expose useful values rather than merely printing `PASS` when practical: a changed arithmetic result tells more than a generic success word.

## Categories

The panel currently covers data movement, calculation, control flow, calls/recursion, separate modules, standard-library routines, storage, and coroutines.

A new case should normally be small, deterministic, independent of other cases, explicit about runtime dependencies, and mechanically decidable. When a real bug is found, reduce it to a panel case if it represents behavior that should not regress.