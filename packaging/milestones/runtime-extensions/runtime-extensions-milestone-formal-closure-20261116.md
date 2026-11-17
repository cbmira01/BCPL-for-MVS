# Milestone Runtime Extensions - formal expanded-milestone closure

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Runtime Extensions - Optional Modules and Global Registration  
**Owner disposition:** **CLOSED (qualified)**  
**Decision date:** 16 November 2026  
**Git authority:** `cbmira01/BCPL-for-MVS`, `main`  
**Prior verified HEAD at decision:** `3da9255cd00dd80605bc50239804354041c786d0`  
**Scope:** Formal closure of the expanded milestone, not a new march, new MVS run, production-object promotion or extension-package release.

## Formal owner decision

On 16 November 2026 the owner explicitly directed: "Close out runtime extensions and record the decision and whatever findings remain." All approved marches **R.0 - Evidence and contract**, **R.1 - Generic registration foundation**, **R.2 - Selective interoperability**, **R.3 - Packaging and acceptance**, **R.4 - IEWL-Driven Extension Selection**, and **R.5 - Optional Extension Packaging and Regression** had already been individually owner-accepted as **CLOSED**.

The expanded **Milestone Runtime Extensions - Optional Modules and Global Registration** is now **CLOSED (qualified)**. The qualification preserves actual acceptance scope and evidence limitations, rather than treating future ideas or historically incomplete checks as newly passed. No approved R march remains open, **no R.6 exists**, and none is created here. The earlier R.3-era milestone closure remains the valid disposition of the original R.0-R.3 scope; this record closes the subsequently expanded R.0-R.5 milestone.

## Accepted implementation and evidence

| March | Accepted result | Governing record |
| --- | --- | --- |
| R.0 - Evidence and contract | Owner-approved A-H BCEX/BCRG v1 ABI, bounded descriptor and registry formats, effective global ownership, finalization and shared QUERY conventions | [R.0 ABI decisions](runtime-extensions-r0-owner-abi-decisions.md) |
| R.1 - Generic registration foundation | Transactional registration, pre-START validation, ownership collision checks, reverse finalizers; 24 integrated MVS jobs PASS, native 00-145 panel 145 PASS / 1 expected SKIP | [R.1 closure](runtime-extensions-r1-closure-20261022.md) |
| R.2 - Selective interoperability | 0/A/B/A+B linked package selection and native dispatch, negative/dependency tests; JOBs 3091/3092 PASS | [R.2 closure](runtime-extensions-r2-closure-20261022.md) |
| R.3 - Packaging and acceptance | Source-distributed developer templates and temporary link acceptance; JOBs 3101-3103 PASS, without permanent object promotion at that march | [R.3 closure](runtime-extensions-r3-closure-20261022.md) |
| R.4 - IEWL-Driven Extension Selection | IEWL-only arbitrary unknown-package discovery not demonstrated; accepted known-package IFOX macro/PUNCH design. JOB 3720 profiles PASS; after recorded JOB 3721 S0C1 entry-selection failure, corrected JOB 3722 PASS | [R.4 closure](runtime-extensions-r4-closure-20261024.md) |
| R.5 - Optional Extension Packaging and Regression | Installed `BCPLDEMO`, `BCXSEL`/`BCXREQ` selection and MVS source/installed-mode verification; installation JOB 5108 and 00-158 production regression 158 PASS / 1 expected SKIP (083) | [R.5 closure](runtime-extensions-r5-closure-20261024.md) |

The accepted implementation retains the **BCEX/BCRG version-1 ABI** and the `BCPLREG` per-application registry, verified global ownership checks in `BCPLMAIN`/`BCPLRGS`, and known-package `BCXCAT` selection producing both `INCLUDE` cards and registration data. `BCPLDEMO` at **G!203 / DEMOSVC** remains an installed, supported reference **System Extension**, not a mandatory Core Runtime component. The Core Runtime and historical Base Library (`BLIB`) remain distinct from optional packages.

Subsequent installed **BCPLTIME** at **G!201 / TIMESVC** and its independent/mixed-package native acceptance are governed by [T.0/T.1](../bcpltime/milestone-date-and-time-services.md); **BCPLQSAM** at **G!200 / QSAMSVC** is governed by the separately [closed QSAM milestone](../qsam/qsam-q5-closure-20261101.md). Their separate acceptance does not create a new R march.

## Accepted limitations and retained findings

1. **Known-package selection, not arbitrary discovery.** The accepted IFOX `BCXSEL`/`BCXREQ` plus `BCXCAT` catalog scheme selects explicitly named known packages. IEWL `INCLUDE` alone was not shown to enumerate unknown BCEX descriptors. There is no runtime dynamic loader, automatic arbitrary-package discovery, or automatic transitive dependency *selection*. The registrar still validates the declared dependencies before `START`.
2. **Public QUERY is a contract with bounded evidence.** The shared opcode-0 side-effect-free size/capability inquiry and numerical caller-owned vector interface are accepted; separate two-dispatcher tests and package-specific tests exist. This closure does **not** assert exhaustive version/capability interoperability for all future packages or arbitrary third-party implementations.
3. **G!150 remains a separate ownership conflict.** The bootstrap `BCPLMAIN` `DEBUGINT` assignment collides with historical full Cambridge Compiler `FORMTREE:150`. No resolution or global reallocation is approved here; defer reconciliation to work that actually needs that compiler/runtime combination. Consult the [Global Number Registry](../../architecture/global-number-registry.md).
4. **Historical G!299 fixtures cannot be co-linked with the production coroutine ABI.** Earlier isolated R.0/R.2 test use is not a production allocation. **G!299** is now permanently assigned to native `CHANGECO`; maintain global collision checks. This is a compatibility warning, not an open R march.
5. **Independent User/Site Library catalogs and dependency expansion are future design choices.** They are not unfinished R.4 or R.5 obligations, and would need separate scope, review and tests. Existing BCEX/BCRG v1 remains authoritative unless explicitly superseded.
6. **Evidence qualifications remain.** R.5's original clean-room campaign crossed two documented Git states; it was not a single-revision end-to-end run. Automated IEWL MAP/XREF checks passed, but raw per-case reports were not all independently audited. Physical failed-install rollback was not tested; controlled reconstruction was the accepted recovery policy. These were disclosed and accepted in [R.5 closure](runtime-extensions-r5-closure-20261024.md). Earlier R.4 failed JOB 3721 remains recorded alongside its corrected passing JOB 3722; this closure does not erase failures.
7. **No further object installation is authorized by this record.** Git source is the implementation authority; IFOX, IEWL and MVS/JES are the target execution authority. Any future permanent `BOOT_OBJ`, `BOOT_DEVOBJ` or `EXT_OBJ` change requires its own explicit authorization and verification.

**Separate low-priority proposal:** `BCPLDEC` / Decimal Arithmetic is **proposed but not started**, and the owner placed it on indefinite deep background on 16 November 2026. It is not an unfinished Runtime Extensions march. The existing G!202 reservation is not silently released; D.0-D.4 remain merely proposed unless separately reactivated.

## Consequence for the project runway

Remove **Milestone Runtime Extensions** from active development tracking. Preserve the accepted BCEX/BCRG v1 ABI, known-package macros, module documentation and regression cases as maintained project infrastructure. Potential general library catalogs, G!150 reconciliation, richer package metadata or broader QUERY interoperability are separate, optional future work and do not condition milestone closure.

**Verification classification:** This is an owner-directed **documentation-only disposition** grounded in earlier committed owner acceptance and MVS evidence records. No new assembler, compiler, JCL, JES, MVS execution, regression run, installed-object promotion or media operation was performed to support this closure.
