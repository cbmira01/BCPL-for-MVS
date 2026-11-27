# DR.5 — Core Runtime authority transfer and DEBUGINT verification authorization

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Documentation Refactoring  
**March:** DR.5 — Validation and Reconciliation  
**Date:** 27 November 2026 EST  
**Reviewed proposal revision:** `0fde1b7c8c7ab1e2d1f6a07e77869030f6c06a24`  
**Disposition:** OWNER APPROVED — C effective in the GitHub main commit introducing this record; D authorized, target acceptance pending.

Owner direction: “Proceed C and D.”

C: The [reviewed proposal](dr5-core-runtime-authority-transfer-proposal.md) maps remaining supported public native Core Runtime clauses of [runtime v1](../../architecture/runtime-contract-v1.md) and [D7 v2](../../archive/core-runtime/m2-1-runtime-contract-v2.md) to chapters 2–3 and relevant scope and limitations in chapters 1 and 9 of the [runtime/library reference](../../../docs/product/Reference-for-the-Cambridge-Runtime-and-Libraries.md). Those chapters are now normative at the specified current development scope. Preserve historical candidate contracts, completion-code oracles, original stack and private allocator designs, source and acceptance records. Explicitly exclude detailed DEBUGINT behavior, private assembler interfaces, coroutine and MR10 contracts, and unimplemented historical facilities. Previously transferred BCPLIO, BLIB and System Extensions contracts and independent registry/configuration authority remain intact.

D: Authorize a focused native BCPL probe of the source-confirmed DEBUGINT negative-operand loss, followed by minimal operand preservation in BCPLMAIN and private IFOX/IEWL/GO verification before any installed-object replacement. Require the installed corrected object to pass the same independent exact oracle. Preserve baseline failure evidence; stop on unexpected outcomes. Do not broaden provisional G!150 semantics, assign a numbered regression, modify existing oracles, or resolve the historical FORMTREE conflict implicitly.

No fresh MVS execution, object replacement, code or oracle change in this acceptance commit. DR.5 remains IN PROGRESS. No new release or march closure.
