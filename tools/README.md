# Host tools

The commands in this directory drive Hercules/TK5, submit and inspect MVS jobs, run the reconstructed interpreter, compile BCPL through the preserved kit compiler, exercise regressions, and manage the project's MVS data sets.

Unless noted otherwise, run them from the repository root.

The MR10 suite runners now live under `tools/mr10/`. Their former tools-root paths have been removed; use the commands listed below.

## Directory organization

- `tools/mvs/` — Hercules/TK5 operation, JES reporting, JCL submission and IFOX job generation.
- `tools/datasets/` — the `dspal` dispatcher and dataset-management modules.
- `tools/mr10/` — MR10 INTCODE interpreter, compiler, and short-named suite runners.
- `tools/native/` — Cambridge/native compilation, bootstrap source staging, native regressions, and resident-JCL build coordination.
- `tools/checks/` — reusable diagnostics and acceptance helpers (unchanged).

Only this README and the five subsystem directories remain at the tools root. The M3 manifest now defines 24 managed MR10, reserved CAMB, and NATIVE datasets. See the clean-room runbook for the full reconstruction order.

## Main commands

| Command | Purpose |
| --- | --- |
| `tools/mvs/start-tk5` | Start the Hercules/TK5 container. |
| `tools/mvs/shutdown-tk5` | Perform an orderly shutdown. |
| `tools/mvs/submit-jcl` | Submit a JCL deck through the JES socket reader. |
| `tools/mvs/job-summary` | Summarize steps and return codes for a JES job. |
| `tools/mvs/dump-report-for-job` | Extract the complete printer report for one job. |
| `tools/mvs/make-asm-job` | Generate IFOX assemble/link/run JCL from assembler source. |
| `tools/mr10/current-icint` | Print the promoted ICINT source selected by `mr10-kit-compiler/asm/CURRENT`. |
| `tools/mr10/run-intcode` | Assemble ICINT and run existing INTCODE modules. |
| `tools/mr10/compile-and-run` | Compile BCPL through SYN/TRN and CGI, then execute the result under ICINT. |
| `tools/native/prepare-bootstrap` | Regenerate disposable demoted Cambridge bootstrap sources and optional TRNILRG. |
| `tools/native/stage-bootstrap` | Stage regenerated source members to `NATIVE_SOURCE`. |
| `NATIVE_JCL(CAMBBLD)` | Authoritative resident compiler image build job in `native-compiler/jcl/`. |
| `NATIVE_JCL(BLIBBLD)` | Authoritative BLIB object build job in `native-compiler/jcl/`. |
| `tools/native/compile-mvs` | Compile one BCPL source using the persistent Cambridge compiler on MVS. |
| `tools/mr10/run-regression-panel` | Run exact-output durable interpreted regressions. |
| `tools/native/run-regression` | Run the native regression panel from a selected start through the current test. |
| `tools/mr10/run-demo-suite` | Run the 17 general BCPL demonstrations. |
| `tools/mr10/run-language-demos` | Run the focused BCPL language demonstrations. |
| `tools/datasets/dspal` | Manage the MVS-side `HERC02.BCPL.*` data sets. |

The old Cambridge-first bootstrap generator is no longer a current tool or workflow.

## MVS job tools

A typical assembler cycle is:

```sh
tools/mvs/make-asm-job asm/program.asm --output-dir jcl --listing heavy
tools/mvs/submit-jcl jcl/program-heavy.jcl
tools/mvs/job-summary JOB_NUMBER
tools/mvs/dump-report-for-job JOB_NUMBER
```

`submit-jcl` uses the Hercules socket reader, normally port 3505. The reporting tools read the configured printer output under `mvs-state/prt/`.

## Running INTCODE

Use `run-intcode` when the primary program is already INTCODE:

```sh
tools/mr10/run-intcode --results \
    "$(tools/mr10/current-icint)" \
    mr10-kit-compiler/tests/01-echo-test/echo-sysin.int \
    +mr10-kit-compiler/source/blibi.int \
    +mr10-kit-compiler/source/iclib.int
```

Additional modules are written as `+PATH` and are loaded in command-line order. `--sysin PATH` supplies card-image input to `SYSIN`.

## Compiling BCPL

`compile-and-run` is the normal interpreted compiler driver:

```sh
tools/mr10/compile-and-run --results \
    --save-ocode \
    --save-intcode \
    "$(tools/mr10/current-icint)" \
    mr10-kit-compiler/tests/03-compile-richards-factorial/richards-factorial-test.bcpl
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
tools/mr10/compile-and-run --results \
    "$(tools/mr10/current-icint)" \
    mr10-kit-compiler/tests/04-module-test/module-test-1.bcpl \
    +mr10-kit-compiler/tests/04-module-test/module-test-2.bcpl
```

Named host files can be exposed as MVS input DDs with repeated `--dd NAME=PATH` options. Host records that cannot be represented safely as card-image input are rejected rather than silently truncated.

Use each command's `--help` output for the full option set.

## Regression and demonstration runners

The durable regression panel is:

```sh
tools/mr10/run-regression-panel
```

It compares stable semantic output and completion codes against checked-in expectations. See `mr10-kit-compiler/tests/00-regression-panel/README.md`.

The broad readable demo suite is:

```sh
tools/mr10/run-demo-suite
```

It currently runs 17 programs. Focused language examples are run with:

```sh
tools/mr10/run-language-demos
```

## `dspal`

`dspal` treats Git as authoritative source and the MVS project libraries as reproducible deployed/build state.

Useful commands include:

```text
tools/datasets/dspal info
tools/datasets/dspal status [--probe]
tools/datasets/dspal stat [DATASET]
tools/datasets/dspal list
tools/datasets/dspal ls [DATASET]
tools/datasets/dspal cat DATASET MEMBER
tools/datasets/dspal get DATASET MEMBER FILE
tools/datasets/dspal put DATASET MEMBER FILE
tools/datasets/dspal rm DATASET MEMBER
tools/datasets/dspal compress DATASET
tools/datasets/dspal initbcpl
tools/datasets/dspal populate all
tools/datasets/dspal submit NATIVE_JCL CAMBBLD
tools/datasets/dspal purgebcpl
```

The normal deployment cycle is:

```sh
tools/datasets/dspal initbcpl
tools/datasets/dspal populate all
tools/datasets/dspal ls
```

`purgebcpl` deletes only the explicit managed data-set set and requires interactive confirmation unless `--yes` is supplied. The full create/populate/purge/recreate lifecycle has been exercised on TK5.

### Submitting stored JCL

Runnable members in the managed JCL PDS are stored as job bodies without a JOB statement. Submit one with:

```sh
tools/datasets/dspal submit JCL CAMBBLD
```

`dspal` generates a small authenticated `DSPALSUB` launcher. Its `IEBGENER` input is an authenticated payload JOB card followed by the requested PDS member, and its output is `SYSOUT=(A,INTRDR)`. The member therefore stays on MVS; it is not copied back through the host.

To wait for the submitted payload and print its summary:

```sh
tools/datasets/dspal submit NATIVE_JCL CAMBBLD --wait
```

To inspect the launcher without submitting it:

```sh
tools/datasets/dspal submit NATIVE_JCL CAMBBLD --show-jcl
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
tools/datasets/dspal populate SOURCE
tools/datasets/dspal populate ASM
tools/datasets/dspal populate INTCODE
```

Populate the stored build job and submit it through the internal-reader launcher:

```sh
tools/datasets/dspal populate JCL
tools/datasets/dspal submit JCL CAMBBLD --wait
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
python3 tools/native/build-cambridge --show-jcl
```

After inspecting the PDSes, compile a source through that resident image with:

```sh
python3 tools/native/compile-mvs path/to/program.bcpl
```

For the native regression panel, use:

```sh
bash native-compiler/regression/run-test-mvs.sh 24
```

The original `run-test.sh` remains the bootstrap-from-source path and is
unchanged by default. `mr10-kit-compiler/asm/CURRENT` remains on ICINT V17.

For a complete rebuild starting with an empty `workarea/`, including interpreter, MR10 suites, resident Cambridge image, runtime objects, and all native regressions, use [the single clean-room reconstruction runbook](../packaging/clean-room-mvs-reconstruction.md).
