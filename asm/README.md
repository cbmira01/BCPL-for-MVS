# System/370 Assembler Sources

This directory contains System/370 assembler source developed for the
BCPL-for-MVS reconstruction.

The sources are intended for the IFOX assembler supplied with the
project's MVS 3.8J environment. The principal reconstructed program here
is the native MVS implementation of `ICINT`, used to host the preserved
BCPL INTCODE compiler and runtime components.

## Files

| File | Purpose |
| --- | --- |
| [`hello-world.asm`](hello-world.asm) | Small IFOX/MVS example program. Demonstrates normal MVS entry/exit linkage, a save area, QSAM output through `OPEN`/`PUT`/`CLOSE`, and a simple `SYSPRINT` DCB. Useful as a basic assembler/toolchain smoke test. |
| [`icintv12.asm`](icintv12.asm) | Validated ICINT V12 milestone. Corrected BCPL pointer representation so BCPL pointers are word-addressed rather than host byte-addressed. Its acceptance target was Richards's factorial program running with `BLIBI` and `ICLIB`, producing the correct factorials and returning code 0. |
| [`icintv13.asm`](icintv13.asm) | V13 milestone. Added a reconstructed `MAPSTORE` diagnostic while preserving V12 execution semantics. The diagnostic format is project reconstruction, not a claim to reproduce Richards's original `MAPSTORE` exactly. |
| [`icintv14.asm`](icintv14.asm) | V14 milestone. Added reliable `FINDOUTPUT("INTCODE")` handling and the special INTCODE output recordizer needed to capture CGI output as valid 80-byte records, allowing generated INTCODE to be saved and re-ingested. |
| [`icintv14-trace.asm`](icintv14-trace.asm) | Development/diagnostic V14 variant retained for historical comparison. |
| [`icintv15.asm`](icintv15.asm) | Current ICINT milestone. Generalizes MVS stream discovery so ordinary BCPL stream names map to discovered DDNAMEs, while retaining special handling only where the host requires it. V15 has successfully hosted the complete interpreted compiler pipeline and separate BCPL compilation with `GLOBAL`-vector linkage. |

The comments at the beginning of each ICINT version are the primary record of
that version's design, scope, representation choices, and acceptance target.
Major numbered versions are retained as milestones; the project does not aim
to create a separate checkpoint file for every successful experiment.

## ICINT development approach

The MVS interpreter is a structural System/370 translation of the
historical `mr10/bcplkit/icint` implementation preserved under
[`richards-bcpltape`](../richards-bcpltape/).

Development deliberately keeps the assembler implementation close to the
organization and semantics of the historical ICINT. Departures from that
pattern are made when required by the MVS/System/370 host, especially for
stream discovery, record-oriented I/O, and MVS data-set handling. Host
representation details should remain visible rather than silently changing
BCPL or INTCODE semantics.

ICINT is primarily bootstrap infrastructure. Once it is sufficiently complete
to host the compiler and useful MVS I/O paths, development emphasis moves to
the native code generator, runtime, and self-hosting compiler rather than
turning ICINT into a general-purpose debugger.

## Building and running assembler programs

The host-side [`tools/make-asm-job`](../tools/make-asm-job) command constructs
an IFOX assemble/link/run JCL deck from an assembler source file.

```text
tools/make-asm-job asm/hello-world.asm \
    --output-dir jcl \
    --listing heavy
```

Submit the generated deck with:

```text
tools/submit-jcl jcl/hello-world-heavy.jcl
```

See [`tools/README.md`](../tools/README.md) for the complete host-side workflow.

## Running INTCODE under ICINT

For direct INTCODE execution, [`tools/run-intcode`](../tools/run-intcode)
assembles and links ICINT, constructs the ordered `INTIN` concatenation,
submits the job, and can extract the results.

For example:

```text
tools/run-intcode --results \
    asm/icintv15.asm \
    tests/01-echo-test/echo-sysin.int \
    +intcode/blibi.int \
    +intcode/iclib.int
```

Additional INTCODE modules use the explicit `+PATH` convention and are loaded
in command-line order.

## Compiling BCPL under ICINT

For compiler-pipeline testing, use
[`tools/compile-and-run`](../tools/compile-and-run), not `run-intcode`.
`compile-and-run` stages `SYNI`, `TRNI`, `CGI`, `BLIBI`, and `ICLIB`, compiles
one or more BCPL source modules independently, and then runs the generated
INTCODE.

```text
tools/compile-and-run \
    --results \
    --save-ocode \
    --save-intcode \
    asm/icintv15.asm \
    tests/03-compile-richards-factorial/richards-factorial-test.bcpl
```

Separate source modules use the same `+PATH` notation:

```text
tools/compile-and-run \
    --results \
    asm/icintv15.asm \
    tests/04-module-test/module-test-1.bcpl \
    +tests/04-module-test/module-test-2.bcpl
```

The standard interpreted compiler/runtime components are described in
[`intcode/README.md`](../intcode/README.md), and regression workloads are
described in [`tests/README.md`](../tests/README.md).

## Next native work

The next major assembler-facing reconstruction target is a System/370 BCPL
code generator that consumes OCODE and emits native assembler. That work is
expected to expose more of the native calling conventions and runtime services
that the eventual `BCPLMAIN` replacement must provide.

## Maintenance

Keep this README focused on significant assembler sources and ICINT milestones.
Detailed implementation history belongs in the source comments and tests rather
than in an ever-growing list of transient checkpoints.
