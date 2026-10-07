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
| `tools/build-cambridge-mvs` | Build the persistent Cambridge compiler from dspal-populated MVS members. |
| `tools/cambridge-compile-mvs` | Compile one BCPL source using the persistent Cambridge compiler on MVS. |
| `tools/run-regression-panel` | Run exact-output durable interpreted regressions. |\n| `tools/run-native-regression` | Run the native regression panel from a selected start through the current test. |
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
tools/dspal submit JCL CAMBBLD
tools/dspal purgebcpl
```

The normal deployment cycle is:

```sh
tools/dspal initbcpl
tools/dspal populate all
tools/dspal ls
```

`purgebcpl` deletes only the explicit managed data-set set and requires interactive confirmation unless `--yes` is supplied. The full create/populate/purge/recreate lifecycle has been exercised on TK5.

### Submitting stored JCL

Runnable members in the managed JCL PDS are stored as job bodies without a JOB statement. Submit one with:

```sh
tools/dspal submit JCL CAMBBLD
```

`dspal` generates a small authenticated `DSPALSUB` launcher. Its `IEBGENER` input is an authenticated payload JOB card followed by the requested PDS member, and its output is `SYSOUT=(A,INTRDR)`. The member therefore stays on MVS; it is not copied back through the host.

To wait for the submitted payload and print its summary:

```sh
tools/dspal submit JCL CAMBBLD --wait
```

To inspect the launcher without submitting it:

```sh
tools/dspal submit JCL CAMBBLD --show-jcl
```

Batch authentication comes from `config/dspal.local.yaml`, which is gitignored. `--show-jcl` redacts both launcher and payload passwords.

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


## Persistent Cambridge compiler on MVS

The native-code regression work has a faster parallel compile path. The
Cambridge compiler is still INTCODE executed by ICINT V19; it is not yet a
native MVS compiler.

Host-to-MVS positioning is owned by `dspal`. First generate the host-side
bootstrap derivatives:

```sh
python3 native-compiler/bootstrap-cambridge/make-demoted.py
bash native-compiler/bootstrap-cambridge/build-mr10-trni-large-names.sh
```

Then populate the managed MVS libraries:

```sh
tools/dspal populate SOURCE
tools/dspal populate ASM
tools/dspal populate INTCODE
```

Populate the stored build job and submit it through the internal-reader launcher:

```sh
tools/dspal populate JCL
tools/dspal submit JCL CAMBBLD --wait
```

The checked-in `CAMBBLD` member is a job body with no JOB card; `dspal submit`
supplies the authenticated payload JOB card from the local dspal configuration.

The build leaves:

```text
HERC02.BCPL.LOAD(ICINT19)
HERC02.BCPL.INTCODE(BCPL)
HERC02.BCPL.INTCODE(SYN)
HERC02.BCPL.INTCODE(LEX)
HERC02.BCPL.INTCODE(TRNA)
HERC02.BCPL.INTCODE(TRNB)
HERC02.BCPL.INTCODE(CGA..CGE)
HERC02.BCPL.INTCODE(BOOTHOST)
HERC02.BCPL.INTCODE(CAMBCOMP)
```

`CAMBCOMP` is the packed ICINT-runnable compiler image. The individual
members are retained for diagnosis and inspection.

Inspect the complete generated build JCL without submitting it:

```sh
python3 tools/build-cambridge-mvs --show-jcl
```

After inspecting the PDSes, compile a source through that resident image with:

```sh
python3 tools/cambridge-compile-mvs path/to/program.bcpl
```

For the native regression panel, use:

```sh
bash native-compiler/regression/run-test-mvs.sh 24
```

The original `run-test.sh` remains the bootstrap-from-source path and is
unchanged by default. `config/CURRENT` remains on ICINT V17.
