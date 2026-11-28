# How to Reconstruct BCPL from Source

**Audience:** Project maintainers operating a dedicated Hercules/TK5 MVS 3.8J development system.  
**Status:** Reconciled procedural guide; original DR.3 review at `2ca15e3feef49eb803bb962ee1644ca97945e44b`. Current operational verification remains pending.

This procedure reconstructs the MR10 Kit Compiler environment, interpreter-hosted demoted Cambridge Compiler, native application runtime, Base Library, native coroutine support and installed System Extensions from repository inputs. It does not build the unfinished native-running Cambridge Compiler, recreate TK5, install a distribution tape, produce a release or authorize promotion of development objects.

**Destructive operation:** A clean-room rebuild removes managed host workarea contents and recreates the configured BCPL datasets, including installed object and load libraries. Obtain explicit authorization for the actual target and scope. Commands below are documentation, not permission to execute them.

The existing [automated rebuild guide](../Rebuild-BCPL-for-MVS-from-source.md) and [manual rebuild procedure](../Manual-Rebuild-BCPL-for-MVS.md) remain operative. This guide consolidates their supported workflow without retiring either path; public tool interfaces are governed by the approved Project Tools reference. For installation from released media, see [How to Install BCPL from Tape](../product/How-to-Install-BCPL-from-Tape.md).

[Documentation catalog](../README.md)

## 1. Establish Git revision, dedicated MVS and prerequisites

Use the Git repository root and an operational, dedicated TK5 instance. The host requires the repository's Docker Compose environment, Bash, Python 3 and the existing project tools and their dependencies. The build runs real MVS jobs through the configured reader and uses the Hercules printer output to identify and verify their results. Ensure adequate host and MVS storage. Do not use a shared production MVS installation as the reconstruction target.

The tracked [dataset configuration](../../config/dspal.yaml) provides the defaults. The ignored `config/dspal.local.yaml` supplies site overrides and credentials. Never publish authentication information, including in diagnostic logs. Inspect the effective settings rather than assuming the defaults below apply.

| Setting | Tracked default |
| --- | --- |
| MVS user/HLQ | `HERC02` |
| Write boundary | `HERC02.**` |
| Docker container | `mvs38j` |
| Reader | `127.0.0.1:3505` |
| Hercules HTTP | `127.0.0.1:8038` |
| Printer file | `mvs-state/prt/prt00e.txt` |

The canonical build JCL contains explicit `HERC02` dataset names. A local HLQ override alone does not make this procedure safe for another namespace; reconcile all affected JCL and tools before attempting a site adaptation.

Before approval, inspect the intended source and target from the repository root:

```sh
git status --short
git rev-parse HEAD
tools/datasets/dspal info
tools/datasets/dspal purgebcpl --show-jcl
tools/datasets/dspal initbcpl --show-jcl
tools/bootstrap/prepare-bootstrap --check-inputs
```

Resolve local changes and review the selected revision before proceeding. The simple rebuild driver prints Git status, runs `git pull --ff-only`, and prints the resulting HEAD. Printing status does not enforce a clean checkout, and a successful pull can change HEAD. If approval refers to a particular revision, ensure that revision is current and that the driver's pull cannot silently introduce an unreviewed revision; stop and renew scope approval on drift. The interactive checkpoint before Step 1 permits review after the pull. Do not use unattended execution if this prerequisite cannot be established.

Step 0 starts TK5 if necessary and probes the target. This is not a JES-idle check. See [the dedicated TK5 operating decision](../../packaging/distribution/dedicated-tk5-operator-controlled-reconstruction-decision-20261106.md).

## 2. Review destructive scope; preserve evidence and authorize cleanup

Stop independent submissions and let earlier JES work finish. During reconstruction do not launch other compile, dataset, regression, JES, reader, console or 3270 submissions or another reconstruction controller. There is no cooperative submission lock. A read-only idle observation is not a reservation of JES.

The tracked configuration defines 29 logical PDSs at the reviewed revision. The purge list is the effective managed dataset selection, not an instruction to delete every dataset matching the HLQ or a guessed prefix. Review the actual names and allocation attributes before authorizing destruction.

| Managed group | Count | Purpose |
| --- | ---: | --- |
| `MR10_*` | 9 | MR10 source, assembler, JCL, library, demos, tests, objects and load modules |
| `CAMB_*` | 9 | Cambridge development namespace; its existence does not establish a native-running compiler |
| `BOOT_*` | 6 | Bootstrap source, INTCODE, assembler, JCL, installed and development objects |
| `EXT_*` | 4 | Extension source, assembler, macros and objects |
| `DIST_DOCS` | 1 | Distribution documentation inputs; not the frozen release companion |

Preserve needed host output, JES reports, regression summaries, release evidence, seals, tape images and no-retry markers in their designated protected locations before cleanup. Do not rely on disposable `workarea/` surviving. Preserve `workarea/.gitignore`; do not manually delete unrelated Git or MVS files. The tracked allocation map is not the release manifest or the release registry. Do not consume or replay a one-shot release operation to reconstruct the development environment. See [distribution evidence and preservation rules](../../packaging/distribution/README.md).

The supported routine driver, [`rebuild-from-source`](../../tools/reconstruction/rebuild-from-source), is deliberately simple. Its interactive confirmations and explicit unattended option differ from the separately designed scope-fingerprinted controller. The simple driver has no integrated JES console probe or immutable-plan gate. Operator responsibility for scope, revision, target and quiescence is therefore essential.

For additional inspection, the separate [reconstruction tools](../../tools/reconstruction/README.md) provide a read-only `plan` (optionally `--probe`) and `run --check-live-guard`. The latter requires two independently qualifying CLEAR observations; ACTIVE, ambiguous, incomplete or unknown responses block. Use it only as an additional read-only diagnostic, not as approval. The standalone `authorize` is an exercise and cannot grant reusable approval. The separate `run --run` path requests an exact interactive scope-bound acknowledgment; it has not inherited live acceptance from the simple driver. Do not substitute that path for the supported routine rebuild or use it for a negative test.

## 3. Perform interactive reconstruction

For routine reconstruction after reviewing and approving the destructive scope, use the existing driver:

```sh
tools/reconstruction/rebuild-from-source
```

| Prompt | Required operator action |
| --- | --- |
| `hit ENTER to continue` | Review prior results and the next step; Enter only when safe. |
| `DELETE` | Authorize removal of managed host workarea contents. |
| `YES` | Authorize deletion of the displayed BCPL MVS datasets. |
| Extension installation checkpoint | Review the actual payload job, IFOX severity and IEBCOMPR result before the next installation. |

Stop on unexpected output, wrong target, incomplete or failed payload, or a changed source/configuration scope. The driver returns nonzero on command failure; interactive checkpoint cancellation stops the run. It always starts at Guide Step 0; no step selection, resume or checkpoint restart is supported. Guide Step 4 is not part of the current sequence; do not renumber or infer a missing build action.

Interactive mode can also request `--batch-populate` to reduce transfer submissions without skipping confirmations. Successful completion prints `REBUILD COMMANDS COMPLETED` and elapsed time. Save evidence separately; this message does not establish complete regression or release acceptance.

## 4. Perform unattended/batch population when explicitly authorized

When the complete deletion and reconstruction scope has been explicitly authorized, the accepted unattended invocation is:

```sh
tools/reconstruction/rebuild-from-source --unattended --batch-populate
```

`--unattended` is the destructive authorization for that invocation; it skips all driver confirmations and invokes the cleanup and purge tools with `--yes`. It does not bypass command-failure stops, but it also skips the manual extension payload inspection checkpoints. Review those receipts afterwards. The flag neither grants permanent authorization nor runs regressions or release steps.

`--batch-populate` is independent: it selects bounded per-PDS IEBGENER batching for both actual population passes. Without it, the default is one member per JES job. The dry runs remain previews; they do not submit population jobs. Batch mode does not authorize deletion and does not change the source selection. A failed or ambiguous batch is not permission to resubmit it automatically.

After the initial population, exactly twelve generated members may be unavailable. The driver treats RC=2 as the expected first-pass exception only when the output identifies twelve `MISSING GENERATED:` records, the matching generated-member diagnostic and a positive count of ready members planned or written, as appropriate. Any other RC=2 is a failure. After generating bootstrap inputs, the generated-only population must complete with RC=0. See [dspal population source](../../tools/datasets/dspal-populate.py).

The [9 November batch closure](../../packaging/distribution/clean-room-batch-reconstruction-closure-20261109.md) records a successful unattended batch reconstruction, subsequent independent regression and 71/71 canonical member-text comparisons. Four MR10 test members remain qualified for trailing blank-record counts; normalized text equality is not raw EBCDIC byte fidelity. Later [CO.5 production reconstruction](../../packaging/milestones/coroutines/co5-production-clean-room-pass-20261116.md) established the ten-object baseline. These are recorded results, not a promise of identical runtime or results on a new revision.

## 5. Understand stages — ICINT19, bootstrap/CAMBCOMP, Core Runtime, BLIB, coroutines and extensions

| Guide step | Actual operation | Required result |
| --- | --- | --- |
| 0 | Git, TK5, effective configuration and input checks | Correct source revision and target; inputs available |
| 1 | Host cleanup | Managed workarea cleared; `.gitignore` retained |
| 2 | Purge, allocate, populate Git-backed members | Approved datasets recreated; first-pass generated-member exception only |
| 3 | `MR10_JCL(IC19BLD)` and SCALVEC smoke test | Installed `MR10_LOAD(ICINT19)` and `MR10_OBJ(ICINT19)`; successful interpreted execution |
| 5 | Prepare bootstrap inputs with TRNILRG and populate generated members | Generation manifest and generated-only transfer successful |
| 6 | `BOOT_JCL(CAMBBLD)`; compile a smoke program and coroutine library | Resident `BOOT_INTCODE(CAMBCOMP)`, nonempty native assembler output and staged `BOOT_ASM(COROUTIN)` |
| 7 | `BOOT_JCL(BLDBMAIN)` | Seven initial runtime/registration object members |
| 8 | `BLIBBLD`, `BLDCORCO`, `BLDCORLB` | Exact ten-member installed baseline and independent installed-coroutine verification |
| 9 | `BCPLDEMO`, `BCPLTIME`, `BCPLQSAM` jobs | Three installed optional extension objects and read-back evidence |

The [ICINT19 build JCL](../../mr10-kit-compiler/jcl/build-icintv19.jcl) uses IFOX00, IEWL and IEBGENER to create the interpreter load module and preserve its relocatable object. The [CAMBBLD job](../../bootstrap-toolchain/jcl/cambbld.jcl) uses the installed interpreter, MR10 phases and rebuilt TRNILRG to generate the demoted Cambridge compiler as INTCODE. CAMBCOMP executes under ICINT19 and emits System/370 assembler for native applications; it is not itself a native-running compiler. See [Explanation of BCPL Compilers](../product/Explanation-of-BCPL-Compilers.md).

[BLDBMAIN](../../bootstrap-toolchain/jcl/bldbmain.jcl) assembles and installs the initial seven runtime and registration objects. [BLIBBLD](../../bootstrap-toolchain/jcl/blibbld.jcl) compiles historical BLIB with CAMBCOMP using its own P2000 free-stack reservation, copies the FB132 compiler report to JES in COMPRPT, requires one exact interpreted CODE=0 in FIXASM before reading generated assembler, repairs the generated cards, assembles them and installs the object. This BLIB-only parameter does not change ICINT19 or default compiler options. All subsequent JCL steps require zero prior step return codes. [BCPLCO](../../bootstrap-toolchain/jcl/bldcorco.jcl) is assembled from tracked source; [COROUTIN](../../bootstrap-toolchain/jcl/bldcorlb.jcl) is assembled from prepared output of the tracked [BCPL coroutine library](../../bootstrap-toolchain/library/coroutines.bcpl). Both coroutine installation jobs compare read-back object records against their assembled decks. Do not reuse a prior object or copy a candidate from `BOOT_DEVOBJ` in place of a source build.

Installed System Extensions remain optional application link/registration selections, not mandatory parts of the Core Runtime. Their build jobs are [BCPLDEMO](../../bootstrap-toolchain/jcl/bcpldemo.jcl), [BCPLTIME](../../bootstrap-toolchain/jcl/bcpltime.jcl) and [BCPLQSAM](../../bootstrap-toolchain/jcl/bcplqsam.jcl). The [runtime and library nomenclature](../../packaging/architecture/runtime-and-library-nomenclature.md) governs logical component names, distinct from physical object libraries. RC4 is a different distribution scope and does not contain CAMBCOMP.

## 6. Verify installation and run supported regressions

Review the actual payload JES job, not merely the launcher or a host command's zero exit code. Require the expected steps and applicable return codes, IFOX severity, interpreted `CODE=` completion records, and read-back comparisons where the JCL implements them. A directory listing proves membership, not executable semantics. A successful compile producing assembler is not native execution.

The installed object checks are:

```sh
python3 -B tools/reconstruction/verify-boot-obj.py
tools/datasets/dspal ls EXT_OBJ
```

`BOOT_OBJ` must contain exactly the ten members below. `EXT_OBJ` must contain the three optional extension objects. Review the individual build receipts for completeness.

| Role | Required members |
| --- | --- |
| Initial runtime and registration objects | `BCPLMAIN`, `BCPLMEM`, `BCPLBYTE`, `BCPLAPT`, `BCPLIO`, `BCPLRGS`, `BCPLREG` |
| Base Library | `BLIB` |
| Native coroutine support | `BCPLCO`, `COROUTIN` |
| Optional extension objects (separate PDS) | `BCPLDEMO`, `BCPLTIME`, `BCPLQSAM` |

The driver runs the [installed coroutine verifier](../../tools/coroutines/verify-installed-production.py) during Step 8. It compiles the CO.3 delete/reuse application and verifies native IFOX/IEWL/GO execution against installed objects and the independent 21-record output oracle. A separate invocation with `--run` submits MVS work and requires authorization. It must not substitute development candidates for installed objects.

The three extension jobs each require successful assembly, installation, read-back and `IEBCOMPR` comparison. `BLIBBLD` does not contain an equivalent IEBCOMPR step: verify COMP, COMPRPT, PREPASM, PREPLK, FIXASM, ASMBLIB and INSTALL, one exact successful interpreted completion, inventory and downstream execution, without inventing a compare receipt. The private [BLIB build-integrity diagnostic](../../tools/checks/run-dr5-blib-build-verification.py) exercises the same job with a temporary output object and a deliberately failing compilation; it does not install BLIB. BCPLQSAM ordinary cases 163–176 run source-selected under production or with resident objects under installed-r5-t1; both scopes have accepted evidence, including independent selection/exclusion. Cases 198–200 use private instrumented objects under both profiles. Earlier acceptance is not proof of freshly reconstructed installed-object identity.

Regression is a separate operation. First perform the host-only manifest check:

```sh
tools/tests/run-project-regressions --check
```

Then, **only with explicit MVS and printer/punch authorization**, use the full supported campaign:

```sh
tools/tests/run-project-regressions \
    --run \
    --suite mr10 \
    --suite mr10-coroutines-supported \
    --suite bootstrap \
    --suite runtime-extensions \
    --suite bcpltime \
    --suite bcplqsam \
    --suite coroutines \
    --suite coroutine-contract \
    --profile production \
    --allow-device \
    --progress
```

`--allow-device` authorizes BCPLQSAM cases 175–176, including the guarded single punch-writer start for case 175 only. An unverified device/queue state or unrelated class-B work blocks the start; do not flush the queue or retry a failed start. Case 176 never starts the punch writer. Without explicit device permission, do not claim the full campaign passed. See the [test runner guide](../../tools/tests/README.md) for profile and device restrictions. The coordinator stops before another suite on failure or blockage and retains independent oracles and per-suite outcomes.

The [CO.6 formal qualified closure](../../packaging/milestones/coroutines/co6-formal-acceptance-and-closure-20261116.md) records this supported campaign at tested revision `216b6707c404a91c796ed8f1419a99ef172b184a`:

| Suite | PASS | FAIL | SKIP | BLOCKED |
| --- | ---: | ---: | ---: | ---: |
| `mr10` | 12 | 0 | 0 | 0 |
| `mr10-coroutines-supported` | 5 | 0 | 0 | 0 |
| `bootstrap` | 145 | 0 | 1 (083) | 0 |
| `runtime-extensions` | 13 | 0 | 0 | 0 |
| `bcpltime` | 4 | 0 | 0 | 0 |
| `bcplqsam` | 14 | 0 | 0 | 0 |
| `coroutines` | 13 | 0 | 0 | 0 |
| `coroutine-contract` | 2 | 0 | 0 | 0 |
| **Supported total** | **208** | **0** | **1** | **0** |

DR.5 subsequently added Bootstrap cases 190–192 to the same supported campaign (no change to the eight-suite command). The [DR.5 supported campaign](../../packaging/milestones/documentation-refactoring/candidates/compiler-verification/README.md) at source revision `3f6a417504ab721c080d5af1ffaf54b580ea346b` reported 211 PASS, 0 FAIL, 1 expected SKIP (083), 0 BLOCKED, including 148 Bootstrap passes. The subsequent [DR.5 BCPLIO campaign](../../packaging/milestones/documentation-refactoring/dr2-runtime-library-manual-migration-20261125.md) at revision `a0efe9a204e1f3f3968b60cb8c7065e9b423bce7` reports 212 PASS, 0 FAIL, 1 expected SKIP (083), 0 BLOCKED, including 149 Bootstrap passes. These are historical full campaigns, not clean-room results; neither replaces the historical CO.6 result above. The [DR.5 System Extensions evidence](../../packaging/milestones/documentation-refactoring/dr2-extension-manual-migration-20261125.md) records 17 Runtime Extensions passes, all 14 ordinary BCPLQSAM cases accepted in source and installed modes, and private diagnostics 198–200 accepted across native runs and retained JOB 1300 evidence reconciliation. The original 2 PASS / 1 FAIL diagnostic receipt remains unchanged. The current supported inventory is 220 selected, with 219 distinct accepted passes and one expected SKIP (083) across separate campaigns; a single consolidated campaign remains outstanding. A new reconstruction requires its own evidence. See [native suite inventory](../../tests/README.md).

The original `mr10-coroutines` historical suite independently returned four PASS and one genuine FAIL (manual fixed-stack first activation, `CODE=-1`). Do not replace its unchanged oracle with that of the supported valid-frame case, reclassify it as SKIP/XFAIL, or add overlapping historical passes to the supported total. `mr10-probes` is a distinct diagnostic selection, not part of the eight-suite supported campaign. An earlier Bootstrap 117 IEWL SB2D failure remains recorded despite subsequent passing runs.

Require the new campaign's `PROJECT REGRESSION RESULT: PASS` and inspect the new per-suite counts and evidence; prior PASS is not a substitute. Save `workarea/project-regressions/` summaries and suite logs, native `workarea/test-suites/` receipts and relevant JES reports outside disposable workarea before another cleanup. Retain both failures and successful receipts with source SHA and configuration identity, without credentials.

## 7. Perform manual stage-by-stage reconstruction with stop/review gates

Use manual reconstruction when diagnosing a stage or when the automated driver is inappropriate. The following sequence follows the existing manual procedure and current driver. Run **one command at a time** and inspect its exit status and MVS payload before advancing. These blocks are not fail-stop scripts and must not be pasted as one unguarded batch. Review and authorize the destructive steps exactly as in Chapter 2. Do not resume a failed automated run from a later step.

### Step 0 — preflight

```sh
git status --short
git pull --ff-only
git rev-parse HEAD
tools/mvs/start-tk5 --detached
tools/datasets/dspal status --probe
tools/datasets/dspal info
tools/bootstrap/prepare-bootstrap --check-inputs
```

Stop on revision or configuration drift. The `dspal status --probe` command submits an actual IEFBR14 JES job and checks its result; it is not merely a host readiness observation or a JES-idle check. Confirm that the probe and other prior jobs have completed and that the operator has exclusive control before deleting anything. The separate reconstruction `plan --probe` performs host/endpoint observations without submitting a JES job.

### Step 1 — clean host workarea

```sh
tools/clean-workarea
git status --short
```

Review the removal list and type `DELETE` only after preservation and explicit approval. The tool retains the tracked `.gitignore`.

### Step 2 — recreate and populate managed datasets

```sh
tools/datasets/dspal purgebcpl --show-jcl
tools/datasets/dspal purgebcpl
tools/datasets/dspal initbcpl --show-jcl
tools/datasets/dspal initbcpl
tools/datasets/dspal stat
tools/datasets/dspal populate all --dry-run
tools/datasets/dspal populate all
tools/datasets/dspal ls
```

Review the exact DSNs before confirming `YES`. Check both first-pass population results against the twelve-generated-member rule in Chapter 4. Do not accept an unrelated RC=2 or missing tracked source. If explicitly choosing batching, add `--batch` only to the actual population command.

### Step 3 — build and execute ICINT19

```sh
tools/datasets/dspal submit MR10_JCL IC19BLD
tools/datasets/dspal ls MR10_LOAD
tools/datasets/dspal ls MR10_OBJ
tools/mr10/compile-and-run --installed-icint MR10_LOAD --results \
    mr10-kit-compiler/tests/00-regression-panel/data-movement/scalar-vector.bcpl
```

Inspect the assembler, link-editor and save-object steps. Inspect the smoke application's interpreted completion and result records. The [actual SCALVEC source](../../mr10-kit-compiler/tests/00-regression-panel/data-movement/scalar-vector.bcpl) prints `EXP: SCALAR 17 42` and `EXP: VECTOR 5 10 15 20`; the corresponding `RP:` values must agree and completion must be `CODE=0`. The independent regression oracle remains a separate gate.

### Step 5 — generate bootstrap inputs

```sh
tools/bootstrap/prepare-bootstrap --with-trnilrg
cat workarea/bootstrap-cambridge/prepare-bootstrap-manifest.json
tools/datasets/dspal populate all --generated-only --dry-run
tools/datasets/dspal populate all --generated-only
tools/datasets/dspal ls BOOT_SOURCE
tools/datasets/dspal ls BOOT_INTCODE
```

Require `trnilrg_rebuilt` to be true, generated input/output manifest consistency and RC=0 for the generated-only population. Add `--batch` to the actual generated-only population only if desired. The preparation tool does not itself populate PDSs.

### Step 6 — rebuild CAMBCOMP and prepare COROUTIN

```sh
tools/datasets/dspal submit BOOT_JCL CAMBBLD
tools/datasets/dspal ls BOOT_INTCODE
tools/bootstrap/compile-mvs \
    tests/bootstrap/00-most-degenerate-bcpl-program/source.bcpl \
    --output workarea/m3-clean-smoke.s370.asm
test -s workarea/m3-clean-smoke.s370.asm
tools/bootstrap/compile-mvs \
    bootstrap-toolchain/library/coroutines.bcpl \
    --job-name COPRLCMP \
    --cambridge-parm \
        packaging/milestones/coroutines/candidates/co3-delete-reuse/cambridge-parm.txt \
    --output workarea/co5-production/coroutines-generated.asm
python3 -B tools/coroutines/prepare-production-library.py \
    --compiled workarea/co5-production/coroutines-generated.asm \
    --output workarea/co5-production/coroutin-prepared.asm
test -s workarea/co5-production/coroutin-prepared.asm
tools/datasets/dspal put BOOT_ASM COROUTIN \
    workarea/co5-production/coroutin-prepared.asm
```

Require CAMBCOMP in the expected library and successful interpreted compiler phase completion. Inspect generated assembler and prepared output before staging. Do not reuse an earlier installed coroutine object. Treat the selected compiler PARM as part of the source-controlled production build contract.

### Step 7 — initial runtime and registration objects

```sh
tools/datasets/dspal ls BOOT_ASM
tools/datasets/dspal ls BOOT_JCL
tools/datasets/dspal ls BOOT_OBJ
tools/datasets/dspal submit BOOT_JCL BLDBMAIN
tools/datasets/dspal ls BOOT_OBJ
```

Verify all IFOX and installation steps and the seven initial objects listed in Chapter 6.

### Step 8 — BLIB and coroutine objects

```sh
tools/datasets/dspal submit BOOT_JCL BLIBBLD
tools/datasets/dspal submit BOOT_JCL BLDCORCO
tools/datasets/dspal submit BOOT_JCL BLDCORLB
python3 -B tools/reconstruction/verify-boot-obj.py
python3 -B tools/coroutines/verify-installed-production.py --run
tools/datasets/dspal ls BOOT_DEVOBJ
```

Inspect the actual build receipts. Require the two coroutine read-back comparisons, the ten-member inventory PASS and successful installed-only application verification. BLIB has its own build steps; do not require an IEBCOMPR step that is not in its JCL. Never substitute `BOOT_DEVOBJ` for the installed baseline.

### Step 9 — extensions

```sh
tools/datasets/dspal ls
tools/datasets/dspal submit BOOT_JCL BCPLDEMO
tools/datasets/dspal submit BOOT_JCL BCPLTIME
tools/datasets/dspal submit BOOT_JCL BCPLQSAM
tools/datasets/dspal ls EXT_OBJ
```

Submit each extension separately. Before submitting the next, inspect the actual payload's expected steps, zero return codes, zero IFOX severity and successful IEBCOMPR read-back. Verify all three required extension objects. Finish with the separate regression and evidence procedures in Chapter 6.

## 8. Diagnose failures and recover through supported procedures

The simple driver stops at the first nonzero command result except for the specifically recognized first-pass generated-member condition. If stopped, do not assume the failed job made no changes. Inspect the last command, actual payload job identity, expected JES step inventory, job termination, IFOX diagnostic severity, IEWL output and ICINT completion records as applicable. A launcher job or generic host error does not establish the payload's result.

| Observation | Action |
| --- | --- |
| Wrong revision, HLQ, reader or purge scope | Stop; reconcile source, target and approval before any destructive command. |
| Active, ambiguous or incomplete JES state | Block destructive work; inspect existing jobs and reestablish operator quiescence. |
| Unexpected missing generated member or RC=2 | Inspect generation manifest and source/transfer diagnostics; do not override the expected-count gate. |
| Submit timeout, ambiguous job identity or incomplete receipt | Determine actual MVS job state and effects; do not automatically resubmit. |
| IFOX/IEWL/ICINT failure | Preserve exact payload evidence; investigate the tracked source or JCL and obtain appropriate approval for any fix. |
| Missing installed object, read-back mismatch or application oracle failure | Preserve failure; do not accept the partially installed baseline or weaken the oracle. |
| Printer/punch verification blocked or failed | Preserve queue and device evidence; do not flush unrelated output or replay the guarded writer start. |

The supported recovery is a newly authorized, complete rebuild from Step 0 after correcting the issue and confirming that prior JES work is no longer outstanding. This entails a new purge, not resume. Preserve the failed run before cleaning; an isolated diagnostic success or a later passing campaign does not erase earlier evidence. Release-specific no-retry protections remain separate and cannot be overridden by this recovery procedure.

The recorded [CO.5 clean-room PASS](../../packaging/milestones/coroutines/co5-production-clean-room-pass-20261116.md) was owner-reported at source revision `788616e6d34325cbe6a9473edcc6be340da3e577`, with driver RC=0, exact ten-member inventory and installed coroutine compiler JOB 6489 / native JOB 6490. The later [CO.6 closure](../../packaging/milestones/coroutines/co6-formal-acceptance-and-closure-20261116.md) reports the supported campaign at its own revision. These records preserve evidence locations and qualifications; the raw private JES reports and local receipts were not independently reopened during this draft. No fresh MVS execution is claimed.

For current command details use the retained [Reference for Project Tools](Reference-for-Project-Tools.md), [reconstruction tools](../../tools/reconstruction/README.md) and [test runner guide](../../tools/tests/README.md). For component contracts use the [compiler reference](../product/Reference-for-BCPL-Compilers.md), [runtime and library reference](../product/Reference-for-the-Cambridge-Runtime-and-Libraries.md) and [System Extensions reference](../product/Reference-for-System-Extensions.md), subject to their retained authority qualifications.
