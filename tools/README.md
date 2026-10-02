# BCPL-for-MVS Host Tools

This directory contains host-side tools used to operate the project's
Hercules/TK5 MVS system and to support development and testing of the
BCPL implementation.

These commands run on the host, not under MVS.

Unless otherwise noted, examples assume that they are run from the
repository root.

## Tools

### `start-tk5`

Starts the Hercules/TK5 MVS container.

```text
tools/start-tk5
tools/start-tk5 --detached
```

The default is attached operation, which leaves the Hercules/MVS event
stream visible in the terminal. `--detached` starts the container in the
background.

The command uses `docker/compose.yaml`.

### `shutdown-tk5`

Stops the MVS container, allowing up to 180 seconds for shutdown.

```text
tools/shutdown-tk5
```

Use this rather than an abrupt container termination when shutting down
the development system normally.

### `make-asm-job`

Generates a self-contained MVS JCL deck that assembles an IFOX assembler
source file, link-edits the resulting object module, and executes it.

```text
tools/make-asm-job asm/program.asm --output-dir jcl
```

Three listing levels are available:

```text
--listing light
--listing medium
--listing heavy
```

`light` is the default and suppresses most assembler and linkage-editor
listing material. `medium` adds an assembler listing, short cross
reference, and linkage map. `heavy` requests the detailed diagnostic
material useful during assembler development.

The program entry point is normally inferred from the operand of the
assembler `END` statement. It can be specified explicitly with
`--entry`.

An MVS EXEC parameter can be supplied with `--parm`.

Use `tools/make-asm-job --help` for the complete interface.

`make-asm-job.py` contains the underlying Python implementation and is
also used as a module by other project tools. For normal command-line
use, use `make-asm-job`.

### `submit-jcl`

Submits a JCL deck to the running TK5 system through the Hercules socket
card reader.

```text
tools/submit-jcl jcl/program-light.jcl
```

The repository's reader is expected on TCP port 3505. The command watches
the main printer output for the JES start message and prints the assigned
JES job number, for example `JOB 42`. This job number can then be passed
to `job-summary` or `dump-report-for-job`.

### `job-summary`

Prints a compact summary of an MVS job from the TK5 printer output.

```text
tools/job-summary 42
```

The report includes the executed steps and return codes and, when
available, assembler status and resource information. By default, return
codes through 4 are considered successful.

Useful options include:

```text
tools/job-summary 42 --verbose
tools/job-summary 42 --max-rc 0
```

The normal printer source is `mvs-state/prt/prt00e.txt`.

### `dump-report-for-job`

Extracts the complete printer report belonging to one JES job.

```text
tools/dump-report-for-job 42
```

This is useful when `job-summary` identifies a problem and the complete
assembler, linkage-editor, execution, or diagnostic output is needed.
Printer form feeds are converted so that the resulting report is
convenient to inspect in a normal terminal or redirect to a file.

### `run-intcode`

Provides the higher-level development path for running INTCODE under
the project's ICINT implementation.

Typical use:

```text
tools/run-intcode asm/icintv13.asm intcode/factorial.int
```

To include the standard INTCODE runtime components:

```text
tools/run-intcode --runtime \
    asm/icintv13.asm intcode/factorial.int
```

To wait for execution and print the ICINT results:

```text
tools/run-intcode --runtime --results \
    asm/icintv13.asm intcode/factorial.int
```

To supply standard input to the running INTCODE/BCPL program, use
`--sysin` with an ASCII host text file:

```text
tools/run-intcode --runtime --results \
    --sysin tests/program-input.txt \
    asm/icintv13.asm intcode/program.int
```

Each line in the host file becomes one MVS `SYSIN` card-image record in
the generated JCL. Blank lines are preserved as blank records. Records
may contain at most 80 characters; `run-intcode` rejects a longer record
rather than silently truncating it. A line consisting exactly of `/*` is
also rejected because that sequence terminates JCL in-stream data.

If `--sysin` is not specified, the generated GO step contains **no
`SYSIN` DD statement**. Thus absence of the option means that no SYSIN
stream is supplied to ICINT; it is not represented by `DD DUMMY`.

The tool constructs an assemble/link/run job for ICINT, supplies the
requested INTCODE input, submits the job through the TK5 socket reader,
and obtains its status and results from the Hercules printer stream.

When `--runtime` is specified, the `INTIN` stream is formed in this order:

```text
program
BLIBI
ICLIB
```

The standard runtime components are located under `intcode/`. `--library`
and `--wrapper` override the default runtime files and imply `--runtime`.

Other useful options are:

```text
--results                 wait for completion and print ICINT output
--jcl PATH                choose the generated JCL path
--job-name NAME           override the generated MVS job name
--listing light|medium|heavy
--reader-host HOST        Hercules socket-reader host
--reader-port PORT        Hercules socket-reader port
--timeout SECONDS         JES/results wait timeout
--poll SECONDS            printer polling interval
```

Use `tools/run-intcode --help` for the complete interface.

## Typical assembler workflow

For ordinary assembler development, the tools fit together as follows:

```text
tools/start-tk5 --detached

tools/make-asm-job asm/program.asm \
    --output-dir jcl \
    --listing heavy

tools/submit-jcl jcl/program-heavy.jcl

tools/job-summary JOB_NUMBER

tools/dump-report-for-job JOB_NUMBER
```

Edit the assembler source, regenerate the JCL deck, and repeat.

## Typical INTCODE workflow

For ICINT development and INTCODE testing, `run-intcode` combines most
of the individual steps:

```text
tools/run-intcode --runtime --results \
    asm/icintv13.asm \
    intcode/program.int
```

For a program requiring input:

```text
tools/run-intcode --runtime --results \
    --sysin tests/program-input.txt \
    asm/icintv13.asm \
    intcode/program.int
```

The lower-level tools remain useful when the generated JCL or complete
MVS job output needs to be examined directly.

## Host requirements

The tools assume the repository's Hercules/TK5 environment and directory
layout.

Depending on the command, host requirements include Python 3, Bash,
Docker with Docker Compose, `nc` (netcat), and standard Unix utilities
such as `awk`, `grep`, `tail`, and `timeout`.

The running MVS system is expected to use the repository's configured
Hercules socket reader on port 3505 and printer output under
`mvs-state/prt/`.
