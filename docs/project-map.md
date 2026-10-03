# BCPL for MVS Project Map

## Purpose

This document is a high-level orientation map for the repository.

It is intended for contributors and readers who want to answer practical questions such as:

- What is this project trying to build?
- Which parts of the repository are historical evidence and which are reconstructed code?
- Where should a new compiler, runtime, test, tool, or document go?
- Why does development involve a running MVS 3.8J system under Hercules?
- What conventions are expected when making changes?
- Where is the detailed documentation for each area?

For historical background on BCPL itself and a non-specialist explanation of compiler porting, see [`BCPL-history-and-porting.md`](BCPL-history-and-porting.md).

For current project status and near-term direction, see the repository [`README.md`](../README.md).

---

## Project goal

The project is reconstructing a usable BCPL development environment for IBM MVS 3.8J on System/370.

The historical BCPL transport material provides preserved compiler and runtime evidence. The reconstruction adds the System/370 and MVS-specific pieces necessary to make that software run again and, eventually, to produce a self-hosting native BCPL system on MVS.

The current interpreted path is:

```text
BCPL source
    |
    v
SYNI / TRNI
    |
    v
OCODE
    |
    v
CGI
    |
    v
INTCODE
    |
    v
ICINT
    |
    v
program execution under MVS
```

The long-term native path is intended to become approximately:

```text
BCPL source
    |
    v
portable compiler front end
    |
    v
OCODE
    |
    v
System/370 code generator
    |
    v
System/370 assembler / object code
    |
    v
native MVS load module
```

---

## Repository map

### `richards-bcpltape/`

Historical BCPL material preserved from the Richards transport tape and related sources.

Treat this area primarily as **evidence**, not as a convenient place to rewrite historical source.

Use it to answer questions such as:

- What did the original compiler phases look like?
- Which runtime routines existed?
- What GLOBAL assignments were historically used?
- What machine-dependent assumptions were present?
- What bootstrap mechanisms were intended?

Start with [`../richards-bcpltape/README.md`](../richards-bcpltape/README.md).

---

### `asm/`

Reconstructed System/370 assembler code.

The principal current component is ICINT, the INTCODE interpreter used to host the preserved BCPL compiler phases under MVS.

This directory also holds numbered ICINT checkpoints. The validated interpreter is selected through `asm/CURRENT` and resolved with:

```sh
tools/current-icint
```

Do not assume that the numerically highest `icintv*.asm` file is the promoted baseline.

See [`../asm/README.md`](../asm/README.md).

---

### `intcode/`

INTCODE-side runtime and support material used by the interpreted bootstrap.

This area contains code that runs inside ICINT rather than as native System/370 instructions.

It includes machine-dependent bootstrap support such as the interpreted implementation of `CHANGECO`.

See [`../intcode/README.md`](../intcode/README.md).

---

### `library/`

Reusable BCPL library and runtime modules reconstructed for the project.

Examples include:

- storage allocation;
- coroutines;
- random-number generation;
- integer utilities;
- string utilities;
- memory/vector helpers;
- numeric conversion;
- character utilities;
- line-oriented I/O.

These are intended to be separately compiled alongside application source, for example:

```sh
tools/compile-and-run --results \
    "$(tools/current-icint)" \
    main.bcpl \
    +library/random.bcpl \
    +library/integer-utils.bcpl
```

GLOBAL assignments and conventions are documented in [`../library/GLOBALS.md`](../library/GLOBALS.md).

See [`../library/README.md`](../library/README.md).

---

### `tests/`

Focused regression and reconstruction tests.

Tests should be small and should establish specific contracts, invariants, language behavior, runtime behavior, or integration behavior.

The regression panel under `tests/00-regression-panel/` is the preferred place for compact tests that should remain continuously valid.

Where practical, tests should check expected semantic output, not merely whether execution ended with `CODE = 0`.

See [`../tests/README.md`](../tests/README.md).

---

### `suite/`

Readable BCPL demonstration programs.

The suite is deliberately different from the focused regression tests. Suite programs show how BCPL looks and behaves in complete, understandable examples such as factorial, quicksort, coroutines, parsers, data structures, and stream processing.

Use this area for examples that are useful to a human reader as well as useful for integration testing.

See [`../suite/README.md`](../suite/README.md).

---

### `tools/`

Host-side development tools.

These scripts generate jobs, submit JCL, extract reports, run compiler pipelines, choose the current ICINT baseline, and execute regression/demo suites.

Important examples include:

```text
compile-and-run
current-icint
run-regression-panel
run-demo-suite.sh
run-language-demos
submit-jcl.sh
job-summary
dump-report-for-job
```

The host tools are conveniences around the real MVS compilation and execution environment. They should not silently replace target-side behavior with a modern-host simulation.

See [`../tools/README.md`](../tools/README.md).

---

### `jcl/`

JCL used for development, experiments, and retained job examples.

JCL is part of the target environment, not incidental wrapper text. It describes how programs are assembled, link-edited, executed, and connected to MVS data sets and devices.

See [`../jcl/README.md`](../jcl/README.md).

---

### `docker/`

Container support for running Hercules and the MVS 3.8J TK5 environment.

The container is a convenient way to reproduce the target machine environment, but the guest operating system is still MVS. The container is not the target platform itself.

See [`../docker/README.md`](../docker/README.md).

---

### `docs/`

Orientation and project documentation.

This directory includes:

- BCPL historical and porting background;
- System/370 architecture briefings;
- MVS programming and execution topics;
- Hercules orientation;
- assembler/JCL/data representation briefings;
- this project map.

See [`README.md`](README.md).

---

## Why we stand up a real MVS instance

This project could appear, at first glance, to be a source-code translation exercise. It is not.

A BCPL port to MVS depends on behavior that belongs to the actual target operating system, assembler, linker, record formats, and execution environment.

Running MVS 3.8J under Hercules lets the project validate those behaviors directly.

### Assembler behavior is part of the target

System/370 assembler source depends on details such as:

- instruction encoding;
- base-register addressability;
- literal and constant representation;
- assembler diagnostics;
- object-module generation;
- macro behavior.

Using IFOX on MVS tests the same class of assembler environment that the reconstructed software is meant to live in.

### Link-editing behavior matters

Native BCPL support will eventually depend on MVS object and load modules, relocation, entry points, and linkage-editor conventions.

Those cannot be validated faithfully by pretending that a modern ELF linker is equivalent.

### MVS I/O is record-oriented

MVS data sets are not Unix byte streams.

Record formats, fixed-length padding, DDNAMEs, DCBs, access methods, and end-of-record behavior all matter. The library `READLINE` regression has already demonstrated why this distinction is observable.

### Character representation matters

MVS uses EBCDIC, while the preserved BCPL system has historical assumptions about character codes and transport representations.

Translation boundaries must therefore be tested on the real guest environment.

### JCL and JES are part of normal execution

Programs are assembled, linked, and run through MVS job control. DD statements determine data-set and stream connections. JES captures job output.

A usable MVS BCPL system must fit into that world.

### Runtime services matter

The eventual native runtime will need actual MVS services for storage, program loading, data sets, and process/runtime control.

Running under MVS makes those interfaces available for direct experiments instead of reconstruction by analogy.

---

## Layers to keep distinct

When diagnosing behavior, identify which layer owns it.

```text
BCPL language semantics
        |
BCPL compiler/runtime conventions
        |
System/370 architecture
        |
MVS 3.8J services and data formats
        |
TK5 configuration/customization
        |
Hercules emulation
        |
Docker/host tooling
```

A behavior observed in one layer should not automatically be attributed to another.

For example, fixed-record blank padding is an MVS/data-set property, not a BCPL string rule and not a Hercules peculiarity.

---

## Development conventions

### Preserve historical evidence

Historical source should remain as close as practical to the surviving material.

Do not modernize valid historical BCPL merely because a different spelling or structure would be more familiar today.

If the historical code fails because of a real host incompatibility, isolate and document that boundary.

---

### Keep ICINT close to the historical model

The reconstructed interpreter should follow the preserved BCPL/INTCODE model closely.

Deviate when the MVS host requires it, not simply because a different design is easier to invent.

Machine-dependent hosting requirements should be visible and documented.

---

### Make small changes and observe them

Preferred development rhythm:

```text
identify one requirement
        |
make one small change
        |
assemble / compile / run
        |
inspect the actual result
        |
add or update regression coverage
        |
continue
```

This is especially important for compiler and runtime work, where a defect can remain latent across many apparently successful programs.

---

### Treat regression tests as retained evidence

Once a behavior becomes part of the reconstructed contract, add a focused regression when practical.

Useful regressions include:

- exact semantic output;
- expected interpreter completion code;
- separate-module linkage;
- GLOBAL conventions;
- storage behavior;
- coroutine behavior;
- stream and record behavior;
- compiler intermediate-output behavior.

Use:

```sh
tools/run-regression-panel
```

The promoted ICINT baseline can be overridden explicitly when testing a candidate interpreter.

---

### Use `asm/CURRENT` for the validated interpreter

Runners should resolve the promoted interpreter through:

```sh
tools/current-icint
```

The reason is simple: a newly created numbered checkpoint may exist before it has passed the regression panel.

Promotion should conceptually follow:

```text
develop candidate
    |
run regression panel explicitly against candidate
    |
validate behavior
    |
update asm/CURRENT
```

---

### Keep GLOBAL assignments deliberate

BCPL modules rendezvous through numbered GLOBAL slots.

A collision can therefore create subtle cross-module failures.

Before assigning new project-local globals, consult:

[`../library/GLOBALS.md`](../library/GLOBALS.md)

Current reconstruction-local conventions distinguish historical/bootstrap globals, runtime globals, and general-purpose library globals.

---

### Prefer separate reusable library modules

General-purpose BCPL routines should normally live under `library/` rather than being copied into demonstrations.

Applications compile the modules they need:

```text
main program
    + library module
    + library module
```

This makes library contracts independently testable and keeps suite programs focused on the algorithm or feature being demonstrated.

---

### Do not use transient JES job numbers as durable evidence

JES job numbers are useful operationally but are not stable reconstruction identifiers.

When documenting an experiment, identify it using reconstructable material such as:

- source file;
- exact tool invocation;
- expected output;
- generated/intermediate artifact;
- committed test or documentation.

A statement like "JOB 332 proved this" is less useful than a retained regression or exact `tools/compile-and-run` command.

---

### Distinguish native MVS success from interpreted BCPL success

An MVS job step may return native `RC=0000` even when an interpreted BCPL program returns a nonzero execution code.

For INTCODE workloads, inspect the interpreter result:

```text
EXECUTION CYCLES = ..., CODE = ...
```

The host tooling knows how to extract this result, but documentation should remain clear about which completion status is being discussed.

---

### Keep documentation close to the code it explains

Each major repository area has its own README.

Use those READMEs for detailed local conventions and keep this project map at the orientation level.

When a development decision becomes stable and affects future contributors, document it rather than relying on conversation history.

---

## Typical contributor workflows

### Run one BCPL program

```sh
tools/compile-and-run --results \
    "$(tools/current-icint)" \
    path/to/program.bcpl
```

### Add library modules

```sh
tools/compile-and-run --results \
    "$(tools/current-icint)" \
    path/to/program.bcpl \
    +library/string-utils.bcpl \
    +library/integer-utils.bcpl
```

### Run the focused regression panel

```sh
tools/run-regression-panel
```

### Run one regression category

```sh
tools/run-regression-panel --category standard-library
```

### Test an unpromoted ICINT candidate

```sh
tools/run-regression-panel --icint asm/icintvNN.asm
```

### Run the demonstration suite

```sh
tools/run-demo-suite.sh
```

---

## Where to read next

| Area | Detailed documentation |
| --- | --- |
| Current project status | [`../README.md`](../README.md) |
| BCPL history and porting | [`BCPL-history-and-porting.md`](BCPL-history-and-porting.md) |
| Historical transport material | [`../richards-bcpltape/README.md`](../richards-bcpltape/README.md) |
| System/370 assembler reconstruction | [`../asm/README.md`](../asm/README.md) |
| INTCODE support | [`../intcode/README.md`](../intcode/README.md) |
| BCPL library/runtime modules | [`../library/README.md`](../library/README.md) |
| GLOBAL assignments | [`../library/GLOBALS.md`](../library/GLOBALS.md) |
| Tests and regression organization | [`../tests/README.md`](../tests/README.md) |
| Demonstration suite | [`../suite/README.md`](../suite/README.md) |
| Host-side tools | [`../tools/README.md`](../tools/README.md) |
| JCL | [`../jcl/README.md`](../jcl/README.md) |
| Hercules/TK5 container environment | [`../docker/README.md`](../docker/README.md) |
| System/370/MVS orientation briefings | [`README.md`](README.md) |

---

## Maintenance

This project map should change when the repository structure or development model changes.

It should remain higher-level than the component READMEs. Its purpose is to help a reader find the right layer, understand the project workflow, and know where to look next.
