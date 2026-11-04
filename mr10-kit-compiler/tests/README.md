# Tests and probes

Two kinds of tests live here:

| Directory | Purpose |
| --- | --- |
| `00-regression-panel/` | 12 short tests with saved expected output |
| `01-echo-test/` | First INTCODE input/output |
| `02-honors-thesis-and-mapstore/` | Early ICINT and MAPSTORE tests |
| `03-compile-richards-factorial/` | Compiler pipeline and saved intermediate code |
| `04-module-test/` | Separate compilation and GLOBAL linkage |
| `05-named-dd/` | Named MVS input DDs |
| `06-dynamic-streams/` | Nested and dynamic streams |
| `07-many-streams/` | 12 simultaneous input streams |
| `08-character-translation/` | ASCII, EBCDIC, and BCPL characters |
| `09-multiple-assignment/` | Historical assignment order |
| `10-coroutines/` | Coroutine calls, frames, and storage |
| `11-getvec-freevec/` | Dynamic storage allocation |

## Existing 12-case regression panel

```sh
tools/mr10/run-regression-panel
```

Use `tools/mr10/compile-and-run` for individual BCPL probes and `tools/mr10/run-intcode` for existing INTCODE files. Some probes need added modules or DD files; consult their local README.

Saved OCODE and INTCODE files are evidence, not build litter. Keep them where they explain an observed compiler or runtime behavior.

## Proposed MR10 development-probe suite (manifest only)

`dev-probes-manifest.tsv` defines **17 proposed checks** across the eleven
numbered historical development-probe groups. It is **not** an executable
or accepted suite. All cases are `UNVERIFIED`. The 12-case `00-regression-panel`
and the five-suite project regression coordinator are unchanged;
`mr10-probes` is not yet a runnable or coordinator-selected suite.

The following commands validate the contract **offline**, without submitting
JES, compiling BCPL, or modifying MVS datasets:

```sh
python3 -B tools/checks/check-mr10-dev-probes-manifest.py
python3 -B -m unittest discover -s tools/checks -p 'test_mr10_dev_probes_manifest.py' -v
```

### Manifest field contract

| Field | Definition |
| --- | --- |
| `case_id` | Existing historical directory identity; optional `/subcheck` for independent tests in a directory |
| `engine` | Intended `compile-and-run` or `run-intcode`; never invoked during manifest checks |
| `interpreter` | `current` (resolved via `asm/CURRENT`) or pinned historical `v12`, `v13`, `v14` |
| `source` | Repo-relative primary BCPL/INTCODE file |
| `modules` | Optional semicolon-separated ordered additional BCPL/INTCODE inputs |
| `dd_bindings` | Optional semicolon-separated `DDNAME=repo-relative-path` bindings |
| `sysin` | Optional repo-relative runtime input |
| `expected_code` | Expected interpreted completion; only MAPSTORE deliberately expects `-1`, the others `0` |
| `oracle` | `file:path` for an existing candidate golden file or `pending:reason` when output/structural expectations still require verification |
| `artifacts` | `none` or `ocode,intcode` for proposed compiler-output evidence |
| `verification` | `UNVERIFIED`; any acceptance/blocking claim requires an independently reviewed record and contract update |

The validator checks the fixed historical case identities, interpreters,
source files, required modules, DD bindings, SYSIN, expected codes, artifacts,
and safe repository-contained paths. It **does not** prove executable
behavior, test outputs, installed objects, or historical compatibility.
A green manifest check is not a passing MR10 probe suite.

### Evidence and open execution questions

- `01-echo-test` references a historical `--RUNTIME` option that the current
  `run-intcode` command does not expose. Proposed `BLIBI`/`ICLIB` linkage and
  exact echo comparison require MVS verification.
- The `v12`, `v13` and `v14` probes remain explicitly version-specific;
  substituting `ICINT19` would change the test being performed.
- The v12 factorial `.expected` file exists but has not been accepted as a
  new runner's golden-output policy.
- Other probes need MVS-derived golden outputs or independently verified
  OCODE/INTCODE structural assertions. `CODE=0` alone never proves PASS.
- The historical source and intermediate artifacts must remain unmodified.
  Future generated artifacts belong in separate workarea evidence directories.

Only after reviewing execution contracts, expected outcomes, and target-MVS
evidence should a separate runner or coordinator integration be approved.
