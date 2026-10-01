# Test Inputs

This directory contains test and diagnostic inputs used while developing
and validating the BCPL-for-MVS reconstruction.

At present the tests are primarily INTCODE workloads for the project's
MVS `ICINT` interpreter. Some preserve historical examples; others are
purpose-built diagnostics for particular interpreter capabilities.

## Files

| File | Purpose |
| --- | --- |
| [`richards-example.int`](richards-example.int) | Martin Richards's published factorial INTCODE example, with a small number of normalized archival readings. It contains the example program only, without runtime-library material or test wrappers. |
| [`intcode-v12-honors-thesis.int`](intcode-v12-honors-thesis.int) | V12 acceptance workload built around Richards's factorial example and used to exercise the interpreter more completely. |
| [`intcode-v12-honors-thesis.expected`](intcode-v12-honors-thesis.expected) | Expected output for the V12 honors-thesis acceptance workload, including factorial results, execution-cycle count, and completion code. |
| [`intcode-v13-mapstore.int`](intcode-v13-mapstore.int) | V13 diagnostic workload that constructs a recognizable BCPL call chain and values in locals/globals, then deliberately executes an unsupported X-op to exercise the interpreter's error and MAPSTORE diagnostics. |

The comments at the beginning of individual `.int` files are part of the
test documentation and should be retained when modifying or extending a
workload.

## Running tests

The host-side [`tools/run-intcode`](../tools/run-intcode) command is the
normal way to execute these workloads under the MVS `ICINT`
implementation.

For example:

```text
tools/run-intcode --runtime --results \
    asm/icintv13.asm \
    tests/richards-example.int
```

See [`tools/README.md`](../tools/README.md) for the current command-line
workflow and [`intcode/README.md`](../intcode/README.md) for the standard
INTCODE runtime components.

## Test organization

Where practical, test names identify the interpreter version or feature
for which the workload was introduced. A version in a filename records
that historical development point; it does not necessarily mean that the
test is useful only with that version.

Files ending in `.expected` contain reference output associated with a
test workload. Diagnostic tests may instead describe their expected
state or failure directly in comments when exact textual output is not
the principal assertion.

## Maintenance

This directory is expected to grow as ICINT, the compiler bootstrap, and
the reconstructed BCPL runtime develop. Add or update entries here when
a test has a distinct purpose that is not obvious from its filename.
