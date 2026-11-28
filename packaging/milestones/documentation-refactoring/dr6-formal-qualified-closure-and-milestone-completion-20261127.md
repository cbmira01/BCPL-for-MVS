# DR.6 — Formal qualified closure and milestone completion

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Documentation Refactoring  
**Date:** 27 November 2026 EST  
**Owner disposition:** DR.6 CLOSED (qualified); Documentation Refactoring CLOSED (qualified)  
**Acceptance review baseline:** `755b943664c0227c1edc2e01eca1b8292d75e35d`

The owner approved the proposed maintenance and release-integration policy: “I do agree with these policies, I'd like to see them adopted as you stated.” After the milestone acceptance review and qualified closure recommendation, the owner directed: “Please do close the current march, and the milestone. Give me a handoff prompt for a post-milestone discussion.” This accepts the policy and the qualified closure. No new milestone or live operation is authorized.

## Approved maintenance and release-integration policy

Maintain documentation alongside implementation, public contract and test changes; investigate discrepancies rather than automatically overriding code or specification. The five reference manuals govern their individually approved supported public contracts; preserve independent authorities and avoid competing active instructions. Maintain examples, terminology, regression references, links, headings and catalog entries. Prefer real verified BCPL, assembler and JCL; label unverified examples. Retain, consolidate, revise, archive or remove older documentation incrementally after dependency investigation and owner-approved disposition. Preserve historical contracts, records, earlier failures and acceptance evidence. Prefer coherent manuals with chapters over proliferation of documents.

Review affected documentation at march acceptance and affected subject areas at milestone acceptance. Verification is proportionate to the change: purely editorial changes do not require native regression; technical claims, examples and procedures require applicable evidence. Existing verification and promotion gates remain in force. Use existing development and release processes, with no new mandatory documentation-specific CI gates, scheduled repository-wide audits, tools, frameworks, independent documentation registry or rendering/distribution infrastructure.

Canonical UTF-8 Markdown remains in GitHub. Release documentation describes the actual distribution; identify the documentation/producer revision by Git SHA separately from the frozen program-source revision when they differ. Use the frozen manifest for payload selection and dataset inventory and the release registry for identity and lifecycle. Preserve existing BT0001–BT0003 generation, seven-member BT0003 DIST.DOCS project-EBCDIC FB80 representation, companion guide and safeguards against silent truncation or substitution. Preserve published RC4 bytes and mandatory companion documentation. No new schema or automatic enforcement is claimed. Before accepting a future candidate, review its actual documentation, source/revision binding, manifest, registry, selected payloads, installation procedure, limitations, verification and provenance.

The approved policy is incorporated into [How to Develop and Test BCPL for MVS, Chapter 8](../../../docs/project/How-to-Develop-and-Test-BCPL-for-MVS.md) and the [canonical release procedure](../../../tools/distribution/How-to-Create-a-Release-Candidate.md). The [DR.1 reference authority decision](dr1-reference-authority-owner-decision-20261125.md) and [DR.4 distribution closure](dr4-formal-qualified-closure-and-dr5-transition-20261125.md) remain in force.

## Milestone acceptance

| March | Final disposition | Acceptance record |
| --- | --- | --- |
| DR.0 — Inventory and Classification | CLOSED (qualified) | [DR.0](dr0-formal-qualified-closure-and-dr1-transition-20261124.md) |
| DR.1 — Architecture and Outlines | CLOSED | [DR.1](dr1-formal-closure-and-dr2-transition-20261125.md) |
| DR.2 — Product Documentation | CLOSED (qualified) | [DR.2](dr2-formal-qualified-closure-and-dr3-transition-20261125.md) |
| DR.3 — Project Documentation | CLOSED (qualified) | [DR.3](dr3-formal-qualified-closure-and-dr4-transition-20261125.md) |
| DR.4 — Documentation Distribution | CLOSED (qualified) | [DR.4](dr4-formal-qualified-closure-and-dr5-transition-20261125.md) |
| DR.5 — Validation and Reconciliation | CLOSED (qualified) | [DR.5](dr5-formal-qualified-closure-and-dr6-transition-20261127.md) |
| DR.6 — Acceptance and Closure | CLOSED (qualified) | This record |

| Approved milestone acceptance criterion | Disposition |
| --- | --- |
| Authoritative technical information identifiable and not silently superseded | PASS: individually approved transfers and independent authorities retained |
| Concise, coherent, navigable documentation accurately representing capabilities and limits | PASS at accepted scope: thirteen product and five project manuals, 152 chapters, five normative references |
| Substantial reduction of redundant and obsolete active documentation | PASS (qualified): consolidated manuals and active authority; old paths and some legacy prose retained pending dependencies |
| Examples and procedures verified where appropriate with limitations recorded | PASS (qualified): accepted DR.5 evidence; illustrative and untested cases remain identified |
| Release-specific documentation describes corresponding distribution | PASS (qualified): RC4 mandatory companion and frozen artifacts preserved; future candidate policy adopted, new driver not live accepted |
| Historical records, contracts and accepted evidence preserved | PASS at reviewed scope; private evidence remains with operator |
| Reconstruction, regression and release capabilities intact | PASS (qualified): routine reconstruction and regression verified, release offline checks passed; guarded reconstruction and new release orchestration not live accepted |
| Owner approves maintenance policy, qualifications and formal closure | PASS by explicit owner direction |

## Accepted verification evidence

The [DR.5 final reconciliation](dr5-final-evidence-reconciliation-and-closure-recommendation-20261127.md) and [formal closure](dr5-formal-qualified-closure-and-dr6-transition-20261127.md) govern exact evidence revisions and scope. No repeat target or offline campaign was necessary for this documentation-only closure.

| Verification | Accepted result |
| --- | --- |
| Navigation | 715 relative link occurrences and eight heading fragments at audited revision |
| Offline | 963 checker and 38 release unit tests; five of five gates PASS at c5b56cef0e2f9aa830a9b49631868cbc5d380b02 |
| DEBUGINT | Private and installed native six-record oracle PASS, including signed extrema |
| BLIBBLD | Private positive and negative verification PASS; original failure retained |
| Routine unattended batch reconstruction | PASS at e922d3daff98181f7e90c8673e15aedca4a9c461; 8m 05s |
| Independent object inventories | Exactly ten BOOT_OBJ and three EXT_OBJ members |
| Original reconstruction payload audit | Nine PASS, zero FAIL after byte-preserving report recovery; unchanged oracle |
| Installed coroutine verification | PASS, JOBs 1454 and 1455 |
| Consolidated production regression | 219 PASS, 0 FAIL, 1 expected SKIP (083), 0 BLOCKED at a70a424567d670ca8ff60d29da1663903663d09d; 13m 40s |

Device cases 175–176 and private BCPLQSAM cases 198–200 passed. Preserve original BLIBBLD failure and report-decoding failure. Accepted target evidence consists of owner-supplied actual transcripts evaluated against independent oracles, not independent inspection of private raw files. Directory membership is not byte identity; production profile is not universal installed-only execution. Historical evidence remains revision-scoped.

## Retained qualifications and disposition

All DR.5 qualifications remain effective; none is waived by this closure.

- DEBUGINT detailed behavior remains outside normative transfer; G!150 provisional and conflicting with historical FORMTREE:150. No allocation change or native-running compiler compatibility claim.
- Private assembler and host helper interfaces, exhaustive pointer/register, diagnostic, exceptional and multifault coverage remain outside accepted scope. BCPLQSAM private rollback does not guarantee genuine exceptional MVS CLOSE recovery; registrar precedence is bounded, not exhaustive.
- Historical BLIB diagnostic limitations remain. Original MR10 manual fixed-stack activation remains genuine historical FAIL; regression 083 is expected SKIP, not proof of complete storage reclamation. Do not rewrite previous failures. Byte-preserving BLIBBLD report recovery is not a general transport encoding redesign.
- Repository-wide inbound dependency and individual-file certification remain incomplete; do not retire old paths without investigation and approval. Navigation audit is not an exhaustive dependency proof.
- DR.4 additional transformation testing, offline rendering and expanded distribution remain deferred. Printed-card verification is not full byte-level FB80 fidelity proof; preserve original RC4 artifact and required companion.
- Routine reconstruction acceptance is not guarded-controller live integration acceptance. New release-driver live acceptance remains pending; BC0005 does not establish it. Development-target verification does not certify native RC4 functional distribution. No replay of consumed operations, release production or publication is authorized.
- Historical redistribution rights remain unresolved. The native-running Cambridge Compiler remains unfinished. Preserve historical sources, provenance, independent registries, configuration, manifests, test oracles, private evidence and no-retry markers. Do not publish authenticated decks or raw reports indiscriminately.
- Hosted MVS integration was deferred until this milestone closed. Closure removes that milestone dependency but does not initiate or authorize integration.

## Completion and next discussion

The milestone supports the four governing objectives: easy to modify, reconstruct from scratch, test and produce a release. Maintenance is now part of ordinary development and acceptance. Formal qualified closure does not establish exhaustive correctness, new native release certification or legal clearance.

The owner requests a post-milestone discussion, not implementation or establishment of another milestone. Review outstanding opportunities and qualifications with the owner before selecting any next work. No new release, destructive reconstruction, expanded distribution, live integration, or new milestone is authorized.

This is a documentation-only acceptance action. Preserve prior accepted results and frozen materials. See the [milestone definition](milestone-documentation-refactoring.md) and [documentation catalog](../../../docs/README.md).
