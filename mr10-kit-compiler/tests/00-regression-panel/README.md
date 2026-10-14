# Regression panel

These 12 small tests check BCPL behavior. They are listed in `manifest.tsv`.

| Item | Meaning |
| --- | --- |
| `source` | Main BCPL file |
| `extras` | Other BCPL modules to compile with it |
| `compile_args` | Special inputs or options |
| `expected` | File of expected `RP:` output |
| `expected_code` | Required interpreted completion code |

The manifest also names each test and its category.

## Run on the host

```sh
tools/run-regression-panel
```

Use `--list` to show cases, `--test NAME` for one test, or `--icint PATH` for another interpreter. The host runner compares `RP:` lines with golden files and checks the interpreted completion code.

## Run on MVS

Install `MR10_TESTS` and submit `MR10_JCL(MRREGRES)`. See [suite jobs](../../jcl/README-SUITES.md). The MVS JCL **does not** yet compare golden output. All steps returning MVS RC=0000 does not prove a test passed: also inspect ICINT `CODE=` and the `RP:` output.

`TEST:` lines tell readers what each program checks; they are not part of the expected-output comparison.
