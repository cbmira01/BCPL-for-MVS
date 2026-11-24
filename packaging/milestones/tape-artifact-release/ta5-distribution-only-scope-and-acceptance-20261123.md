# TA.5 — Owner-directed distribution-only scope and acceptance review

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**Date:** 23 November 2026 EST  
**Candidate:** `BCPL-0.1.0-rc4` / `BC0004` / `native_compiler: absent`  
**Disposition:** TA.5 technical distribution acceptance satisfied (qualified); formal closure subject to explicit owner disposition.

## Binding owner decision

Until a full native Cambridge Compiler is available, functional release testing is limited to the MR10 Kit Compiler. Include the native runtime, libraries, extensions, sources, headers, macros and associated build material on the tape as work in progress. Preserve existing RC4 objects as distribution artifacts; no new object build or object reproducibility test is required. Do not generate native test applications, use interpreter-hosted CAMBCOMP as a substitute for the full native compiler, or perform native assembly, linkage, execution, regression or extension-selection testing for release acceptance. Defer those gates until the full native compiler is available. Previously accepted development evidence remains historical evidence, not a new release test requirement.

This supersedes the native functional and rebuild requirements in the earlier TA.5 kickoff and entry audit, and the unconditional native functional test requirement in TA.7. TA.7 still requires clean-target installation verification of all three profiles and MR10 functional acceptance; native functional acceptance is conditional on the full native compiler being included. TA.6 remains N/A for RC4, not PASS.

## Existing distribution evidence

The frozen [RC4 manifest](../../distribution/manifest/releases/BCPL-0.1.0-rc4.yaml) includes these native-group libraries, all PO/FB/80/800:

| Tape sequence | Library | Members |
| --- | --- | ---: |
| 13 | BOOT_OBJ | 10 |
| 14 | BOOT_ASM | 9 |
| 15 | BOOT_SOURCE | 4 |
| 16 | BOOT_JCL | 6 |
| 17 | EXT_OBJ | 3 |
| 18 | EXT_ASM | 3 |
| 19 | EXT_SOURCE | 3 |
| 20 | EXT_MAC | 3 |
| | Total | 41 |

RC4 preserved the 19 unchanged RC3 payload PDSes; MVS JOBS 9393–9397 established RC4 production and structural acceptance. The [TA.3 accepted installation record](../../distribution/install-from-tape/ta3-rc4-all-profiles-accepted-20261123.md) reports exact manifest-selected directory/DCB verification of NATIVE (11 PDSes/71 members, HERC02.BCPL.R4NT) and COMBINED (20 PDSes/150 members, HERC02.BCPL.R4CB). Both include all eight native-group libraries. The owner-reported sealed continuation evidence is retained at `workarea/ta3-rc4-continuation/20261123T163929Z-37828`; private raw receipts were not directly inspected in this review. The unchanged AWS SHA-256 is `7cc5a1d61882bf88469fd9f9e38512f1976ef1a775e3095e12e3988600c57af1`.

These accepted predecessor results satisfy the revised TA.5 inventory and installation gate on a qualified basis. No new source-to-object equivalence, source rebuild, native execution, or independent raw record comparison is asserted. The generated COROUTIN build-receipt qualification and BLIB rebuild dependency remain documented; rights and provenance clearance remain TA.8. Do not change the frozen manifest or tape, rerun accepted MVS operations, or remove existing distributed objects merely because testing is deferred.

TA.4 remains formally closed with the accepted MR10 automated receipt; no repeat is required absent a changed payload or demonstrated defect. TA.5 is technically ready for formal qualified closure. TA.7 clean-target installation and MR10 functional verification remain separate; no new MVS state change or publication is authorized here.
