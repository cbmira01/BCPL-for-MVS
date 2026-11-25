# DR.4 — Formal qualified closure and DR.5 transition

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Documentation Refactoring  
**Date:** 25 November 2026 EST  
**Owner disposition:** DR.4 CLOSED (qualified); DR.5 IN PROGRESS; DR.6 NOT STARTED  
**Design review baseline:** `2a4f25a805cd08c73d75281dc1d9305d9dcb9b6d`

The owner directed: “Commit these decisions, close DR4, and give me a handoff to DR5.” Qualified closure records the approved narrowed distribution policy, not a new implementation or verification campaign. The previous [DR.3 closure](dr3-formal-qualified-closure-and-dr4-transition-20261125.md), [canonical Markdown decision](dr1-canonical-markdown-owner-decision-20261125.md), [navigation decision](dr1-navigation-owner-decision-20261125.md) and [reference authority decision](dr1-reference-authority-owner-decision-20261125.md) remain applicable.

## Approved distribution decisions

| Area | Decision |
| --- | --- |
| Canonical manuals | UTF-8 Markdown in Git; GitHub primary. Offline reading may use Markdown itself. |
| Other representations | Defer HTML, PDF and other offline rendering; no independent Wiki; Pages remains deferred. |
| MVS scope | Small release-specific operational document set, not the complete product or project manuals. |
| MVS organization | Retain existing BT0003 / DIST.DOCS PDS and seven-member inventory: README, INSTALL, DATASETS, COMPILE, VERIFY, RELEASE, LICENSE. |
| MVS format | Plain text, not Markdown or Unicode, in the established project EBCDIC representation; DSORG=PO, RECFM=FB, LRECL=80, BLKSIZE=800. |
| Release archive | Retain existing required companion materials; defer inclusion of complete manuals. |
| Version binding | Identify documentation by Git commit SHA. Distinguish documentation/producer revision from frozen program-source revision when they differ. |
| Release integration | Retain current create-release generation of BT0001–BT0003 and companion guide, drawing release facts from the applicable frozen manifest and registry. No new renderer or distribution infrastructure. |
| Safeguards | Retain existing record-width, character and encoding safeguards; no silent truncation or substitution. |
| Additional tests | No new documentation-specific test suite or dedicated MVS documentation verification campaign at this time. |
| Tape layout | Unchanged. No extra members or datasets authorized. |

The existing [distribution index](../../distribution/README.md), [manifest authority](../../distribution/manifest/README.md), [release registry](../../distribution/registry/releases.yaml), [RC4 frozen manifest](../../distribution/manifest/releases/BCPL-0.1.0-rc4.yaml), [release procedure](../../../tools/distribution/How-to-Create-a-Release-Candidate.md) and [release driver](../../../tools/distribution/create-release) remain operative. Documentation revision identification is a policy using Git SHA, not a new manifest schema or implemented enforcement mechanism. In particular, an RC4 program-payload reuse does not make the current documentation revision the program-source revision.

## Closure scope and qualifications

Read-only repository review confirmed the existing BT0003 seven-member FB80 contract and the release driver's fixed RC4 layout, generation of the bootstrap, installer, documentation and companion guide, and existing character/width checks. The current printed-card verifier is not a complete byte-level FB80 fidelity oracle: it rejects blank canonical cards and ignores trailing blanks. No new encoding or record-fidelity proof is claimed. The current release driver is offline-tested only; BC0005 does not prove its live acceptance.

No rendering, code, configuration, manifests, registry entries, historical contracts or published artifacts are changed by this closure. No documentation tests, actual MVS jobs, private evidence inspection, release reservations, tape production or publication are performed. HTML/PDF rendering, full manual packaging, additional MVS manual organization and dedicated transformation verification are deferred rather than passed. Preserve exact published RC4 bytes, mandatory companion guide, frozen manifests, tag, reservations, provenance, private evidence and no-retry markers. Historical redistribution rights remain unresolved.

The documentation distribution march is closed by owner direction within this narrowed policy scope. The larger technical validation and reconciliation obligations remain for DR.5; no individual normative authority transfer is implied.

## DR.5 — Validation and Reconciliation

Begin with read-only review of the [milestone](milestone-documentation-refactoring.md), DR.0 dependency qualifications, DR.2/DR.3 closure records and per-manual migration ledgers, the [approved outlines and migration approach](dr1-manual-outlines-and-migration-20261125.md), [reference authority decision](dr1-reference-authority-owner-decision-20261125.md) and [documentation catalog](../../../docs/README.md).

- Establish an economical reconciliation inventory for all thirteen product and five project manuals (152 chapters). Use existing migration ledgers, actual code, headers, accepted evidence and governing contracts; prioritize substantive inaccuracies and safety-sensitive procedures.
- Reconcile normative clauses, compiler-specific scope, global allocations, extension APIs, runtime/library terminology, tool interfaces, reconstruction, test and release procedures. Distinguish supported, distributed, verified and unfinished facilities.
- Review link/anchor navigation, dependencies and candidate dispositions for redundant or obsolete documents. Preserve historical records and executable dependencies. No bulk relocation, deletion or authority transfer without owner approval.
- Use existing accepted evidence where sufficient; seek focused actual BCPL, IFOX, IEWL, JES and MVS evidence when material uncertainty warrants it and the owner authorizes state-changing operations. Do not replay consumed operations. The DR.4 deferral of dedicated documentation transformation tests does not remove DR.5's technical reconciliation responsibility.
- Record each unresolved qualification and proposed normative transfer, including exact scope, old and new references, evidence, effective revision and owner approval. Registries, configuration, manifests, oracles, legal records and frozen release-specific documentation retain their independent authority.
- Discuss the reconciliation sequence and any major design choices before implementing. Obtain approval for further commits and state-changing actions; DR.6 remains NOT STARTED.

Acceptance of DR.5 requires explicit owner review of the reconciliation, verification limits, remaining dependencies and proposed dispositions. Do not treat drafting completeness or this policy closure as final milestone acceptance.
