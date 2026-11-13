# Coroutine research and design gates

**Milestone:** [Implement coroutine support for native compiler](milestone-implement-coroutine-support-for-native-compiler.md)  
**Recorded:** 10 November 2026  
**Status:** OPEN; CO.0 CLOSED (qualified acceptance); CO.1 IN PROGRESS (source investigation, not native implementation evidence)

**Five-probe execution checkpoint:** [11 November JES review and second-pass extraction](co0-mr10-coroutine-jes-summary-review-20261111.md) documents five OBSERVED cases, 62 zero-RC JES steps, 23 zero interpreted phase codes extracted from local reports, five matched program-output sequences, and four matched compiler-artifact pairs. The owner accepted the five golden contracts on 11 November; these are interpreted, not native, tests. The expanded runner has since been re-executed on MVS under the promoted canonical implementation: four original probes pass, the legacy fixed-stack source fails (JOB 5318), and the separately retained corrected-frame source passes (JOB 5321). CO0-U02 is resolved with this explicit compatibility qualification, not with an unqualified five-case PASS.

**Five-probe verification plan:** [CO.0 MR10 coroutine development-probe procedure](co0-mr10-coroutine-probe-verification-plan-20261110.md) records runner selection, candidate oracle and required JES evidence; no new probe execution or acceptance is claimed.

**CO.0 discovery (10 November):** The tape's `INDEX` explicitly identifies a **KM10 coroutine library**, including `KM10.COMACRO`, `KM10.COBLIB(CORTN)`, `KM10.COBLIB(STANDARD)`, `KM10.J(COLIB)`, and the **missing** `KM10.COMAIN`. This materially expands the prior historical-source inventory. See the [CO.0 source audit](co0-historical-source-audit-20261110.md). The native switching algorithm and full historical callable API remain unrecovered.

## Approved engineering direction — 11 November 2026

**Governing principle: Historical fidelity where evidence exists; contemporary engineering judgment where it does not.**

The overarching objective remains a working, capable native System/370 Cambridge compiler and runtime under MVS 3.8J. Historical reconstruction is its foundation, not a requirement to duplicate every undocumented or obsolete implementation detail. Where historical code is missing, make explicit, reviewable contemporary engineering decisions; distinguish historical evidence, inference and deliberate reconstruction choices.

- **Correctness and compatibility:** retain recoverable BCPL semantics, callable interfaces and observable behavior. Treat source observations, interpreted MVS tests and native MVS tests as distinct levels of evidence.
- **Maintainability and reproducibility:** preserve easy modification, unattended clean-room reconstruction, isolated testing and repeatable release production. The established modular Core Runtime is the baseline, not a disposable approximation.
- **Targeted research, not wholesale imitation:** investigate historical MLIB and coroutine architecture only where it may affect native ABI/call-return behavior, switching, per-coroutine stack protection, startup, allocation/ownership, global registration, diagnostics or lifecycle. An exhaustive MLIB restoration is out of scope.
- **Evidence-driven architectural changes:** revise the existing runtime only to correct a demonstrated deficiency, satisfy a substantiated historical compatibility requirement, or secure a meaningful engineering improvement. Historical source packaging does not dictate current module boundaries.
- **Future research:** a sufficiently capable native Cambridge compiler and runtime can enable deeper historical study later; do not delay the working implementation pending recovery of missing original modules.

The historical `BCPLIB.JCL(MAKEOBJ)` and `BCPLIB.JCL(MAKELIB)` show a monolithic assembler-source `BCPLMAIN` split into several library members, plus separately compiled BCPL `BLIB`, `IOS` and `PM`. This **does not** require collapsing the reconstructed `BCPLMAIN`, `BCPLMEM`, `BCPLBYTE` or other modular components. See the focused comparison appended to the [CO.0 historical source audit](co0-historical-source-audit-20261110.md).

**Pending CO.1 (not an ABI decision):** retain the working direction of an isolated machine-dependent native switch and BCPL-language management routines where feasible; historical accounts of MLIB's ownership of coroutine operations are evidence to consider, not a mandate to rewrite all management routines in assembler. Preserve explicit root context, independent checked stacks, continuation/value transfer and lifecycle/error invariants.

**Status:** This is owner-approved research direction, not acceptance of a native descriptor, global assignment, test oracle or implementation. CO.0 remains **IN PROGRESS**; CO.1–CO.5 remain **NOT STARTED**.

**11 November CO.0 observation:** The separate [JOB 5231
continuation-divergence review](co0-changeco-continuation-divergence-jes-5231-review-20261111.md)
records a zero-RC / zero-CODE run with an incorrect post-CHANGECO
execution order. This interpreted counterexample limits the known MR10
switching contract; the saved INTCODE listing is not yet independently
reviewed. A correct *candidate* contract saves each coroutine's own
frame and continuation, subject to later owner design review.

## Evidence already in Git

| Area | Established source observation | Research still open |
| --- | --- | --- |
| MR10 BCPL routines | `mr10-kit-compiler/library/coroutines.bcpl` implements reconstructed `CREATECO`, `DELETECO`, `CALLCO`, `COWAIT`, `RESUMECO`. | Distinguish designed/tested behavior from historical interfaces and cover error/termination paths. |
| MR10 switch | `mr10-kit-compiler/source/iclib.int` uses existing INTCODE `X32`; `icintv19.asm` implements `X32` by restoring interpreted P and C. | Trace each scratch global, saved continuation and value-transfer rule in `CHANGECO`; document first activation and resumption. |
| MR10 descriptor | Existing probe documentation records `C!0` saved P, `C!1` parent, `C!2` list link; `P=C+3`; `P!2` FN, `P!3` SIZE, `P!4` C. | Do **not** assume these interpreted offsets/registers map onto native S/370. |
| Tests | MR10 12-case regression panel has accepted `basic-coroutine`; `10-coroutines/` has five additional owner-accepted interpreted development probes. | The five candidate outputs and structural artifacts were reviewed and are frozen as goldens; native behavior and negative-path semantics remain unverified. |
| Historical Cambridge/KM10 | Ordinary `sys3/bcpl/libhdr` and `bcplib/bcpl/blib` do not expose the MR10-named coroutine API, **but** original `km10/comacro`, `km10/coblib/cortn` and `km10/j/colib` prove a historical native coroutine variant existed. | The tape-listed `km10/comain` is missing. Recover full historical interface, initialization and switching behavior from surviving indirect evidence; do not conflate the variants. |
| Native ABI | Native contract assigns R5 frame, R6 return, R7–R9 arguments/results, R4 restored from frame, R11 system vector; current BCPLMAIN has a single bounded working stack. | Identify all live registers/condition codes/stack state and restoration requirements using actual CG370 output and MVS probes. |
| Globals | MR10 numbers 6–8 and 91–95 conflict with the Cambridge `LIBHDR`. | Choose and approve new native slots and exports against Global Number Registry, compiler CGHDR and whole-executable collisions. |
| Storage | Native `BCPLMEM` supplies `GETVEC`/`FREEVEC`; stack checks use `STKLIM` and runtime diagnostics. | Establish isolated per-coroutine stack layout, guard, high-water, root stack, exhaustion and cleanup. |

Interpret a claim as **DECLARED**, **SOURCE-OBSERVED**, **INTERPRETED-MVS-TESTED**, **NATIVE-MVS-TESTED**, **INFERRED** or **UNVERIFIED**. Do not substitute a source observation or GO RC for behavioral proof.

## CO.0 — Historical Research and Behavioral Contract

- [ ] Trace the full `ICLIB` `CHANGECO` instruction path (saved P/C and scratch globals) and inspect original MR10 kit `ICINT` plus the project's `ICINT19`.
- [ ] Compare `compiler-probe.bcpl` and `frame-layout-probe.bcpl` with saved OCODE/INTCODE; prove argument order and actual synthetic frame behavior.
- [x] Verify all five existing `10-coroutines/` probes: call layout, frame layout, fixed-stack producer/consumer, RESUMECO parent chain, CREATE/DELETE/reuse. Record exact inputs, phase RCs, output oracle and JES evidence when authorized.
- [ ] Establish entry argument, yield value, return value, parent relation, natural return/termination, repeated resume, invalid/deleted coroutine and error behavior; classify any inferred behavior.
- [x] Identify the surviving historical KM10 coroutine-library inventory, control-block macro, coroutine-aware BLIB source, and link-edit job; distinguish it from project-created MR10 code (source audit only).
- [ ] Continue searching period documentation, tape sources and related references for the **missing KM10.COMAIN** implementation and a full historical callable coroutine contract.
- [ ] Design equivalent interpreted/native BCPL behavior tests, permitting only documented header/global mapping differences.

**CO.0 gate:** reviewed behavior table, provenance, reproducible interpreted test recipe, open unknowns. No new native implementation.

## CO.1 — Native ABI and Stack Architecture

- [ ] Examine actual CG370-emitted call/return/checked-entry sequences around nested `CHANGECO` calls; document R4/R5/R6/R7–R9/R11/R12/R15, workspace and continuation behavior.
- [ ] Prove how a never-run coroutine's first frame and continuation are initialized, how context switching returns values, and how the root context is represented.
- [ ] Compare separate GETVEC-backed stacks with the current single `STKLIM`/stack paint/overflow path and `STACKBASE`/`STACKEND`/`STACKHWM`; decide whether and how per-coroutine bounds are installed without violating accepted ABI.
- [ ] Specify ownership, allocation size units, lifecycle states, active/suspended deletion rules, stale references, error reporting and cleanup on ordinary and exceptional termination.
- [ ] Resolve native global numbers and historical BLIB versus separate BCPL library ownership. Establish actual BCPL object trailer/global import and assembler Core Runtime integration; do not assume System Extension BCEX/BCRG provides library linking.
- [ ] Provide a bounded native IFOX/IEWL/GO probe matrix and a non-production object/JCL workflow before submitting JES.

**CO.1 gate:** explicit owner approval of descriptor, stack bounds, register/continuation restoration, public BCPL API/global allocations, library location and lifecycle contract before CO.2.

## CO.2–CO.5 — Required independent verification

| March | Required demonstration |
| --- | --- |
| **CO.2** | Two native contexts, first transfer, suspend/resume, nested locals and return linkage, precise result and register behavior, actual IFOX/IEWL/GO/JES evidence. |
| **CO.3** | Separately compiled BCPL management routines, linked Core Runtime primitive, root/parent-chain behavior, normal completion, deletion and allocation reuse. |
| **CO.4** | Repeated interleaving, recursion, boundaries, overflow, allocation failure, invalid/active/stale pointers, teardown; explicit distinctions between safe negative returns and unrecoverable machine faults. |
| **CO.5** | New named native Bootstrap regression cases preserving 00–176 identities; applicable interpreted MR10, native Bootstrap and project suites; full clean-room rebuild; independent per-case output/RC oracles; exact PASS/FAIL/SKIP/BLOCKED; owner sign-off. |

Use the current `tests/README.md` / `tests/suites/*.tsv` suite system and `mr10-kit-compiler/tests/dev-probes-manifest.tsv`. No test IDs are allocated and no executions are authorized by this document.

## Source inventory

- `packaging/architecture/coroutine-design-discussion-20261103.md`
- `packaging/architecture/{runtime-and-library-nomenclature,global-number-registry,runtime-contract-v1,stack-check-contract}.md`
- `richards-bcpltape/{mr10/bcplkit,sys3/bcpl/libhdr,bcplib/bcpl/blib}`
- `mr10-kit-compiler/{source/iclib.int,asm/icintv19.asm,library/coroutines.bcpl,tests/10-coroutines,tests/00-regression-panel,tests/dev-probes-manifest.tsv}`
- `bootstrap-toolchain/{asm/bcplmain.asm,asm/bcplmem.asm,bootstrap-cambridge}`
- `tests/README.md`, `docs/Rebuild-BCPL-for-MVS-from-source.md`
- `packaging/operations/{git-mvs-authority,operator-wsl-command-policy}.md`


**12 November U01/U05 update:** Canonical JOB 5322 verified nested
CHANGECO continuations and value transfer with thirteen matching
records, final CODE=0, 14/14 JES RC=0000 and runner RC=0.
U01's bounded observed behavior is verified, but the precise
interpreter-cycle trace and native mechanism remain open.
A new isolated U05 worker-return/re-entry candidate is untested
and is not part of the accepted five-probe or regression manifest.


**12 November U05/U04 update:** Canonical JOB 5324 established
bounded normal worker return/re-entry and deletion with five
correct records, CODE=0, runner RC=0 and 14/14 JES RC=0000.
A separate unaccepted U04 probe now tests null/current
deletion and busy valid-root rejection with post-test liveness.
No stale-pointer safety or native coroutine behavior is claimed.


**12 November U04/U06 checkpoint:** Canonical JOB 5325 verified
seven bounded null/live descriptor rejection records, CODE=0,
runner RC=0 and 14/14 JES RC=0000. Arbitrary/stale descriptor
safety is still open. A distinct U06 candidate now targets
positive oversize GETVEC refusal and ordinary allocator reuse,
not stack overflow or native stack architecture.


**12 November CO0-U06 acceptance:** Canonical JOB 5326
verified positive oversize refusal, normal successful
execution/deletion and allocator reuse: five output
records, interpreted CODE=0, runner RC=0, independent
14/14 JES steps RC=0000. A distinct exact-fit candidate
is source-checked but remains MVS-unverified. Broader
SIZE, stack-guard and exceptional cleanup questions remain.


**12 November U06 exact-fit checkpoint:** JOB 5327
independently verified one-word-over refusal, exact-fit
allocation and reuse with five correct records, interpreted
CODE=0, runner RC=0 and all 14 JES RC=0000. A bounded
fragmentation/coalescing source candidate is prepared but
not executed on MVS. Malformed SIZE and native stack limits
remain open questions.


**12 November U06 coalescing acceptance:** JOB 5328 passed
the nine-record fragmentation/coalescing oracle, interpreted
CODE=0, runner RC=0 and independently all 14 JES steps
RC=0000. A further bounded live-list middle-unlink
candidate has been prepared but is not MVS-tested.
General SIZE validity, exception cleanup, and native
stack protection remain open.


**12 November U06 middle-descriptor acceptance:** JOB 5329
passed eleven exact records, interpreter CODE=0, runner RC=0,
14/14 JES RC=0000. The remaining SIZE question is now
partitioned: source-guarded SIZE<=-10 (new candidate) versus
SIZE=-9..-1 (unsafe undersized synthetic-frame writes).
General validation and native stack safety require
CO.1 design, not speculative interpreted stress testing.


**12 November U06 negative-SIZE checkpoint:** JOB **5330** (`BCCO0NEG`) matched four guarded refusal/recovery records, interpreted CODE=0, runner RC=0 and independently **14/14 JES steps RC=0000**. This is **INTERPRETED-MVS-TESTED** only for SIZE=-10 and SIZE=-20 followed by normal coroutine execution/deletion. The nearby SIZE=-9..-1 range, arithmetic overflow, stack overflow and native lifecycle/ownership remain unverified. See [U06 negative-SIZE record](co0-u06-negative-size-guard-plan-20261112.md). CO.0 remains IN PROGRESS; no CO.1 approval or native implementation is implied.


**12 November CO0-U08 independent-local oracle:** JOB **5331** (`BCCO0TWO`) matched eight A/B alternating accumulator and ordinary deletion records, interpreted CODE=0 (5138 cycles), runner RC=0, and independently summarized **12/12 JES steps RC=0000**. This is **INTERPRETED-MVS-TESTED** for the bounded two-coroutine sequence only. [U08 acceptance record](co0-u08-two-coroutine-oracle-plan-20261112.md). Native System/370 correspondence, descriptor ABI and native execution remain unverified. No CO.0 closure or CO.1 decision is implied.


**12 November CO0-U08 nested-call acceptance:** JOB **5332** (`BCCO0NES`) precisely matched 14 nested A/B `LEAF`/`MIDDLE`/worker/root and deletion records. Final interpreted CODE=0 (9017 cycles), runner RC=0, independent **12/12 JES steps RC=0000**, JOB RESULT SUCCESS. This is **INTERPRETED-MVS-TESTED**, not native execution. In combination with JOB 5331, two distinct U08 behavioral oracles are accepted for subsequent native comparison. [U08 nested-activation record](co0-u08-nested-activation-continuation-plan-20261112.md). Native stack/register/ABI design and equivalence remain open; CO.0 status unchanged.


**12 November CO0-U08 repeated nested suspension acceptance:** JOB **5333** (`BCCO0NES`) matched 18/18 records for two alternately resumed nested LEAF call frames, each suspending twice and retaining locals. ICINT19 CODE=0 (11593 cycles), runner RC=0, independently **12/12 JES steps RC=0000**, JOB RESULT SUCCESS, `tools/mvs/job-summary 5333` shell RC=0. [JOB 5333 record](co0-u08-nested-double-yield-plan-20261112.md). **INTERPRETED-MVS-TESTED** only. Alongside JOBS 5331–5332, three U08 interpreted oracles are now accepted; native counterparts remain unverified. CO.0 stays IN PROGRESS; no CO.1 approval or implementation is implied.


**12 November CO0-U08 comparison matrix:** [Interpreted-to-native behavioral oracle matrix](co0-u08-interpreted-to-native-oracle-matrix-20261112.md) reconciles JOBS 5331–5333 as **40 exact expected records** across three independent **INTERPRETED-MVS-TESTED** tests, each with 12/12 successful JES steps. This research mapping makes no native ABI decision and claims no native MVS execution; CO.0 remains IN PROGRESS, CO.1–CO.5 NOT STARTED.


**12 November CO0-U04 audit and U08 JES recheck:** [Descriptor validation and source-safety audit](co0-u04-descriptor-validation-and-source-safety-audit-20261112.md) records the canonical MR10 dereference-before-membership limitation and separates supported live-descriptor behavior from unsafe null/stale/nonmember experiments. It also records owner rechecks of JOBS 5331–5333: each summary shell RC=0, each 12/12 JES steps RC=0000 (**36/36** total). This is not a new run or native acceptance. CO.0 IN PROGRESS; CO.1–CO.5 NOT STARTED.


**12 November CO0-U09 design briefing and JOB 5325 JES recheck:** [Source-backed native ownership/descriptor/stack alternatives](co0-u09-native-coroutine-ownership-and-stack-decision-briefing-20261112.md) compares native runtime constraints without allocating globals or approving a descriptor ABI. Owner-rechecked JOB 5325: JOB SUCCESS, **14/14 JES RC=0000**, summary shell RC=0. This recheck does not upgrade interpreted evidence to native acceptance. CO.0 remains IN PROGRESS; CO.1–CO.5 NOT STARTED.


**12 November CO0-U09 owner direction and stack-check source audit:** The owner selected **Approach A (opaque-to-client, valid-live pointer descriptors)** for an initial release, with managed generation-aware handles deferred to future research; recorded in [CO0-U09 owner-decision briefing](co0-u09-native-coroutine-ownership-and-stack-decision-briefing-20261112.md). The [stack-check integration investigation](co0-u09-native-coroutine-stack-check-integration-investigation-20261112.md) verifies the current single active BCPLMAIN `STKLIM` path and compares S1 current-bound switching against S2 per-check lookup **without approving either**. Native register/stack/global design stays pending owner review. CO.0 IN PROGRESS; CO.1–CO.5 NOT STARTED.


**12 November CO.0 gate preparation:** The owner approved **S1 active stack-limit switching** (alongside Approach A pointer descriptors) for the initial release direction; see [U09 stack-check decision](co0-u09-native-coroutine-stack-check-integration-investigation-20261112.md). A [qualified CO.0 acceptance candidate and CO.1 transfer register](co0-acceptance-candidate-and-co1-transfer-20261112.md) consolidates the evidence and clearly retains the original fixed-stack probe FAIL, missing `KM10.COMAIN`, internal tracing limitations and all native ABI/stack/global questions as open or deferred. **READY FOR OWNER REVIEW; CO.0 NOT CLOSED. CO.1–CO.5 NOT STARTED.**


## 12 November 2026 — Formal owner closure supersedes earlier CO.0 status notes

The owner explicitly accepted and **CLOSED CO.0 — Historical Research and Behavioral Contract** with documented qualifications. See [formal CO.0 closure](co0-formal-closure-20261112.md). Earlier dated references to CO.0 IN PROGRESS or NOT CLOSED describe historical checkpoints and are superseded. Original post-promotion fixed-stack JOB 5318 remains FAIL; corrected candidate JOB 5321 PASS is separate. Missing KM10.COMAIN, incomplete internal trace and native-unverified status remain limitations. **CO.1–CO.5 NOT STARTED**; no native implementation authorized.

## 12 November 2026 — CO.1 source investigation initiated

The owner authorized **CO.1 — Native ABI and Stack Architecture** source investigation and an evidence commit. The [initial CO.1 source investigation](co1-native-abi-and-stack-source-investigation-20261112.md) records CG370 linkage, native checked entry, both `STKLIM` and `APLIMIT` consumers, external G40 source/contract discrepancy, stack paint and STACKHWM, allocator constraints, global collisions and isolated candidate verification gates. No descriptor offsets, register-save set, native globals, code implementation or native MVS test results are accepted by this record. **CO.1 IN PROGRESS; CO.2–CO.5 NOT STARTED.**

## 12 November 2026 — CO.1 historical native and ABI checkpoint 2

The owner authorized continuing CO.1 investigation and committing source-backed evidence. [CO.1 checkpoint 2](co1-historical-native-control-block-and-abi-discrepancies-20261112.md) identifies the historical KM10 `COBASE` saved-pointer/parent/per-stack-limit fields; `CSTKBASE/CSTKEND/CSTKHWM` 107–109 source declarations; KM10's callable `STACKBASE()/STACKEND()` versus current G54/G55 data; direct assembler-call versus compiled-wrapper entry choices; `BCPLAPT` hard `APMAXN` cap; test-era `RETIMPL` drift and distinct BCPLM6/D6 versus D7/BCPLM7 overflow RC fixtures. No historical offset, public global number, machine save set or diagnostic alternative is approved by this evidence. **CO.1 IN PROGRESS, design gate OPEN; CO.2–CO.5 NOT STARTED.**

## 12 November 2026 — CO.1 checked-entry source matrix (checkpoint 3)

The [CG370 checked-entry option matrix](co1-cg370-checked-entry-option-matrix-20261112.md) records the source-derived `CGSAVE` +20, +60 and +80 paths. With `STKCKING` and `CALLCOUNTING` together, CG370 emits **two** inline fullwords, but reconstructed `STKCIMP` (+80) only skips one and does not set R5 or check `STKLIM`. Historical `BCPLCLG` defaults to `/CK`; native Bootstrap 48–52 evidence concerns +60, not +80. This is a **SOURCE-OBSERVED compatibility gap**, not a native-failure claim. Do not execute the current +80 path as if its checked-entry contract were accepted. **CO.1 IN PROGRESS; design gate OPEN; CO.2–CO.5 NOT STARTED.**

## 12 November 2026 — CO.1 CK-B production checked-stack baseline reported PASS

[CK-B native production baseline](co1-ck-b-native-checked-stack-production-baseline-20261112.md) records the owner's MVS regression coordinator output from evidence directory `workarea/test-suites/20261113T004711Z-10548-bootstrap-production-76esg_or` (13 November UTC): **Bootstrap 49–52 PASS 4, FAIL 0, SKIP 0, BLOCKED 0; native runner RC=0 for every case**. This is **OWNER-REPORTED NATIVE REGRESSION SUMMARY**, not an independent JES/IFOX/IEWL/GO log review, and the console output does not establish its `git_head`. It verifies the previously tested **+60** checked-entry path at the coordinator level; the combined `/CK` **+80** gap, first coroutine activation and S1 stack switching remain unverified. **CO.1 IN PROGRESS; design gate OPEN; CO.2–CO.5 NOT STARTED.**

## 12 November 2026 — CO.1 CK-C compile-only probe prepared, MVS result pending

The owner authorized further CO.1 investigation and evidence commits. [CK-C candidate preparation](co1-ck-c-compile-only-probe-preparation-20261112.md) reuses existing Bootstrap 51 source, a separate 80-column `/CKN` option fixture, and the established MVS `compile-mvs` driver. The new `tools/bootstrap/probe-co1-ckc.py` automatically checks two or more +80 entry sequences, both inline metadata words, positive frame sizes and `BALR 6,4`, with no IFOX/IEWL/GO. The offline validator passed **11/11 tests**, Python compilation checks passed and a **fake-driver** smoke check passed; no real CK-C JES job or native result is claimed. This probes source-emission shape only, **not** the defective current +80 runtime service. **CO.1 IN PROGRESS; design gate OPEN; CO.2–CO.5 NOT STARTED.**

## 12 November 2026 — CO.1 CK-C compiler-emission result: JOB 5342 PASS

[CK-C JOB 5342 compile-only result](co1-ck-c-jes-5342-compile-only-result-20261112.md) records the owner's guarded-source MVS compiler-only test at HEAD `2aa2058e50eb26b79f2a0f173f2e9669f8ed624c`: **PASS, JOB 5342, two +80 entries, probe RC=0**, with artifacts retained at `workarea/co1-ckc/20261113T013333Z-yv1f65e9`. Classified as **OWNER-REPORTED REAL MVS COMPILER-ONLY PROBE**, backed by tracked code but without independent review of local assembler/JES logs. The earlier preparation note's pending state is superseded for this probe; no native IFOX/IEWL/GO or +80 runtime execution occurred. The `STKCIMP` compatibility gap and design gate remain open. **CO.1 IN PROGRESS; CO.2–CO.5 NOT STARTED.**

## 12 November 2026 — CO.1 CK-D shared-entry and counting source investigation

[CK-D shared-entry design review and /CPN compile-only probe](co1-ck-d-shared-checked-entry-and-counting-investigation-20261112.md) records that compiler option `P` adds `INSERTCOUNT` +20 sites beyond `CGSAVE` +80 procedure-entry metadata, while both reconstructed `CNTIMPL` and `STKCIMP` are stub-only and **do not increment counters**. A proposed `LA 14,4(14); B STKIMPL` bridge could reuse existing safe checked entry but **does not restore historical counting semantics**. These are alternatives for OWNER REVIEW, not approved Core Runtime changes. A separate `/CPN` **compiler-only** probe was locally tested (12/12 unit tests, fake-driver smoke; no real MVS result yet) and added to GitHub to verify extra +20 emission without executing current +80 code. **CO.1 IN PROGRESS; design gate OPEN; CO.2–CO.5 NOT STARTED.**

## 12 November 2026 — CO.1 /CPN compiler-only JOB 5343 counting-site result

[CK-D JOB 5343 /CPN result](co1-ck-d-counting-jes-5343-compile-only-result-20261112.md) records the owner's MVS compiler-only PASS with **two +80 procedure entries, five additional +20 counting sites, JOB 5343, probe RC=0**, and evidence directory `workarea/co1-counting/20261113T015924Z-jv4onj2p`. The guarded WSL operation checked out expected HEAD `89e19b2a160ddc5914bf87f02895b9fd34c8544b`. Evidence class: **OWNER-REPORTED MVS COMPILER-ONLY PROBE**; exact generated assembler and individual JES step reports were not independently reviewed. This supersedes the earlier "not yet MVS-run" status in the CK-D preparation checkpoint; no IFOX/IEWL/GO, native coroutine switch or correct runtime counting is claimed. Owner decision on stub-level compatibility versus real counting remains OPEN. **CO.1 IN PROGRESS; CO.2–CO.5 NOT STARTED.**

## 12 November 2026 — CO.1 checked four-argument and nested-call compiler probe prepared

The [CO.1 four-argument/nested-call checked ABI preparation](co1-native-four-argument-nested-call-checked-abi-probe-20261112.md) introduces a standalone `/CN` **compile-only** source (SUM4/WRAP/START) and `tools/bootstrap/probe-co1-native-call-abi.py`. It checks one `STM 4,10,0(15)`, three or more +60 frame-check entries, R15 workspace formation, `BALR 6,4` nested calls and `BCR 15,11` return without executing native GO. Host-only verifier tests **15/15 PASS**, Python syntax PASS and synthetic end-to-end smoke PASS; **JOB 8123 in the smoke is fake**, not target evidence. Existing native Bootstrap 15 (historical JOB 994) and 17 (JOB 998) guide the source oracle; no current native acceptance is claimed until an MVS compiler run reports its own JOB and artifacts. **CO.1 IN PROGRESS; design gate OPEN; CO.2–CO.5 NOT STARTED.**

## 13 November 2026 — CO.1 checked four-argument/nested-call JOB 5345 compiler-only PASS

[CO.1 native ABI JOB 5345 result](co1-native-call-abi-jes-5345-compile-only-result-20261113.md) records the owner's guarded revision `f09bdf8e63b063b934b9b1ffda42a4c3e99b7b4e` MVS compile-only probe: **PASS, JOB 5345; one four-argument entry, three +60 checked entries, three ordinary calls, probe RC=0**, and evidence retained at `workarea/co1-native-call-abi/20261113T075334Z-aprk7_km`. Classified **OWNER-REPORTED COMPILER-EMISSION EVIDENCE**, not independently reviewed JES/compiler logs or IFOX/IEWL/GO. The earlier probe preparation's MVS-pending note is now superseded. An unrelated root-level untracked `FETCH_HEAD` was observed in the owner's checkout and remains untouched. The +80 and native coroutine design gates remain OPEN. **CO.1 IN PROGRESS; CO.2–CO.5 NOT STARTED.**

## 13 November 2026 — CO.1 first-activation frame and indirect-entry source review

[First-activation return-frame and indirect-entry review](co1-first-activation-return-frame-and-indirect-call-investigation-20261113.md) demonstrates from the exact current `RETIMPL` order that a normally returning first-run worker needs a readable **synthetic caller P/frame word 0** as well as its own R6 exit continuation; a saved entry pointer and stack pointer alone are insufficient. `BCPLMEM` uses R10 as a private base, so its helpers cannot be assumed to preserve the fourth BCPL argument register. A standalone `/CN` procedure-valued indirect-entry **compiler-only** probe and unit tests are prepared (16/16 local tests, fake-driver smoke JOB 8124—NOT MVS); 21/21 source assertions pass. No first-activation layout or E1/E2 choice is approved, and there is no real MVS result yet. **CO.1 IN PROGRESS; design gate OPEN; CO.2–CO.5 NOT STARTED.**

## 13 November 2026 — CO.1 indirect procedure-valued call JOB 5346 compile-only PASS

[CO.1 JOB 5346 indirect-entry result](co1-indirect-entry-jes-5346-compile-only-result-20261113.md) records the owner's guarded-`main` `/CN` compiler-only probe at `c2a68b719be82fcb8d6f23191edaaef10a930aef`: **PASS; JOB 5346; four +60 checked entries, one three-formal entry, four ordinary calls; probe RC=0**. Local evidence: `workarea/co1-indirect-entry/20261113T082652Z-rjkhlkxp`. Classified **OWNER-REPORTED REAL MVS COMPILER-EMISSION EVIDENCE**, not an independently inspected JES or assembler report and not native IFOX/IEWL/GO. The structure-only oracle does not verify the instruction that fetches procedure parameter `F`; the synthetic first-activation frame and all CO.1 owner design decisions remain OPEN. The earlier compile-probe 'pending' note is superseded. **CO.1 IN PROGRESS; CO.2–CO.5 NOT STARTED.**

## 13 November 2026 — CO.1 R4 indirect-target provenance audit prepared

[CO.1 R4 CALLIND origin audit](co1-indirect-r4-origin-compiler-audit-preparation-20261113.md) strengthens the accepted JOB 5346 **structural** compiler-emission evidence without pretending that listing was independently reviewed. Historical `CGENTRY` provides `ENTRY TO CALLIND` labels; `CGSAVE` places the first formal `F` at `P!3` (12 bytes) and `CGAPPLY` calls through R4. A new **compile-only** wrapper audits one CALLIND-specific R4 definition and associated `BALR 6,4`, preserves the full listing and produces a small machine-readable report. Its bounded oracle deliberately fails closed for unknown emitted forms and does not prove GO. Assistant-local checks: **29/29 unit tests**, Python syntax and fake-driver smoke PASS (**synthetic JOB 8125, not JES**), with **16/16** source assertions. Actual MVS result PENDING; first-activation layout, E1/E2 and S1 design gates OPEN. **CO.1 IN PROGRESS; CO.2–CO.5 NOT STARTED.**
