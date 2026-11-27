# DR.5 — BCPL compiler authority transfer acceptance

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Documentation Refactoring  
**March:** DR.5 — Validation and Reconciliation  
**Date:** 27 November 2026 EST  
**Reviewed proposal revision:** `d05dd2d43c4272fac1cfb406b707fc9819b051be`  
**Disposition:** OWNER APPROVED — effective in the GitHub main commit introducing this record.

Owner direction: “compiler authority transfer approved, proceed to the *Reference for Project Tools*.”

The [reviewed proposal](dr5-compiler-authority-transfer-proposal.md) maps the existing option/parameter notes, compiler sources and accepted evidence to chapters 1–7 of the [Reference for BCPL Compilers](../../../docs/product/Reference-for-BCPL-Compilers.md). Those chapters are now normative for the qualified supported compiler interfaces and behavior. The [explanation](../../../docs/product/Explanation-of-BCPL-Compilers.md) remains explanatory. Preserve original MR10 and Cambridge option notes, historical sources, negative observations and original acceptance evidence. Current /N/ transport, checked-only supported scope, compiler-only combined-mode evidence, host compatibility shims and output gates remain distinct; no direct binary deck, native-running compiler, universal switch or diagnostic guarantee. Exact source comparisons 21/22/15 do not imply installed binary equivalence.

Tool operational contracts, configuration, release/manifest/registry, runtime and independent test oracles retain their authorities. No new MVS execution, executable change, source deletion, release or march closure. DEBUGINT and consolidated operational gates remain open. Proceed to Project Tools reconciliation.
