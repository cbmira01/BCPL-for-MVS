# How to Develop and Test BCPL for MVS

**Audience:** Developers and maintainers of the BCPL for MVS 3.8 Reconstruction project.  
**Status:** Working draft, DR.3 — Project Documentation. Source reviewed at `c81fee5ca42263f862e5fa6a9826d68706b47887`.

Develop in small, reproducible increments, with real BCPL, assembler and JCL. Verify the behavior on MVS 3.8J before treating a candidate as accepted. This guide covers the development environment, not the operation of the public release or the installation of a distribution tape. The existing policies, contracts, test manifests and accepted engineering records remain authoritative during migration.

[Documentation catalog](../README.md) | [Reconstruct from source](How-to-Reconstruct-BCPL-from-Source.md) | [Compile and run BCPL programs](../product/How-to-Compile-and-Run-BCPL-Programs.md)

## 1. Working authority, target isolation and approvals

GitHub `main` is authoritative for project source, configuration, JCL, test contracts and records. MVS, IFOX, IEWL and JES establish observed target behavior. An installed object is a deployment artifact, not an independently maintained source. Follow the [Git/MVS authority policy](../../packaging/operations/git-mvs-authority.md) and [WSL operator command policy](../../packaging/operations/operator-wsl-command-policy.md).

Work in a dedicated Hercules/TK5 MVS 3.8J environment. Use one operator; quiesce independent submissions before reconstruction or controlled installations, and do not interleave another build with a guarded operation. An idle display does not reserve JES. Keep the actual effective HLQ, reader, printer and dataset selection visible; private `config/dspal.local.yaml` credentials do not belong in Git or published JES extracts.

| Action | Authority and required boundary |
| --- | --- |
| Inspect source and run independent host checks | Developer workspace; no MVS writes or submissions |
| Change an interface, architecture or global allocation | Discuss and obtain owner approval; preserve existing contracts |
| Commit reviewed source, tests or documentation | Explicit owner authorization; work on `main` |
| Run target tests | Separate MVS execution authorization for the stated scope |
| Install/replace accepted objects | Separate explicit promotion and write authorization |
| Purge/reconstruct, operate devices, produce or publish a release | Separate scope-specific approval; follow the relevant runbook and guards |
| Close a march or milestone | Explicit owner acceptance of evidence and qualifications |

Do not infer MVS authorization from a Git commit, a documented command, a PASS on another revision or an approval for a different task. Do not create feature branches, rewrite committed history, or ask the owner to do routine editing or offline checking that the developer can perform. After operational commits, supply the MVS-facing update and execution procedure when needed. Operator-pasted shell blocks must preserve the interactive shell: no fail-fast options or top-level `exit`; capture and report return codes and skip dependent operations after failure.

## 2. Development — investigate, define contract and edit real BCPL, JCL or assembler

Identify the active milestone and march in the [milestone index](../../packaging/milestones/README.md), current public contract, source, test coverage and actual failing evidence. Preserve the official names, identifiers and historical source. Distinguish a reproducible defect from a proposed new capability; define the scope, expected behavior and exclusions before modifying implementation.

Use the actual [dataset map](../../config/dspal.yaml), not an obsolete pathname or an MVS member guessed from a logical package name.

| Area | Maintained source or authority |
| --- | --- |
| Historical evidence | [richards-bcpltape](../../richards-bcpltape/) — preserve original material and provenance |
| MR10 Kit Compiler | [mr10-kit-compiler](../../mr10-kit-compiler/) — INTCODE phases, ICINT19 assembler, interpreted tests and JCL |
| Interpreter-hosted demoted Cambridge Compiler | [bootstrap-toolchain](../../bootstrap-toolchain/) — bootstrap inputs, CG370, Core Runtime, BLIB build and native tests |
| Native-running Cambridge Compiler | [cambridge-compiler](../../cambridge-compiler/) — separate unfinished reconstruction |
| Optional packages | [system-extensions](../../system-extensions/) and the [Global Number Registry](../../packaging/architecture/global-number-registry.md) |
| Native test ownership | [tests](../../tests/README.md), suite manifests and individual case fixtures |
| Host orchestration | [tools](../../tools/) and focused checks under `tools/checks/` |

The [canonical runtime source map](../../bootstrap-toolchain/asm/README.md) distinguishes BCPLMAIN, BCPLIO, BCPLMEM, BCPLBYTE, BCPLAPT, BCPLRGS and the empty BCPLREG table. The historical `bcplmain-wip` fragments are not the production implementation. BLIB is compiled separately. For coroutine work distinguish `bcplco.asm` (accepted candidate-source fixture) from `bcplco-production.asm` (production bridge), and the tracked `bootstrap-toolchain/library/coroutines.bcpl` from its prepared assembler output.

Before a change, establish the failing case, exact source revision, expected output, actual receipt and linkage selection. If a new contract is needed, specify data representation, inputs, outputs, exceptional behavior, resource ownership and compatibility. Use the [runtime and library nomenclature](../../packaging/architecture/runtime-and-library-nomenclature.md). Check GLOBAL declarations against the registry; declarations, object inclusion and registration are separate. Do not allocate a new global, change a published opcode or quietly repurpose a test number.

Edit the tracked implementation rather than a resident PDS as the durable source. Keep source edits and test changes small and attributable. Preserve historical examples even when they reveal incompatibility. For IFOX use the maintained source conventions: ASCII, no tabs or trailing whitespace, text through column 71 and labels of at most eight characters. Check JCL record width, continuation, DD names, dataset disposition and intended execution sequence. Generated assembler and authenticated JCL belong in controlled scratch locations, not as unreviewed replacement sources.

Examples of host-only checks, chosen to match the actual change:

```sh
python3 tools/checks/check-asm-source.py bootstrap-toolchain/asm/bcplmain.asm
python3 tools/checks/check-bcplmain-canonical.py
python3 tools/checks/check-native-jcl-manifest.py
tools/tests/run-suite --check
tools/tests/run-project-regressions --check
```

Inspect the result of each check; a nonzero result blocks dependent work. The source-local checker README contains older examples and inventory counts, so inspect the actual checker's current assumptions. A failed checker may identify a stale tool contract rather than an MVS defect; investigate instead of bypassing it. Run relevant host unit tests for changes to helpers, manifests or generators. For example, the focused coordinator checks use:

```sh
python3 -B -m unittest discover -s tools/checks -p 'test_stage2b_suite.py' -v
python3 -B -m unittest discover -s tools/checks -p 'test_stage3_coordinator.py' -v
```

These are offline development tasks, not requests for operator execution. Do not claim that passing them proves an instruction, macro, assembler listing or application behavior on MVS.

## 3. Development — build candidate, inspect listings/maps without premature promotion

Select an explicit compiler execution environment. The MR10 Kit Compiler compiles to INTCODE and runs under ICINT19. The demoted Cambridge Compiler is itself INTCODE under ICINT19; it emits System/370 assembly for a native application. The latter still needs IFOX assembly, IEWL link-edit and actual execution. Do not describe generated assembler as a native-running compiler.

Use a non-installing candidate job or the relevant accepted candidate test adapter. Temporary decks and load modules should be discarded after the test; where persistent development objects are needed, use the approved `BOOT_DEVOBJ` members. Preserve `BOOT_OBJ` and `EXT_OBJ` until a separate installation decision. Do not change a candidate into the installed profile by renaming an input or substituting another library.

The following source-compile example uses the actual native case 075 and a dedicated disposable output. It is a source-derived invocation of the resident compiler, not a new verified test. The preview performs no JES submission but **may delete an existing output file**: choose a new scratch path even for `--show-jcl` and keep it separate from valuable evidence.

```sh
tools/bootstrap/compile-mvs tests/bootstrap/075-blib-writef-mixed-object/source.bcpl     --compiler-image CAMBCOMP     --output workarea/dr3-075-preview.s370.asm --show-jcl
```

After review and MVS authorization, compile to a different scratch destination:

```sh
tools/bootstrap/compile-mvs tests/bootstrap/075-blib-writef-mixed-object/source.bcpl     --compiler-image CAMBCOMP     --output workarea/dr3-075.s370.asm
```

Require successful ICINT completion and recovered nonempty CODE output; check the actual compiler image and PARM. Inspect generated assembler, the actual JCL and the candidate's linkage plan. `--listing` does not add an assembler stage to `compile-mvs`. A source-mode candidate with a different compiler image or checked-frame PARM is a different evidence scope.

For assembler/runtime work, use the applicable non-installing job to establish exact CSECT and external entry symbols, assembler severity and flagged statements. Verify the IEWL map and cross-reference for the intended providers; an INCLUDE statement with the wrong DD or a missing ENTRY is a link defect even if compilation passed. Verify that any required `BCPLREG` selection is the intended one. Then run the application with its independent oracle. Never submit an installation job just to see whether source assembles.

When a job is supplied as a stored body, `dspal submit` creates and waits for a launcher and payload; examine the payload, not merely the launcher. Before staging even text members, check the exact logical dataset and member. Do not transfer relocatable object decks through `dspal put` or text conversion; use the applicable MVS binary-safe build/installation JCL. Use fresh temporary object decks rather than silently reusing unrecorded objects.

For a concrete non-installing native test, use the focused suite workflow in Chapter 4. For a change requiring candidate-specific assembly or linking, use its pinned milestone procedure and verify the actual candidate sources and dependencies before execution. The historical [paired BCPLMAIN/BCPLMEM promotion record](../../packaging/operations/runtime-object-promotion.md) illustrates assembly-only, link-only and GO gates, but its pre-M3 paths, OBJ names and historical installation status are not a current recipe.

## 4. Testing — design independent oracles; focused tests and source/installed modes

Before running a test, write down what must be observed independently of the implementation. The test contract may include exact ordered logical output, expected completion or GO return code, record count and byte identity, guard bytes, device receipt, and required job steps. Include boundary and negative cases where relevant. Do not revise a golden result just because an incorrect implementation produced something else.

For example, the tracked [native case 075](../../tests/bootstrap/075-blib-writef-mixed-object/README.md) contains this actual BCPL source:

```bcpl
GLOBAL $( START:1; WRITEF:76 $)

LET START () BE
$(1
    WRITEF("C:%C S:%S N:%N", 'Z', "HI", 42)
    FINISH
$)1
```

Its independent [expected.txt](../../tests/bootstrap/075-blib-writef-mixed-object/expected.txt) is:

```text
C:Z S:HI N:42
```

The early JOB 2583 had zero assembler, linker and GO return codes but emitted `N:2`, so it failed. A later G!76 binding correction passed cases 075 and 076; do not erase the earlier incident. The current installed profile is the BOOT namespace, not the old OBJ path in the case's historical description.

Use the coordinator to select a focused case. First inspect its identity offline; then execute only when authorized:

```sh
tools/tests/run-suite bootstrap --list --case 75
tools/tests/run-suite bootstrap --run --profile production --case 75
```

The second command invokes the native backend and submits real JES jobs. Require an exact matching case PASS with the complete expected return-code and output evidence, not simply one line of plausible output.

For the interpreted path, the installed ICINT19 smoke command is:

```sh
tools/mr10/compile-and-run --installed-icint MR10_LOAD --results     mr10-kit-compiler/tests/00-regression-panel/data-movement/scalar-vector.bcpl
```

SCALVEC prints EXP/RP records; the tracked [independent oracle](../../mr10-kit-compiler/tests/00-regression-panel/data-movement/scalar-vector.expected) is:

```text
RP: SCALAR 17 42
RP: VECTOR 5 10 15 20
```

The interpreted result and applicable `CODE=` records must also pass. The MR10 panel performs its independent checks; the smoke invocation is not a substitute for the panel. Without `--installed-icint`, the direct driver can assemble the selected interpreter source. For investigation use its supported `--save-ocode`, `--save-intcode` and `--artifact-dir` controls, with artifacts under `workarea/`. Preserve source selection and independent goldens.

| Native selection | Actual linkage scope |
| --- | --- |
| `production` | Installed `BOOT_OBJ`; source-selected R.5/T.1 extension tests when needed |
| `installed-r5-t1` | Installed `BOOT_OBJ`, installed R.5/T.1 extension objects and macros |
| Both profiles, QSAM 163–176 | Source-selected BCPLQSAM; not new installed-BCPLQSAM execution evidence |
| Both profiles, coroutines 177–189 | Pinned CO.2–CO.4 candidate-source tests; not a substitute for installed-only coroutine verification |
| Historic source instrumentation | Case 083 requires source-only counters; expected SKIP in the two installed-BOOT_OBJ profiles |

The explicit production wrapper sets the runtime PDS and OBJ selection and clears inherited runtime-candidate settings. Do not mix environment overrides or historical DEVOBJ flags into that profile. The installed R.5/T.1 profile still does not change QSAM or coroutine candidate selection. For a candidate not covered by the standard profiles, use a separately reviewed source-selected test adapter and record its actual inputs and linkage.

## 5. Testing — native 00–192, MR10 baseline/supported/development and paired coroutine suites

The [native suite manifests](../../tests/README.md) and MR10 manifests retain ownership of test identities. Use the project coordinator for regular campaigns and `run-suite` for focused native selection. `--check` and `--list` are host-only; `--run` submits jobs. An explicit native profile is required for native execution; paired coroutine cases have their own pinned compile/linkage choices.

| Regular suite selector | Identity | Cases | Last accepted supported outcomes |
| --- | --- | ---: | --- |
| `mr10` | Independent MR10 Regression Panel | 12 | 12 PASS |
| `mr10-coroutines-supported` | Five valid-domain interpreted cases | 5 | 5 PASS |
| `bootstrap` | 00–145, 190–192 | 149 | 148 PASS, 1 SKIP (083) |
| `runtime-extensions` | 146–158 | 13 | 13 PASS |
| `bcpltime` | 159–162 | 4 | 4 PASS |
| `bcplqsam` | 163–176 | 14 | 14 PASS, device opt-in |
| `coroutines` | 177–189 | 13 | 13 PASS |
| `coroutine-contract` | co6-pair, co6-nested | 2 | 2 PASS |

The historical eight-suite campaign is recorded in [CO.6 formal qualified closure](../../packaging/milestones/coroutines/co6-formal-acceptance-and-closure-20261116.md), tested revision `216b6707c404a91c796ed8f1419a99ef172b184a`: 208 PASS, 0 FAIL, 0 BLOCKED, 1 expected SKIP. The [DR.5 supported campaign](../../packaging/milestones/documentation-refactoring/candidates/compiler-verification/README.md) at source revision `3f6a417504ab721c080d5af1ffaf54b580ea346b` reported 211 PASS, 0 FAIL, 0 BLOCKED, 1 expected SKIP; the table above reflects that campaign. Neither result is proof that a later checkout has been tested.

Inspect selections or run a deliberately limited campaign:

```sh
tools/tests/run-project-regressions --list
tools/tests/run-project-regressions --check
tools/tests/run-project-regressions --run --suite mr10 --progress
tools/tests/run-project-regressions --run --suite bcpltime     --profile installed-r5-t1 --progress
```

The last two commands are separate examples of authorized execution, not an unattended script. The coordinator stops before starting another selected suite after a failed or blocked suite. A NOT_RUN or NOT_SELECTED suite is not a PASS. `--progress` changes console reporting, not scope, authorization or verification.

MR10 diagnostics remain independent:

- `mr10-probes` selects eleven accepted-contract development probes from the [17-entry historical manifest](../../mr10-kit-compiler/tests/dev-probes-manifest.tsv). Six experimental probes remain outside this selection; an observation without an accepted oracle is not PASS.
- `mr10-coroutines` selects the five original historical coroutine probes, retaining the actual fixed-stack first-activation `CODE=-1` failure. The accepted historical campaign was four PASS and one FAIL. A bounded continuation option collects later evidence only after that exact known failure; the case and suite remain FAIL. Do not reinterpret the manifest's ACCEPTED contract label as a passing execution.
- `mr10-coroutines-supported` uses its [separate manifest](../../mr10-kit-compiler/tests/10-coroutines/supported-manifest.tsv), including the separately named valid-frame fixed-stack candidate. Four cases overlap the historical selection; do not count them twice or replace the original source/expected output.
- `coroutine-contract` uses the [paired manifest](../../tests/suites/coroutine-contract.tsv): the interpreted and native engines must independently match the same 11-record co6-pair or 18-record co6-nested oracle. It requires both receipts, not shared descriptor layout or identical global numbers.

For an individual diagnostic, inspect `tools/mr10/run-dev-probes --list` and use explicit `--run --case CASE_ID` only under approved scope. `--all-provisional` retains the original six-case selection; `--all-candidates` submits the entire 17-entry selection and is not the regular regression campaign.

The native 193-case inventory (including 083) is separate from MR10 and paired cases. Preserve all IDs and expected files when extending test coverage. Update the appropriate manifest and verify unique ownership, expected files and reporting semantics before execution. Do not invent a new test ID or change existing policy without the required review.

## 6. Testing — offline versus MVS results, JES, printer/punch attribution and failure evidence

Host checks validate source structure, manifest coverage, generated decks, parser behavior and synthetic receipts. They do not prove actual resident PDS contents, IFOX, IEWL, MVS allocation, application behavior or physical SYSOUT output. Verify at each layer, retaining exact source and configuration, job name and number, expected steps, return codes, abends, IFOX severity, IEWL map, ICINT completion and the relevant oracle.

For ordinary submitted jobs the common utilities support a pre-submission printer cursor. The following is a **syntax pattern**, not a supplied executable deck: replace the placeholders with the reviewed scratch JCL, unused cursor path and actual returned JES job identity. Execute each operation separately with its result checked; do not proceed after ambiguous submission.

```sh
tools/mvs/submit-jcl --cursor-file workarea/candidate.cursor workarea/candidate.jcl
tools/mvs/job-summary JOBNUMBER --cursor-file workarea/candidate.cursor
tools/mvs/dump-report-for-job JOBNUMBER --cursor-file workarea/candidate.cursor
```

Do not trust an old job report selected only by a reused job number. The guarded cursor uses the printer identity and pre-submission offset, validating that earlier data was not replaced or truncated. An invalid cursor fails closed. For the numbered native regression path the printer-window default is enabled; `BCPL_PRINTER_WINDOW_TRIAL=0` explicitly requests the legacy full-file reader. Generic reporting and independently invoked `compile-mvs` retain their established opt-in defaults. See the [printer-window default decision](../../packaging/operations/maintenance/jes-printer-window-default-decision-20261110.md). Preserve the cursor, source, job identity and new output, including failure evidence.

Device tests require separate authorization. BCPLQSAM case 175 sends FB80 binary card images to the JES punch, and 176 sends FBA133 output to the printer. Without `--allow-device` they are BLOCKED, not SKIP. Neither a successful PUT nor GO RC=0 alone proves the physical output. Use the suite's bounded independent printer/punch capture and exact device-specific checks.

The current `run-suite` and project coordinator strip inherited punch-resume settings. Explicit device opt-in for case 175 alone permits a guarded single `$S PUN1` when PUNCH1 is paused (`P=Y, Q=B`) and a fresh queue check identifies only the current Q4PUNCH job. Unrelated class-B work, missing target or ambiguous state blocks the start. Do not flush the queue, retry a failed start or start a writer for case 176. Case 175 additionally requires the exact new 172-byte punch image and matching job receipt. The older suite README's statement that the runner never enables the writer is superseded by actual current guarded behavior; do not reproduce the older unguarded standalone resume procedure.

| Evidence outcome | Required handling |
| --- | --- |
| Offline check fails | Diagnose checker/source mismatch; do not submit dependent jobs |
| JES submission ambiguous or timed out | Investigate actual outstanding job and effects; no automatic resubmission |
| IFOX, IEWL, ICINT or GO failure | Preserve listing/report and exact step or completion result; do not claim success |
| Oracle mismatch with zero RCs | FAIL; investigate code, not the golden output |
| Missing/ambiguous capture or required device approval | BLOCKED or FAIL according to the actual runner; no bypass |
| Expected case 083 installed skip | Retain SKIP reason; not a new test PASS |

Preserve the [Q.5 closure](../../packaging/milestones/qsam/qsam-q5-closure-20261101.md) qualification (175 FAIL followed by a separate successful rerun), the earlier CO.5 Bootstrap 117 LKED SB2D incident (cause not established), and the genuine MR10 historical fixed-stack FAIL. A later successful run is additional evidence, not a rewrite of earlier results. No retry authorization carries over from an earlier release or guarded device operation.

## 7. Review and promote — controlled installation, evidence and rollback

Promotion is a distinct owner decision after the contract, source, candidate tests and reproducibility evidence are reviewed. Do not overwrite accepted objects just to shorten a development cycle. Record the exact input revision and any generated-source hashes, candidate object selection and intended installed member set. Determine the last known-good reproducible revision, dependencies and recovery procedure before the write. A prior installed binary without provenance is not guaranteed recoverable.

| Gate | Evidence required before advancing |
| --- | --- |
| Candidate build | Actual IFOX success and intended symbols; no unintended permanent writes |
| Candidate integration | Correct IEWL map/registrations; focused independent execution oracles and applicable regression results |
| Readiness and owner decision | Reviewed source and exact target/write scope; recovery plan, required permissions and known qualifications |
| Installation | Actual authorized source-to-object build JCL, zero required step codes, recorded installed members and binary read-back where implemented |
| Installed acceptance | Link and run against the installed members (not substituted candidate objects); applicable complete regression and reproduction evidence |

The [CO.5 production promotion](../../packaging/milestones/coroutines/co5-production-promotion-20261115.md) is a concrete historical example. The owner approved a coordinated BCPLMAIN, BCPLCO and COROUTIN installation and permanent G!289–300 assignment. At that checkpoint manifest integration was deferred; the later [clean-room integration](../../packaging/milestones/coroutines/co5-reconstruction-integration-20261115.md) and [clean-room PASS](../../packaging/milestones/coroutines/co5-production-clean-room-pass-20261116.md) established that the promoted objects were reconstructed from Git. Do not treat the earlier deferral as the current state.

The actual [BLDCORCO](../../bootstrap-toolchain/jcl/bldcorco.jcl) and [BLDCORLB](../../bootstrap-toolchain/jcl/bldcorlb.jcl) jobs assemble, install, read back and compare their binary decks using IEBCOMPR. BLDBMAIN installs the seven runtime/registration objects; BLIBBLD has no IEBCOMPR step. Use the current source reconstruction manual for the complete installed inventory and procedure. Do not adopt the historical pre-M3 paired OBJ commands as the current installation instructions.

For separately authorized installed-coroutine verification, the following actual verifier compiles the accepted CO.3 application, link-edits against the installed BOOT_OBJ objects and tests its ordered 21-record oracle. It does not overwrite the installed object library.

```sh
python3 -B tools/coroutines/verify-installed-production.py --check
python3 -B tools/coroutines/verify-installed-production.py --run
```

The first operation is host-only; the second submits MVS jobs. A native candidate-source suite PASS alone cannot replace this installed-only verification. Preserve the qualified coroutine domain (root and at most two live registered workers, fixed 1024-word worker stacks and known-live descriptor lifecycle), not broader unverified behavior. For other components require their own installed-object test and accepted contract; the QSAM source-selected regression profile does not prove installed QSAM linkage.

If installation fails partway through, freeze further writes, retain actual job results and determine which members changed. Multi-member replacement is not atomic. Do not assume the previous binary decks are backed up. With separate approval rebuild a coherent known-good source revision using its verified dependency/installation procedure, or correct and redeploy a newly reviewed candidate if that is the approved recovery. Rerun installed tests and record any inability to restore exact incumbent bytes. Do not automatically roll back, purge, retry or publish.

## 8. Full regression, record evidence, maintain documentation and obtain acceptance

After focused tests and any authorized installation, run the applicable full supported regression campaign. Use the exact command and device-approval prerequisites in [How to Reconstruct BCPL from Source, Chapter 6](How-to-Reconstruct-BCPL-from-Source.md#6-verify-installation-and-run-supported-regressions). It selects the eight supported suites in Chapter 5, with explicit production profile and separately authorized device cases. Do not append the historical FAIL selection and describe it as an all-PASS regular campaign. Run additional diagnostics independently where needed. A full regression is not an instruction to rebuild or promote.

Check the newly generated `workarea/project-regressions/<run>/summary.json`, per-suite logs, `workarea/test-suites/` case receipts and relevant printer/punch evidence. Each run has its own scope; preserve per-suite accounting and retain omitted, blocked and not-run distinctions. Keep reports needed for acceptance outside disposable `workarea/` before cleanup. Follow the [distribution evidence preservation rules](../../packaging/distribution/README.md) for protected release materials and consumed one-shot markers. Do not commit private credentials or unredacted authenticated decks.

An acceptance record should identify the milestone/march and decision requested, Git revision and dirty/clean status, exact tool/profile and installed/candidate objects, target and job receipts, independent expected/observed results, PASS/FAIL/SKIP/BLOCKED/NOT_RUN counts, known limitations and preserved earlier failures. Classify owner-reported execution distinctly from independently reviewed raw receipts. If the change modifies public behavior, update the appropriate source contract and working reference; maintain the registry, config, manifest and oracles according to their independent authorities. Never move normative authority by editing a manual alone.

The goal is a small reproducible change, independently verified on MVS and reflected in coherent documentation. Seek the owner's acceptance before closing a march. DR.5 retains detailed reconciliation and integrated validation responsibilities. Neither a regression PASS nor documentation acceptance authorizes release production, publication, destructive reconstruction or another milestone's closure.
