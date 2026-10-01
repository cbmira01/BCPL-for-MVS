# System/370 Assembler Sources

This directory contains System/370 assembler source developed for the
BCPL-for-MVS reconstruction.

The sources are intended for the IFOX assembler supplied with the
project's MVS 3.8J environment. The principal work here is the native
MVS implementation of `ICINT`, the interpreter used to execute the
preserved BCPL INTCODE compiler and runtime components.

## Files

| File | Purpose |
| --- | --- |
| [`hello-world.asm`](hello-world.asm) | Small IFOX/MVS example program. Demonstrates normal MVS entry/exit linkage, a save area, QSAM output through `OPEN`/`PUT`/`CLOSE`, and a simple `SYSPRINT` DCB. Useful as a basic assembler/toolchain smoke test. |
| [`icintv12.asm`](icintv12.asm) | Frozen, target-validated ICINT V12. V12 corrected BCPL pointer representation so that BCPL pointers are word-addressed rather than host byte-addressed. Its acceptance target was Richards's factorial program running with complete `BLIBI` and `ICLIB`, producing the correct factorials and returning code 0. |
| [`icintv13.asm`](icintv13.asm) | Current V13 ICINT development version. Based on validated V12 and adds an explicitly reconstructed `MAPSTORE` diagnostic while preserving V12 INTCODE execution semantics. The diagnostic format is not claimed to reproduce Richards's original `MAPSTORE`. |

The comments at the beginning of each ICINT version are important
engineering documentation. They record the version's base, scope,
representation choices, acceptance target, and register conventions.

## ICINT development approach

The MVS interpreter is a structural System/370 translation of the
historical `mr10/bcplkit/icint` implementation preserved under
[`richards-bcpltape`](../richards-bcpltape/).

Development deliberately keeps the assembler implementation close to
the organization and semantics of the historical ICINT. Departures from
that pattern should be made when required by the MVS/System/370 host or
when an explicitly reconstructed diagnostic or development facility is
being added. Host representation details should remain visible rather
than being allowed to alter BCPL or INTCODE semantics implicitly.

Versioned ICINT files are checkpoints, not merely old copies. A version
identified as validated should remain available as a known baseline for
comparison with later development.

## Building and running assembler programs

The host-side [`tools/make-asm-job`](../tools/make-asm-job) command
constructs an IFOX assemble/link/run JCL deck from an assembler source
file.

For example:

```text
tools/make-asm-job asm/hello-world.asm \
    --output-dir jcl \
    --listing heavy
```

Submit the generated deck with:

```text
tools/submit-jcl jcl/hello-world-heavy.jcl
```

See [`tools/README.md`](../tools/README.md) for the complete host-side
workflow.

## Running ICINT

For normal ICINT development, [`tools/run-intcode`](../tools/run-intcode)
combines assembly, linkage, execution, INTCODE input, job submission,
and result collection.

For example:

```text
tools/run-intcode --runtime --results \
    asm/icintv13.asm \
    tests/richards-example.int
```

The standard interpreted runtime components are described in
[`intcode/README.md`](../intcode/README.md), and diagnostic workloads are
described in [`tests/README.md`](../tests/README.md).

## Maintenance

This directory is expected to acquire additional native assembler code
as the BCPL bootstrap and runtime reconstruction proceed. Keep this
README focused on the role of significant source files and development
checkpoints rather than duplicating detailed implementation comments
from the assembler sources themselves.
