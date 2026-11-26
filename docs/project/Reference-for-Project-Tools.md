# Reference for Project Tools

**Audience:** Developers, maintainers and project operators.  
**Status:** Working reference, DR.3 — Project Documentation; reviewed at `8a5c6a8b3fa7ee2badf39756b0a2e436e6423b5c`. Existing tool contracts remain operative pending reconciliation and explicit authority transfer.

This reference describes the host tools of the BCPL for MVS 3.8 Reconstruction project. It is not an installation or execution authorization. Use the [reconstruction how-to](How-to-Reconstruct-BCPL-from-Source.md) and [development and testing how-to](How-to-Develop-and-Test-BCPL-for-MVS.md) for ordered procedures. Use the [existing release how-to](../../tools/distribution/How-to-Create-a-Release-Candidate.md) for release operations. Tool source, configuration, manifests, test oracles and owner-approved contracts retain their respective authority.

[Documentation catalog](../README.md)

## 1. Shared conventions — repository root, prerequisites and configuration

Commands in this reference are relative to the Git repository root unless stated otherwise. Uppercase operands such as SOURCE, FILE and JOBNUMBER denote substitutions, not literal filenames. Brackets denote optional syntax and vertical bars denote alternatives. Syntax descriptions are not ready-to-submit operational command blocks.

The host environment requires Bash, Python 3, Docker with Compose, netcat and ordinary Unix utilities, with the established Hercules/TK5 instance and MVS reader/printer facilities. Manifest-driven Python tools require PyYAML; the release driver requires Python 3.11 or later. Inspect the specific tool's dependencies before attempting a new host platform. The guest remains MVS 3.8J; host checks do not emulate all of its behavior.

| Path or configuration | Contract |
| --- | --- |
| [config/dspal.yaml](../../config/dspal.yaml) | Tracked managed dataset map, allocation, encoding, endpoint and identity defaults |
| `config/dspal.local.yaml` | Optional ignored override, deep-merged over tracked defaults; contains private credentials |
| [mr10-kit-compiler/asm/CURRENT](../../mr10-kit-compiler/asm/CURRENT) | Promoted interpreter selection; not the numerically highest source filename |
| `workarea/` | Disposable host-generated inputs, output and test evidence; preserve required private evidence before cleanup |
| `mvs-state/` | Persistent guest and emulator state, printers, logs, tape and protected evidence; not disposable workarea |

Tracked defaults include `HERC02`, `HERC02.**` write boundary, `SYSDA`, container `mvs38j`, reader `127.0.0.1:3505`, Hercules HTTP port `8038` and printer `mvs-state/prt/prt00e.txt`. Consult [configuration notes](../../config/README.md) and effective settings. Individual utilities can have different hard-coded/default paths or explicit endpoint overrides; do not assume that changing DSPAL configuration retargets every tool or literal JCL DSN. The default map contains 29 managed PDSs, distinct from release manifests.

| Operation class | Meaning |
| --- | --- |
| Host inspection | Reads Git/configuration, listings, saved evidence; no target execution |
| Host generation | Writes scratch files or rendered decks; no submission unless explicitly documented |
| Target inquiry | Reads live state or runs query/probe JCL; may consume JES job numbers |
| Target execution | Submits compiler, test or other JCL, or issues operational console commands |
| Persistent mutation | Changes managed members, libraries, media, registry or guest state; separate approval required |

A command's process return code, JES step RC, interpreted ICINT CODE, native GO RC and independent output verdict are different. A zero status is not a universal assertion of program correctness. Use the relevant contract and evidence. Follow [Git/MVS authority](../../packaging/operations/git-mvs-authority.md) and [WSL operator command policy](../../packaging/operations/operator-wsl-command-policy.md). Do not commit, install, purge, promote, run device tests or release without the respective approvals. Avoid fail-fast shell options and top-level exit in operator-pasted blocks; gate dependent operations explicitly.

## 2. Hercules/TK5 and MVS console/job tools

The maintained entry points are under [tools/mvs](../../tools/mvs/README.md). The old tools-root names are not a supported assumption.

| Command | Arguments and behavior |
| --- | --- |
| `start-tk5 [--attached or --detached]` | Start Docker Compose TK5; detached starts in background. Changes live host/guest state. |
| `shutdown-tk5` | Compose stop of service mvs with timeout 180 seconds. Quiesce work first. |
| `submit-jcl [--timeout SECONDS] [--cursor-file FILE] JCL` | Send a deck to JES socket reader; timeout concerns job start/assignment, not independent completion or semantic success. Optional cursor captures pre-submission printer state. |
| `job-summary JOBNUMBER [--file FILE] [--cursor-file FILE] [--max-rc RC] [--verbose]` | Read existing printer output; show job, executed steps, RCs, abend/JCL/bypass indicators, assembler information if present and resource information. Default maximum accepted RC is 4; use 0 where the test/install contract requires zero. |
| `dump-report-for-job JOBNUMBER [--cursor-file FILE]` | Extract saved job output from the printer file; not an execution operation. |
| `printer-window.py capture/read --printer FILE --cursor-file FILE` | Capture identity/offset/prefix validation or read appended bytes. Capture writes a host cursor; read rejects invalid/truncated/replaced printer data. |

`job-summary` returns 0 for its configured success predicate, 1 for a reported unsuccessful job and 2 for read/parse error. Its predicate rejects abends, JCL errors and bypassed steps, requires executed steps and compares highest RC to threshold; it does not enforce every expected step, IFOX severity or semantic output contract automatically. Check the actual full job receipt. Never infer new evidence merely from a reused JES number. [Printer-window decision](../../packaging/operations/maintenance/jes-printer-window-default-decision-20261110.md) enables this mechanism by default for numbered native regressions; independent `compile-mvs` and generic reporting retain opt-in cursor behavior.

### Console

[Console guide](../../tools/mvs/mvs-console-README.md) and [implementation](../../tools/mvs/mvs-console) define the current command catalog. With no command, `mvs-console` opens an interactive REPL. `help`, `commands`, `?`, `devices` (static IBM model catalog), `history` in the REPL and contextual help are local operations. `hercules devices`, optional device-category filter, `jes2 printers`, `mvs tapes` and other display aliases query the live system. Literal namespace commands are passed to the appropriate Hercules/MVS/JES2 transport; quote arguments with spaces.

Startup options precede the command: `--dry-run`, `--timeout SECONDS`, `--settle SECONDS`, `--yes` and `--allow-disruptive`. Dry-run sends no console command. Options inside the REPL cannot change the startup safety settings. Operational commands require exact YES or an allowed explicit noninteractive opt-in. Recognized disruptive commands require `--allow-disruptive` and interactive YES. This classification is conservative, not a complete parser or an authorization system.

The console uses Docker/HTTP transport and captures newly appended console log output; asynchronous unrelated replies and incomplete responses are possible. HTTP success is not guest completion. It does not automatically resend commands.

### Tape and assembler utilities

| Command | Contract |
| --- | --- |
| `mvs-console tape list` / `tape status ADDRESS` | Live Hercules device inventory/filter; not proof of MVS allocation release |
| `mvs-console tape files` | Host tape directory listing |
| `mvs-console tape mount ADDRESS FILENAME` | Mount existing ordinary image under mvs-state/tape; fresh tape-type and non-busy inquiry required |
| `mvs-console tape unmount ADDRESS` | Reinitialize virtual drive with no image; not guest unload or allocation release |
| `tape-map [--labels or --all or --files or --datasets or --text] IMAGE` | Read existing AWS/HET image via container hetmap; no mount or write. Image must be a regular filename under tape directory, no symlink or path escape. Default labels. |
| `make-asm-job SOURCE --output-dir DIRECTORY [--listing light/medium/heavy] [--entry NAME] [--job-name NAME] [--parm TEXT] [--force]` | Generate self-contained ASCII IFOX/IEWL/GO deck; directory must exist. Default light, output SOURCESTEM-PROFILE.jcl. Refuses existing output unless force. No JES submission. |

The current [make-asm-job executable](../../tools/mvs/make-asm-job) differs from the older [make-asm-job.py helper](../../tools/mvs/make-asm-job.py), which has basename-oriented defaults and a different output interface. Do not interchange their flags. The current generator validates ASCII source, column 71, inline SYSIN delimiter and MVS names, infers an entry from END when possible, and uses temporary object/load datasets. Generated LKED/GO conditions permit RC 4; this does not waive a particular zero-RC acceptance requirement. The generator is not a complete assembler or a production installation mechanism.

Mounting existing media does not initialize a new tape. Before a live mount or unmount verify guest and emulator state, correct media identity and allocation ownership, even if the emulator reports non-busy. Do not use console tools to bypass protected release-drive or no-retry controls.

## 3. DSPAL — aliases, mappings, population, submission, readback and deletion

Use [tools/datasets/dspal](../../tools/datasets/dspal), which dispatches to specialized Python modules. `dspal help [COMMAND]` displays command-specific syntax. It deep-merges local overrides and uses the effective managed map. A configured logical alias such as `BOOT_OBJ` resolves to its configured DSN with HLQ prepended if absent. Explicit DSN operands are also accepted by certain operations, subject to validation and the command-specific boundary. Do not treat arbitrary DSN access as supported for all commands. The historical `JCL` alias is not a current default; use `BOOT_JCL` or `MR10_JCL` as appropriate.

| Command | Options | Effects/result |
| --- | --- | --- |
| `info` | — | Effective configuration, non-secret information |
| `list` | — | Managed inventory from manifest; no live catalog inquiry |
| `status` | `--quiet`, `--probe`, `--show-jcl` with probe | Local readiness; probe **submits IEFBR14** for end-to-end JES check unless preview |
| `stat [DATASET]` | `--show-jcl` or `--raw` | Actual dataset attributes via LISTDS; omitted operand all managed. Raw full report; preview no submission. |
| `ls [DATASET]` | `--show-jcl` or `--raw` | Actual PDS directory via query JCL, one or all; not binary identity |
| `cat DATASET MEMBER` | `--show-jcl` | Read normalized text member to stdout via MVS |
| `get DATASET MEMBER FILE` | `--show-jcl` | Read normalized text to host file or stdout with - |
| `put DATASET MEMBER FILE` | `--show-jcl` | Replace/create text member from host file or stdin with -; persistent mutation |
| `rm DATASET MEMBER` | `--show-jcl` | Delete exactly one member; persistent mutation |
| `compress DATASET` | `--show-jcl` | In-place IEBCOPY compression; persistent mutation |
| `initbcpl` | `--show-jcl` | Attribute preflight and allocate missing managed datasets; preview worst-case allocation JCL |
| `populate TARGET` | `--generated-only`, `--batch`, `--dry-run` or `--show-jcl` | Transfer mapped sources; target managed logical name or all |
| `submit DATASET MEMBER` | `--wait` or `--show-jcl` | Submit stored JOB-less JCL body; wait for payload summary by default |
| `purgebcpl` | `--yes` or `--show-jcl` | Delete explicit existing managed dataset set after review/confirmation; destructive |

Use actual dispatcher routes; the core module's internal parser may expose options not routed by the front end (for example `initbcpl --raw` is not an option of the dispatched init implementation). See [core](../../tools/datasets/dspal-core.py), [init](../../tools/datasets/dspal-init.py), [member I/O](../../tools/datasets/dspal-io.py), [readback](../../tools/datasets/dspal-read.py), [directory](../../tools/datasets/dspal-ls.py), [maintenance](../../tools/datasets/dspal-maint.py), [population](../../tools/datasets/dspal-populate.py), [submission](../../tools/datasets/dspal-submit.py) and [purge](../../tools/datasets/dspal-purge.py) for actual routes.

### Transfer and allocation contract

Text transfers use the configured host encoding and strict MVS text conversion policy (tracked UTF-8/CP037). Observe dataset record lengths and card-image/JCL restrictions. Text readback normalizes records, including trailing spaces; it is not a raw-record or binary-object fidelity proof. Do not pass object decks or load modules through text put/get, even if they use FB80. Use binary-safe MVS IEBGENER/IEBCOPY and applicable independent verification. File destination and source - are stream conventions, not binary modes.

`populate` transfers Git-backed members and mapped generated members, not object or load libraries marked non-populating. It does not allocate PDSs. Generated inputs require the corresponding SHA-256 generation inventory; `--generated-only` skips tracked source writes. The initial clean-room pass can report RC=2 after writing ready sources if twelve generated inputs are absent; acceptance of this specific condition belongs to the reconstruction driver, not every population call.

Default population is one job per member. `--batch` uses bounded groups within one PDS: at most 60 IEBGENER steps and a 4000-card budget. It verifies the batch step inventory; missing generated inputs or failed receipts must not be silently ignored. `--dry-run` reports validated actions; `--show-jcl` renders redacted JCL. Neither submits population jobs. Normalized readback comparison remains qualified for terminal blank-record counts; see the [batch acceptance record](../../packaging/distribution/clean-room-batch-reconstruction-closure-20261109.md).

The stored JCL submission path creates an authenticated DSPALSUB launcher that copies an authenticated payload JOB card plus the stored member to JES INTRDR. The member remains resident. It waits for the payload and prints its summary; `--wait` is compatibility syntax, not an extra requirement. Preview redacts passwords. RC=0 means the tool's payload summary succeeded, RC=1 unsuccessful summary, RC=2 tool/transport/validation error; separately require the actual payload steps and component-specific results. An uncertain submission must not be automatically repeated.

`purgebcpl` previews the explicit configured targets and deletes only the managed set. Interactive exact YES or explicit `--yes` is required. A command flag is not a substitute for owner authorization. `initbcpl` does not repair every mismatched existing dataset automatically; inspect preflight and actual DCBs. Read/query operations may submit jobs despite having no intended persistent dataset writes.

## 4. MR10 tools — interpreter, compiler and suites

The [MR10 tool directory](../../tools/mr10/README.md) operates the MR10 Kit Compiler and ICINT19. Source selection is independent of the resident Cambridge Compiler and native application runtime.

| Tool (under tools/mr10/) | Syntax and result |
| --- | --- |
| `current-icint` | Resolve promoted assembler source from CURRENT; host-only |
| `run-intcode INTERPRETER PROGRAM [+MODULE ...]` | Assemble/link interpreter and execute existing INTCODE modules in order; live JES |
| `compile-and-run INTERPRETER SOURCE [+MODULE ...]` | Source-interpreter path; compile BCPL through SYN/TRN and CGI, run interpreted output |
| `compile-and-run --installed-icint MR10_LOAD SOURCE [+MODULE ...]` | Use installed ICINT19 load module via STEPLIB instead of assembling/linking interpreter; omit interpreter positional argument |
| `run-regression-panel` | Execute manifest-selected independent MR10 regressions; default promoted interpreter source |
| `run-demo-suite [--icint PATH]` | Execute general 17-program demonstration suite |
| `run-language-demos [--icint PATH]` | Execute language demonstrations |
| `run-dev-probes --check/--list` | Host-only manifest validation/selection |
| `run-dev-probes --run --case CASE_ID` | Explicit development probe execution; repeat case selection |

Direct drivers support `--results` (wait for completion and print result block), `--jcl PATH`, `--job-name NAME`, `--listing light/medium/heavy` (default light), `--reader-host HOST`, `--reader-port PORT`, `--timeout SECONDS` and `--poll SECONDS`. Without results mode, job assignment alone does not prove execution completion. `run-intcode --sysin PATH` supplies runtime ASCII card records up to 80 characters. `compile-and-run` supports repeated `--dd NAME=PATH`, alternate `--iclib PATH` and ordered `+MODULE` operands. `--save-ocode` and `--save-intcode` save recovered intermediates; `--artifact-dir PATH` is restricted to workarea and requires at least one save option. Choose disposable paths; existing generated files may be replaced or removed.

[run-intcode source](../../tools/mr10/run-intcode) and [compile-and-run core](../../tools/mr10/compile-and-run-core.py) define the actual arguments and output handling. Compiler and interpreter CODE records are separate from JES RC. Use the original compiler options contract in [MR10 compiler options](../../mr10-kit-compiler/docs/compiler-options.md). An emitted result block or demonstration does not necessarily implement the regression oracle.

The panel accepts `--icint PATH`, `--iclib PATH`, repeated `--module-override FROM=TO`, repeated `--category NAME` and `--test NAME`, `--list`, `--verbose` and `--stop-on-fail`. List is offline. Alternate source/library selection changes the evidence scope. See [actual runner](../../tools/mr10/run-regression-panel).

For [development probes](../../tools/mr10/run-dev-probes), `--all-provisional` selects the original six accepted cases, whereas `--all-candidates` selects all 17, including six unverified probes. The latter requires separate authorization. The eleven accepted-contract entries include a known genuine historical failure. `--continue-known-fixed-stack-failure` is narrowly gated to explicit historical fixed-stack selection and exact failure evidence; not a generic continue-on-error option. Preserve OBSERVED for unverified execution; it is not PASS. The separate supported coroutine runner and project suite use the distinct five-case supported manifest. See Chapter 6 for suite ownership and historical qualifications.

## 5. Bootstrap/native tools — prepare, compile, assemble and install

These tools build the interpreter-hosted demoted Cambridge Compiler and native application artifacts. CAMBCOMP is INTCODE executed by ICINT19; the native-running Cambridge Compiler remains unfinished.

| Tool (under tools/bootstrap/) | Interface and side effects |
| --- | --- |
| `prepare-bootstrap --check-inputs` | Check tracked input paths without writing; host-only |
| `prepare-bootstrap` | Generate disposable demoted inputs and provenance manifest; no PDS population |
| `prepare-bootstrap --with-trnilrg` | Additionally build TRNILRG through live MR10 compiler; MVS required |
| `compile-mvs SOURCE [--compiler-image MEMBER] [--cambridge-parm PATH] [--job-name NAME] [--output PATH] [--show-jcl]` | Compile using resident image, default CAMBCOMP (or CAMBRIDGE_IMAGE); output recovered CODE to workarea/SOURCESTEM.s370.asm by default |
| `run-production-regression START [END]` | Installed BOOT_OBJ native profile, inclusive numbered range; live tests |
| `run-installed-r5-t1-regression START [END]` | Installed R.5/T.1 optional extension objects and macros, same native runtime; live tests |
| `run-regression START [END]` | Lower-level native harness; environment/profile-sensitive, not preferred for ordinary suite selection |

[prepare-bootstrap](../../tools/bootstrap/prepare-bootstrap) writes `workarea/bootstrap-cambridge/prepare-bootstrap-manifest.json` including TRNILRG generation status and hashes. `--with-trnilrg` is not offline preflight. The resident compiler's [compile-mvs](../../tools/bootstrap/compile-mvs) accepts `--listing` and `--timeout` for interface compatibility; no IFOX stage is implied. `--show-jcl` does not submit but creates the output parent directory and **unlinks a pre-existing chosen output file before rendering**. Use an unused scratch output. A source compile is not native GO verification.

Resident job bodies are mapped by DSPAL from [bootstrap-toolchain/jcl](../../bootstrap-toolchain/jcl/). The following names are job members, not separate host executable scripts.

| Member | Actual purpose |
| --- | --- |
| `MR10_JCL(IC19BLD)` | IFOX/IEWL and object save for ICINT19 |
| `BOOT_JCL(CAMBBLD)` | Generate resident compiler image in BOOT_INTCODE |
| `BOOT_JCL(BLDBMAIN)` | Assemble/install seven initial runtime and registration objects |
| `BOOT_JCL(BLIBBLD)` | Compile, prepare, assemble and install BLIB; no IEBCOMPR step |
| `BOOT_JCL(BLDCORCO)` / `BLDCORLB` | Assemble, install, read back and compare coroutine objects |
| `BOOT_JCL(BCPLDEMO)` / `BCPLTIME` / `BCPLQSAM` | Assemble, install and compare optional extension objects |

These jobs write managed datasets. Preview and submission use DSPAL and require proper staged inputs and separate authorization. Production coroutine preparation uses [prepare-production-library.py](../../tools/coroutines/prepare-production-library.py), then explicit BOOT_ASM(COROUTIN) staging; [verify-installed-production.py](../../tools/coroutines/verify-installed-production.py) separates `--check` from live `--run`. See the reconstruction manual for exact order, ten-object baseline and installed application oracle. Do not use old six/eight-object README descriptions as current installation contracts.

The production wrapper sets installed runtime selection, clears inherited candidate flags and selects OBJ logical linkage. The installed-r5-t1 wrapper sets optional extension selection through effective configuration and clears inherited punch-resume settings. Both QSAM 163–176 and native coroutine 177–189 use source-selected candidate paths where specified, not new installed-object execution evidence. The lower-level runner supports `--show-output` and absolute `--log-dir` (subject to case-specific restrictions) and host-only `--check-numbering`. The old direct `--resume-punch` path is not a substitute for the current guarded suite selection. Consult the [suite contracts](../../tests/README.md) and current [runner](../../tools/bootstrap/run-regression).

## 6. Checks, runners and coordinators — selectors, modes, evidence and exit codes

The reusable [checks directory](../../tools/checks/README.md) contains static validators and focused research harnesses. Not all scripts under tools/checks are read-only: inspect their actual interface, especially probes and generators with execution modes. Typical host-only validators are `check-asm-source.py PATH`, `check-bcplmain-canonical.py` and `check-native-jcl-manifest.py`. The assembler checker enforces source hygiene; it is not IFOX. The older checker README's historical paths and job counts are not authoritative for current manifest contents. Python unit tests use the repository's existing test patterns; a mocked transport is not real MVS.

### Suite interfaces

| Executable | Supported selection and mode |
| --- | --- |
| `tools/tests/run-suite [SUITE] --list` | List native suites/cases offline |
| `tools/tests/run-suite [SUITE] --check` | Validate all five native manifests offline |
| `tools/tests/run-suite SUITE --run --profile PROFILE` | Execute selected native suite; repeat `--case ID` or `--tag TAG` to restrict selection |
| `tools/tests/run-project-regressions --list/--check` | Offline inventory/contract validation |
| `tools/tests/run-project-regressions --run --suite NAME ...` | Execute explicit suites, repeated selectors; explicit `--profile` for native suites |
| `tools/tests/profile-native-jes-overhead --evidence DIRECTORY` | Analyze existing receipts; optional repeated `--case N` and `--bench N`; no JES execution |

Native profiles: `production` and `installed-r5-t1`. Tags on native suite selection combine as AND; case IDs retain canonical formatting in reports. Project coordinator rejects duplicate suite selectors, requires at least one for execution and stops before another suite on failure or blockage. `--progress` is execution-only console progress, not a change in verification. `--allow-device` is execution-only and must have separate authorization; project selection must include BCPLQSAM.

| Selector | Inventory / accepted scope |
| --- | --- |
| mr10 | 12 independent interpreted baseline cases |
| mr10-coroutines-supported | 5 valid-domain interpreted cases |
| bootstrap | 00–145, 190–193, 150 cases; 083 source-only instrumentation expected SKIP in installed profiles |
| runtime-extensions | 146–158, 13 cases |
| bcpltime | 159–162, 4 cases |
| bcplqsam | 163–176, 14 source-selected cases |
| coroutines | 177–189, 13 candidate-source cases |
| coroutine-contract | 2 pinned interpreted/native paired cases; no native-only profile required by this suite |
| mr10-probes | 11 accepted-contract development probes; six unverified cases excluded |
| mr10-coroutines | 5 original historical cases; one genuine known fixed-stack FAIL |

The historical [CO.6 accepted supported campaign](../../packaging/milestones/coroutines/co6-formal-acceptance-and-closure-20261116.md) reports 208 PASS, zero FAIL/BLOCKED and one expected SKIP. The [DR.5 supported campaign](../../packaging/milestones/documentation-refactoring/candidates/compiler-verification/README.md) reports 211 PASS, zero FAIL/BLOCKED and one expected SKIP; the subsequent [DR.5 BCPLIO campaign](../../packaging/milestones/documentation-refactoring/dr2-runtime-library-manual-migration-20261125.md) reports 212 PASS, zero FAIL/BLOCKED and one expected SKIP, including 149 Bootstrap passes (150 selected). Historical original fixed-stack CODE=-1 remains FAIL, not XFAIL or SKIP; the supported valid-frame replacement is separately named. Overlapping selections are not additive acceptance counts. Native manifest, MR10 manifest and individual independent oracles remain controlling.

Native and project suite summaries retain distinct outcome classes. The project coordinator returns 0 for PASS, 1 for failure/incomplete, 2 for blocked or argument/validation errors as applicable. Inspect actual structured results, not just RC. Native case-level evidence lives under `workarea/test-suites/`; project execution creates `workarea/project-regressions/<run>/summary.json` and suite logs. The coordinator checks exact identities, counts and child receipts. NOT_RUN/NOT_SELECTED are not PASS. Preserve these records before cleanup.

### Device and receipt controls

Case 175 punch and 176 printer require `--allow-device`. Otherwise they report BLOCKED. Inherited Q4_PUNCH_RESUME is stripped by the suite interface. With explicit case-175 device permission only, the guarded writer start is allowed when paused PUNCH1 has the expected state and fresh JES queue shows only the current Q4PUNCH job. Unrelated queued work, missing or ambiguous target state block the start. No automatic retry or queue flush. Exact new 172-byte punch capture and matching receipt remain mandatory. Case 176 never starts that writer. The [current run-suite source](../../tools/tests/run-suite) supersedes the old README assertion that it never enables the writer. See [test tool guide](../../tools/tests/README.md) for details.

Numbered native regressions default to bounded printer-window reading; `BCPL_PRINTER_WINDOW_TRIAL=0` opts into the older full-file reader. Invalid cursor fails closed. Generic utilities keep their own default. QSAM physical device captures retain separate offsets. Do not reclassify failed jobs merely because a later run passed. The [Q.5 closure](../../packaging/milestones/qsam/qsam-q5-closure-20261101.md) and CO.6 closure preserve the earlier failures and remaining qualifications.

## 7. Reconstruction — scope, options, safety and workarea

The accepted routine driver is [rebuild-from-source](../../tools/reconstruction/rebuild-from-source). It always starts at Guide Step 0, executes 0, 1, 2, 3, 5, 6, 7, 8, 9 and does not execute the full regression campaign. It runs git status/pull/HEAD display, but does not enforce an immutable source revision or clean checkout. It starts/probes TK5, cleans workarea, recreates managed datasets and builds the supported programming system. It does not rebuild TK5 itself or the native-running Cambridge Compiler.

| Interface | Contract |
| --- | --- |
| `rebuild-from-source` | Interactive checkpoints; cleanup DELETE, purge YES and extension review prompts |
| `rebuild-from-source --unattended` | Explicit destructive authorization for invocation; skips confirmations, still stops on command failure |
| `rebuild-from-source --batch-populate` | Optional bounded per-PDS source transfers; independent of unattended mode |
| `clean-workarea [--yes]` | Delete managed disposable host contents, retain tracked .gitignore; explicit confirmation unless authorized yes |
| `verify-boot-obj.py` | Live DSPAL directory verification of exactly ten accepted production object names |

The [clean-workarea source](../../tools/clean-workarea) also has a scope-fingerprint interface for the separate guarded controller, not a reusable approval token. Do not use it to bypass the single-run gate. Preserve private evidence and no-retry markers before cleanup. The [routine reconstruction guide](How-to-Reconstruct-BCPL-from-Source.md) covers the first-pass RC=2 generated-member exception, exact expected installation inventory and full regression selection.

The [guarded reconstruction tools](../../tools/reconstruction/README.md) are a separate implementation, not the accepted routine driver.

| Command (tools/reconstruction/) | Contract |
| --- | --- |
| `plan [--dry-run] [--probe]` | Read-only plan; optional Docker/TCP observation, not JES idle or authenticated probe |
| `authorize [--probe]` | Interactive exact scope approval exercise; no execution or persisted/transferred authorization |
| `run --list` | Read-only canonical 25-operation sequence |
| `run --check-live-guard` | Two-sample read-only JES observation, no reconstruction |
| `jes-idle --live [--diagnose]` | Two fixed $DA inquiries; diagnostic raw console deltas only on blocked state, redact before sharing |
| `run --run` | Fresh interactive scope-bound acknowledgment and guarded execution; **live integration acceptance pending** |

Plan and acknowledgment bind source, effective configuration, target and destructive inventory. The guarded controller checks scope drift, safe host deletion and two fresh verified CLEAR observations; no host/MVS submission lock. Exact REBUILD HLQ fingerprint acknowledgment is not transferable; the standalone exercise cannot authorize another process. A clear JES result is not a lock or exclusive reservation. Do not run the guarded live command as a negative test.

Standalone authorize RC=0 is accepted exercise, 2 blocked/noninteractive, 3 cancelled. Guard RC=0 means qualifying CLEAR observations, 2 blocked, 130 interruption. The routine driver has no integrated JES console idle gate and relies on operator quiescence; do not describe it as the guarded engine. The accepted [batch reconstruction closure](../../packaging/distribution/clean-room-batch-reconstruction-closure-20261109.md) and [CO.5 clean-room PASS](../../packaging/milestones/coroutines/co5-production-clean-room-pass-20261116.md) apply to the simple driver at recorded revisions, not the unaccepted separate orchestration. A stopped rebuild cannot resume: inspect outstanding JES work, correct the defect, renew authorization and start a complete reconstruction.

## 8. Distribution — manifest/registry, orchestration and evidence review

The [distribution tool guide](../../tools/distribution/README.md) describes the released RC4 layout and reusable functions. The [canonical release how-to](../../tools/distribution/How-to-Create-a-Release-Candidate.md) remains operative at its existing path. Do not create a competing recipe or replay consumed BC0005. The release registry and frozen manifests are separate from DSPAL configuration. [Release registry](../../packaging/distribution/registry/releases.yaml) owns candidate/version/VOLSER and lifecycle identity; [manifest index](../../packaging/distribution/manifest/README.md) owns selected release layout and payload bindings.

### create-release

The [driver](../../tools/distribution/create-release) supports the current single-volume RC4 layout only. It is implemented and offline-tested, not yet live-accepted; the actual earlier BC0005 exercise does not establish its live verification. The default invocation is read-only. Mutating modes and source selections are mutually constrained.

| Mode | Inputs | Result / side effect |
| --- | --- | --- |
| `create-release [--version VERSION]` | Registry, unused prerelease identity | Proposed version and next VOLSER, no reservation |
| `--prepare --reuse-rc4 [--version VERSION]` | Explicit frozen program-payload reuse | Sealed local reservation draft, no tracked changes or MVS writes |
| `--prepare --inputs FILE [--version VERSION]` | Prepared source receipt and reviewed payload | Sealed local reservation draft; not source preparation |
| `--reserve DRAFT` | Reviewed reservation directory | After confirmation, local new manifest and registry append; separately reviewed authorized commit required |
| `--run CANDIDATE` | Committed authoritative reservation and verified inputs | Read-only live preflight, interactive approval, exclusive no-retry marker, MVS production/installation/verification and private package |
| `--record EVIDENCE` | Sealed completed run evidence | After confirmation, local registry lifecycle annotation; separately reviewed authorized commit required |

The input JSON for prepared mode contains exactly mode, source_commit, sources (18 distinct prepared PDSs, sequence keys 4–21), allocations (19 entries 3–21 with three positive allocation quantities), evidence and evidence_seal_sha256. The sealed prepared-inputs.json binds the program revision, source map and allocations. No arbitrary receipt seal proves lineage or rights. Current supported site/drive/media/space and catalog/VTOC preflight requirements are in the canonical how-to; exact preparation and verification are required.

The run can decline before writes with RC=0 and status DECLINED_NO_WRITE. It may halt with RC=2; inspect marker, structured result and evidence before interpreting outcome. Once intent is consumed, **NO RETRY**, even if later operations fail. Do not remove the marker, reuse the reserved VOLSER, overwrite media, or rerun the historical harness. No mode automatically commits, pushes, tags, publishes, reconstructs source or certifies native execution.

### Reusable offline release interface

[release.py](../../tools/distribution/release.py) never submits JES, mounts/writes media, reserves identities or publishes. Its subcommands:

| Subcommand | Required inputs | Output |
| --- | --- | --- |
| `write-jcl` | `--manifest`, `--source-map`, `--unit` | JOB-less SL writer using IEBGENER/IEBCOPY; source map decimal sequence keys covering all logical datasets |
| `install-jcl` | `--manifest`, `--allocations`, `--profile`, `--hlq`, `--site`, `--tape-unit`, `--dasd-unit`, `--dasd-vol` | JOB-less in-stream installer PROC; allocation map for sequences 3 onward |
| `review-tape` | `--manifest`, `--labels`, `--files` | Saved HETMAP comparison JSON |
| `review-mr10` | `--report`, optional `--root` | Saved JES TEST/RP/EXP/CODE comparison JSON against checked-in independent goldens |

The supported installation profiles are MR10, NATIVE and COMBINED; the accepted layout uses BT0001 bootstrap and BT0002 COPY control followed by recipient PDS payloads. Unsupported layouts/DCBs are refused. RC=0 indicates operation success according to helper; RC=2 error. Saved-evidence review is not new live execution.

[validate-manifest.py](../../tools/distribution/validate-manifest.py) accepts `--manifest PATH`, `--dspal PATH`, `--root PATH`, `--release` and `--audit-json`. Default manifest is the design inventory, so explicitly select the intended candidate. Strict release validation fails closed on incomplete inventory/rights evidence; a validation or audit report is not legal approval. [mvs_release.py](../../tools/distribution/mvs_release.py) is a parameterized library, not a standalone live command. It exposes staging, bootstrap, drive/VOL1 and catalog/record checks, JES evidence and sealing functions used by the new driver. Its focused tests are offline; no live acceptance inherited from BC0005.

The remaining TA.0 inventory, decoder, audit, pilot/recovery and evidence relocation tools retain historical use or reusable functions. Some submit real jobs or move evidence. Do not run them merely because they remain tracked. See [post-release audit](../../packaging/distribution/post-release-audit-20261124.md) for retained/retired paths and the exact consumed harness. The RC4 release companion and publication reviewer retain their original evidence scope. New driver testing does not authorize publication.

## 9. Command and failure reference — inputs, outputs, changes and recovery limits

Consult command-specific help for optional arguments and source before invoking an unfamiliar tool. Do not assume that similarly named programs or old examples share flags, defaults or side effects. In particular:

| Observation | Interpretation / action |
| --- | --- |
| Local command or manifest validation fails | Inspect inputs, effective configuration and actual implementation. Block dependent operations. |
| Preview returns zero | Only the preview contract; may generate host files. compile-mvs preview can remove an existing output. |
| JES probe returns zero | Demonstrated probe result, not idle/exclusive ownership, installation or regression acceptance. |
| Submission timeout or missing payload | Establish actual JES identity and outstanding work before any further submit; no automatic retry. |
| job-summary success at default threshold 4 | Check required zero-RC steps, severity, complete report and independent oracle. |
| Interpreter CODE nonzero despite JES zero | Program/compiler completion failure unless the exact test contract expects it. |
| Native GO zero but oracle mismatch | FAIL; preserve golden, actual output and linker evidence. |
| PDS listing or normalized text readback matches | Inventory/text evidence only; no claim of raw binary or terminal blank-record fidelity. |
| Case 083 SKIP or device BLOCKED | Record actual outcome; do not turn it into PASS. |
| Device capture uncertain, writer guard blocks | Preserve evidence, no queue flush or unsafe writer start/retry. |
| Reconstruction stopped | Preserve evidence and inspect outstanding work; newly authorized full rebuild, no resume. |
| Release intent consumed or output image exists | Stop; preserve media, marker and evidence; separate reviewed disposition and new identity if needed. |

### Evidence and return-code conventions

For every target execution preserve Git revision, exact input/selection and effective target, actual JES job identity, required step RCs, assembler severity, compiler completion records, IEWL linkage and expected/actual oracle as applicable. For important receipts retain complete reports, not just console summaries. For installed verification record source vs resident object selection. For releases retain protected media hashes, sealed evidence, registry/manifest association and consumed intent; never publish private credentials or raw authenticated decks.

Not all tools use the same return-code convention. In addition to the explicit codes in previous chapters, argparse often uses 2 for invalid input; shell wrappers may propagate underlying process status. `validate-manifest.py` returns 1 for failed validation. `run-intcode` reports execution/transport errors with nonzero status. Read actual runner summaries and structured evidence before relying on a process RC. A no-write decline can return zero. Never treat a missing report, a previous successful job with the same number, or a later passing rerun as proof of the current attempt.

### Known scope and reconciliation

This working reference covers the principal maintained interfaces and safety-critical exceptions. The full internal helper APIs, all diagnostic modes, option combinations, return-code branches, environment-variable precedence and stale source-local dependencies have not been exhaustively reconciled. Use current executable help/source and existing contracts for details not specified here. DR.5 must review exact normative mappings and appropriate operational evidence before any authority transfer. No fresh target execution, release production, software change or promotion is implied by this reference.
