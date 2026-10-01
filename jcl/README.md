# MVS JCL Decks

This directory contains JCL used to build, run, test, and inspect the
BCPL-for-MVS development system under MVS 3.8J.

Some decks are generated development artifacts that capture a particular
assembler or ICINT test configuration. Others are small hand-written
system-inspection jobs used while investigating the TK5/MVS environment.

## Files

| File | Purpose |
| --- | --- |
| [`hello-world-heavy.jcl`](hello-world-heavy.jcl) | Assemble, link-edit, and run the `hello-world.asm` example with the heavy diagnostic/listing profile. Useful as a complete IFOX toolchain example. |
| [`icintv12-honors-thesis.jcl`](icintv12-honors-thesis.jcl) | Self-contained V12 ICINT acceptance job for the honors-thesis/factorial workload. Preserves the JCL used to validate the V12 word-addressed representation. |
| [`icintv13-honors-thesis.jcl`](icintv13-honors-thesis.jcl) | V13 ICINT job using the honors-thesis/factorial acceptance workload, retained for regression testing against the validated V12 behavior. |
| [`icintv13-mapstore.jcl`](icintv13-mapstore.jcl) | V13 diagnostic job for the reconstructed MAPSTORE facility and its deliberately failing INTCODE workload. |
| [`dump-jes2-parameters.jcl`](dump-jes2-parameters.jcl) | Uses `IEBPTPCH` to print selected members of `SYS1.JES2PARM` for inspection of the TK5 JES2 configuration. |
| [`list-parmlib-members.jcl`](list-parmlib-members.jcl) | Uses `IEHLIST` to list the members of `SYS1.PARMLIB` on the TK5 system residence volume. |

## Generated assembler jobs

The host-side [`tools/make-asm-job`](../tools/make-asm-job) command
creates self-contained IFOX assemble/link/run decks in this directory
when `jcl` is supplied as its output directory.

For example:

```text
tools/make-asm-job asm/hello-world.asm \
    --output-dir jcl \
    --listing heavy
```

Generated decks inline the assembler source. If the source changes, the
corresponding generated JCL should be regenerated rather than edited as
though it were the primary source.

The listing suffix records the requested diagnostic profile, such as
`-light`, `-medium`, or `-heavy`.

## ICINT jobs

The larger `icint*.jcl` files are self-contained development and
acceptance jobs. They combine the ICINT assembler source with the
INTCODE input needed for a particular test. Keeping selected known-good
decks in the repository provides a reproducible record of important
interpreter checkpoints.

For day-to-day ICINT development, [`tools/run-intcode`](../tools/run-intcode)
is normally more convenient than maintaining a JCL deck by hand. It can
construct and submit the required job directly from an ICINT assembler
source and an INTCODE workload.

See [`asm/README.md`](../asm/README.md),
[`intcode/README.md`](../intcode/README.md), and
[`tests/README.md`](../tests/README.md) for the corresponding source,
runtime, and test material.

## Submitting a deck

With the TK5 system running, submit a JCL file through the Hercules
socket reader with:

```text
tools/submit-jcl jcl/job.jcl
```

The command reports the assigned JES job number. That number can then be
used with:

```text
tools/job-summary JOB_NUMBER
tools/dump-report-for-job JOB_NUMBER
```

See [`tools/README.md`](../tools/README.md) for details.

## Maintenance

This directory may contain both durable checkpoint decks and temporary
or investigative JCL. When a deck represents an important reproducible
project checkpoint or has a distinct system-administration purpose, add
or update its description here.
