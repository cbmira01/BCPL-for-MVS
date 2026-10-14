# MR10KIT MVS-resident suite jobs

Three host-authored JCL **bodies** are committed and registered in `config/dspal.yaml`. None contains its own JOB card: `tools/dspal submit MR10_JCL MEMBER` inserts the authenticated JOB card and submits the stored member on MVS.

| Host file | MR10_JCL member / payload job | Cases |
| --- | --- | --- |
| `run-bcpl-demos.jcl` | `MRBCDEMO` | 17 BCPL demos |
| `run-language-demos.jcl` | `MRLANGDM` | 11 language demos |
| `run-regression-tests.jcl` | `MRREGRES` | 12 cases from `tests/00-regression-panel/manifest.tsv` |

These are **MVS-only execution workflows after installation**. Each case executes a BCPL compilation using `MR10KIT.SOURCE(SYNI,TRNI,BLIBI,ICLIB)`, invokes CGI on OCODE to create INTCODE, and runs that INTCODE with BLIBI/ICLIB. Every such step uses `PGM=ICINT19`, with `STEPLIB=HERC02.BCPL.MR10KIT.LOAD`. Modules and named-DD input fixtures are obtained from the MR10KIT BCPLDEMO, LANGDEMO, LIBRARY and TESTS PDSes. Compiler and program outputs appear in separate JES step `SYSPRINT` listings. The supplied JCL is not a host-side loop and does not reassemble ICINT.

The BCPL demo suite requires four additional PDS fixture members: `BCPLDEMO(WORDIN,FANAIN,FANBIN,FANCIN)`. They are now mapped in the manifest but must be populated on MVS.

## Installation and first run

```sh
git pull --ff-only
tools/dspal populate MR10_BCPLDEMO
tools/dspal put MR10_JCL MRBCDEMO mr10-kit-compiler/jcl/run-bcpl-demos.jcl
tools/dspal put MR10_JCL MRLANGDM mr10-kit-compiler/jcl/run-language-demos.jcl
tools/dspal put MR10_JCL MRREGRES mr10-kit-compiler/jcl/run-regression-tests.jcl
tools/dspal ls MR10_JCL
tools/dspal submit MR10_JCL MRBCDEMO
tools/dspal submit MR10_JCL MRLANGDM
tools/dspal submit MR10_JCL MRREGRES
```

Prefer starting with **MRLANGDM**, the simplest suite, and examining its JES payload report before attempting the larger suites. Inspect generated `dspal submit ... --show-jcl` first if desired. Avoid concurrent submissions while establishing the baseline.

## Validation scope and limitations

- Static checks performed before Git commit: all three JCL members have no line longer than 71 characters; all 3 source bundles are deterministic and use explicit PDS members. **Not yet MVS-tested**. Record JES payload JOB numbers and `tools/job-summary` for each.
- These jobs compile and execute cases; **they do not yet evaluate golden-output `.expected` member contents automatically**. `MRREGRES` is an execution panel, not yet an authoritative semantic PASS/FAIL harness. Inspect interpreter-reported `EXECUTION CYCLES ... CODE=` and `RP:` lines, comparing the saved expected-output fixtures to each test's output.
- A successful JES RC alone is not proof that BCPL semantic tests passed. The interpreter may print its own completion status while returning MVS RC=0.
- `COND=(4,LT)` stops subsequent steps after a failing MVS step. The full suite requires successful earlier compiler/generator steps.
- The jobs cover the **12 cases in the current regression panel**, not all other exploratory `mr10-kit-compiler/tests/` directories. Expansion can follow after the first MVS acceptance run.

The host JCL and PDS members are the same FB80 job body, installed with `dspal put`. Run with `dspal submit` rather than `tools/submit-jcl`, which expects a leading JOB card.
