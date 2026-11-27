# Host tools

The commands in this directory drive Hercules/TK5, submit and inspect MVS jobs, run the reconstructed interpreter, compile BCPL through the preserved kit compiler, exercise regressions, and manage the project's MVS data sets.

Unless noted otherwise, run them from the repository root.

The MR10 suite runners now live under `tools/mr10/`. Their former tools-root paths have been removed; use the commands listed below.

## Directory organization

- `tools/mvs/` — Hercules/TK5 operation, JES reporting, JCL submission and IFOX job generation.
- `tools/datasets/` — the `dspal` dispatcher and dataset-management modules.
- `tools/mr10/` — MR10 INTCODE interpreter, compiler, and short-named suite runners.
- `tools/bootstrap/` — Cambridge/native compilation, bootstrap source staging, native regressions, and resident-JCL build coordination.
- `tools/checks/` — reusable static checks, test-only QSAM output probes, job/RC auditing, and final-run freshness evidence.
- `tools/reconstruction/` — clean-room reconstruction tooling; see its [README](reconstruction/README.md) and the canonical runbook.
- `tools/distribution/` — [manifest validation and release evidence tools](distribution/README.md); not a general-purpose release producer.

See [the managed dataset configuration](../config/dspal.yaml) and [clean-room runbook](../docs/Rebuild-BCPL-for-MVS-from-source.md) for the current development inventory. The published RC4 release is documented separately in [distribution](../packaging/distribution/README.md).

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
| `tools/bootstrap/prepare-bootstrap` | Regenerate disposable demoted Cambridge bootstrap sources and optional TRNILRG. |
| `BOOT_JCL(CAMBBLD)` | Authoritative resident compiler image build job in `bootstrap-toolchain/jcl/`. |
| `BOOT_JCL(BLIBBLD)` | Authoritative BLIB object build job in `bootstrap-toolchain/jcl/`. |
| `tools/bootstrap/compile-mvs` | Compile one BCPL source using the persistent Cambridge compiler on MVS. |
| `tools/mr10/run-regression-panel` | Run exact-output durable interpreted regressions. |
| `tools/bootstrap/run-regression` | Run the native regression panel from a selected start through the current test. |
| `tools/mr10/run-demo-suite` | Run the 17 general BCPL demonstrations. |
| `tools/mr10/run-language-demos` | Run the focused BCPL language demonstrations. |
| `tools/datasets/dspal` | Manage the MVS-side `HERC02.BCPL.*` data sets. |
| `tools/reconstruction/run --list` | Display the reconstruction stage sequence; consult the canonical runbook for current execution policy. |

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
tools/datasets/dspal submit BOOT_JCL CAMBBLD
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
tools/datasets/dspal submit BOOT_JCL CAMBBLD
```

`dspal` generates a small authenticated `DSPALSUB` launcher. Its `IEBGENER` input is an authenticated payload JOB card followed by the requested PDS member, and its output is `SYSOUT=(A,INTRDR)`. The member therefore stays on MVS; it is not copied back through the host.

To wait for the submitted payload and print its summary:

```sh
tools/datasets/dspal submit BOOT_JCL CAMBBLD --wait
```

To inspect the launcher without submitting it:

```sh
tools/datasets/dspal submit BOOT_JCL CAMBBLD --show-jcl
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

The development Cambridge Compiler runs as INTCODE under ICINT19 (the promoted interpreter selected by [CURRENT](../mr10-kit-compiler/asm/CURRENT)); it produces native code but is not itself native-running. Use the [canonical clean-room reconstruction runbook](../docs/Rebuild-BCPL-for-MVS-from-source.md) for current managed dataset aliases, build order and regression commands. Do not use older unqualified dataset aliases or old interpreter-version instructions.

## Distribution

The release milestone is closed. [RC4 installation instructions](../packaging/distribution/publication/RC4-README.md) are the recipient-facing procedure. The [distribution tools](distribution/README.md) contain the consolidated JCL and MVS verification helpers. Retired candidate-specific production/recipient orchestration is preserved in Git history; source-preparation and historical evidence tools remain under [packaging/distribution](../packaging/distribution/README.md), not as authorization to replay consumed operations. See the [post-release audit](../packaging/distribution/post-release-audit-20261124.md) for the retirement policy.

[Previous host-tool README](https://github.com/cbmira01/BCPL-for-MVS/blob/9f382203fcd6a5424cd916f304e3210c0f650212/tools/README.md) is preserved in Git history.
