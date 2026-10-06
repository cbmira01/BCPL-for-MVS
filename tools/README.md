# Host tools

The commands in this directory drive Hercules/TK5, submit and inspect MVS jobs, run the reconstructed interpreter, compile BCPL through the preserved kit compiler, exercise regressions, and manage the project's MVS data sets.

Unless noted otherwise, run them from the repository root.

## Main commands

| Command | Purpose |
| --- | --- |
| `tools/start-tk5` | Start the Hercules/TK5 container. |
| `tools/shutdown-tk5` | Perform an orderly shutdown. |
| `tools/submit-jcl` | Submit a JCL deck through the JES socket reader. |
| `tools/job-summary` | Summarize steps and return codes for a JES job. |
| `tools/dump-report-for-job` | Extract the complete printer report for one job. |
| `tools/make-asm-job` | Generate IFOX assemble/link/run JCL from assembler source. |
| `tools/current-icint` | Print the promoted ICINT source selected by `config/CURRENT`. |
| `tools/run-intcode` | Assemble ICINT and run existing INTCODE modules. |
| `tools/compile-and-run` | Compile BCPL through SYN/TRN and CGI, then execute the result under ICINT. |
| `tools/run-regression-panel` | Run exact-output durable regressions. |
| `tools/run-demo-suite.sh` | Run the 17 general BCPL demonstrations. |
| `tools/run-language-demos` | Run the focused BCPL language demonstrations. |
| `tools/dspal` | Manage the MVS-side `HERC02.BCPL.*` data sets. |

The old Cambridge-first bootstrap generator is no longer a current tool or workflow.

## MVS job tools

A typical assembler cycle is:

```sh
tools/make-asm-job asm/program.asm --output-dir jcl --listing heavy
tools/submit-jcl jcl/program-heavy.jcl
tools/job-summary JOB_NUMBER
tools/dump-report-for-job JOB_NUMBER
```

`submit-jcl` uses the Hercules socket reader, normally port 3505. The reporting tools read the configured printer output under `mvs-state/prt/`.

## Running INTCODE

Use `run-intcode` when the primary program is already INTCODE:

```sh
tools/run-intcode --results \
    "$(tools/current-icint)" \
    tests/01-echo-test/echo-sysin.int \
    +intcode/blibi.int \
    +intcode/iclib.int
```

Additional modules are written as `+PATH` and are loaded in command-line order. `--sysin PATH` supplies card-image input to `SYSIN`.

## Compiling BCPL

`compile-and-run` is the normal interpreted compiler driver:

```sh
tools/compile-and-run --results \
    --save-ocode \
    --save-intcode \
    "$(tools/current-icint)" \
    tests/03-compile-richards-factorial/richards-factorial-test.bcpl
```

The MVS job runs:

```text
BCPL source
   -> SYNI + TRNI
   -> OCODE
   -> CGI
   -> INTCODE
   -> ICINT + BLIBI + ICLIB
```

`--save-ocode` and `--save-intcode` recover the compiler intermediates to `workarea/`.

Separate compilation units use the same explicit `+PATH` convention:

```sh
tools/compile-and-run --results \
    "$(tools/current-icint)" \
    tests/04-module-test/module-test-1.bcpl \
    +tests/04-module-test/module-test-2.bcpl
```

Named host files can be exposed as MVS input DDs with repeated `--dd NAME=PATH` options. Host records that cannot be represented safely as card-image input are rejected rather than silently truncated.

Use each command's `--help` output for the full option set.

## Regression and demonstration runners

The durable regression panel is:

```sh
tools/run-regression-panel
```

It compares stable semantic output and completion codes against checked-in expectations. See `tests/00-regression-panel/README.md`.

The broad readable demo suite is:

```sh
tools/run-demo-suite.sh
```

It currently runs 17 programs. Focused language examples are run with:

```sh
tools/run-language-demos
```

## `dspal`

`dspal` treats Git as authoritative source and the MVS project libraries as reproducible deployed/build state.

Useful commands include:

```text
tools/dspal info
tools/dspal status [--probe]
tools/dspal stat [DATASET]
tools/dspal list
tools/dspal ls [DATASET]
tools/dspal cat DATASET MEMBER
tools/dspal get DATASET MEMBER FILE
tools/dspal put DATASET MEMBER FILE
tools/dspal rm DATASET MEMBER
tools/dspal compress DATASET
tools/dspal initbcpl
tools/dspal populate all
tools/dspal purgebcpl
```

The normal deployment cycle is:

```sh
tools/dspal initbcpl
tools/dspal populate all
tools/dspal ls
```

`purgebcpl` deletes only the explicit managed data-set set and requires interactive confirmation unless `--yes` is supplied. The full create/populate/purge/recreate lifecycle has been exercised on TK5.

Batch authentication comes from `config/dspal.local.yaml`, which is gitignored. `--show-jcl` redacts the password.

See `config/README.md` and `packaging/README.md` for the deployment model.

## Host requirements

The tools assume Python 3, Bash, Docker with Docker Compose, `nc`/netcat, and ordinary Unix utilities. They also assume the repository's Hercules/TK5 directory layout and configured JES reader/printer endpoints.

## Durable pre-flight checks

Reusable source validators live under `tools/checks/`.  Before creating an
ad-hoc checker in a temporary environment, look there first; if a scratch
validator proves useful more than once, promote it there so later work can
reuse and improve it.

The current assembler checker is:

```sh
python3 tools/checks/check-asm-source.py asm/program.asm
```

It checks ASCII-only source, tabs, trailing whitespace, and text beyond column
71.  See `tools/checks/README.md` for the standing convention.
