# DR.1 — Reference manuals as normative authorities

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Documentation Refactoring  
**March:** DR.1 — Architecture and Outlines (IN PROGRESS)  
**Date:** 25 November 2026 EST  
**Status:** Owner-approved authority direction; individual authority transfers not yet performed.

## Decision

The owner agreed that the new reference manuals should be authoritative as to behavior and contracts. This follows the assistant's proposal that reference manuals eventually become normative authorities for public interfaces and behavior, with existing contracts retained as historical engineering records after explicit reconciliation and validation.

The objective is that a programmer can consult a single current reference for the supported contract rather than reconstruct it from scattered engineering records. This supersedes the earlier proposed long-term arrangement in which manuals would merely summarize contracts residing elsewhere.

## Proposed application of the decision

- Reference for the BCPL Language: implemented language syntax and semantics, with compiler-specific differences and qualifications.
- Reference for BCPL Compilers: supported compiler interfaces, options, input/output and constraints.
- Reference for the Cambridge Runtime and Libraries: supported runtime and library behavior, including relevant ABI contracts and compiler-specific boundaries.
- Reference for System Extensions: public extension interfaces and common calling, selection, registration and lifecycle contracts.
- Reference for Project Tools: supported tool interfaces and operational contracts, subject to the same reconciliation discipline.

These scopes follow the [revised catalog](dr1-manual-catalog-owner-decisions-20261125.md). The detailed boundary between reference chapters and independently authoritative registries/configuration remains to be reviewed.

## Transfer safeguards

The agreed principle is not an immediate supersession of any existing contract. The following implementation safeguards are proposed:

1. Identify each old contract, exact scope, owner decisions, source/header bindings, acceptance evidence and outstanding qualifications.
2. Map each normative provision to the relevant reference section. Reconcile conflicting or candidate-scoped statements against current code, actual compiler/MVS results and accepted scope. Do not silently broaden or change behavior.
3. Review the resulting complete contract and verification limits before explicit approval of its transfer. Until then, the original authority remains operative.
4. Record the effective replacement reference and revision, preserve the original contract and its acceptance history, and provide stable navigation. Preserve old paths where required; do not modify historical records merely to advertise supersession.
5. Maintain the current reference alongside corresponding source and test changes. Treat a discrepancy as an issue to investigate, not automatic authorization to change either specification or code.

The Global Number Registry retains its allocation authority; machine-readable manifests, release registry, dataset configuration, test oracles and frozen release-specific documentation retain their respective authority. Reference manuals express the applicable facts without creating independent competing allocations or release identities. Actual BCPL, MVS, IFOX, IEWL and JES evidence establishes observed behavior; owner acceptance establishes its accepted scope. Historical records continue to substantiate decisions and provenance.

No authority transfer, manual creation, relocation, deletion, code change, MVS operation or release activity is performed by this decision. DR.0's dependency qualification remains in effect. DR.1 remains open pending detailed outlines, physical organization, navigation, transfer arrangements and formal owner acceptance.
