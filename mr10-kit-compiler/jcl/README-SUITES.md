# Run the MR10 suites on MVS

All three jobs use the installed `ICINT19`. They **do not rebuild the compiler**. Each job copies the existing SYNI, TRNI, CGI, BLIBI, and ICLIB decks to temporary sequential datasets, compiles every program, and then runs the programs.

| MVS JCL member | Source | Programs | Compiler/generator steps | Run steps |
| --- | --- | ---: | ---: | ---: |
| `MRLANGDM` | `run-language-demos.jcl` | 11 | 22 | 11 |
| `MRBCDEMO` | `run-bcpl-demos.jcl` | 17 | 40 | 17 |
| `MRREGRES` | `run-regression-tests.jcl` | 12 | 46 | 12 |

Each job also has five staging steps. Some programs compile extra library modules.

## Install

Run at the repository root with Hercules/MVS running:

```sh
git pull --ff-only
tools/dspal populate MR10_BCPLDEMO
tools/dspal populate MR10_LANGDEMO
tools/dspal populate MR10_TESTS
tools/dspal populate MR10_LIBRARY

tools/dspal put MR10_JCL MRBCDEMO mr10-kit-compiler/jcl/run-bcpl-demos.jcl
tools/dspal put MR10_JCL MRLANGDM mr10-kit-compiler/jcl/run-language-demos.jcl
tools/dspal put MR10_JCL MRREGRES mr10-kit-compiler/jcl/run-regression-tests.jcl
```

The JCL files are stored **without JOB cards**. `dspal submit` adds the authenticated JOB card.

## Run

```sh
tools/dspal submit MR10_JCL MRLANGDM
tools/dspal submit MR10_JCL MRBCDEMO
tools/dspal submit MR10_JCL MRREGRES
```

## Read the report

| Look for | Meaning |
| --- | --- |
| `Cxx` | Compile BCPL into OCODE |
| `Gxx` | Generate INTCODE from OCODE |
| `Rxx` | Run the generated program |
| `DEMO:` | Program's short description |
| `TEST:` | Regression case description |
| `RP:` | Regression result to compare |
| `CODE=0` | Successful interpreted completion |
| `SYNTAX ERROR`, `INTCODE ERROR`, `MAPSTORE` | Investigate even if JES says success |

**JES RC=0000 is not enough.** ICINT19 may still print a nonzero interpreted `CODE`. The MVS regression JCL does not yet compare results with `.expected` files. The host `tools/run-mr10kit-regression-panel` does.

A prior regression run exposed invalid placement of `TEST:` statements before local `LET` declarations. Those source lines were moved below the declarations, and a later MVS run showed zero interpreted codes and the expected result records. Do not use JES job numbers as unique historical proof; they wrap.

For reproducible evidence, record the Git revision, installed member versions, job name, run date/time, and observed output.
