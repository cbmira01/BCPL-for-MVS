# Native regression suites — Stage 2C

Stage 2B established ownership of all **177** native cases (00–176).
Stage 2C physically organizes the unchanged case directories by suite.
Case numbers, source contracts and expected results remain unchanged.
`tests/suites/*.tsv` retains the authoritative case inventory and reporting
metadata. Shared execution machinery remains in `bootstrap-toolchain/regression/`.

| Suite | Manifest | Case IDs | Cases |
| --- | --- | --- | ---: |
| Bootstrap | `suites/bootstrap.tsv` | 00–145 | 146 |
| Runtime Extensions | `suites/runtime-extensions.tsv` | 146–158 | 13 |
| BCPLTIME | `suites/bcpltime.tsv` | 159–162 | 4 |
| BCPLQSAM | `suites/bcplqsam.tsv` | 163–176 | 14 |

The independent MR10 regression panel remains at
`mr10-kit-compiler/tests/00-regression-panel/manifest.tsv` and runs via
`tools/mr10/run-regression-panel`. The new native suite command does not
reinterpret or count MR10 tests.

## Manifest schema

Every UTF-8 TSV has the same header:

```text
case_id  directory  profiles  requires  tags  policy
```

(The separators are actual tab characters, not spaces.) Each `case_id` uses
the historic canonical two-digit (00–52) or three-digit (053–176) form.
`directory` is the literal child directory of its owning suite:
`tests/bootstrap/`, `tests/runtime-extensions/`,
`tests/system-extensions/bcpltime/`, or
`tests/system-extensions/bcplqsam/`.
`profiles`, `requires`, and `tags` are comma-separated identifiers. Case
identity and ownership are unique; tags may overlap, but must not create
duplicate acceptance counts. `requires` documents conditions; it is not a
claim that resident MVS objects have been independently probed.

`profiles` currently permits `production` and `installed-r5-t1`:

- `production` uses `BOOT_OBJ` and **source-selected R.5/T.1** optional
  extension assembly when needed.
- `installed-r5-t1` uses `BOOT_OBJ` plus installed R.5/T.1 objects in
  `EXT_OBJ` and macros in `EXT_MAC`.
- **In both profiles, cases 163–176 use source-selected BCPLQSAM.** Neither
  profile constitutes proof of installed `EXT_OBJ(BCPLQSAM)` execution.

The fixture files (`expected.txt`, GO RC markers, `.asm` selections, etc.)
remain the sole expected-output/return-code contract. `policy` is one of:
`standard`, `skip-installed` (historic source-only instrumentation case 083),
or `device-opt-in` (175 punch and 176 printer).

## Finding a test

For example, case 170 is under
`tests/system-extensions/bcplqsam/170-qsam-demo-interoperability/`;
case 083 is under
`tests/bootstrap/083-instrumented-storage-reclamation/`.

Use `tools/tests/run-suite --list` to discover suites and case identities.
The suite manifests map every stable case ID to its directory name.
There are no duplicate physical test implementations across suites.
The MR10 regression panel remains independent.

## Usage

All commands are run from the repository root:

```sh
tools/tests/run-suite --list
tools/tests/run-suite bootstrap --list
tools/tests/run-suite bootstrap --check
# Each --run submits MVS JES jobs; separate owner authorization is required.
tools/tests/run-suite bootstrap --run --profile production
tools/tests/run-suite bcpltime --run --profile installed-r5-t1
tools/tests/run-suite bcplqsam --list --tag integration
tools/tests/run-suite bcplqsam --run --profile production --case 163
```

`--check` validates **all four** manifests against all 177 physical cases,
including marker files, canonical IDs, complete coverage, ownership and
case-directory identity; it is entirely offline. `--list` is also offline.
`--case ID` can be repeated; `--tag TAG` can be repeated as an AND filter.

`--run` always requires an explicit profile and creates a unique directory
under `workarea/test-suites/`, with one `runner.log`, isolated native-runner
logs per case, and incremental `summary.json` recording suite, profile,
Git commit, cases, results and return codes. The native run is successful
only if the existing runner reports a matching case PASS and 1 PASS / 0 FAIL /
0 SKIP / 1 TOTAL, with RC=0. The new reporting totals distinguish PASS,
FAIL, SKIP, and BLOCKED; any FAIL or BLOCKED makes its final RC nonzero.

**Safety:** Case 083 is reported as the established expected SKIP in
installed-BOOT_OBJ profiles. Cases 175–176 are BLOCKED unless the operator
explicitly selects `--allow-device` **and** has separate authorization to run
JES device-dependent cases. The suite runner never enables the JES2 punch
writer, even if the shell previously exported `Q4_PUNCH_RESUME=1`.
Any missing/unproven resident PDS, device availability, allocation and actual
JES result still requires checking against native evidence; manifest
prerequisite declarations do not perform MVS probes. Existing runner failures
are recorded as FAIL, not silently waived as SKIP.

All previous commands in `tools/bootstrap/` retain their historical
selection and default logging semantics. The new native
`tools/bootstrap/run-regression --log-dir /absolute/path` option is used by
suite runs to isolate evidence. It does not affect legacy invocations.

The historical QSAM Q.5 full-panel outcome remains 175 PASS / 1 FAIL
(case 175) / 1 expected SKIP (083), followed by a separate case-175 PASS
rerun; Stage 2B does not rewrite any accepted historical evidence.

## Project-level coordination — Stage 3

The project-level coordinator is `tools/tests/run-project-regressions`.
It includes the independent MR10 regression panel alongside the four
native suites while preserving separate suite identities, profiles,
outcomes and evidence. See [coordinator usage](../tools/tests/README.md).
