# MVS JCL Decks

This directory contains retained JCL used to build, run, test, and inspect the
BCPL-for-MVS development system under MVS 3.8J.

The project now generates most day-to-day assembler, ICINT, and compiler jobs
from host-side tools. Files kept here are therefore either durable examples,
important historical acceptance decks, or small system-inspection jobs.

## Files

| File | Purpose |
| --- | --- |
| [`hello-world-heavy.jcl`](hello-world-heavy.jcl) | Assemble, link-edit, and run `asm/hello-world.asm` with the heavy listing profile. Useful as a compact complete IFOX toolchain example. |
| [`icintv12-honors-thesis.jcl`](icintv12-honors-thesis.jcl) | Self-contained V12 ICINT acceptance job for the honors-thesis/factorial workload. Preserves the job used to validate the V12 word-addressed BCPL representation. |
| [`icintv13-honors-thesis.jcl`](icintv13-honors-thesis.jcl) | V13 ICINT regression job using the same factorial acceptance workload. |
| [`icintv13-mapstore.jcl`](icintv13-mapstore.jcl) | V13 diagnostic job for the reconstructed MAPSTORE path and deliberately failing INTCODE workload. |
| [`dump-jes2-parameters.jcl`](dump-jes2-parameters.jcl) | Uses `IEBPTPCH` to inspect selected JES2 parameter material. |
| [`list-parmlib-members.jcl`](list-parmlib-members.jcl) | Uses `IEHLIST` to list members of `SYS1.PARMLIB` on the TK5 system residence volume. |

## Generated assembler jobs

[`tools/make-asm-job`](../tools/make-asm-job) creates self-contained IFOX
assemble/link/run decks.

```text
tools/make-asm-job asm/hello-world.asm \
    --output-dir jcl \
    --listing heavy
```

Generated decks inline the assembler source. Regenerate them after source
changes rather than treating the JCL as the primary source.

## ICINT and compiler jobs

For direct INTCODE execution, use [`tools/run-intcode`](../tools/run-intcode).
For BCPL source compilation through the preserved interpreted compiler, use
[`tools/compile-and-run`](../tools/compile-and-run).

Those tools generate working decks under `workarea/` by default. In particular,
`compile-and-run` now emits a prominent job map and phase banners so long JES
printouts can be navigated easily. It supports single- and multi-module BCPL
compilation, optional saved OCODE/INTCODE intermediates, and explicit listing
profiles.

The older `icint*.jcl` files retained here are therefore historical acceptance
artifacts, not templates that must be kept synchronized with the current V15
implementation.

## Submitting and inspecting a deck

With TK5 running:

```text
tools/submit-jcl jcl/job.jcl
```

The command reports the assigned JES job number. Inspect it with:

```text
tools/job-summary JOB_NUMBER
tools/dump-report-for-job JOB_NUMBER
```

The complete report is often the most useful artifact when diagnosing
assembler addressability, linkage-editor behavior, DD/data-set handling, or
compiler-pipeline failures.

## Future JCL work

As the reconstruction moves toward native code generation and MVS-resident
operation, this directory is expected to gain a few deliberately annotated job
streams rather than a large collection of transient generated decks. Important
future candidates include:

- DASD-resident compiler and data-handling examples;
- native OCODE-to-System/370 code-generation jobs; and
- a reproducible "compile the compiler and compare the results" bootstrap job.

See [`asm/README.md`](../asm/README.md),
[`intcode/README.md`](../intcode/README.md),
[`tests/README.md`](../tests/README.md), and
[`tools/README.md`](../tools/README.md) for the corresponding source,
runtime, tests, and host tooling.

## Maintenance

Keep only JCL that is useful as a durable example, acceptance record, bootstrap
artifact, or system-inspection tool. Temporary generated decks belong in
`workarea/`.
