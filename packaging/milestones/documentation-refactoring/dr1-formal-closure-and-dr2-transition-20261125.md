# DR.1 — Formal closure and DR.2 transition

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Documentation Refactoring  
**Date:** 25 November 2026 EST  
**Owner disposition:** DR.1 CLOSED; DR.2 IN PROGRESS  
**Accepted design revision:** b4f977163bcb28d8854b1a878fa8092d02be2e9c

The owner explicitly directed: "Chapter outlines approved; proceed." This completes the DR.1 design gate and authorizes commencement of DR.2 — Product Documentation. Earlier owner-approved decisions remain effective.

## Accepted design

- [Manual catalog](dr1-manual-catalog-owner-decisions-20261125.md): eighteen manuals, thirteen product and five project/background.
- [Reference authority](dr1-reference-authority-owner-decision-20261125.md): reference manuals become normative after validated individual transfers.
- [Directory organization](dr1-directory-organization-owner-decision-20261125.md): docs/product and docs/project.
- [Canonical format](dr1-canonical-markdown-owner-decision-20261125.md): repository Markdown, GitHub presentation; derived representations in DR.4.
- [Navigation](dr1-navigation-owner-decision-20261125.md): Diataxis-first catalog plus subject index.
- [Detailed outlines and migration](dr1-manual-outlines-and-migration-20261125.md): 152 proposed chapters now owner-approved; incremental migration and reconciliation approach approved.

DR.1 design deliverables are accepted. DR.0's qualification remains: full repository dependency graph and per-file verification are incomplete. Individual contract transfers, target verification and implementation are subsequent work, not claims of DR.1 completion.

## DR.2 kickoff

Develop the thirteen approved product manuals in docs/product, beginning with the Tutorial on BCPL Programming and Reference for the BCPL Language. Use the approved outlines, historical MR10 and Cambridge sources, accepted demonstrations/regressions, and actual compiler/MVS behavior. Start with existing verified examples; distinguish observed evidence from inferred or untested semantics. Do not conflate MR10, interpreter-hosted demoted Cambridge Compiler and unfinished native-running Cambridge Compiler. RC4 supports MR10 compilation; native payload is work in progress and CAMBCOMP is not distributed in RC4.

Build an economical migration/contract ledger as drafting proceeds. Preserve existing authority until explicitly approved transfer; preserve records and dependency paths. Add only substantive manuals and link only existing documents. No removal, code change, release production or MVS state change is authorized by the design closure. Owner approval is required for individual authority transfers, destructive operations and march closure.

Preliminary read-only language investigation at the accepted revision examined MR10 suite instructions, language examples, arithmetic regression and expected output, MR10 global assignments, historical SYN lexer/parser leads and RC4 companion. No new manual or target execution was completed before the handoff. Begin drafting from these sources; verify exact release/source correspondence before attributing accepted results to changed examples.

DR.3–DR.6 remain NOT STARTED.
