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

## 14 October 2026 — JOB 4028 diagnosis and light-report revision

JOB **4028** (MRLANGDM) compiled DECLS in C01A RC=0000 and ran CGI in G01A RC=0000, both with interpreted CODE=0, but first execution R01 failed **ABEND S001-4**, `IEC020I` against the concatenated `MR10KIT.SOURCE` member stream. Later steps were flushed; runtime acceptance **NOT PASSED**.

The three jobs now begin with five `IEBGENER` stages copying SYNI/TRNI/CGI/BLIBI/ICLIB from their PDS members into temporary **sequential FB80** datasets, following the staging convention used in the previously proven host-generated workflow. All repeated INTIN concatenations use those sequential copies, not direct PDS members. Each staging step has `SYSPRINT DD DUMMY`. The compiler and CGI `SYSPRINT` remains visible so their interpreted completion codes and diagnostics are not hidden. Each interpreter step now uses `SYSUDUMP DD DUMMY` to prevent a routine incident from producing thousands of dump lines; when investigating failures, switch the affected step back to `SYSOUT=*` or use dedicated diagnostic JCL.

These changes are **not yet tested on Hercules**. Repopulate/reinstall the three JCL bodies via `tools/dspal put MR10_JCL ...` before retesting. First re-run MRLANGDM, inspect interpreter `CODE=` and R01/other step results, then the remaining suites. Do not infer a correct semantic result from MVS RC=0 alone.

## Language demos: compile-first ordering (14 October 2026)

`MRLANGDM` now stages the five existing INTCODE components, completes all 11 BCPL compilation and CGI code-generation pairs, and then executes all 11 generated INTCODE programs. The anonymous temporary `&&IxxA` datasets remain `DISP=(NEW,PASS)` at generation and `DISP=(OLD,DELETE)` at execution. This separates compiler reports from the demonstration outputs and does not rebuild the MR10 compiler. JOB 4050 passed under the previous interleaved order; **the reordered job requires its own MVS execution validation**. Reinstall the JCL member using `tools/dspal put MR10_JCL MRLANGDM mr10-kit-compiler/jcl/run-language-demos.jcl` before resubmitting.

## BCPL demo suite: descriptions and compile-first ordering (14 October 2026)

All 17 BCPL demo main programs now print one brief `DEMO:` line describing their purpose when executed. The additional library modules used by QUICKSRT and COROUTIN were not modified. `MRBCDEMO` follows the same compile-first organization as `MRLANGDM`: stage five prebuilt MR10 compiler/library INTCODE members into temporary sequential FB80 datasets, compile and generate all 17 demos (20 compilation units: QUICKSRT also uses RANDOM, and COROUTIN also uses GETVEC and COROUTIN library members), then run the 17 demos. This yields 5 staging, 40 compiler/generator, and 17 execution steps. Generated `&&Ixx` datasets are passed to the later execution steps, where they are deleted. No compiler sources are rebuilt.

**Deployment requires two MVS updates:** `tools/dspal populate MR10_BCPLDEMO` for changed BCPL sources, and `tools/dspal put MR10_JCL MRBCDEMO mr10-kit-compiler/jcl/run-bcpl-demos.jcl` for the changed stored JCL. Then `tools/dspal submit MR10_JCL MRBCDEMO`. JOB 4059 executed the *older* stored JCL, which lacked sequential staging and abended S001-4 in R01; the repository version already contains sequential staging. The revised compile-first job has not yet been verified on MVS.

## Regression panel: compile-first ordering and descriptions (14 October 2026)

`MRREGRES` now stages the five precompiled compiler/runtime INTCODE components, compiles and generates all 12 regression cases (23 compilation units, 46 compiler/generator steps), then executes the 12 cases. Program INTCODE temporary datasets stay passed between generation and execution. Each main regression source prints a short `TEST:` purpose line at runtime. The existing `RP:` semantic-result lines and `.expected` files are unchanged; `tools/run-regression-panel` extracts only `RP:` records, so the new descriptive lines do not affect golden-output comparisons. Extra library sources are untouched.

JOB 4095 ran an outdated MVS JCL member and abended S001-4 in R01; the committed JCL preserves the already-written sequential FB80 staging fix and `SYSUDUMP DD DUMMY`. To deploy both changes, run `git pull --ff-only`, `tools/dspal populate MR10_TESTS`, `tools/dspal put MR10_JCL MRREGRES mr10-kit-compiler/jcl/run-regression-tests.jcl`, and `tools/dspal submit MR10_JCL MRREGRES`. **The reordered job and new test descriptions remain unverified on Hercules**. The MVS job executes tests but still does not automate comparison with `.expected` files.
