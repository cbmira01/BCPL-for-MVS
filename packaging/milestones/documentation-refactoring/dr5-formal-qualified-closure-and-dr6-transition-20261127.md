# DR.5 — Formal qualified closure and DR.6 transition

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Documentation Refactoring  
**Date:** 27 November 2026 EST  
**Owner disposition:** DR.5 CLOSED (qualified); DR.6 IN PROGRESS  
**Accepted reconciliation revision:** `0f154a5f35d27a43b0c12431a5557a74a23b2888`

The owner directed: “Close DR5, open DR6 with a handoff prompt”. This accepts the [final evidence reconciliation and qualified closure recommendation](dr5-final-evidence-reconciliation-and-closure-recommendation-20261127.md), including its recorded scope and qualifications. That recommendation remains an historical pre-acceptance record. This document establishes the effective march transition; it does not close the milestone.

## Accepted DR.5 results

All thirteen product manuals and five project manuals (152 chapters) remain committed. The five reference manuals govern their individually approved supported public contracts. The [navigation audit](dr5-documentation-navigation-and-reconciliation-audit-20261127.md) checked 715 relative link occurrences and eight heading fragments at its reviewed revision. Current operational documentation and regression totals have been reconciled. Preserve the historical receipts and independent authorities.

| Verification | Accepted scope |
| --- | --- |
| Offline | 963 checker and 38 release tests; all five gates PASS at c5b56cef0e2f9aa830a9b49631868cbc5d380b02 |
| DEBUGINT | Corrected private and installed native six-record oracle PASS; signed extrema included |
| BLIBBLD | Private positive and negative oracles PASS; retain original JOB 1379 failure |
| Routine reconstruction | PASS at e922d3daff98181f7e90c8673e15aedca4a9c461; 8m 05s |
| Independent installed inventory | Exact ten BOOT_OBJ and three EXT_OBJ members |
| Original build payloads | 9 PASS, 0 FAIL after byte-preserving JOB 1448 report recovery; unchanged oracle |
| Installed coroutine verification | PASS, compiler JOB 1454 and native JOB 1455 |
| Consolidated production regression | 219 PASS, 0 FAIL, 1 expected SKIP (083), 0 BLOCKED at a70a424567d670ca8ff60d29da1663903663d09d; 13m 40s |

Device cases 175–176 and private BCPLQSAM cases 198–200 passed. The accepted target receipts are owner-supplied actual transcripts evaluated by the existing independent oracles, not independent access to the operator's raw files. Preserve private successful and unsuccessful evidence outside disposable workarea. Do not publish authenticated decks or raw reports indiscriminately. The initial failed reconstruction and initial report decoding failure remain historical facts. No repeat of accepted operations is required without a demonstrated defect or changed scope.

## Carried qualifications

All qualifications in the final reconciliation remain effective. In particular: private interfaces and exhaustive diagnostic/exceptional-condition coverage; provisional DEBUGINT G!150 and historical FORMTREE:150 conflict; historical BLIB and MR10 diagnostics; expected SKIP 083; repository-wide inbound dependency and individual-file certification; DR.4 deferred transformations, additional documentation testing and distribution; guarded reconstruction controller and new release-driver live integration; historical redistribution rights; and unfinished native-running Cambridge Compiler. Routine reconstruction acceptance is not guarded-controller acceptance. Development verification is not native RC4 functional certification. Preserve published RC4, frozen manifests, registry, allocations, independent oracles, historic contracts, attribution and no-retry evidence. Hosted MVS integration remains deferred until Documentation Refactoring closes.

## DR.6 — Acceptance and Closure

Begin with read-only review and owner discussion of practical maintenance and release-integration policy, consistent with the [milestone](milestone-documentation-refactoring.md), [DR.1 reference authority decision](dr1-reference-authority-owner-decision-20261125.md), [DR.4 distribution closure](dr4-formal-qualified-closure-and-dr5-transition-20261125.md), [final DR.5 reconciliation](dr5-final-evidence-reconciliation-and-closure-recommendation-20261127.md), [documentation catalog](../../../docs/README.md), [runtime and library nomenclature](../../architecture/runtime-and-library-nomenclature.md), [operator policy](../../operations/operator-wsl-command-policy.md), and [release procedure](../../../tools/distribution/How-to-Create-a-Release-Candidate.md).

Proposed discussion agenda, not yet an approved policy:

- Establish economical maintenance rules for code, contract, manual, example and test changes; prevent duplicate active authorities and stale procedural facts.
- Establish release documentation revision binding and review responsibilities under the existing DR.4 policy, without modifying frozen releases or expanding distribution.
- Review the milestone acceptance criteria, approved manual catalog and actual evidence; state each retained qualification and practical disposition. Preserve old paths until their dependencies are understood.
- Agree how future verification, documentation consistency and release-readiness checks fit the four project objectives: easy to modify, reconstruct, test and produce a release.
- Prepare final milestone acceptance recommendation and obtain explicit owner approval before formal closure.

No new milestone, executable changes, MVS execution, release candidate, release publication, renderer, or expanded test campaign is authorized by this transition. Major design and policy decisions require owner review. Follow existing commit and MVS operation approval rules. DR.6 remains IN PROGRESS until separately accepted; the Documentation Refactoring milestone remains open.
