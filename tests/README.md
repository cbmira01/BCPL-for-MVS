# Tests

This directory contains regression, acceptance, and diagnostic workloads for
the BCPL-for-MVS reconstruction. The tests cover both direct INTCODE execution
under `ICINT` and the interpreted BCPL compiler pipeline through SYNI/TRNI,
CGI, and the runtime libraries.

The tests are grouped by purpose rather than kept as one flat collection.
Numbered directory names roughly follow the order in which the capabilities
were established.

## Test groups

| Directory | Purpose |
| --- | --- |
| [`01-echo-test`](01-echo-test/) | Basic stream-I/O test. `echo-sysin.int` uses the historical-style `RDCH`/`WRCH` calling idiom to copy `SYSIN` to `SYSPRINT`; `best-of-times.txt` is sample input. |
| [`02-honors-thesis-and-mapstore`](02-honors-thesis-and-mapstore/) | Interpreter acceptance and diagnostics. Includes the V12 honors-thesis workload and expected output, plus the V13 MAPSTORE diagnostic that deliberately executes unsupported `X38` after building a recognizable BCPL call chain and global/local state. |
| [`03-compile-richards-factorial`](03-compile-richards-factorial/) | Compiler-pipeline evidence centered on Martin Richards's factorial example. Contains BCPL source plus historical/derived OCODE and INTCODE artifacts used while validating compilation through SYN/TRN and CGI and subsequent execution under ICINT. |
| [`04-module-test`](04-module-test/) | Separate-compilation test. The factorial program is split into two independently compiled BCPL modules: module 1 contains `START`, module 2 contains recursive `F`, and both rendezvous through `GLOBAL` slot 2. Saved `.ocode` and `.intcode` files show the independently generated intermediate forms. |
| [`05-named-dd`](05-named-dd/) | Named-stream discovery test. `main.bcpl` executes `GET "EXTRA"`; `compile-and-run --dd EXTRA=...` supplies `extra.bcpl` as an MVS `//EXTRA` input DD, whose manifest value must become visible in the compilation unit. |

## Running direct INTCODE tests

[`tools/run-intcode`](../tools/run-intcode) is the normal driver for tests
whose primary input is already INTCODE.

For example, the stream echo test uses the standard interpreted runtime and a
host file mapped to `SYSIN`:

```text
tools/run-intcode --results \
    --sysin tests/01-echo-test/best-of-times.txt \
    asm/icintv15.asm \
    tests/01-echo-test/echo-sysin.int \
    +intcode/blibi.int \
    +intcode/iclib.int
```

The test program itself documents that it uses the `RDCH`/`WRCH` idiom and
expects runtime support.

The files in `02-honors-thesis-and-mapstore` are likewise direct INTCODE
workloads. The MAPSTORE test is intentionally a failure-path diagnostic:
`X38` is outside the implemented X-op range and is used to force the normal
INTCODE error and MAPSTORE path.

## Running BCPL compiler tests

[`tools/compile-and-run`](../tools/compile-and-run) drives BCPL source through
the interpreted compiler pipeline and then executes the generated INTCODE.

A single-module Richards factorial run is represented by the material in
`03-compile-richards-factorial`:

```text
tools/compile-and-run \
    --results \
    --save-ocode \
    --save-intcode \
    asm/icintv15.asm \
    tests/03-compile-richards-factorial/richards-factorial-test.bcpl
```

With the save options enabled, generated host-side intermediates use these
extensions:

```text
<module>.ocode
<module>.intcode
```

The older `.int`, `.OCODE`, and similarly named files retained in
`03-compile-richards-factorial` are historical development artifacts and should
not be mistaken for the current save-file naming convention.

## Separate BCPL modules

`04-module-test` is the first regression test for true separate BCPL
compilation under the interpreted toolchain. Its two source files are compiled
independently through SYN/TRN and CGI, then their INTCODE modules are loaded in
command-line order into the common ICINT global vector.

Run it with the same `+PATH` convention used by `run-intcode` for additional
modules:

```text
tools/compile-and-run \
    --results \
    --save-ocode \
    --save-intcode \
    --job-name MODLTEST \
    asm/icintv15.asm \
    tests/04-module-test/module-test-1.bcpl \
    +tests/04-module-test/module-test-2.bcpl
```

Module 1 declares `F:2` and calls through global slot 2. Module 2 also declares
`F:2` and defines `F`, so its generated INTCODE publishes the entry point in
that same slot. Successful execution therefore demonstrates cross-module
GLOBAL-vector rendezvous rather than simple BCPL source concatenation.

## Named DD and `GET` test

`05-named-dd` exercises V15's generic input-stream discovery through the
historical compiler's textual `GET` mechanism. Run it as:

```text
tools/compile-and-run \
    --results \
    --job-name NAMEDD \
    --dd EXTRA=tests/05-named-dd/extra.bcpl \
    asm/icintv15.asm \
    tests/05-named-dd/main.bcpl
```

`compile-and-run` places the host file into the compiler step as an in-stream
MVS DD named `EXTRA`. When SYN encounters:

```text
GET "EXTRA"
```

it calls the normal named-input-stream path. V15 should discover `//EXTRA`,
open it, and allow the compiler to read the included BCPL text. The included
file defines:

```text
MANIFEST $( XVAL = 12345 $)
```

so successful compilation and execution should print:

```text
VALUE FROM EXTRA = 12345
```

This is intentionally a textual inclusion test, not a separate-compilation
or `GLOBAL`-linkage test.

## File conventions

BCPL source files use `.bcpl`. Current saved compiler intermediates use
`.ocode` and `.intcode`. Direct or historical INTCODE workloads may still use
`.int`; those filenames record the development state in which the tests were
created and are intentionally retained where they are useful as evidence.

Files ending in `.expected` contain reference output associated with a test.
Comments at the beginning of diagnostic INTCODE files are part of the test
documentation and should be retained when modifying or extending a workload.

## Future test directions

Useful next test groups include:

- additional arbitrary named input DDs, including optional compiler `OPTIONS`;
- DASD-resident input and output data sets rather than only in-stream data;
- native System/370 code generated from OCODE;
- reconstructed runtime/`BCPLMAIN` services as they are discovered; and
- a small suite of BCPL example programs that exercise language and runtime
  facilities in readable, practical ways.

## Maintenance

Keep each test group focused on one capability or milestone. When a new test
establishes a distinct compiler, interpreter, stream, runtime, storage, or
linkage behavior, add it as a clearly named test group and update this README
so the purpose and normal invocation remain obvious.

See [`tools/README.md`](../tools/README.md) for the host-side command-line tools
and [`intcode/README.md`](../intcode/README.md) for the standard INTCODE compiler
and runtime components.
