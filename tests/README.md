# BCPL-for-MVS tests

The `tests` tree contains focused workloads used to validate the reconstructed BCPL bootstrap, compiler phases, INTCODE interpreter, runtime behavior, and MVS host adapters. Each numbered directory represents a distinct reconstruction milestone or regression target and should remain reproducible from the repository root.

The commands below are the normal evidence-producing units. Prefer reproducible command stanzas and expected output over transient JES job numbers when documenting results.

## 01-echo-test

Exercises the historical `RDCH` / `WRCH` calling idiom by echoing runtime `SYSIN` to `SYSPRINT`. The input fixture is `best-of-times.txt`; the INTCODE program is `echo-sysin.int`.

Run:

```bash
tools/run-intcode --results \
    --sysin tests/01-echo-test/best-of-times.txt \
    asm/icintv17.asm \
    tests/01-echo-test/echo-sysin.int \
    +intcode/iclib.int
```

A successful run reproduces the supplied text through the ordinary ICINT input/output path and completes with interpreted code zero.

## 02-honors-thesis-and-mapstore

Contains two direct INTCODE acceptance/diagnostic workloads.

`intcode-v12-honors-thesis.int` packages Richards' published factorial example together with the required BLIBI and ICLIB material. Its expected output is retained in `intcode-v12-honors-thesis.expected`.

Run:

```bash
tools/run-intcode --results \
    asm/icintv12.asm \
    tests/02-honors-thesis-and-mapstore/intcode-v12-honors-thesis.int
```

The expected result is `F(1)` through `F(10)`, ending at `3628800`, with interpreted code zero.

`intcode-v13-mapstore.int` is a deliberate diagnostic workload. It builds a recognizable call chain and global state, then executes unsupported `X38` so ICINT V13 takes its normal INTCODE error path and emits MAPSTORE information.

Run:

```bash
tools/run-intcode --results \
    asm/icintv13.asm \
    tests/02-honors-thesis-and-mapstore/intcode-v13-mapstore.int
```

The source comments record the expected derived globals and stack shape at failure.

## 03-compile-richards-factorial

Exercises the complete preserved compiler path: BCPL source through SYN/TRN to OCODE, through CGI to INTCODE, then execution under ICINT with BLIBI and ICLIB.

Run:

```bash
tools/compile-and-run --results --save-ocode --save-intcode \
    asm/icintv17.asm \
    tests/03-compile-richards-factorial/richards-factorial-test.bcpl
```

The program prints factorials from 1 through 10. The directory also retains historical OCODE/INTCODE artifacts from earlier stages of reconstruction, including `richards-example.int`, `compiled-factorial-v14.int`, and both historical and current `richards-factorial-test` intermediates.

## 04-module-test

Exercises separate BCPL compilation and common-`GLOBAL`-vector rendezvous. Module 1 declares `F:2` and calls through global slot 2; module 2 declares the same slot and defines `F`.

Run:

```bash
tools/compile-and-run --results --save-ocode --save-intcode \
    asm/icintv17.asm \
    tests/04-module-test/module-test-1.bcpl \
    +tests/04-module-test/module-test-2.bcpl
```

Successful execution demonstrates cross-module linkage through the shared BCPL global vector rather than source concatenation. Saved `.ocode` and `.intcode` files for both modules are retained in the directory as evidence.

## 05-named-dd

Exercises named MVS input discovery through the historical compiler's textual `GET` mechanism. `main.bcpl` contains `GET "EXTRA"`; `extra.bcpl` defines `XVAL = 12345`.

Run:

```bash
tools/compile-and-run --results \
    --dd EXTRA=tests/05-named-dd/extra.bcpl \
    asm/icintv17.asm \
    tests/05-named-dd/main.bcpl
```

Expected output:

```text
VALUE FROM EXTRA = 12345
```

This is textual inclusion through a named DD, not separate compilation or `GLOBAL` linkage.

## 06-dynamic-streams

Exercises GETMAIN-managed ordinary input streams introduced by the V16 stream refactor. The nested include chain keeps four generic input streams live at once:

```text
SYSIN -> LEVEL1 -> LEVEL2 -> LEVEL3
```

Run:

```bash
tools/compile-and-run --results \
    --dd LEVEL1=tests/06-dynamic-streams/level1.bcpl \
    --dd LEVEL2=tests/06-dynamic-streams/level2.bcpl \
    --dd LEVEL3=tests/06-dynamic-streams/level3.bcpl \
    asm/icintv17.asm \
    tests/06-dynamic-streams/main.bcpl
```

Expected output:

```text
DEEPEST GET VALUE = 24680
```

The test specifically guards against regression to V15's fixed three-slot generic input pool.

## 07-many-streams

Stresses dynamic stream management independently of SYN's nested `GET` mechanism. The BCPL program opens twelve named input streams (`DD01` through `DD12`) simultaneously, reads each one, and closes it while the others remain live.

Run:

```bash
tools/compile-and-run --results --listing heavy \
    --dd DD01=tests/07-many-streams/dd01.txt \
    --dd DD02=tests/07-many-streams/dd02.txt \
    --dd DD03=tests/07-many-streams/dd03.txt \
    --dd DD04=tests/07-many-streams/dd04.txt \
    --dd DD05=tests/07-many-streams/dd05.txt \
    --dd DD06=tests/07-many-streams/dd06.txt \
    --dd DD07=tests/07-many-streams/dd07.txt \
    --dd DD08=tests/07-many-streams/dd08.txt \
    --dd DD09=tests/07-many-streams/dd09.txt \
    --dd DD10=tests/07-many-streams/dd10.txt \
    --dd DD11=tests/07-many-streams/dd11.txt \
    --dd DD12=tests/07-many-streams/dd12.txt \
    asm/icintv17.asm \
    tests/07-many-streams/main.bcpl
```

Expected output begins with `OPENED 12 STREAMS`, reports `DD1 = STREAM 01` through `DD12 = STREAM 12`, and ends with `ALL 12 STREAMS READ AND CLOSED`.

See [`07-many-streams/README.md`](07-many-streams/README.md) for the complete expected output and diagnostic intent.

## 08-character-translation

Exercises the boundary between host ASCII, MVS EBCDIC records, ICINT's translation tables, and the historical BCPL character model. The BCPL source deliberately contains the historical spellings `\/`, `/\`, `\=`, and unary `\`; the `PUNCT` fixture checks additional punctuation through ordinary `RDCH`.

Run with intermediate recovery enabled:

```bash
tools/compile-and-run --results --save-ocode --save-intcode \
    --dd PUNCT=tests/08-character-translation/punct.txt \
    asm/icintv17.asm \
    tests/08-character-translation/character-translation.bcpl
```

A successful compile recovers:

```text
workarea/character-translation.ocode
workarea/character-translation.intcode
```

and the runtime prints the Boolean operator results followed by the BCPL character codes read from `PUNCT`.

See [`08-character-translation/README.md`](08-character-translation/README.md) for the fixture and regression rationale.

## 09-multiple-assignment

Records the historical MR10 translator's sequential treatment of comma-separated multiple assignment. In particular, `A, B := B, A` starting from `A=1, B=2` produces `A=2, B=2`, and the Euclid-style assignment likewise reflects sequential stores.

Run:

```bash
tools/compile-and-run --results --listing heavy \
    asm/icintv17.asm \
    tests/09-multiple-assignment/multiple-assignment.bcpl
```

Expected output:

```text
SWAP BEFORE A=1 B=2
SWAP AFTER  A=2 B=2
EUCLID BEFORE A=1071 B=462
EUCLID AFTER  A=462 B=0
```

See [`09-multiple-assignment/README.md`](09-multiple-assignment/README.md) for the compiler-behavior explanation.

## 10-coroutines

Contains the first BCPL coroutine reconstruction experiments. Two compiler-observation probes establish the MR10 calling/frame conventions used by `CHANGECO`; a third test demonstrates genuine fixed-stack producer/consumer coroutine switching.

The call-shape probe is reproduced with:

```bash
tools/compile-and-run --results --save-ocode --save-intcode \
    asm/icintv17.asm \
    tests/10-coroutines/compiler-probe.bcpl
```

The synthetic-frame probe is reproduced with:

```bash
tools/compile-and-run --results --save-ocode --save-intcode \
    asm/icintv17.asm \
    tests/10-coroutines/frame-layout-probe.bcpl
```

The executable producer/consumer test is reproduced with:

```bash
tools/compile-and-run --results --listing heavy \
    asm/icintv17.asm \
    tests/10-coroutines/fixed-stack-producer-consumer.bcpl
```

Its expected output alternates `PRODUCER: 1` / `CONSUMER: 1` through value 5 and completes with interpreted code zero. The generated OCODE and INTCODE from the two probes are preserved under `10-coroutines/evidence/` as primary reconstruction evidence.

See [`10-coroutines/README.md`](10-coroutines/README.md) for the detailed `CHANGECO` findings and the distinction between the portable coroutine ABI and the eventual native System/370 implementation.

## File conventions

BCPL source files use `.bcpl`. Current saved compiler intermediates use `.ocode` and `.intcode`. Direct or historical INTCODE workloads may use `.int`; those names are retained where they record reconstruction history. Files ending in `.expected` contain reference output.

Generated intermediates belong in `workarea/` unless they are intentionally retained as reconstruction evidence. Preserved evidence should live with the test that explains why it matters, as in `10-coroutines/evidence/`.

## Maintenance

Keep each test group focused on one capability or milestone. When a new test establishes a distinct compiler, interpreter, stream, runtime, storage, linkage, language, or calling-convention behavior, add it as a clearly named test group and update this README with a reproducible command stanza and expected result.

See [`tools/README.md`](../tools/README.md) for the host-side command-line tools and [`intcode/README.md`](../intcode/README.md) for the standard INTCODE compiler/runtime components.
