# INTCODE Files

This directory contains the preserved INTCODE components used to host the BCPL bootstrap environment under MVS.

These files are executable input for the project's `ICINT` interpreter, not System/370 object code. They preserve important pieces of the historical BCPL compiler and its interpreted runtime environment.

## Files

| File | Purpose |
| --- | --- |
| [`syni.int`](syni.int) | INTCODE form of the BCPL syntax-analysis/compiler front-end phase (`SYNI`). |
| [`trni.int`](trni.int) | INTCODE form of the BCPL translation phase (`TRNI`). |
| [`cgi.int`](cgi.int) | INTCODE form of the historical compiler code-generator phase (`CGI`), which translates OCODE into INTCODE. |
| [`blibi.int`](blibi.int) | INTCODE BCPL library support (`BLIBI`) used by interpreted compiler phases and programs. |
| [`iclib.int`](iclib.int) | Small INTCODE support library (`ICLIB`) used by the interpreted environment. |

Together, `SYNI`, `TRNI`, and `CGI` form the preserved compiler pipeline used by the current bootstrap:

```text
BCPL source
    |
    v
SYNI + TRNI
    |
    v
OCODE
    |
    v
CGI
    |
    v
INTCODE
```

The generated INTCODE is then loaded with `BLIBI` and `ICLIB` and executed by `ICINT`.

## Direct INTCODE execution

Use [`tools/run-intcode`](../tools/run-intcode) when the primary thing being tested is already INTCODE.

```text
tools/run-intcode --results \
    asm/icintv15.asm \
    tests/01-echo-test/echo-sysin.int \
    +intcode/blibi.int \
    +intcode/iclib.int
```

Additional modules are specified explicitly with `+PATH` and are concatenated into `INTIN` in command-line order. Runtime components are ordinary modules; the old special-purpose runtime/library wrapper switches are no longer the normal interface.

## Compiling BCPL through the interpreted pipeline

Use [`tools/compile-and-run`](../tools/compile-and-run) for BCPL compiler work. It stages the standard compiler/runtime INTCODE components automatically, compiles BCPL source to OCODE, runs CGI to produce INTCODE, and executes the result.

```text
tools/compile-and-run \
    --results \
    --save-ocode \
    --save-intcode \
    asm/icintv15.asm \
    tests/03-compile-richards-factorial/richards-factorial-test.bcpl
```

With the save options enabled, host-side intermediate files are written as:

```text
<module>.ocode
<module>.intcode
```

Separate BCPL compilation units are supported. Additional sources use the same `+PATH` convention as `run-intcode`; each source is compiled independently before the generated INTCODE modules are loaded together through the common BCPL `GLOBAL` vector.

See [`tests/04-module-test`](../tests/04-module-test/) for the first validated separate-compilation example.

## Historical role and future direction

These files are bootstrap assets. The current interpreted path proves that the preserved compiler can be hosted under MVS and provides a working reference while the project develops a native System/370 code generator and runtime.

As native code generation comes online, the INTCODE compiler phases will remain valuable both as historical evidence and as a reference implementation against which the native bootstrap can be compared.

## Maintenance

Keep this directory focused on preserved or directly useful INTCODE compiler/runtime components. Tests and generated intermediates belong under [`tests/`](../tests/) or `workarea/` rather than being added here casually.
