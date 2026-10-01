# INTCODE Files

This directory contains INTCODE components used while reconstructing the
BCPL bootstrap environment under MVS.

The files are executable input for the project's `ICINT` interpreter,
not System/370 object code. They preserve important pieces of the
historical BCPL compiler and its INTCODE runtime environment.

## Files

| File | Purpose |
| --- | --- |
| [`syni.int`](syni.int) | INTCODE form of the BCPL syntax-analysis/compiler front-end phase (`SYNI`). |
| [`trni.int`](trni.int) | INTCODE form of the BCPL translation phase (`TRNI`). |
| [`cgi.int`](cgi.int) | INTCODE form of the compiler code-generator phase (`CGI`), which generates INTCODE. |
| [`blibi.int`](blibi.int) | INTCODE BCPL library support (`BLIBI`) used by programs running under the interpreter. |
| [`iclib.int`](iclib.int) | Small INTCODE support library (`ICLIB`) used by the interpreted environment. |

Together, `SYNI`, `TRNI`, and `CGI` are the preserved compiler stages
that make the INTCODE bootstrap path possible. `BLIBI` and `ICLIB`
provide runtime support needed by interpreted programs.

## Running INTCODE

The host-side [`tools/run-intcode`](../tools/run-intcode) command is the
normal development interface for executing an INTCODE program with the
project's MVS `ICINT` implementation.

For example:

```text
tools/run-intcode --runtime --results \
    asm/icintv13.asm \
    intcode/program.int
```

With `--runtime`, `run-intcode` constructs the interpreter input stream
in this order:

```text
program
BLIBI
ICLIB
```

See [`tools/README.md`](../tools/README.md) for the host-tool workflow.

## Maintenance

This directory is expected to grow as additional INTCODE programs,
compiler components, test inputs, or reconstructed runtime material are
added. Keep this README updated when files with distinct roles are added.
