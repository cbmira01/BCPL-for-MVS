# CO.6 — Common Coroutine Behavioral Contract and Cross-Compiler Verification

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.6 — Common Coroutine Behavioral Contract and Cross-Compiler Verification  
**Established:** 16 November 2026 (owner approval in project conversation)  
**Status:** CLOSED (qualified) — owner accepted 16 November 2026  
**Baseline:** GitHub main `60750004f5826bac1355c9c2d32b35ba141628c3` before CO.6 edits

## Scope and comparison boundary

The MR10 kit compiler produces INTCODE executed under ICINT19. The bootstrap/Cambridge compiler currently runs under ICINT19 but produces native System/370 code. CO.6 compares **observable coroutine behavior in the compiled applications**, not the machine code that runs either compiler. Completion of the separate future native-running Cambridge compiler is not a prerequisite.

The common domain is cooperative, valid/live coroutines with one root and no more than two workers; valid first activation, explicit parent transfers, integer argument and result passing, preserved nested continuations and locals, and ordinary deletion/reuse of known-live inactive workers. MR10 and native code retain separate descriptor layouts, stack representations, global-number assignments, limits and ABIs. The accepted native Approach A/S1 1024-word checked worker-stack limit and G!289–300 remain unchanged.

## Observable behavioral requirements

| Topic | Common observation and verification |
| --- | --- |
| Creation and first activation | A valid worker starts at its designated BCPL entry via an implementation-correct bootstrap frame; initial transfer and yield occur in the specified order |
| CALLCO/COWAIT | Parent-to-worker arguments and worker-to-parent values match independent exact-output oracles |
| RESUMECO/parent chain | Valid inactive targets resume with correct parent ownership; busy-target rejection preserves the caller's parent |
| Suspension and continuation | Local and nested-call state survive multiple yields at distinct continuation sites |
| Deletion and reuse | Inactive registered descriptors can be deleted and bounded storage reused without corrupting surviving workers |
| Natural worker return | **SOURCE-OBSERVED shared behavior:** canonical MR10 `COBOOT` and production native `CO3BOOT` can both invoke `FN` again on a later call after ordinary return. Paired interpreted/native execution must still verify the common observable oracle. |

No comparison depends on matching internal descriptor offsets, interpreter P/C, native register values, compiler-generated decks or MR10-local G!6–10/91–95. No arbitrary stale/freed-pointer recovery, unlimited coroutine count or stack size, preemption, abend recovery or untested native compiler execution is implied.

## Original fixed-stack producer/consumer diagnosis

The unmodified accepted `10-coroutines/fixed-stack-producer-consumer` writes `C!0 := C` and treats descriptor words as its initial frame. The reconstructed canonical MR10 bridge instead requires a valid saved CHANGECO frame and first-activation continuation. JOBS **5318 and 5499** failed with interpreted `CODE=-1`, `INTCODE ERROR AT C = 803`, and no producer/consumer records; the JIG10 continuation entered invalid INTCODE. The separately named `fixed-stack-co0-candidate.bcpl` constructs `P=C+3`, `P!0=P`, `P!1=COBOOT` and passed ten alternating producer/consumer records under canonical ICINT19/ICLIB in JOB **5321**.

**Initial contract decision:** Manually constructed workers must satisfy the implementation's supported first-activation frame preconditions. This source-level mismatch is not evidence that the accepted native runtime is defective. Retain the original fixture and its genuine FAIL unmodified. Do not convert it to PASS/SKIP/XFAIL, alter canonical ICLIB to accommodate malformed descriptors, or overwrite native BCPLCO/COROUTIN without a separate evidence-backed design and owner approval. A separately named valid-frame fixture can be promoted after independent MVS verification, but cannot erase the failed original.

## Regression integration

Create project-coordinator selector **`mr10-coroutines`** for the five previously owner-accepted original MR10 `10-coroutines/` identities: compiler-probe, frame-layout-probe, fixed-stack-producer-consumer, resumeco-chain, and create-delete-static-pool. Reuse existing real MR10 compilation, interpreter, output-golden, generated-artifact and JES verification. Preserve `mr10-probes` (eleven accepted cases), regular `mr10` (twelve), and native `coroutines` (177–189; thirteen). The fixed-stack original keeps its expected CODE=0 and real FAIL when it fails: it is not an expected-failure success.

The new interpreted suite and existing native suite are initially **independent** MVS evidence producers; a passing native test is not yet a paired MR10 oracle. If interpreted execution fail-stops at the fixed-stack case, subsequent cases are NOT_RUN and the native suite must be executed separately to retain useful evidence. Do not silently omit a failed case to obtain a green coordinated run.

## Planned CO.6 implementation deliverables

1. Complete the five-case interpreted suite registration and source/contract tests without modifying original historical fixtures.
2. Introduce separately identified valid-frame and common-domain interpreted/native BCPL cases for first activation, nested transfers, exact value round trips, parent-chain handoff, valid deletion/reuse, and natural-return policy. Adapt only implementation-specific bootstrap, globals and linkage.
3. Compare exact complete ordered program outputs, final interpreted phase CODEs, and native Cambridge/IFOX/IEWL/GO/JES steps. Keep explicit per-case PASS, FAIL, BLOCKED, NOT_RUN and UNVERIFIED records.
4. Investigate any demonstrated mismatch and repair a common-contract violation using source changes, independent host checks, isolated MVS builds and owner approval for production runtime modifications.

## Acceptance gate

- MR10's five original coroutine probes are independently selectable and honestly classified. The original fixed-stack FAIL remains visible until genuinely resolved or separately dispositioned by owner approval.
- Paired, source-controlled, valid-domain BCPL cases satisfy the agreed observable contract under **both** interpreted MR10 and native System/370 execution with retained MVS/JES evidence. Do not infer parity from shared test names alone.
- Explicitly disposition the historical invalid first-activation frame and verify the source-shared ordinary-return/re-entry contract in paired interpreted/native MVS runs; document any genuine differences without weakening accepted oracles.
- The prior six regular project suites remain verified against the installed production objects, retaining expected Bootstrap SKIP 083 and the original case 117 IEWL SB2D failure record. Separate new-suite failure is not folded into the 201-PASS CO.5 count.
- Separate owner review and acceptance precede any CO.6 qualified closure, production object promotion or next march. No public release is authorized.

## Governing evidence

- [CO.5 qualified closure](co5-formal-acceptance-and-closure-20261116.md)
- [CO.0 first-activation trace and JOB 5321](co0-u01-static-interpreter-transfer-and-u02-five-probe-gate-20261112.md)
- [CO.5 fixed-stack recurrence](co5-mr10-fixed-stack-negative-code-20261115.md)
- [CO.0 interpreted/native oracle matrix](co0-u08-interpreted-to-native-oracle-matrix-20261112.md)
- [Runtime nomenclature](../../architecture/runtime-and-library-nomenclature.md)
- [Global Number Registry](../../architecture/global-number-registry.md)
- [Git/MVS authority](../../operations/git-mvs-authority.md)

## 16 November 2026 — first CO.6 MVS results and diagnostic continuation

**Tested GitHub `main`:** `b4efa179a3d98b83b310fd9986d2e5fcf02881c2`.
**Evidence class:** OWNER-REPORTED MVS runner excerpts; original summary
JSON and full JES reports were not directly inspected by the assistant.

- `mr10-coroutines` returned coordinator **RC=1 / FAIL**: compiler-probe
  PASS, frame-layout-probe PASS, fixed-stack-producer-consumer genuine FAIL
  (interpreted CODE expected 0, received -1); two subsequent cases NOT_RUN
  under the runner's fail-stop policy. **2 PASS, 1 FAIL, 2 NOT_RUN.**
  Evidence `workarea/project-regressions/20261116T061411Z-32072-jzwqxcat/summary.json`;
  console log `mvs-state/reconstruction-evidence/co6-mr10-20261116T061411Z.log`.
- `coroutines` native production profile returned coordinator **RC=0 /
  PASS**, all existing native cases **177–189 PASS** (13 PASS, zero FAIL,
  SKIP or BLOCKED). Evidence
  `workarea/project-regressions/20261116T061422Z-32091-j8q5ib8j/summary.json`;
  console log `mvs-state/reconstruction-evidence/co6-native-20261116T061411Z.log`.

These separate campaigns do not establish equivalent paired source
oracles or remove the existing original fixed-stack FAIL.

**CO.6 tooling change:** Enable `--continue-known-fixed-stack-failure` exclusively for
the `mr10-coroutines` selection. It continues collecting accepted
later-case evidence **only** after the exact known fixed-stack
diagnostic (compiler/runner RC0, interpreted CODE=-1, unique JES ID).
Any unrelated failure stops immediately. The aggregate still returns
FAIL / nonzero RC, and no historical source or golden changes.

## 16 November 2026 — second interpreted campaign and corrected-frame JOB 7693

**Tested GitHub `main`:** `d0cd9543e3a0f947d61fee497fe1b2d606bb0fa4`.
**Evidence:** OWNER-REPORTED MVS runner excerpt; raw JES reports and complete candidate output not independently inspected.

- `mr10-coroutines` **RC=1 / FAIL**, **4 PASS, 1 genuine FAIL,
  zero SKIP/BLOCKED**. Compiler-probe, frame-layout-probe,
  resumeco-chain and create-delete-static-pool all PASS. The original
  fixed-stack-producer-consumer still fails the exact interpreted
  CODE=0 requirement with observed CODE=-1. The narrow continuation
  policy permitted both later tests to run; it did not hide the failure.
- Coordinator receipt:
  `workarea/project-regressions/20261116T064034Z-34134-dbofgojz/summary.json`;
  operator console log:
  `mvs-state/reconstruction-evidence/co6-mr10-full-20261116T064033Z.log`.
- The separately run corrected-frame
  `fixed-stack-co0-candidate.bcpl` returned compiler driver **RC=0**,
  **JOB 7693**. The supplied grep excerpt showed the job ID but not the
  ten intended producer/consumer records or final interpreted CODE.
  Therefore this attempt is **RUNNER-RC0, ORACLE NOT INDEPENDENTLY VERIFIED**
  on supplied evidence. Earlier JOB 5321 is the existing
  exact-oracle/code-zero/ten-step verified candidate evidence.
  Operator log:
  `mvs-state/reconstruction-evidence/co6-fixed-frame-20261116T064033Z.log`.

## CO.6 paired BCPL application candidate — verification pending

The [CO.6 paired application fixture](candidates/co6-pair/README.md)
introduces separate real BCPL entry programs for MR10 INTCODE and native
System/370, with one shared **eleven-record** output oracle. Both use
valid library-mediated creation rather than hand-constructed interpreter
frames; the observed contract is first activation, 11/31/51/71 argument
delivery, 21/41/61/81 yields, preservation of local 717 across two
suspensions, ordinary worker return and later re-entry, root-controlled
inactive deletion, and ordered completion.

The [new isolated driver](../../../tools/coroutines/run-co6-pair.py)
submits a distinct interpreted MR10 compiler/ICINT job and two
Cambridge compilation jobs plus one four-IFOX/IEWL/native GO job;
it checks complete independent output/JES/phase evidence and retains
both receipts. It reuses the accepted CO.3 isolated linkage adapter
with pinned source hashes, temporary candidate datasets and
read-only BOOT_OBJ. The historical negative fixture, existing
production objects, native numbered regression suite, and
other test oracles are unchanged.

**Independent host verification:** Eight focused Python unit tests PASS
in assistant workspace; Python syntax checked; source files checked for
ASCII, 80-column BCPL card limits and expected markers. This is **not**
a BCPL syntax/compiler or IFOX/IEWL/MVS execution PASS. The paired
application remains **UNVERIFIED on MVS** until the owner supplies
separate actual execution receipts. CO.6 remains IN PROGRESS.

## 16 November 2026 — first paired contract PASS (owner-reported)

**Tested source:** `6cf1bf7444bc3dc8a694a638fbfbb2c051bd8e01`.
The owner executed `tools/coroutines/run-co6-pair.py --run` on MVS,
reporting **RC=0**, `CO.6 MR10 PASS`, `CO.6 NATIVE PASS`, and
`CO.6 PAIRED RESULT: PASS`. The retained evidence directory is
`workarea/co6-pair/20261116T123048Z-sfas9clu`, with operator log
`mvs-state/reconstruction-evidence/co6-paired-20261116T123048Z.log`.

This **OWNER-REPORTED PAIRED-MVS-TESTED** result is stronger than
host-only checks: the versioned runner requires the same **eleven ordered
CO6PAIR records** from both paths, seven zero MR10 ICINT completion
codes, fourteen MR10 zero-RC JES steps, two Cambridge compiler jobs,
and native four IFOX, IEWL and GO zero-RC steps. Its structured receipts
and full JES reports remain in the operator workarea and were **not
independently opened** here. Do not claim those raw reports have been
separately audited or that the original MR10 fixed-stack test has passed.

**Accepted contract coverage for this individual execution:** valid
first activation, repeated CALLCO/COWAIT value transfer, preserved
locals, ordinary worker return/re-entry, and known-live deletion for
one worker. This is not evidence of two-worker parent transfer or reuse
on a paired basis.

## 16 November 2026 — second paired nested/parent-chain candidate

Added [`co6-nested`](candidates/co6-nested/README.md), a distinct
**18-record** paired BCPL scenario for two live workers, recursive
suspended frames, busy RESUMECO refusal, valid parent-chain transfer,
root return, inactive deletion and subsequent reuse. Both executors
reuse the accepted first-pair MVS pipeline and keep separate BCPL
globals, descriptor layouts and sizes; the original first-pair fixture
and original historical fixed-stack negative fixture are unmodified.

The isolated wrapper `tools/coroutines/run-co6-nested.py` delegates
to the already tested driver after revalidating its original fixture
and pinned CO.3 dependencies. Nine focused real host-workspace tests
passed, including golden tampering, malformed records, stack-size and
MR10 descriptor-link rejection, preflight preservation and failure
propagation. No MVS jobs were executed for this new scenario yet.

**CO.6 remains IN PROGRESS.** The next gate is independent interpreted
and native MVS execution of this second source pair, with structured
JES and exact-oracle receipts before any regression-panel promotion
or closure. The original fixed-stack case stays an actual FAIL.

## 16 November 2026 — nested cross-compiler MVS PASS

**Tested source:** GitHub `main` `c71dcc77ee2b8eabdf7f141a2497c3e811f7a7b2`. The owner ran `tools/coroutines/run-co6-nested.py --run`, reporting **RC=0**, `CO.6 MR10 PASS`, `CO.6 NATIVE PASS` and `CO.6 PAIRED RESULT: PASS`. Evidence directory `workarea/co6-nested/20261116T124503Z-mczybqy0`; operator log `mvs-state/reconstruction-evidence/co6-nested-20261116T124503Z.log`.

**Evidence class:** OWNER-REPORTED PAIRED-MVS-TESTED. The source-controlled nested wrapper reuses the first paired interpreter/compiler and native IFOX/IEWL/GO/JES validators, replacing only the two BCPL programs, the exact **18-record CO6NEST** oracle and its isolated workarea. The owner-provided excerpt establishes the overall PASS and the two independent engine statuses. The assistant has **not separately inspected** the raw JES reports, individual job IDs or inner structured receipts.

This complements the previous **11-record** one-worker pairing with two-worker nested continuations, busy RESUMECO refusal, parent-chain handoff, deletion and reuse. Both pairs pass independently on MVS. The original manual-frame MR10 fixed-stack source remains **one genuine interpreted FAIL**, unchanged and not disguised as PASS or SKIP.

## CO.6 — promote paired candidates into regular regression coordination

Two already MVS-tested source pairs are promoted to an independently selectable, source-controlled regular project suite named **`coroutine-contract`** with exact case identities `co6-pair` and `co6-nested`. The suite executes the existing paired engines unchanged, verifies each retained MR10 CODE=0/JES and Cambridge/IFOX/IEWL/GO receipt, requires both individual exact BCPL output oracles and fails closed on any incomplete or mismatched record. The suite manifest is `tests/suites/coroutine-contract.tsv` and the MVS-facing driver is `tools/coroutines/run-co6-contract-regressions.py`.

This is distinct from the original **`mr10-coroutines`** five-probe diagnostic selection (four PASS / one original FAIL) and from the native `coroutines` cases 177–189 (13 PASS in their last verified run). The new paired suite needs its **own fresh MVS run through the project coordinator** before the integrated regression claim is accepted; separate prior pairs do not constitute that run. Owner approval remains required for any qualified CO.6 closure or release decision.

## 16 November 2026 — final consolidated MVS acceptance checkpoint

At GitHub `main` `7e41425cc272c68edea792b1d16b1b2c783eb556`, the owner reported an uninterrupted **PASS / RC=0** for the seven selected regular and paired suites (`mr10`, `bootstrap`, `runtime-extensions`, `bcpltime`, `bcplqsam`, `coroutines`, `coroutine-contract`): **203 PASS, zero FAIL/BLOCKED, one expected SKIP 083**, including both new paired BCPL cases. The original five-case `mr10-coroutines` diagnostic was separately run, returning **4 PASS, one genuine historical FAIL, RC=1**. Combined outcomes are **207 PASS, one SKIP, one real FAIL** across eight suite selections, **not** an unqualified all-suite PASS.

Sources and evidence paths are in the [CO.6 formal qualified acceptance review candidate](co6-qualified-acceptance-review-candidate-20261116.md). Full JES reports remain operator-local and were not independently inspected here. No additional MVS test is required for the qualified acceptance decision; CO.6 **remains IN PROGRESS pending explicit owner approval**.

## 16 November 2026 — approved supported MR10 fixed-stack disposition

After the 203-PASS plus one expected SKIP coordinated campaign
and the genuine original MR10 fixed-stack failure (four PASS, one FAIL),
the owner approved **promoting the distinct valid-frame candidate**
and separating supported regressions from historical compatibility
diagnostics, before accepting CO.6 closure.

The immutable 17-entry historical development-probe manifest,
`fixed-stack-producer-consumer.bcpl`, its original golden, and its
CODE=-1 evidence remain unchanged. A separate five-case
`mr10-coroutines-supported` source manifest selects four accepted
passing probes and the existing `fixed-stack-co0-candidate.bcpl`.
The candidate now has its own exact golden file, identical in records
to the preserved original golden but separate in identity.

The source-controlled runner
`tools/mr10/run-supported-coroutines.py` delegates the four prior
accepted tests to `run-dev-probes`, then verifies the corrected
candidate under ICINT19 using the original accepted *structural*
ten-step/three-phase JES contract. This reuse of structural checks
does **not** change or mark the historical fixture as PASS.
The project coordinator now exposes `mr10-coroutines-supported`
alongside the unchanged `mr10-coroutines` diagnostic.

**Host verification:** eighteen isolated synthetic host unit tests
PASS, including exact original/corrected Git source blobs, manifest
and golden tampering refusals, ICINT19 preflight, semantic record
order, JES/phase mismatch, original accepted receipt rejection,
fail-stop and aggregate RC classification. Python syntax checks PASS.
These are **not** new MVS execution results. A single consolidated
MVS campaign is the remaining gate before updating the formal
qualified acceptance review and requesting explicit owner closure.
No ICLIB, BCPLCO, COROUTIN, historical fixture or production object
was changed.

See the [CO.6 supported/historical resolution record]
(co6-fixed-stack-supported-disposition-20261116.md).

## 16 November 2026 — final supported/historical MVS campaign completed

At **tested** GitHub `main` `216b6707c404a91c796ed8f1419a99ef172b184a`, the owner executed the
single eight-suite supported campaign with `--profile production`,
`--allow-device`, and `--progress`: **RC=0,
PROJECT REGRESSION RESULT: PASS; 208 PASS, zero FAIL/BLOCKED,
one expected Bootstrap SKIP 083**. These are six established
suites (201 PASS, one SKIP) plus the verified
`mr10-coroutines-supported` selection (5 PASS) and the
`coroutine-contract` paired selection (2 PASS).
The supported suite's **five real interpreted MVS tests** passed;
this supersedes only the earlier MVS-UNVERIFIED status of the
supported runner, not historical evidence.

A separate original historical `mr10-coroutines` diagnostic
returned **RC=1/FAIL** with **4 PASS, one genuine original
`fixed-stack-producer-consumer` interpreted CODE=-1 FAIL**.
No original fixture, golden, accepted code or manifest was changed.
The four overlapping historical passing identities are not new
unique supported test cases.

Evidence: `workarea/project-regressions/20261116T151624Z-56400-i4ueoalx/summary.json`,
`workarea/project-regressions/20261116T152532Z-76357-_s4f83jy/summary.json`;
operator logs `mvs-state/reconstruction-evidence/co6-supported-final-20261116T151623Z.log`
and `mvs-state/reconstruction-evidence/co6-historical-final-20261116T151623Z.log`.
The submitted terminal excerpts show status/counts, not the
raw JES reports or the whole receipts independently.

The [revised CO.6 formal qualified acceptance review candidate](co6-qualified-acceptance-review-candidate-20261116.md)
documents met gates and retained limits. **CO.6 remains IN PROGRESS
until explicit owner qualified-closure approval.**
No MVS reruns, source/runtime changes or new march are requested.

## 16 November 2026 — formal owner decision

The owner expressly accepted [CO.6 qualified closure](co6-formal-acceptance-and-closure-20261116.md) following the final MVS-supported campaign. This records **CO.6 CLOSED (qualified)**. All agreed supported verification gates are met within the documented common-domain boundary. The original manually framed MR10 probe still genuinely fails, separately classified, and the previously accepted Approach A/S1 and historical limitations remain. No new official march, production runtime change, or distribution publication follows automatically from closure.
