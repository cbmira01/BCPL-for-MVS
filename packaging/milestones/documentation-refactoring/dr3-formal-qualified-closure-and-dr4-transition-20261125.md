# DR.3 — Formal qualified closure and DR.4 transition

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Documentation Refactoring  
**Date:** 25 November 2026 EST  
**Owner disposition:** DR.3 CLOSED (qualified); DR.4 IN PROGRESS  
**DR.3 starting revision:** 2ca15e3feef49eb803bb962ee1644ca97945e44b  
**Acceptance review baseline:** ead6af457b3e96209d246589cef33d2c00cb3060

Owner direction: “Commit the final three files, conduct acceptance review, commit acceptance, then give me a handoff to DR4.” This authorizes the final draft commit, the drafting-march acceptance record and transition. Closure is qualified to the completed drafting and preservation scope; it does not approve individual normative transfers, software changes, destructive operations, a new release or publication.

## Acceptance review

Compared the complete Git trees at the DR.3 starting revision and acceptance baseline. Before this closure, exactly five project manuals and five migration ledgers were added, and docs/README.md was changed. No deletions or other modified blobs occurred. The final manual batch is committed at the acceptance baseline.

| Manual | Approved chapters | Draft commit |
| --- | ---: | --- |
| [How to Reconstruct BCPL from Source](../../../docs/project/How-to-Reconstruct-BCPL-from-Source.md) | 8 | c81fee5ca42263f862e5fa6a9826d68706b47887 |
| [How to Develop and Test BCPL for MVS](../../../docs/project/How-to-Develop-and-Test-BCPL-for-MVS.md) | 8 | 8a5c6a8b3fa7ee2badf39756b0a2e436e6423b5c |
| [Reference for Project Tools](../../../docs/project/Reference-for-Project-Tools.md) | 9 | a07fe5290c507c575269b2acd1e1ac7914a35704 |
| [How to Create a Release Candidate](../../../docs/project/How-to-Create-a-Release-Candidate.md) | 8 | f111b92ff7fb8805c4f62bde46d8249752b5740b |
| [Explanation of the MVS Programming Environment](../../../docs/project/Explanation-of-the-MVS-Programming-Environment.md) | 12 | ead6af457b3e96209d246589cef33d2c00cb3060 |

| Gate | Disposition |
| --- | --- |
| Approved manual catalog and exact chapter headings/order | PASS: 5/5, 45/45, compared to [approved outlines](dr1-manual-outlines-and-migration-20261125.md) |
| Documentation catalog and subject navigation | PASS for drafting scope: all five manuals linked; 13 product manuals with 107 chapters also remain present |
| Repository-relative paths in new project manuals | PASS: 198 link occurrences |
| Repository-relative paths in manuals, five ledgers and docs/README.md | PASS: 417 link occurrences; no missing paths (not exhaustive external link/anchor review) |
| Fenced code/diagram blocks | PASS: 40 balanced; no literal backslash-n formatting defect |
| Existing source/contract/evidence preservation | PASS: complete tracked-tree comparison, no changes outside above drafting inventory |
| Current procedure, test and release boundaries | PASS for drafting scope with clarification below; retain original canonical paths |
| Complete clause-level reconciliation, technical validation and target verification | Deferred to DR.5; not PASS |

The five manuals give coherent treatment to safe manual and unattended reconstruction, development and promotion, independent tests and device safeguards, maintained tool interfaces, candidate review and release, and the System/370/MVS programming environment. The review checked the recorded migration findings and material safety distinctions, not every executable option or historical statement. All eighteen approved product/project manuals (152 chapters) now have substantive drafts. The existing execution instructions, reference contracts and source-local documents remain available; neither this review nor chapter completeness constitutes transfer of their authority.

### Acceptance-review clarification

The manual reconstruction preflight now explicitly states that DSPAL status --probe submits a real IEFBR14 JES job and checks its result. It is not a JES-idle check; distinguish the separate host/endpoint reconstruction plan --probe. This source-derived clarification is supported by [DSPAL core](../../../tools/datasets/dspal-core.py) and [the reconstruction tools reference](../../../tools/reconstruction/README.md). No command, policy or executable behavior changed. Existing operator-approval and quiescence requirements remain.

## Retained migration obligations

- [Reconstruction ledger](dr3-reconstruction-manual-migration-20261125.md): accepted simple driver versus guarded controller pending live acceptance; source pinning, destructive scope, actual BLIBBLD verification limits, twelve-generated-member exception, ten installed production objects; prior owner-reported runs remain revision-scoped.
- [Development/testing ledger](dr3-development-testing-manual-migration-20261125.md): actual source/installed selections, device guard, case 083 expected SKIP, supported 208 PASS / 0 FAIL / 0 BLOCKED / 1 SKIP campaign and distinct historical failure; exact source identity and complete current evidence remain unverified.
- [Tools ledger](dr3-project-tools-reference-migration-20261125.md): dispatcher/parser and RC differences, preview output deletion, principal-interface coverage rather than exhaustive options, environment precedence and error-path verification.
- [Release ledger](dr3-release-candidate-manual-migration-20261125.md): canonical procedure remains at tools/distribution/How-to-Create-a-Release-Candidate.md; registry and frozen manifest authority unchanged, no-retry and evidence binding, new orchestration offline-tested only; BC0005 does not prove current driver's live behavior.
- [MVS explanation ledger](dr3-mvs-environment-explanation-migration-20261125.md): selected IBM indexed primary-source text and source excerpts, incomplete scanned-page retrieval and exact-edition review; no fresh target execution of explanatory/adapted examples.

Carry forward DR.0 dependency qualifications and the DR.2 reconciliation obligations. Source-local instructions and older active prose may still be stale, contradictory or redundant; original paths are intentionally retained until coverage, dependency analysis and owner-approved disposition. No comprehensive manual-to-contract transfer is approved. The [reference authority decision](dr1-reference-authority-owner-decision-20261125.md) remains operative. Global allocations, config, registry, manifests, independent oracles, legal and release-specific documentation remain separately authoritative. No new unit-test campaign, MVS job, release operation, independent private receipt inspection, published asset rehash or complete cross-revision source-identity comparison was performed in this acceptance review. Existing preservation and qualified release status are unchanged.

## DR.4 — Documentation Distribution

Begin design review with the owner, not immediate implementation. [Canonical Markdown decision](dr1-canonical-markdown-owner-decision-20261125.md), [navigation decision](dr1-navigation-owner-decision-20261125.md), [approved outlines and migration](dr1-manual-outlines-and-migration-20261125.md), [documentation discussion](../../architecture/documentation-refactoring-discussion-20261124.md), [distribution index](../../distribution/README.md), [manifest index](../../distribution/manifest/README.md), [registry](../../distribution/registry/releases.yaml), [canonical release how-to](../../../tools/distribution/How-to-Create-a-Release-Candidate.md) and current [release driver](../../../tools/distribution/create-release) govern the initial review.

- Repository UTF-8 Markdown remains canonical; GitHub repository presentation remains primary. No independent Wiki; Pages remains deferred.
- Agree on offline representation, selected audience/manual scope, minimal rendering approach, MVS-readable FB80 representation, member mapping, navigation, record-width and target encoding policy, and release integration before implementing. No arbitrary format/size assumption.
- Review existing generated BT0001–BT0003 and companion package, frozen layout and release-specific facts. Distinguish product content from maintainer documentation and derive release identity, inventory and supported scope from the applicable frozen manifest and registry where practical. Preserve exact RC4 bytes, mandatory companion, frozen manifests, existing reservations, provenance and private evidence.
- Propose independently reviewable transformations and deterministic checks for width, encoding, meaningful content, code/diagram/table handling, links and member names, no silent truncation or lossy substitution. Establish actual MVS verification plan and obtain separate owner approval for target writes or media operations.
- Do not silently extend the accepted tape layout, publish draft contracts as normative, replay consumed production, or treat offline transformations as actual MVS verification. DR.5 and DR.6 remain NOT STARTED.

This transition authorizes discussion and read-only design inspection. Major design decisions, implementation, commits, relocation/retirement and any state-changing MVS or release action remain subject to the applicable owner authorization.
