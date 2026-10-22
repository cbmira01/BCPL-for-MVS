# Core Runtime canonical-source consolidation — 22 October 2026

**Scope:** Source-only consolidation following owner closure of
Milestone Runtime Extensions (R.0-R.3), based on Git `f2f5918`.
No new march is established and R.0-R.3 are not reopened.

- Canonical `BCPLMAIN` includes the previously tested R.1
  registration integration, effective-global owner ledger, startup
  validation and termination finalizers.
- The six shared Core Runtime assembler source modules and empty
  application `BCPLREG` selection-table template have consistent
  introductory banners. Other established assembler module
  executable cards are unchanged.
- `BOOT_ASM` now maps the registrar and empty table source members.
- `BOOT_JCL` now maps a non-installing assembly check `BLDRGCHK`.
- Canonical manifest checks and the historical R.1 source adapter
  recognize the integrated `BCPLMAIN` without double adaptation.
- `BLDBMAIN` remains an unchanged, **on-hold** five-module writer.
  No object library contents or deployment decision are changed.

**Validation status:** The source adaptation and fixed-card constraints
have been checked before the Git commit. Local full repository host
tests, MVS IFOX assembly, IEWL linkage, JES execution, and fresh
00-145 regression are **still required** before treating the new
canonical source set as independently release-verified.
The original R.3 acceptance used temporary objects and remains
the evidence for the accepted integration behavior.

**Deployment boundary:** Persistent writes to `BOOT_OBJ` or
`BOOT_DEVOBJ` remain deferred. Do not run `BLDBMAIN` until its
object membership, selection and recovery process are approved.
