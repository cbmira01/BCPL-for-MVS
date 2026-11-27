# DR.5 — Common registration and finalizer authority transfer acceptance

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Documentation Refactoring  
**March:** DR.5 — Validation and Reconciliation  
**Date:** 27 November 2026 EST  
**Reviewed proposal revision:** `3f3d867fe99d1f152f9ebba8b680bfe4b32b3dce`  
**Disposition:** OWNER APPROVED — effective in the GitHub main commit introducing this record.

Owner direction: "Approved, continue".

The [reviewed proposal](dr5-registration-authority-transfer-proposal.md)
maps all eight R.0 decisions and Decision G to the
[Reference for System Extensions](../../../../docs/product/Reference-for-System-Extensions.md),
chapter 2 (and the common dispatcher convention in chapter 1). The
common registration and finalizer provisions of the
[R.0 A–H record](../runtime-extensions/runtime-extensions-r0-owner-abi-decisions.md)
and [Decision G](../../archive/runtime-extensions/runtime-extensions-r0-decision-g-contract-20261021.md)
are superseded as current normative authority by the reference, with
original records retained as historical evidence.

The owner approves the stated qualification: structural category precedence
is retained; later checks traverse linked records as described in the
reference, not a universal numerical diagnostic priority. Full multifault
precedence remains unverified. No registrar redesign authorized or needed
at the accepted scope.

Chapter 2 now states the exact bounds, source/link trust, lazy initialization,
transitive validation without automatic selection, eight-byte finalizer ABI,
and post-structural order. Existing acceptance evidence and qualifications
remain intact. Package-specific and macro/tool interfaces are not transferred.
Global Number Registry allocations, configurations, manifests, oracles and
frozen release documentation retain their respective authorities.

No source or object change, fresh MVS execution, release action, numbered
case or march closure. Other individual authority transfers remain pending.
