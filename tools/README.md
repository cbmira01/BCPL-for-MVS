# BCPL-for-MVS Host Tools

This directory contains host-side tools used to operate the project's
Hercules/TK5 MVS system and to support assembler, ICINT, and BCPL compiler
development.

These commands run on the host, not under MVS. Unless otherwise noted,
examples assume they are run from the repository root.

## Tool overview

| Tool | Purpose |
| --- | --- |
| `start-tk5` | Start the Hercules/TK5 MVS environment. |
| `shutdown-tk5` | Perform an orderly MVS/Hercules shutdown. |
| `make-asm-job` | Generate a self-contained IFOX assemble/link/run JCL deck. |
| `submit-jcl` | Submit a JCL deck through the Hercules socket reader and report the JES job number. |
| `job-summary` | Summarize executed steps and return codes from printer output. |
| `dump-report-for-job` | Extract the complete printer report for one JES job. |
| `run-intcode` | Assemble/link ICINT and run one or more already-existing INTCODE modules. |
| `compile-and-run` | Compile one or more BCPL source modules through the interpreted compiler pipeline and execute the generated INTCODE. |
| `run-demo-suite.sh` | Run the complete BCPL demonstration suite through the current ICINT/compiler pipeline. |

## Starting and stopping MVS

Start attached to the Hercules/MVS event stream:

```text
tools/start-tk5
```

or start detached:

```text
tools/start-tk5 --detached
```

For normal shutdown:

```text
tools/shutdown-tk5
```

The container and persistent-state layout are documented in
[`docker/README.md`](../docker/README.md).

## `make-asm-job`

Generates a self-contained MVS JCL deck that assembles an IFOX assembler
source, link-edits the resulting object module, and executes it.

```text
tools/make-asm-job asm/program.asm --output-dir jcl
```

Listing profiles are:

```text
--listing light
--listing medium
--listing heavy
```

`light` is the default. `medium` adds an assembler listing, short cross
reference, and linkage map. `heavy` requests the detailed material useful
when inspecting assembler and linkage-editor behavior.

The program entry point is normally inferred from the assembler `END`
operand; `--entry` can override it. An MVS EXEC parameter can be supplied
with `--parm`.

`make-asm-job.py` is the underlying Python implementation and is imported by
other tools. For normal command-line use, invoke `make-asm-job`.

## `submit-jcl`

Submits a deck through the Hercules socket card reader, normally TCP port
3505:

```text
tools/submit-jcl jcl/program-light.jcl
```

The command watches the main printer output for the JES start record and
prints the assigned job number, for example:

```text
JOB 42
```

That number can be passed directly to the reporting tools.

## `job-summary`

Prints a compact summary of an MVS job:

```text
tools/job-summary 42
```

Useful options include:

```text
tools/job-summary 42 --verbose
tools/job-summary 42 --max-rc 0
```

The normal printer source is `mvs-state/prt/prt00e.txt`.

## `dump-report-for-job`

Extracts the complete printer report belonging to one JES job:

```text
tools/dump-report-for-job 42
```

This is the normal follow-up when a job summary shows a failure or when the
assembler listing, link map, generated JCL banners, data-set disposition, or
program output needs close inspection.

## `run-intcode`

`run-intcode` is the direct ICINT/INTCODE driver. Use it when the program or
component being tested is already INTCODE.

```text
tools/run-intcode --results \
    asm/icintv15.asm \
    tests/01-echo-test/echo-sysin.int \
    +intcode/blibi.int \
    +intcode/iclib.int
```

The first INTCODE path is the primary module. Every additional module is
written explicitly as `+PATH` and is concatenated to `INTIN` in command-line
order:

```text
primary
+module 1
+module 2
...
```

Runtime components are ordinary modules. Earlier special-purpose runtime,
library, or wrapper switches are not the current interface.

### SYSIN input

A host text file can be supplied as MVS `SYSIN`:

```text
tools/run-intcode --results \
    --sysin tests/01-echo-test/best-of-times.txt \
    asm/icintv15.asm \
    tests/01-echo-test/echo-sysin.int \
    +intcode/blibi.int \
    +intcode/iclib.int
```

Each host line becomes one 80-column-or-shorter card-image record. Blank lines
are preserved. A record longer than 80 characters, or a line consisting
exactly of `/*`, is rejected rather than silently changed.

If `--sysin` is omitted, the generated execution step has no `SYSIN` DD. This
is intentionally different from `DD DUMMY`: absence of the DD allows ICINT's
stream-discovery semantics to distinguish an unavailable stream.

Other useful options include:

```text
--results
--jcl PATH
--job-name NAME
--listing light|medium|heavy
--reader-host HOST
--reader-port PORT
--timeout SECONDS
--poll SECONDS
```

Use `tools/run-intcode --help` for the complete interface.

## `compile-and-run`

`compile-and-run` is the normal driver for the interpreted BCPL compiler
pipeline. It deliberately remains separate from `run-intcode` so direct
INTCODE testing and compiler-phase work do not become entangled.

For one BCPL source module:

```text
tools/compile-and-run \
    --results \
    --save-ocode \
    --save-intcode \
    --listing heavy \
    asm/icintv15.asm \
    tests/03-compile-richards-factorial/richards-factorial-test.bcpl
```

The generated MVS job assembles and links ICINT once, stages the preserved
compiler/runtime components, and runs this pipeline:

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
    |
    v
ICINT + BLIBI + ICLIB
```

The generated JCL contains a job map and conspicuous phase banners so long
printer reports can be navigated by eye.

### Saved intermediates

`--save-ocode` recovers each compiler unit's OCODE to:

```text
workarea/<module>.ocode
```

`--save-intcode` recovers generated INTCODE to:

```text
workarea/<module>.intcode
```

The save steps copy temporary MVS data sets after the compiler phases; they do
not alter the OCODE/INTCODE streams used by the pipeline itself.

### Separate BCPL compilation units

Additional BCPL sources use the same explicit `+PATH` convention as
`run-intcode`:

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

Each BCPL source is compiled independently through SYN/TRN and CGI. Only the
generated INTCODE modules are concatenated for the final ICINT load/run, in
command-line order. The `04-module-test` regression demonstrates cross-module
BCPL `GLOBAL`-vector linkage.

### Named input DDs

Repeatable `--dd NAME=PATH` options make ASCII host text files available to
each BCPL compile step under ordinary MVS DDNAMEs:

```text
tools/compile-and-run \
    --results \
    --dd EXTRA=tests/05-named-dd/extra.bcpl \
    asm/icintv15.asm \
    tests/05-named-dd/main.bcpl
```

The example above emits an in-stream `//EXTRA DD *` on the compiler step.
Historical BCPL code can then obtain that stream through `FINDINPUT("EXTRA")`;
the compiler's `GET "EXTRA"` facility uses that same path. The
`05-named-dd` regression test uses `GET` to include a small manifest from the
host file.

`--dd` may be repeated for multiple names. DDNAMEs are uppercased and must be
valid one-to-eight-character MVS names. Names already owned by the generated
compile step, such as `SYSIN`, `OCODE`, `INTIN`, and `SYSPRINT`, are rejected.
Duplicate names are also rejected.

Named input files use the same conservative card-image rules as other host
text inputs: ASCII, nonempty, no record longer than 80 characters, and no
record consisting exactly of `/*`. The named DDs are supplied to every
separate BCPL compile step; CGI and final RUN steps do not receive them.

Current compiler options include:

```text
--dd NAME=PATH
--results
--save-ocode
--save-intcode
--jcl PATH
--job-name NAME
--listing light|medium|heavy
--reader-host HOST
--reader-port PORT
--timeout SECONDS
--poll SECONDS
```

Use `tools/compile-and-run --help` for the current interface.

## `run-demo-suite.sh`

`run-demo-suite.sh` is the convenient regression driver for the example
programs under `suite/`. It runs each demo through `compile-and-run` using the
current ICINT V17 interpreter and reports each workload as `PASS` or `FAIL`.

Run the complete suite with:

```text
tools/run-demo-suite.sh
```

The script determines its own location, changes to the repository root, and
therefore does not depend on the caller's current working directory.

The current suite contains 15 demonstrations covering recursion, arithmetic,
iteration, vectors, sorting and searching, linked structures, parsing,
character and string handling, and stream I/O. A normal successful run ends
with:

```text
================================================================
SUITE COMPLETE
================================================================
All 15 demos passed.
```

A `PASS` means the BCPL source compiled through the interpreted compiler
pipeline, CGI generated INTCODE, the resulting program executed under ICINT,
and the execution completed with code zero. The demonstrations are also
intended to have human-readable results so semantic errors remain visible in
the printed output; the suite runner itself should not be treated as a
substitute for checking or adding explicit expected-output regressions when a
specific language or runtime behavior matters.

The suite currently provides a useful broad regression checkpoint for ICINT
and compiler-host changes. Focused behavior tests remain under `tests/` and
should be preferred when isolating a particular compiler, interpreter,
stream, storage, linkage, or language-semantic issue.

## Typical workflows

Assembler development:

```text
tools/make-asm-job asm/program.asm --output-dir jcl --listing heavy
tools/submit-jcl jcl/program-heavy.jcl
tools/job-summary JOB_NUMBER
tools/dump-report-for-job JOB_NUMBER
```

Direct INTCODE execution:

```text
tools/run-intcode --results \
    asm/icintv15.asm \
    program.intcode \
    +intcode/blibi.int \
    +intcode/iclib.int
```

BCPL source compilation and execution:

```text
tools/compile-and-run --results \
    asm/icintv15.asm \
    program.bcpl
```

Complete demo regression suite:

```text
tools/run-demo-suite.sh
```

The lower-level tools remain useful whenever generated JCL or complete MVS
job output needs to be examined directly.

## Host requirements

The tools assume the repository's Hercules/TK5 environment and directory
layout. Depending on the command, host requirements include Python 3, Bash,
Docker with Docker Compose, `nc` (netcat), and standard Unix utilities.

The running system is expected to use the configured socket reader on port
3505 and printer output under `mvs-state/prt/`.
