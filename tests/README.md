# Native regression suites — Stage 2C

Stage 2B established ownership of the original **177** native cases (00–176).
CO.5 adds thirteen independently named source-selected coroutine cases
177–189 without changing the earlier identities or their acceptance contracts.
Stage 2C physically organizes the unchanged case directories by suite.
The original case numbers, source contracts and expected results remain unchanged.
DR.5 appends three permanent compiler-compatibility cases (190–192) and one BCPLIO guard case (193) to Bootstrap, plus four installed-registrar cases (194–197) to Runtime Extensions and three private QSAM diagnostics (198–200).
`tests/suites/*.tsv` retains the authoritative case inventory and reporting
metadata. Shared execution machinery remains in `bootstrap-toolchain/regression/`.

| Suite | Manifest | Case IDs | Cases |
| --- | --- | --- | ---: |
| Bootstrap | `suites/bootstrap.tsv` | 00–145, 190–193 | 150 |
| Runtime Extensions | `suites/runtime-extensions.tsv` | 146–158, 194–197 | 17 |
| BCPLTIME | `suites/bcpltime.tsv` | 159–162 | 4 |
| BCPLQSAM | `suites/bcplqsam.tsv` | 163–176, 198–200 | 17 |
| Coroutines | `suites/coroutines.tsv` | 177–189 | 13 |

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
the historic canonical two-digit (00–52) or three-digit (053–200) form.
`directory` is the literal child directory of its owning suite:
`tests/bootstrap/`, `tests/runtime-extensions/`,
`tests/system-extensions/bcpltime/`, or
`tests/system-extensions/bcplqsam/`, or `tests/coroutines/`.
`profiles`, `requires`, and `tags` are comma-separated identifiers. Case
identity and ownership are unique; tags may overlap, but must not create
duplicate acceptance counts. `requires` documents conditions; it is not a
claim that resident MVS objects have been independently probed.

`profiles` currently permits `production` and `installed-r5-t1`:

- `production` uses `BOOT_OBJ` and source-selected optional extension assembly
  when needed (R.5/T.1 and BCPLQSAM; case 170 also selects installed BCPLDEMO).
- `installed-r5-t1` retains its historical profile name and selects installed
  R.5/T.1 and BCPLQSAM objects from `EXT_OBJ` and macros from `EXT_MAC`.
  DR.5 extends the existing 163–176 QSAM fixtures to this mode without
  renumbering or duplicating them. Initial full installed-suite MVS execution
  passed all 14 cases at c96523d970d4; focused installed QUERY and exclusion also passed.

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

`--check` validates **all five** manifests against all 201 physical cases (00–200),
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
JES device-dependent cases. The suite runner strips any inherited `Q4_PUNCH_RESUME` setting.
For explicitly opted-in case 175 only, it enables the guarded single
`$S PUN1` recovery (production environment flag or installed-profile
`--resume-punch`). The native QSAM runner requires verified paused
PUNCH1 and an exclusive current Q4PUNCH queue before starting the writer;
it does not automatically retry a failed start. Case 176 never starts
PUNCH1. See the [coordinator safety contract](../tools/tests/README.md).
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
It includes the independent MR10 regression panel alongside the five
native suites and separately selectable coroutine contracts/probes, while
preserving separate suite identities, profiles, outcomes and evidence. See [coordinator usage](../tools/tests/README.md).

## CO.5 coroutine suite (177–189)

These thirteen native candidate-source tests use the accepted CO.2/CO.3/CO.4
Cambridge compiler, four-IFOX (three for CO.2), IEWL and GO/JES runners.
Their numbered fixture directories reference canonical accepted candidate
BCPL sources; `expected.txt` holds exact ordered logical record oracles.
The independent CO.3 library and BCPLCO/BCPLMAIN assemblies remain test-local;
BOOT_OBJ is read-only, and G!289–305 are not public globals.

Host-only selection: `tools/tests/run-suite coroutines --list`.
Native execution, following explicit operator approval:
`tools/tests/run-project-regressions --run --suite coroutines --profile production --progress`.
This describes the original candidate-source selection. See the later
[CO.6 qualified closure](../packaging/milestones/coroutines/co6-formal-acceptance-and-closure-20261116.md)
for accepted scope; the numbered coroutine cases still use source-selected assemblies.

## DR.5 compiler compatibility (190–192)

These non-installing Bootstrap regressions use the resident CAMBCOMP and
installed production Core Runtime/Base Library. Case 190 checks both logical
newline representations, ordinary EBCDIC A and exact FB132 records/EOF using
an independent QSAM assembler verifier. Case 191 checks unknown/numeric
compiler options, GET LIBHDR and native output; H600 is a compile-only probe.
Case 192 exercises top-level period record skipping and source lookahead,
requiring both independently linked native units to run correctly. No new
suite or changes to earlier test IDs or oracles. Both existing profiles run
these cases. See the case READMEs. All three passed focused and full production-profile MVS regression after CAMBBLD JOB 9925. The [DR.5 verification record](../packaging/milestones/documentation-refactoring/candidates/compiler-verification/README.md) records 211 supported passes and one expected SKIP (083).

## DR.5 BCPLIO stream guards (193)

The ordinary installed production Bootstrap runner tests the corrected BCPLIO
with wrong-direction selection guards, fixed input close guards and normalized
built-in DD identity/cursor preservation. Private candidate JOB 363, BLDIOFIX
JOB 366 and installed case 193 passed on 26 November 2026. The [subsequent
supported campaign](../packaging/milestones/documentation-refactoring/dr2-runtime-library-manual-migration-20261125.md) reported 212 PASS, one expected SKIP (083),
zero FAIL/BLOCKED. The earlier 211-pass campaign predates case 193.
Do not run case 193 against the uncorrected installed BCPLIO.

## DR.5 — Registrar regressions 194–197

| ID | Contract |
| --- | --- |
| 194 | Multiple distinct dependencies, duplicate/missing, ownership, repeat/finalization |
| 195 | Nonzero dependency ordinal, single dependency and forward rejection |
| 196 | Structural preflight and extent/header/count precedence |
| 197 | Malformed and incompatible dependency versions, self/blank dependency |

These read-only installed BCPLRGS assembler tests derive from the
[18-assertion contract probe](../bootstrap-toolchain/probes/dr5-registrar/README.md).
No compiler is needed for these four cases. Both profiles use BOOT_OBJ.
The owner-reported JOBs 798/801/802 and following 212-PASS production
campaign establish the corrected installed registrar at their tested
scope; see [DR.5 evidence](../packaging/milestones/documentation-refactoring/dr2-extension-manual-migration-20261125.md).
First numbered production-profile execution passed all 17 Runtime Extensions
cases (146–158 and 194–197). The preceding complete eight-suite campaign
remains 212 PASS and one expected SKIP; the then-expanded consolidated
target was 216 PASS, 1 expected SKIP 083, 0 FAIL/BLOCKED (217 selected).
The two reported runs account for all supported identities but are not one
expanded campaign.

## DR.5 — Supplemental installed BCPLQSAM verification

The separate [installed verification driver](../tools/checks/run-dr5-qsam-installed.py)
passed cases 163 and 146 using installed objects and resident BCX macros
(native JOBs 1261 and 1263). This proves installed QUERY selection and
exclusion at the tested scope. The later DR.5 dual-mode integration extends
the installed profile to the existing QSAM cases; its initial run passed all 14.
No new case IDs or campaign counts are introduced. See the
[DR.5 evidence](../packaging/milestones/documentation-refactoring/dr2-extension-manual-migration-20261125.md).

## DR.5 — Private QSAM fault regressions 198–200

| Case | Contract | Expected GO RC |
| --- | --- | ---: |
| 198 | Injected stage refusal, real rollback CLOSE, reopen and zero finalizer counters | 0 |
| 199 | Real bounded conditional GETMAIN RC=4, all pressure freed, surviving handle and zero final counters | 0 |
| 200 | Combined stage refusal and injected nonzero returned CLOSE; primary -11, no published handle, quarantine, no repeat CLOSE | 8 |

Both profiles compile these cases afresh and link a disposable instrumented
BCPLQSAM object with temporary runtime/registry assemblies and read-only
BOOT_OBJ. Neither mode uses the installed BCPLQSAM for these diagnostics.
No permanent writes, device operations or historical workarea prerequisites.
Exact GO results and job-bounded WTO traces in both console and hardcopy
are required. Case 200 records the current provisional primary-status
precedence; genuine exceptional MVS CLOSE remains unverified. Initial
numbered run passed 198 and 199; JOB 1300 satisfied case 200 native behavior
but failed the host registrar-message parser. The parser is corrected;
retained-evidence automated replay passed at e9f0f7380fcf without a new JES job. All 17 QSAM cases have accepted evidence across separate runs. New inventory 201 native cases;
complete eight-suite target 219 PASS and one expected SKIP (220 selected).
Earlier reported counts remain historical, not expanded passing results.
