# BCPL-for-MVS tests

The `tests` tree contains small, focused workloads used to validate the reconstructed BCPL bootstrap, compiler phases, INTCODE interpreter, runtime behavior, and MVS host adapters. Each directory should test one distinct capability and should remain readable enough to serve as evidence when later changes regress behavior.

The current test groups are organized as follows.

## 01-factorial

A minimal INTCODE execution test. It is useful for verifying that ICINT still assembles, interprets ordinary arithmetic/control flow, and returns expected output after structural changes to the interpreter.

## 02-cg-test

Exercises CGI and INTCODE generation. This test is useful when changes affect CGI output formatting, ICINT input recordization, or the path by which generated INTCODE is fed back to the interpreter.

## 03-compiler-test

Exercises the historical SYN/TRN compiler path and the CGI code generator as an integrated bootstrap chain.

## 04-module-test

Exercises separate BCPL compilation and common-GLOBAL-vector rendezvous. Each BCPL source module is compiled independently through SYN/TRN and CGI, then their INTCODE modules are loaded in command-line order into the common ICINT global vector.

Run it with the same `+PATH` convention used by `run-intcode` for additional modules:

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

## V16 dynamic stream test

`06-dynamic-streams` exercises V16's GETMAIN-managed ordinary input streams.
The source nesting deliberately requires four simultaneously live generic
input streams: `SYSIN`, `LEVEL1`, `LEVEL2`, and `LEVEL3`. That exceeds V15's
three fixed generic-input slots and therefore directly tests the reason for
the V16 stream refactor.

Run it as:

```text
tools/compile-and-run \
    --results \
    --job-name DYNSTRM \
    --dd LEVEL1=tests/06-dynamic-streams/level1.bcpl \
    --dd LEVEL2=tests/06-dynamic-streams/level2.bcpl \
    --dd LEVEL3=tests/06-dynamic-streams/level3.bcpl \
    asm/icintv16.asm \
    tests/06-dynamic-streams/main.bcpl
```

The include chain is:

```text
SYSIN -> LEVEL1 -> LEVEL2 -> LEVEL3
```

`LEVEL3` defines:

```text
MANIFEST $( DEEPVAL = 24680 $)
```

Successful compilation and execution should print:

```text
DEEPEST GET VALUE = 24680
```

## Character translation regression test

`08-character-translation` exercises host ASCII to MVS EBCDIC to ICINT to BCPL character handling, with particular attention to punctuation whose EBCDIC encoding varies by code page.

The source deliberately contains the historical BCPL spellings `\/`, `/\`, `\=`, and unary `\`. These must compile correctly; replacing them with alternate syntax would hide the host-character defect instead of fixing it.

Run it from the repository root with intermediate recovery enabled:

```text
tools/compile-and-run \
    --results \
    --save-ocode \
    --save-intcode \
    --job-name CHARXLT \
    --dd PUNCT=tests/08-character-translation/punct.txt \
    asm/icintv16.asm \
    tests/08-character-translation/character-translation.bcpl
```

A successful run should recover both:

```text
workarea/character-translation.ocode
workarea/character-translation.intcode
```

The program then reads the `PUNCT` DD through ordinary `RDCH` and reports the resulting BCPL character codes. See the test-local README for the fixture and diagnostic intent.

## File conventions

BCPL source files use `.bcpl`. Current saved compiler intermediates use `.ocode` and `.intcode`. Direct or historical INTCODE workloads may still use `.int`; those filenames record the development state in which the tests were created and are intentionally retained where they are useful as evidence.

Files ending in `.expected` contain reference output associated with a test. Comments at the beginning of diagnostic INTCODE files are part of the test documentation and should be retained when modifying or extending a workload.

## Future test directions

Useful next test groups include:

- additional arbitrary named input DDs, including optional compiler `OPTIONS`;
- DASD-resident input and output data sets rather than only in-stream data;
- native System/370 code generated from OCODE;
- reconstructed runtime/`BCPLMAIN` services as they are discovered; and
- a small suite of BCPL example programs that exercise language and runtime facilities in readable, practical ways.

## Maintenance

Keep each test group focused on one capability or milestone. When a new test establishes a distinct compiler, interpreter, stream, runtime, storage, or linkage behavior, add it as a clearly named test group and update this README so the purpose and normal invocation remain obvious.

See [`tools/README.md`](../tools/README.md) for the host-side command-line tools and [`intcode/README.md`](../intcode/README.md) for the standard INTCODE compiler and runtime components.
