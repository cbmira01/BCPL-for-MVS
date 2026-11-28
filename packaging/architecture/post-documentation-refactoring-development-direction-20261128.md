# Post-Documentation Refactoring — development direction

**Project:** BCPL for MVS 3.8 Reconstruction  
**Date:** 28 November 2026 EST  
**Disposition:** Owner-approved post-milestone direction; establish the next milestone in a separate discussion.  
**Review baseline:** `b4856c6fac6591c6657124cefc339a20d1cc15d2`.

Documentation Refactoring is CLOSED (qualified). The owner and assistant discussed the remaining technical obligations and future opportunities. The owner agreed to prioritize completion of the native-running Cambridge Compiler and directed that the discussion be recorded and committed, followed by a handoff to establish that milestone. This record does not assign a new milestone title or march identifiers, authorize implementation or reopen accepted milestones.

## Governing philosophy

Keep the project easy to modify, reconstruct from scratch, test, and produce a release. Prefer simple, inspectable orchestration built on independently testable MVS tooling. In particular, clean-room reconstruction should remain a straightforward, deterministic full rebuild, not an elaborate transaction-management system. Preserve independent verification, actual MVS evidence and failure records. Avoid duplicate orchestration, unnecessary infrastructure and recurring verification without a defect or changed scope.

## Agreed dispositions

| Subject | Owner-approved direction |
| --- | --- |
| Native-running Cambridge Compiler | Next principal product objective. Establish its milestone purpose, technical scope, architecture, marches and acceptance criteria before implementation. |
| Hosted MVS integration | Deferred by owner direction; retain the separate [discussion and deferred direction](hosted-mvs-integration-discussion-20261127.md). Continue the established WSL/Docker/Hercules/TK5 environment and preserve existing offline Actions capabilities. |
| Guarded reconstruction controller | Retire as a separate reconstruction path, subject to dependency review and separate approval of actual changes. Do not pursue live acceptance merely to certify a redundant driver. |
| Routine clean-room reconstruction | Retain [rebuild-from-source](../../tools/reconstruction/rebuild-from-source) and the [canonical runbook](../../docs/Rebuild-BCPL-for-MVS-from-source.md) as the operative reconstruction path. Preserve unattended and batch-population capabilities and independent checks. Consider genuinely useful safeguards at the underlying tool level only when justified and approved. |
| New release driver | Defer substantial development and live MVS acceptance until the native-running Cambridge Compiler is available and another release is warranted. Preserve current tools, offline evidence and release contracts. Address demonstrated deficiencies proportionately; no new release-tool milestone now. |
| Remaining runtime and compiler qualifications | Retain as outstanding technical obligations; address when relevant to development, an accepted contract or native compiler reconstruction. No separate corrective milestone or general verification campaign now. |
| Standard Libraries, System Extensions and applications | Defer expansion until after completion of the native-running Cambridge Compiler, except any separately approved facility demonstrated necessary for reconstruction. Preserve existing proposals and practical application ideas. |
| Decimal Arithmetic | Remains indefinitely deferred to deep background under the existing owner decision. |
| Historical redistribution rights | Retain unresolved qualification and revisit before future public releases. No new permission or legal clearance is implied. |
| Project simplification | Ordinary development responsibility, not a separate milestone. Reduce redundant tooling and documentation only after dependency investigation and approval. |

## Reconstruction-controller retirement boundary

The existing guarded controller adds scope-bound interactive approval, exact managed-dataset and workarea checks, source/configuration drift refusal, two-sample JES-idle observation and automatic payload/evidence verification. These are useful capabilities, but a second orchestration implementation also increases maintenance cost, interaction and failure modes. The dedicated single-operator MVS model and demonstrated routine reconstruction make the second path unnecessary as a prerequisite to further compiler work.

Retirement direction is agreed, not executed. Preserve the [guarded integration plan](../distribution/clean-room-reconstruction-live-integration-plan-20261105.md), [controller documentation](../../tools/reconstruction/README.md), accepted historical records, independent payload oracles, object inventories and regression tests. Identify actual callers, imports, shared verification modules, documentation and tests before proposing removal. No removal, path relocation, test retirement, or conversion of existing public contracts is authorized by this record. Live guarded acceptance remains unestablished; routine reconstruction does not establish it. The owner remains responsible for quiescing other submissions and authorizing destructive reconstruction.

## Outstanding technical obligations

All qualifications in the [DR.6 formal closure](../milestones/documentation-refactoring/dr6-formal-qualified-closure-and-milestone-completion-20261127.md) and [DR.5 final reconciliation](../milestones/documentation-refactoring/dr5-final-evidence-reconciliation-and-closure-recommendation-20261127.md) remain effective, including:

- Detailed DEBUGINT normative behavior and the G!150/FORMTREE:150 allocation conflict; investigate in compiler integration, with no global reassignment authorized now.
- Private assembler and host-tool interfaces; historical BLIB diagnostics; original MR10 fixed-stack activation FAIL and expected regression SKIP 083.
- Incomplete exceptional-condition, pointer/register, diagnostic and multifault coverage; bounded registrar precedence and BCPLQSAM exceptional CLOSE/rollback limitations.
- Incomplete repository-wide inbound documentation dependency certification; deferred transformation testing, offline rendering and expanded distribution.
- Pending new release-driver live acceptance and absent native distribution functional certification for RC4.
- Historical redistribution rights and unfinished native-running Cambridge Compiler.

Preserve the exact accepted evidence revisions and scope. The routine unattended reconstruction PASS (8m 05s), nine original payload audits PASS, independent ten BOOT_OBJ and three EXT_OBJ inventories, installed coroutine verification and production regression 219 PASS / 0 FAIL / 1 expected SKIP / 0 BLOCKED (13m 40s) are not repeated merely for this transition. The offline five-gate PASS (963 checker and 38 release unit tests) is likewise retained at its recorded revision.

Preserve published RC4, frozen manifests, registry records, documentation, Global Number Registry, historical source, independent oracles, accepted engineering and verification evidence, and private no-retry markers. Do not publish authenticated decks or raw JES reports indiscriminately.

## Next milestone establishment

Begin a source-grounded design discussion for completion of the native-running Cambridge Compiler. Distinguish the MR10 Kit Compiler, interpreter-hosted demoted Cambridge Compiler and native-running Cambridge Compiler. Reuse the established bootstrap, Core Runtime, Base Library, Coroutine Support Library and MVS tools. Determine the historical compiler source selection, demotion differences, dependency/global requirements, native compiler build and execution model, self-compilation criteria, test scope, reproducibility and promotion boundaries. Consult the existing project records before choosing any milestone name or march numbering. Obtain owner approval of the detailed scope and roadmap before implementation or milestone opening. Future release production remains separately authorized.

Documentation maintenance is ordinary development responsibility under the DR.6 policy. No new milestone, MVS operation, code change, release production or publication is effected by this record.
