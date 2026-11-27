# DR.5 — BCX selection-macro authority transfer proposal

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Documentation Refactoring  
**March:** DR.5 — Validation and Reconciliation  
**Date:** 27 November 2026 EST  
**Reviewed source:** `c2ba705ca7e6bac62484f7ea3483a8b73f7883dd`  
**Disposition:** PROPOSED — explicit owner approval required.

Under [DR.1 safeguards](dr1-reference-authority-owner-decision-20261125.md), transfer the remaining supported public BCX selection interface in chapter 2.3 of the [Reference for System Extensions](../../../docs/product/Reference-for-System-Extensions.md), plus applicable scope/evidence in chapters 6–7. Preserve existing approved registration/finalization, QUERY and package APIs; source, build, registry, allocation, and independent test oracles retain their authority.

## Contract reconciliation

[BCXPRE](../../../system-extensions/bcx/BCXPRE.asm), [BCXCAT](../../../system-extensions/bcx/BCXCAT.asm), [BCXPOST](../../../system-extensions/bcx/BCXPOST.asm) are MVS-native IFOX source members concatenated PRE, CAT, application selection cards, POST. Use uppercase exact known package spelling. The maintained catalog maps BCPLDEMO to EXTLIB(BCPLDEMO) and DMOBEG/DMOEND, BCPLTIME to EXTLIB(BCPLTIME) and TIMBEG/TIMEND, BCPLQSAM to EXTLIB(BCPLQSAM) and QSMBEG/QSMEND. Unknown names cause MNOTE 8 and no selection; the internal array limit is 32 distinct selected packages, MNOTE 8 on excess; current installed catalog can select only three, so limit exhaustion is source-observed, not verified with 33 actual packages. BCXSEL selects; BCXREQ also marks required. Duplicate selection is idempotent; a later requirement upgrades without a new INCLUDE or extent. A later BCXSEL does not downgrade. First selection fixes descriptor order; required IDs are emitted in selected order, not upgrade-call order. No runtime loading or auto dependency expansion.

BCXADD punches one INCLUDE per new known selected package before first CSECT. BCXPOST expands BCXEND and END BCPLREG. BCXEND emits one BCPLREG CSECT with BCRGBEG/BCRGEND and BCRG v1 (28+8*N+8*M bytes, including empty 28 bytes); selected pairs are relocated EXTRN symbols, required IDs CL8, no extra package-specific startup. Use one registry; explicitly select the application ENTRY, link actual application, Core Runtime, BLIB, BCPLRGS and selected packages; do not accidentally enter a registry/descriptor or include the default empty registry in addition. EXTLIB is approved read-only FB80 relocatable object PDS, not text source; source-mode fixture catalogs refer to temporary objects. Application selection is independent of declarations and installation. The actual registrar validates dependency order, versions, extent and ownership; macro selection does not prove those checks passed. No general independent User/Site catalogs or unlisted-package discovery; R2TESTB is test-only, never an installed package or allocation. No transfer of internal BCXADD/BCXCAT macro programming API beyond this supported selection workflow.

## Evidence and qualification

[R.4 closure](../runtime-extensions/runtime-extensions-r4-closure-20261024.md): JOB 3720, 21 EXEC steps, five temporary known-package profiles; observed BCRG byte lengths 28,44,44,52,60 (standalone GO RC measures extent). JOB 3721 initial integrated GO S0C1 (wrong entry) remains FAIL; JOB 3722 explicit ENTRY R4APP at zero, 11 zero steps and actual compiled BCPL START dispatch PASS. No general linker discovery established. [R.5 closure](../runtime-extensions/runtime-extensions-r5-closure-20261024.md) accepts original resident DEMO macros and binary comparison JOB 5108, 158 PASS and one expected SKIP 083, with automated IEWL MAP rather than manual audit of all raw reports; the original two-revision chronology and lack of tested physical rollback remain.

The [current report verifier](../../../tools/checks/check-r5-extension-report.py) requires one XREF table, R0APP/BCPLMAIN/RGINIT, expected BCPLREG lengths 28 (146/158),36 (156),44 (other selected cases), correct DEMO inclusion, TIME/QSAM exclusion and one zero entry. Existing 157 tests selection upgrade; 160–162 include two-package order and upgrade. Current QSAM installed selected/unselected JOBs 1261/1263 and all ordinary 163–176 installed cases are accepted, separate from private source diagnostics 198–200. See [DR.5 ledger](dr2-extension-manual-migration-20261125.md) and [expanded milestone closure](../runtime-extensions/runtime-extensions-milestone-formal-closure-20261116.md).

30/30 selected blobs (three macros and 27 source/oracle/selection files for 146,156–158,160–162,172–174) match both CO.6 tested revision `216b6707c404a91c796ed8f1419a99ef172b184a` and RC4 frozen program-source revision `e910de51c19c09698be139e33084a90401511cc9`. This is source identity, not binary identity or native RC4 functional acceptance. No fresh MVS execution, exhaustive macro failure/limit testing or independently reopened private receipts. No additional focused target tests recommended for the bounded contract.

## Requested decision

Approve chapter 2.3's remaining supported selection-macro authority and corresponding chapters 6–7 evidence scope. Preserve the existing BCX source-local history, R.4/R.5 closure and source-mode fixtures. Do not change macros, registry, JCL, suites or installed members. Correct catalog navigation and current-facing descriptions without retiring historical paths. DR.5 operational verification remains pending.
