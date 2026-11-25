# DR.2 — Formal qualified closure and DR.3 transition

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Documentation Refactoring  
**Date:** 25 November 2026 EST  
**Owner disposition:** DR.2 CLOSED (qualified); DR.3 IN PROGRESS  
**Acceptance review baseline:** ee820740d5e928d490fc1a7e4e0a890eded487f3  
**DR.2 starting revision:** 28e1831b63886c9cff1110b10bf37ed7e236b660

Owner direction: "Correct the two defects, commit the acceptance record, close DR2, theen give me a handoff prompt for DR3." The two review findings are corrected in the same commit as this record. The owner authorizes formal closure of the product drafting march and requests the DR.3 handoff; no broader software, destructive, release or target-system operation is authorized.

## Acceptance review and corrections

All thirteen approved product manuals are substantive working drafts in [docs/product](../../../docs/product/), indexed in the [documentation catalog and subject index](../../../docs/README.md). Review against the [approved outlines](dr1-manual-outlines-and-migration-20261125.md) established all 107 chapters, official names, Diátaxis organization and cross-manual navigation. The review found nine fenced code/diagram lines containing literal backslash-n sequences across three manuals and an invalid runtime-sized local VEC recommendation in the System Extensions how-to.

- Repaired nine affected lines (23 literal backslash-n sequences) in Tutorial on BCPL Programming, Explanation of BCPL Compilers and Reference for BCPL Compilers. Actual newlines restore the intended source/JCL/diagram layout.
- Corrected How to Use System Extensions, chapter 5: constant local VEC 255 covers the current 1024-byte ceiling; actual capacity is checked against successful INFO. For dynamic allocation use checked GETVEC with the calculated upper bound and FREEVEC after use. Chapter 2 now also distinguishes constant VEC and runtime-sized GETVEC. Historical [Cambridge TRN](../../../richards-bcpltape/bcplib/bcpl/trn) and current [bootstrap TRN input](../../../bootstrap-toolchain/bootstrap-cambridge/source/trn) both use EVALCONST in TRANSDYNDEFS for S.VECDEF. The [existing case 171](../../../tests/system-extensions/bcplqsam/171-qsam-v-read/source.bcpl) uses a constant VEC 259 and checks guard bytes. The new buffer recommendation is source-derived, not a newly executed example.

| Gate | Disposition |
| --- | --- |
| Product catalog and approved chapters | PASS: 13/13; 107/107 |
| Title, chapter order and navigation | PASS |
| Repository-relative links in product manuals | PASS: 329; no broken paths |
| Fenced code blocks | PASS: 49; balanced; no remaining literal backslash-n formatting defect |
| Nomenclature and release/development distinctions | PASS for draft scope |
| Existing authority and evidence preservation | PASS |
| Complete normative and target verification | Deferred to DR.5, not claimed PASS |

Before these corrections, comparison with the DR.2 starting revision found thirteen new manuals, five new ledgers, one existing index modified, and no deletions or changes to pre-existing software, JCL, contracts, manifests or release artifacts. This closure changes only the four affected new manuals and milestone documentation/index. No new MVS jobs, independent raw private receipt inspection, release asset rehash or normative transfer. New/adapted snippets remain unverified on target.

## Retained migration and reconciliation obligations

- [Language ledger](dr2-language-manual-migration-20261125.md): complete grammar and dialect, evaluation and edge-case semantics.
- [Compiler ledger](dr2-compiler-manual-migration-20261125.md): nondefault options, GET and parameter behavior; checked/counting emission is not native execution.
- [Runtime and library ledger](dr2-runtime-library-manual-migration-20261125.md): exact exports/signatures, ABI and exceptional behavior, dated stack-overflow contracts and global conflicts.
- [Extension ledger](dr2-extension-manual-migration-20261125.md): complete provision mappings, Q.5 installed selection qualification, genuine exceptional CLOSE and rollback precedence, header transport.
- [Operational ledger](dr2-operational-manual-migration-20261125.md): adapted JCL execution, site/HLQ and independent IPL limitations, source-observed compile-mvs preview output deletion (no software fix).

These are explicit DR.5 obligations. Existing contracts remain operative until individual reconciled transfers receive owner approval, per [reference authority decision](dr1-reference-authority-owner-decision-20261125.md). Registry, manifest, config, oracle, legal and frozen release authorities remain independent. RC4 is MR10 functional; native payload is inventory/installation accepted only, CAMBCOMP and native-running compiler absent. DR.0 dependency audit remains qualified. Do not retire or relocate existing authoritative documents without coverage/dependency review and approval.

## DR.3 — Project Documentation

Proceed to the five approved project/background manuals in docs/project, following the [approved outlines](dr1-manual-outlines-and-migration-20261125.md):

| Manual | Chapters |
| --- | ---: |
| How to Reconstruct BCPL from Source | 8 |
| How to Develop and Test BCPL for MVS | 8 |
| Reference for Project Tools | 9 |
| How to Create a Release Candidate | 8 |
| Explanation of the MVS Programming Environment | 12 |

Read current source, executable tool contracts, config, accepted build/test/release evidence and existing procedures before drafting. Prioritize actual BCPL/JCL/assembler/MVS verification and distinguish source-derived from target-tested behavior. Preserve manual and unattended reconstruction, approval and destructive-scope safeguards, device and no-retry gates, test modes and oracles. Preserve existing canonical release how-to path until dependency review; do not create competing authoritative versions. The current release driver is offline-tested, not live-qualified by the prior BC0005 exercise.

Maintain an economical migration ledger, link only substantive existing manuals, avoid redundant recipes and preserve original paths. No automatic reference authority transfer, software changes, relocation, deletion, MVS operations, release production or publication. Major decisions and commits require owner authorization. DR.4–DR.6 remain NOT STARTED. Formal DR.3 closure requires owner approval.
