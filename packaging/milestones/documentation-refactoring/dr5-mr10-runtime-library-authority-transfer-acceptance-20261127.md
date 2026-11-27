# DR.5 — Remaining MR10 runtime and library authority transfer acceptance

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Documentation Refactoring  
**March:** DR.5 — Validation and Reconciliation  
**Date:** 27 November 2026 EST  
**Reviewed proposal revision:** `d274b19a75407f715606879167d267091420341e`  
**Disposition:** OWNER APPROVED — effective in the GitHub main commit introducing this record.

Owner direction: “Remaining MR10 approved, proceed to BCPL langauge reference”.

The [reviewed proposal](dr5-mr10-runtime-library-authority-transfer-proposal.md) maps ICINT19/ICLIB, historical BLIBI, reconstructed MR10 library sources and accepted panel evidence to chapter 7 and applicable scope and verification provisions of the [Reference for the Cambridge Runtime and Libraries](../../../docs/product/Reference-for-the-Cambridge-Runtime-and-Libraries.md). These provisions are now normative within their supported interpreted domain. Preserve the [MR10 GLOBALS map](../../../mr10-kit-compiler/library/GLOBALS.md), [Global Number Registry](../../architecture/global-number-registry.md), source declarations, test manifests/oracles, frozen RC4 documentation, original contracts, and distinct compiler/tool authority.

The transferred clauses distinguish logical byte packing, interpreter capacity and CODE, source-derived ICLIB services and character-stream obligations, the historical 11-procedure BLIBI subset, arena allocation, and reconstructed library calls. Source-observed limitations are not exhaustive target verification. Dynamic PUTREC's empty-record suppression is explicit; the approved stream boundary does not imply blanket blank-record preservation, recovery, pointer safety or arbitrary DDNAME validation. Previously approved native and coroutine contracts remain intact.

38 selected source/fixture blobs match the earlier accepted 212-pass campaign checkpoint, not installed binary identity. No new MVS job, software change, numbered test or release change. D (DEBUGINT) remains pending. Proceed to language reference reconciliation; DR.5 remains IN PROGRESS.
