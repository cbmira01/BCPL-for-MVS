# CO.6 — Common Coroutine Behavioral Contract and Cross-Compiler Verification

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.6 — Common Coroutine Behavioral Contract and Cross-Compiler Verification  
**Established:** 16 November 2026 (owner approval in project conversation)  
**Status:** IN PROGRESS; MVS acceptance gates outstanding  
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
| Natural worker return | **Known divergence:** MR10 COBOOT can invoke FN again after a natural return; accepted native support terminates the worker. Do not call these equivalent before an explicit common-contract decision and tests |

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
- Resolve or obtain explicit owner-approved *narrow exceptions* for first-activation and natural-return differences; never silently weaken either contract.
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
