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

## MR10 development-probe manifest contract

`dev-probes-manifest.tsv` defines **17 checks** across the eleven
numbered historical development-probe groups. A standalone runner exists; the original six current-ICINT BCPL probes and five reconstructed coroutine probes have owner-accepted
golden baselines. The other **six** historical cases remain `UNVERIFIED`.
The 12-case `00-regression-panel` remains separate. The project regression
coordinator includes `mr10-probes` as a sixth suite for the eleven accepted
probes. The six unverified historical candidates remain excluded.

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
| `verification` | `ACCEPTED` for eleven independently reviewed probes; `UNVERIFIED` for the other six cases |

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

Further case acceptance or any coordinator integration requires separate owner review.

## Standalone MR10 development-probe runner (first phase)

Of the **17** development-probe contracts, **eleven are ACCEPTED** (the six original current-ICINT BCPL probes plus five reconstructed coroutine probes). **Six remain UNVERIFIED**.
`tools/mr10/run-dev-probes` remains a standalone runner and is also
invoked by the project coordinator for exactly the eleven ACCEPTED cases.
The 12-case MR10 Regression Panel is independent. It implements the original six current-ICINT BCPL probes: `04-module-test`, `05-named-dd`,
`06-dynamic-streams`, `07-many-streams`, `09-multiple-assignment`, and
`11-getvec-freevec`. The five reconstructed MR10 coroutine probes were executed in JES jobs 5223–5227 as experimental candidates and are now owner-accepted. The other six historical probes remain experimental.

Project-wide host-only listing (no JES submissions):

```sh
tools/tests/run-project-regressions --list
tools/tests/run-project-regressions --check
```

The coordinated suite may be selected with `--suite mr10-probes --run --progress`
and needs no native `--profile` when run by itself. It submits JES jobs and
is not automatically included unless explicitly selected. The coordinator
stops after a failed or unverified probe, preserves per-case evidence, and
does not select the six remaining experimental probes.

Host-only commands (no JES submissions):

```sh
tools/mr10/run-dev-probes --check
tools/mr10/run-dev-probes --list
tools/mr10/run-dev-probes --list --case 05-named-dd
tools/mr10/run-dev-probes --list
python3 -B -m unittest discover -s tools/checks -p 'test_mr10_dev_probes_runner.py' -v
```

**Operator authorization is required before any `--run`.** Only after
separate approval for JES execution, use a selected case such as:

```sh
tools/mr10/run-dev-probes --run --case 05-named-dd
```

`--run --all-provisional` retains the original six-case selection (now all
accepted); `--run --all-candidates` explicitly selects **all 17**
(eleven accepted, six experimental).
Neither option runs without `--run`; there is no implicit default execution.
Each new experimental case may also be selected independently with
`--run --case CASE_ID`, after separate JES authorization. Unsupported cases or mixed selections containing
them are rejected **before** JES submission. Each selected case uses
`tools/mr10/compile-and-run` with its declared input bindings, a unique
JCL deck and job name, and an isolated evidence directory under
`workarea/mr10-probes/`. The JSON summary retains Git HEAD, selected
interpreter, exact command, expected and actual completion, JES job ID,
runner logs, and provisional output checks. The command stops after the
first unexpected failure.

For each of the original six BCPL probes, a fresh execution reports
**PASS** and exits **0** only when its exact golden-output records,
expected JES step return codes, and interpreted phase codes are verified.
The two-module cases (`04-module-test`, `11-getvec-freevec`) require 12
JES steps and five interpreted phases; the four single-module cases require
10 steps and three interpreted phases.
The original [05-named-dd acceptance](05-named-dd/acceptance-20261104.md)
and the five additional acceptance records in the corresponding test
directories document the evidence.

The six experimental historical probes remain **OBSERVED** when their
source-derived candidate checks succeed, with overall **UNVERIFIED**
(exit code **3**) unless run alongside failed cases.
Unexpected execution or comparison failures return **1**. Invalid
inputs and unsupported selections return **2** before JES submission;
host-only `--check` and `--list` return **0**.
A mixed run with accepted PASS and provisional OBSERVED remains
UNVERIFIED (exit code 3), never an accepted suite-wide PASS.

The `.expected` files for all eleven accepted cases contain exact semantic
program-output records. ICINT memory statistics and cycle counts are
excluded from comparison, while unexpected program-output lines are not. The runner saves the independently
extracted job summary and full JES report under `workarea/mr10-probes/`.
Experimental cases have candidate semantic and JES step/phase checks;
saved OCODE/INTCODE is directed to an isolated per-case artifact folder.
The historical `v12`, `v13` and `v14` assemblers remain pinned.
The existing `compile-and-run` defaults are unchanged.
The original six golden baselines are grounded in independently reviewed MVS
execution: JOB 9543 for 05-named-dd, and JOBs 9545, 9547, 9548, 9549,
and 9550 for the five newly accepted cases.
No additional JES job was submitted for this evidence review.
The revised eleven-case runner requires fresh MVS execution before claiming a post-promotion all-PASS run.

### Expanded candidate contract (not an acceptance decision)

See [the 4 November candidate contract review](development-probe-expansion-20261104.md)
for the five newly accepted cases, the eleven still-unverified historical
experimental cases, and their source-derived output or structural checks.
Five coroutine probes were promoted by a [separate 11 November acceptance](10-coroutines/acceptance-20261111.md); that does not retroactively revise the 4 November expansion review.
No new JES execution is authorized by checking out or validating this code.

### Five accepted coroutine probes (11 November 2026)

The [five-case acceptance record](10-coroutines/acceptance-20261111.md) pins the exact `.expected` outputs from MR10 JES jobs 5223–5227. The 11 accepted probes, including these five, are now selected by the `mr10-probes` suite. The runner verifies exact output, JES step/program order/RCs, interpreted phase CODEs, and (for the two compilation probes) fresh OCODE/INTCODE token correspondence. The earlier five-job run used the **experimental pre-promotion runner**; an eleven-case acceptance run remains pending separate JES authorization.
