# DR.5 — BCPLIO and Base Library authority transfer acceptance

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Documentation Refactoring  
**March:** DR.5 — Validation and Reconciliation  
**Date:** 27 November 2026 EST  
**Reviewed proposal revision:** `8f4f922df30015ea9c8ac3c070dd8bb74fd4d655`  
**Disposition:** OWNER APPROVED — effective in the GitHub main commit introducing this record.

Owner direction: "Approved, proceed".

The [reviewed proposal](dr5-stream-and-base-library-authority-transfer-proposal.md) maps the provisions, source, acceptance evidence, and limitations to the [Reference for the Cambridge Runtime and Libraries](../../../docs/product/Reference-for-the-Cambridge-Runtime-and-Libraries.md).

- **A:** Chapter 4, with relevant public character-stream termination behavior in chapter 3.2, supersedes the current public behavioral provisions of the [M5.4 dynamic stream contract](../bcplio-dynamic-stream/BCPLIO-dynamic-runtime-contract.md) and [M4.2 JCL/QSAM responsibility contract](../bcplio-dynamic-stream/BCPLIO-JCL-QSAM-stream-contract.md). Retain fixed built-in versus non-recycled dynamic handles, returned-control failure scope, FB80/FB132 logical translation, and QSAM/JES2 responsibility boundaries. Case 193 and earlier native evidence remain scoped as recorded. No genuine unsuccessful SVC19 or raw spool-byte proof.
- **B:** Chapter 5 becomes the current supported native BLIB behavioral authority for the thirteen ordinary procedures and previously accepted bounded diagnostic behavior, consolidating the applicable public BLIB provisions of [runtime v1](../../architecture/runtime-contract-v1.md) and [D7 v2](../../archive/core-runtime/m2-1-runtime-contract-v2.md). Retain the 21-slot census, 12 READN/TERMINATOR assertions, and all accepted historical diagnostic limitations. Export membership is not general execution support; no pre-call TERMINATOR guarantee, arbitrary pointer safety or historical diagnostic reconstruction.

Both transfers apply to the corrected native development environment, not older RC4 objects or MR10. Original historical contracts, source, declarations, test oracles, and candidate-specific acceptance records remain intact. The Global Number Registry retains allocation authority; configuration, manifests, release-specific documentation and other normative contracts retain their respective authority.

Remaining Core Runtime public startup, native ABI, storage/byte, stack and non-stream termination provisions, private assembler interfaces, coroutine and MR10 contracts remain outside this transfer. No new MVS execution, code, object, test, release or march status change. DR.5 remains IN PROGRESS.
