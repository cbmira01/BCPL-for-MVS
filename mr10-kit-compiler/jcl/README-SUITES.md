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
tools/datasets/dspal populate MR10_BCPLDEMO
tools/datasets/dspal populate MR10_LANGDEMO
tools/datasets/dspal populate MR10_TESTS
tools/datasets/dspal populate MR10_LIBRARY

tools/datasets/dspal put MR10_JCL MRBCDEMO mr10-kit-compiler/jcl/run-bcpl-demos.jcl
tools/datasets/dspal put MR10_JCL MRLANGDM mr10-kit-compiler/jcl/run-language-demos.jcl
tools/datasets/dspal put MR10_JCL MRREGRES mr10-kit-compiler/jcl/run-regression-tests.jcl
```

The JCL files are stored **without JOB cards**. `dspal submit` adds the authenticated JOB card.

## Run

```sh
tools/datasets/dspal submit MR10_JCL MRLANGDM
tools/datasets/dspal submit MR10_JCL MRBCDEMO
tools/datasets/dspal submit MR10_JCL MRREGRES
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

**JES RC=0000 is not enough.** ICINT19 may still print a nonzero interpreted `CODE`. The MVS regression JCL does not yet compare results with `.expected` files. The host `tools/mr10/run-regression-panel` does.

A prior regression run exposed invalid placement of `TEST:` statements before local `LET` declarations. Those source lines were moved below the declarations, and a later MVS run showed zero interpreted codes and the expected result records. Do not use JES job numbers as unique historical proof; they wrap.

For reproducible evidence, record the Git revision, installed member versions, job name, run date/time, and observed output.

## Observe physical PDS capacity with dspal stat

`tools/datasets/dspal stat MR10_ASM` and `tools/datasets/dspal stat` now request
read-only IEHLIST VTOC and directory listings in addition to LISTDS.
The report prints allocated tracks, tracks occupied through the
end-of-data high-water mark, unused tail tracks, extent count, and
PDS directory allocation/unused-block counts.

The high-water mark is **not** live-member utilization; replaced members
may leave reclaimable dead space. The requested allocation in
`config/dspal.yaml` is distinct from the physical extents actually
allocated on MVS. If IEHLIST cannot be parsed, stat reports
`unavailable` rather than substituting manifest values. This feature
requires runtime verification on MVS before it is considered accepted.

## Complete manifest-driven reinitialization

Use the manifest for allocations, not the historical one-off
`recreate-mr10-asm.jcl`. A purge deletes all managed datasets,
including MR10_OBJ and MR10_LOAD; the latter must be rebuilt before any
MR10 suite is run. After allocating, run `dspal populate all`,
then `dspal submit MR10_JCL IC19BLD` and check its ASM, LKED,
and SAVEOBJ steps before running the three suites above.
