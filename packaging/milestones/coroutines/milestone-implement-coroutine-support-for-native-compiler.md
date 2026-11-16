# Milestone: Implement coroutine support for native compiler

**Project:** BCPL for MVS 3.8 Reconstruction  
**Established:** 10 November 2026  
**Status:** ESTABLISHED; CO.0–CO.4 CLOSED (qualified); CO.5 IN PROGRESS

**Marches:** CO.0 CLOSED (qualified); CO.1 CLOSED (qualified); CO.2 CLOSED (qualified); CO.3 CLOSED (qualified); CO.4 CLOSED (qualified); CO.5 IN PROGRESS

**Target:** Native System/370 BCPL applications under MVS 3.8J

## Purpose and boundaries

Implement cooperative coroutine execution for native System/370 BCPL: an ABI-compatible context switch, persistent independent execution stacks, lifecycle routines written in BCPL where feasible, and complete native regression coverage.

"Native compiler" in this milestone title refers to coroutine support in **the native System/370 code the Cambridge compiler generates**. The currently available Cambridge compiler runs as INTCODE under ICINT19 and emits System/370 code. The independently reconstructed, native-running compiler under `cambridge-compiler/` is a separate project deliverable; its completion is **not a prerequisite**. The coroutine contract must remain suitable for applications compiled by that future compiler. This milestone does not claim to make the compiler itself run natively or self-host.

No new BCPL language construct or INTCODE opcode is anticipated. A compiler/code-generator change requires separate evidence and design review.

## Sources of authority

- [Architecture discussion, 3 November](../../architecture/coroutine-design-discussion-20261103.md)
- [Runtime and library nomenclature](../../architecture/runtime-and-library-nomenclature.md)
- [Native runtime contract](../../architecture/runtime-contract-v1.md) and [stack-check contract](../../architecture/stack-check-contract.md)
- [Global Number Registry](../../architecture/global-number-registry.md)
- `richards-bcpltape/` (historical evidence); `mr10-kit-compiler/` (kit and interpreter reconstruction)
- [Research goals and approval gates](coroutine-research-and-design-gates.md)
- [CO.0 historical source audit, 10 November 2026](co0-historical-source-audit-20261110.md) — source findings, historical KM10 coroutine evidence and open execution questions
- [CO.0 MR10 coroutine probe verification plan, 10 November 2026](co0-mr10-coroutine-probe-verification-plan-20261110.md) — five-case JES selection, expected outputs and evidence interpretation
- [CO.0 MR10 coroutine JES summary review, 11 November 2026](co0-mr10-coroutine-jes-summary-review-20261111.md) — five OBSERVED, 62 zero-RC steps, second-pass extracted output and 4/4 compiler-token comparisons matched; owner-accepted golden fixtures; fresh post-promotion runner execution pending

## Architectural direction (qualified CO.1 baseline for CO.2; public ABI still gated)

| Component | Responsibility |
| --- | --- |
| **Core Runtime** | Native `CHANGECO`-equivalent context switch and any minimal stack-limit integration. Prefer a separate IFOX module over unnecessary additions to BCPLMAIN. |
| **BCPL coroutine library** | Portable `CREATECO`, `DELETECO`, `CALLCO`, `COWAIT`, `RESUMECO` where their behavior is verified. Do not modify historical BLIB until historical ownership is supported. |
| **BCPLMEM** | Existing native `GETVEC`/`FREEVEC` candidate for descriptor and stack storage; do not port the MR10 private arena allocator as native G87/G88. |
| **Compiler** | Ordinary procedure-call and activation-record ABI; no coroutine-specific syntax planned. |
| **System Extensions** | No new optional System Extension required for this fundamental runtime mechanism. |

These were working boundaries, now accepted **only as the bounded CO.2 implementation direction** under the [qualified CO.1 closure](co1-formal-acceptance-and-co2-transition-20261113.md). The candidate 24-word descriptor and experimental G!295–299 are **not** approved permanent public ABI allocations. Do not automatically reuse MR10's conflicting global numbers. The [CO.2 kickoff](co2-native-changeco-implementation-kickoff-20261113.md) sets the isolated implementation and MVS evidence gate.

## Discrete, named marches

| March | Name | Work and acceptance gate |
| --- | --- | --- |
| **CO.0** | **Historical Research and Behavioral Contract** | Audit MR10 `ICLIB`, coroutine BCPL, historical tape, saved compiler OCODE/INTCODE, accepted panel and unverified probes. Establish call, yield, resume, result, parent, termination, deletion and reuse semantics. **Gate:** evidence-classified behavior specification and open-question ledger; no native runtime changes. |
| **CO.1** | **Native ABI and Stack Architecture** | Trace actual CG370 call/return sequences, register liveness, first activation, stack limits/guards, global collisions, module linkage, lifecycle ownership. Resolve descriptor, interface, allocation and diagnostic contracts. **Gate:** owner-reviewed native design with isolated native probe plan **before** implementation. |
| **CO.2** | **Native CHANGECO Implementation** | Implement an isolated Core Runtime IFOX primitive against CO.1 design; verify two contexts, first transfer, suspension/resumption, nested locals, continuations and result passing. **Gate:** focused IFOX/IEWL/GO evidence under MVS 3.8J from candidate objects only. |
| **CO.3** | **Coroutine Library and Lifecycle** | Implement and link the agreed BCPL callable routines; verify creation, parent-chain calls, waiting, resumption, termination, deletion and storage reuse. **Gate:** independent BCPL module linkage and deterministic MVS behavioral tests. |
| **CO.4** | **Robustness and Edge-Case Verification** | Verify stack boundaries, recursion, repeated switches, allocation exhaustion, invalid/active/stale descriptors, cleanup and error paths. Do not claim general recovery from arbitrary machine addresses or unrecovered MVS abends. **Gate:** focused positive/negative evidence and no newly broken runtime invariants. |
| **CO.5** | **Integration, Regression, and Release** | Add named tests to the native Bootstrap suite without renumbering historical cases; run MR10, native and applicable project suites; prove clean-room reconstruction, reproducible linking, documentation and release readiness. **Gate:** separate owner acceptance with source revision, complete per-suite outcomes, IFOX/IEWL/GO/JES evidence and separately authorized installation/promotion. |

**Historical 14 November CO.2 checkpoint: CO.0 and CO.1 CLOSED (qualified); CO.2 — Native CHANGECO Implementation CLOSED (qualified owner acceptance); CO.3 — Coroutine Library and Lifecycle IN PROGRESS; CO.4–CO.5 NOT STARTED.** The bounded CO.2 architecture inherits Approach A (valid/live descriptor preconditions), S1 (independent stacks and coordinated limits), native register/continuation restoration and private candidate-only linkage. The public ABI, permanent global allocations, and complete lifecycle rules are not approved for production promotion. See [formal CO.0 closure](co0-formal-closure-20261112.md) and [CO.1 source investigation](co1-native-abi-and-stack-source-investigation-20261112.md). Subsequent marches close only after separate evidence-backed owner decisions. See the [JOB 5356/5357 native candidate PASS](co1-bcpl-native-candidate-jes-5356-5357-pass-20261113.md) for the first fully successful compiler/IFOX/IEWL/GO BCPL coroutine switch. Subsequent candidate successes establish [nested checked-frame survival under JOB 5360/5361](co1-nested-frames-jes-5360-5361-pass-20261113.md) and [two live worker contexts under JOB 5362/5363](co1-two-worker-jes-5362-5363-pass-20261113.md); neither resolves the production design gate. The [direct worker-to-worker candidate PASS, JOB 5364/5365](co1-worker-to-worker-jes-5364-5365-pass-20261113.md), extends the native context-switch evidence while preserving creation-parent semantics. The [terminated-worker re-entry guard candidate PASS, JOB 5366/5367](co1-terminal-worker-reentry-jes-5366-5367-pass-20261113.md), verifies a bounded negative return from a **known-live** terminated descriptor; this remains an experimental interface, not an approved production lifecycle policy. The [bounded descriptor registry PASS, JOB 5368/5369](co1-bounded-descriptor-registry-jes-5368-5369-pass-20261113.md), adds MVS evidence for rejecting unregistered, null, active and terminated targets before an invalid target dereference; it does not establish safe deletion/reuse or a final registry design. The [revocation-before-FREEVEC candidate PASS, JOB 5370/5371](co1-terminated-descriptor-revocation-jes-5370-5371-pass-20261113.md), verifies revoking a terminated descriptor before freeing its storage and rejecting the former address without re-registration. It does **not** establish safe storage-address reuse. The [generation-token same-descriptor-address PASS, JOB 5372/5373](co1-generation-token-same-address-jes-5372-5373-pass-20261113.md), demonstrates a revoked old token remaining invalid after the same still-allocated descriptor is reused for a second worker lifetime, using a test-only BCPL resolution wrapper. It is not proof of actual MVS allocation-address reuse or a production-enforced opaque handle ABI.

## 14 November 2026 — CO.2 native positive-path checkpoint

The [owner-reported CO.2 JOB 5374/5375 PASS](co2-native-changeco-jes-5374-5375-pass-20261114.md)
establishes one completed Cambridge compilation, three RC=0000 IFOX
steps, one RC=0000 IEWL, one RC=0000 GO and a seven-record ordered BCPL
oracle, with native runner RC=0. This is qualified
**OWNER-REPORTED NATIVE-MVS-TESTED** evidence, not independent inspection
of the owner's raw JES receipts. It is promoted as the **CO.2 source
verification baseline**, not as a public API or installed runtime object.

The separate [repeated-continuation CO.2 candidate](candidates/co2-native-continuations/README.md)
extends the check to two suspensions per nested worker, with independent
native MVS evidence pending. Source-only offline verification and a
fail-closed BCPL output marker parser precede its first MVS attempt.
**CO.2 remains IN PROGRESS; CO.3–CO.5 NOT STARTED.**

## 14 November 2026 — CO.2 repeated-continuation first-run failure

The [first repeated-continuation native MVS attempt](co2-native-continuations-failed-oracle-20261114.md)
at `ae51ea4bd3c142bc3aa349d74ee850f2a6fdc4f5` reported
`X1 Y1 X2 Y2 X3 FVALUE`, runner RC=1. The failure is consistent
with proven BCPL source-oracle errors: `DEEP1(4)` computes 23, not 17,
and `DEEP2(5)` computes 32, not 22. Only the fixture's two numeric
assertions were repaired; a new host regression verifies the recurrence
and rejects the previously faulty fixture. The initial failed native
result remains FAIL. A corrected IFOX/IEWL/GO run is pending;
**CO.2 stays IN PROGRESS, CO.3–CO.5 NOT STARTED**.

## 14 November 2026 — CO.2 second native PASS and acceptance review

The [corrected native repeated-continuation JOB 5378/5379 PASS](co2-native-continuations-jes-5378-5379-pass-20261114.md)
at `5f941bb34cc70649f0325bd73f42eeb67397c5d6` reports three
zero-RC IFOX steps, one zero-RC IEWL, one zero-RC GO, and the exact
`X1 Y1 X2 Y2 X3 R1 Y3 R2 PASS` BCPL sequence; runner RC=0.
The earlier `FVALUE` result remains a separately documented FAIL.

The two positive-path native runs use the same separate candidate
`BCPLCO` assembler module and support the focused CO.2 implementation
gate. A [qualified CO.2 acceptance candidate](co2-qualified-acceptance-candidate-20261114.md)
maps the verified behavior to the march gate and explicitly retains
production ABI, public globals, lifecycle, robustness and release hold
points. It is **not** an owner acceptance or closure document.
**CO.0 and CO.1 remain CLOSED (qualified); CO.2 remains IN PROGRESS;
CO.3–CO.5 remain NOT STARTED.**

## 14 November 2026 — CO.2 formally CLOSED (qualified); CO.3 opened

The owner explicitly directed **“Close out CO.2 and proceed to CO.3 without delay.”**
The [formal CO.2 qualified closure](co2-formal-acceptance-and-co3-transition-20261114.md)
accepts the isolated separate IFOX `BCPLCO` candidate's native
behavioral gate with compiler/native JOBS 5374/5375 and 5378/5379.
The original repeated-continuation `FVALUE` fixture failure remains
documented separately and is not converted to a PASS. No installed
`BOOT_OBJ` object, permanent global number or public coroutine ABI
is promoted by this decision.

[CO.3 — Coroutine Library and Lifecycle kickoff](co3-coroutine-library-and-lifecycle-kickoff-20261114.md)
opens the independent BCPL coroutine library and management implementation
work. Its parent-chain, allocation/ownership, module linkage and
lifecycle interfaces require further review and MVS verification.
**CO.0–CO.2 CLOSED (qualified); CO.3 IN PROGRESS; CO.4–CO.5 NOT STARTED.**

## Rules applying to every march

1. GitHub `main` remains the source authority. Use real BCPL, IFOX assembler and JCL; MVS/JES, IFOX and IEWL provide target verification. Preserve current installed `BOOT_OBJ` and use isolated candidates.
2. The native Core Runtime currently has a single working stack and global `STKLIM`; coroutine stacks require explicit bounds/guard and `STACKBASE`, `STACKEND`, `STACKHWM` semantics. No implicit workaround may bypass native checked entry.
3. MR10 uses `CHANGECO:6`, `CURRCO:7`, `COLIST:8`, `CREATECO`–`RESUMECO:91..95`, which conflict with historical Cambridge `LIBHDR`. Allocate native slots only through a subsequent Global Number Registry decision, after checking the full compiler/application export set.
4. A `GLOBAL` declaration is not executable implementation; IEWL linkage is not automatically BCPL global registration. Demonstrate any proposed BCPL library import and Core Runtime export path.
5. Preserve historical sources and provenance. The project-created MR10 coroutine module is behavioral reference, not proof that these precise entry points lived in historical Cambridge BLIB.
6. Preserve all existing regression IDs, manifests, known expected SKIPs and accepted qualifications. The accepted MR10 `basic-coroutine` panel case is not the same as the five `10-coroutines/` probes now independently accepted as interpreted development tests, not native verification.
7. New code must be easy to modify, rebuild from scratch, test in isolation and distribute; no changes to authoritative historical source and no hidden resident-MVS-only patches.

## Exclusions and authorization

No preemptive scheduling, MVS subtasks, timer-driven yields, general thread safety, automatic coroutine syntax, reimplementation of the entire compiler or blanket historical compatibility claims.

**CO.1 → CO.2 transition, 13 November 2026:** The owner explicitly authorized immediate qualified CO.1 acceptance and the start of CO.2. See the [formal acceptance record](co1-formal-acceptance-and-co2-transition-20261113.md) and [CO.2 kickoff](co2-native-changeco-implementation-kickoff-20261113.md). The original authorization boundary below describes milestone creation, not this subsequent approval. Production object installation, permanent global-number assignment and release publication remain separately gated. CO.2's owner-accepted closure on 14 November 2026 is separately recorded above.

Creation of this milestone authorizes only this documentation and planning. It does **not** authorize implementation, JES submissions, new MVS datasets, promotion/overwrite of accepted objects, release publication, or any march closure. The major ABI, stack and library decisions must be discussed and approved before CO.2.

## 14 November 2026 — CO.3 independently compiled lifecycle PASS evidence

Owner-reported native **JOBS 5384–5386** (first lifecycle),
**5390–5392** (nested `RESUMECO` parent-chain) and
**5395–5397** (private `DELETECO` revoke-before-`FREEVEC`
and registry-slot reuse) satisfy the corresponding strict
Cambridge compiler / four-IFOX / IEWL / native GO candidate
oracles. See [parent-chain PASS](co3-parent-chain-jes-5390-5392-pass-20261114.md)
and [delete/reuse PASS](co3-delete-reuse-jes-5395-5397-pass-20261114.md).
Failures in earlier adapter and output-buffer candidates are
preserved separately. This is **bounded candidate evidence**:
no public ABI/global allocation, stale-pointer guarantee,
production object installation or release acceptance is implied.

**Historical checkpoint:** At the time of the three native PASS records,
CO.3 awaited owner acceptance. The subsequent formal closure and CO.4
transition are linked below.

## 14 November 2026 — CO.3 qualified closure and CO.4 opening

Following explicit owner direction, [CO.3 — Coroutine Library and Lifecycle](co3-formal-acceptance-and-co4-transition-20261114.md)
was formally **CLOSED (qualified)** against its independent BCPL module
linkage and deterministic native lifecycle gate. The same decision
opens [CO.4 — Robustness and Edge-Case Verification](co4-robustness-and-edge-case-verification-kickoff-20261114.md)
**IN PROGRESS**, with CO.5 **NOT STARTED**. Public ABI, permanent
global assignments, production object installation, stale-pointer
recovery, full robustness and release acceptance remain unapproved.

**Historical status before owner decision on 15 November 2026:** CO.0–CO.3 CLOSED (qualified); CO.4 IN PROGRESS; CO.5 NOT STARTED.

## 15 November 2026 — CO.4 qualified closure; CO.5 opened

The owner explicitly directed **“Close CO.4, and proceed to CO.5 without delay. Give me a handoff prompt for a new conversation.”** The direction accepts the bounded qualifying disposition in the [CO.4 acceptance review candidate](co4-qualified-acceptance-review-candidate-20261115.md), following the separate owner-reported native PASS results for LIMITS, DENY and ACCOUNT and prior CO.4 bounded stress, safe-negative and STACK/CHURN/BUSY cases.

[Formal CO.4 qualified closure and transition](co4-formal-acceptance-and-co5-transition-20261115.md) documents the source revisions, exact evidence qualifications and untested failure surfaces. **CO.4 — Robustness and Edge-Case Verification: CLOSED (qualified).** This does not establish real MVS GETMAIN exhaustion, deliberate stack-overflow behavior, arbitrary stale-address or ABA-safe pointer recovery, reentrancy or exceptional MVS abend recovery.

[CO.5 — Integration, Regression, and Release kickoff](co5-integration-regression-and-release-kickoff-20261115.md) begins immediately **IN PROGRESS**. Its separate gate requires named native Bootstrap test integration without renumbering existing cases, MR10/native/applicable project suites, clean-room reconstruction, reproducible linking, release documentation, and owner-reviewed per-suite/JES evidence. A CO.5 start does **not** authorize destructive rebuilds, installed-object changes, permanent globals, public ABI freeze, release publication or CO.5 closure.

**Current status as of 15 November 2026: CO.0–CO.4 CLOSED (qualified); CO.5 IN PROGRESS.**

## 15 November 2026 — CO.5 integrated native coroutine suite PASS

At tested GitHub `main` revision `53a4e4feebfec3f41223288416d2f0a3011bb77a`, the owner-reported
`production` run passed all thirteen native coroutine cases 177–189:
**13 PASS, 0 FAIL, 0 SKIP, 0 BLOCKED; RC=0; 0m52s**.
[Execution evidence, exact case matrix and qualifications](co5-integrated-coroutine-native-pass-20261115.md).
Raw JES reports were retained in the operator workarea, but not separately
audited in this conversation. Other project suites and clean-room/release
gates remain open. **CO.5 stays IN PROGRESS.**

## 15 November 2026 — CO.5 MR10 interpreted legacy compatibility qualification

The coordinated MR10 Development Probe campaign at
`803c5ba0c712a36c043f20da7cbc4987c17feb1d`
recorded **7 PASS, 1 FAIL, 3 NOT_RUN**. JES 5499's interpreted
`CODE=-1`, `INTCODE ERROR AT C = 803`, 101-cycle signature matches
CO.0 JOB 5318's documented legacy fixed-stack incompatibility; it is
not a new native System/370 coroutine regression.
[CO.5 recurrence evidence](co5-mr10-fixed-stack-negative-code-20261115.md)
and [the accepted CO.0 qualified disposition](co0-u01-static-interpreter-transfer-and-u02-five-probe-gate-20261112.md)
require preserving that original FAIL; the compatible separate
`COBOOT`-style source passed JOB 5321. Continue unexecuted MR10 probes
and other suites as separately reported runs. Do not claim an
unqualified full-project PASS without a distinct owner-approved
resolution of the known incompatible accepted fixture.
**CO.5 stays IN PROGRESS.**

## 15 November 2026 — CO.5 cross-suite regression checkpoint

At GitHub `main` revision `6f039e7bd1e3cd8e57ef8b4fede986920b1172e7`, the owner reported a
**PASS/RC=0** five-suite coordinated campaign (MR10 12/12; Bootstrap
145 PASS + expected SKIP 083; Runtime Extensions 13/13; BCPLTIME
4/4; Coroutines native 177–189 13/13), a separate 12/12 PASS for
BCPLQSAM non-device cases 163–174, and a 3/3 PASS for the remaining
MR10 Development Probes with 40 JES step contracts verified by the
runner. These supplement the preceding seven Development Probe PASS
results and their **one preserved legacy fixed-stack FAIL**. Across
unique current suite identities, **209 PASS, 1 legacy FAIL, 1 expected
SKIP and 2 device cases not run**. There is no claim of a single
unqualified all-suites PASS.

See [CO.5 cross-suite regression checkpoint](co5-cross-suite-regression-checkpoint-20261115.md)
for the exact evidence paths, status distinctions and release gates.
The known legacy failure remains under CO.0's qualified compatibility
disposition. Unapproved device operation, clean-room reconstruction,
installed-object promotion, public ABI publication and separate owner
CO.5 acceptance remain outstanding. **CO.5 IN PROGRESS.**

## 15 November 2026 — clean-room reconstruction verification

At GitHub revision `2d0cfb90a1cda0cfeb73c45cb00a8fe1f90b3c18`, the operator completed
`tools/reconstruction/rebuild-from-source --unattended --batch-populate`,
all nine driver guide steps **RC=0**, total **2m 11s, RC=0**. The
29 managed MVS datasets were deleted/recreated; **171** tracked and
**12** generated members populated; ICINT19, CAMBBLD, seven native IFOX
Core Runtime members, BLIB and the three optional System Extensions
rebuilt/installed with zero-RC MVS job receipts. The candidate coroutine
module was **not** installed in production `BOOT_OBJ`.
See [CO.5 clean-room reconstruction MVS evidence](co5-clean-room-reconstruction-mvs-pass-20261115.md).
This baseline rebuild **does not establish post-rebuild regression
acceptance**. **CO.5 IN PROGRESS.**

## 15 November 2026 — owner-approved coroutine production allocation

The owner authorized permanent native coroutine **G!289–300**
assignments and production promotion, explicitly deferring the
`config/dspal.yaml` update. The new Git production sources retain
the accepted CO.2/CO.3 implementations and test oracles, export
`STKLIM` from canonical `BCPLMAIN`, and provide two separately
rebuildable production relocatable objects: `BCPLCO` and
`COROUTIN`. See
[CO.5 production promotion and operator verification](co5-production-promotion-20261115.md).
Until the manifest is updated, staging is manual and the accepted
clean-room procedure cannot reproduce these two new members by
itself. Installed MVS object and IEWL/GO verification remain
pending. All CO.4 bounds remain binding. **CO.5 IN PROGRESS.**

## 15 November 2026 — production installation and installed-link PASS

At tested GitHub revision `4bdf3509d99a82ee9784f5978bef0c6f2802829a`, the owner confirmed five host
unit PASS results, Cambridge library compilation JOB **5972** and
manual MVS source/JCL staging JOBS **5973–5979**. Production
`BLDBMAIN` JOB **5981** built and installed seven Core Runtime
modules, all RC=0000. `BLDCORCO` JOB **5983** installed and
IEBCOMPR-verified `BOOT_OBJ(BCPLCO)`, and `BLDCORLB` JOB
**5985** did the same for `BOOT_OBJ(COROUTIN)`. Both reported
IFOX severity 0 and every stage RC=0000. The installed object
library now contains **10 members**.

The installed-only verifier compiled the accepted BCPL application
as JOB **5987** and ran IFOX/IEWL/GO JOB **5988** against the
installed production objects, all RC=0000 with the accepted
21-record `CO3BCPL` oracle. See
[CO.5 installed production verification](co5-installed-production-pass-20261115.md).
Post-promotion full regressions and the owner-deferred
`config/dspal.yaml` clean-room integration remain open.
**CO.5 IN PROGRESS.**

## 15 November 2026 — CO.5 production installation and regression checkpoint

The owner reported installed `BOOT_OBJ(BCPLCO/COROUTIN)` binary
readback and native IFOX/IEWL/GO **PASS** (JOBS 5981/5983/5985,
5987/5988). Post-installation tests at Git
`b2ff3bc8d4d8e1373aa1a58e8b08bcf1ab51be30` yielded **201
regular-suite PASS, zero FAIL, one expected SKIP (083)**, including
coroutines 177–189 and device-authorized BCPLQSAM 175/176.
The separate 11 accepted MR10 Development Probes produced 10 PASS
and one already-qualified but actual FAIL in the original fixed-stack
probe. See [post-install regression checkpoint](co5-post-installation-regressions-20261115.md).

The owner subsequently authorized the deferred `config/dspal.yaml`
and both clean-room entry-point changes. Git integration now stages the
tracked coroutine source/JCL, compiles COROUTIN after rebuilding
CAMBCOMP, installs and binary-verifies both objects, requires the
ten-object inventory, and executes the installed-only oracle.
**Fresh operator MVS clean-room evidence and separate owner acceptance
are still required. CO.5 remains IN PROGRESS.**

## 16 November 2026 — reconstructed production coroutine clean-room PASS

Owner-reported clean-room driver RC=0 at revision `788616e6d34325cbe6a9473edcc6be340da3e577`:
`BOOT_OBJ` verified **10 exact production members**, and the installed
coroutine oracle reported **PASS** (compiler JOB 6489, native JOB 6490;
IFOX/IEWL/GO all RC=0000). Rebuild elapsed **2m 47s**. The retained
operator log is `mvs-state/reconstruction-evidence/co5-rebuild-20261116T005114Z.log`.
See [CO.5 Git-driven production clean-room evidence](co5-production-clean-room-pass-20261116.md).
Fresh post-rebuild project regressions and separate owner closure are
still required. **CO.5 IN PROGRESS.**
