# TA.5 — Native Runtime, Libraries, and Extensions Distribution: entry audit

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.5 — Native Runtime, Libraries, and Extensions Distribution  
**Status:** READ-ONLY ENTRY AUDIT / DESIGN PREPARATION; not yet formally opened  
**Date:** 23 November 2026 EST  
**Candidate:** `BCPL-0.1.0-rc4` / `BC0004` (`native_compiler: absent`)

## Authoritative scope

The milestone requires executable, independently installed native
Core Runtime and historical Base Library `BLIB`, separate
`BCPLCO`/`COROUTIN` Coroutine Support, and the optional
System Extensions `BCPLDEMO`, `BCPLTIME`, `BCPLQSAM`.
Verify real MVS IFOX, IEWL, execution/semantic results,
source/binary lineage, and **BCEX/BCRG v1** optional
linkage and known-package registration behavior.
Do not confuse the interpreter-hosted Cambridge compiler
`CAMBCOMP` with a native compiler, and do not silently expand
TA.5 to TA.6 or the clean-target TA.7 acceptance.

Governing documents:
[release milestone](milestone-tape-artifact-release.md),
[canonical runtime/library nomenclature](../../architecture/runtime-and-library-nomenclature.md),
[accepted Runtime Extensions milestone](../runtime-extensions/milestone-runtime-extensions.md),
[TA.0 provenance/dependency audit](../../distribution/manifest/ta0-provenance-and-dependency-audit.md),
and [RC4 manifest](../../distribution/manifest/releases/BCPL-0.1.0-rc4.yaml).

## Already installed release inventory

TA.3 accepted actual MVS `BC0004` tape-resident NATIVE
(11 PDSes / 71 members) and COMBINED
(20 PDSes / 150 members) recipient profiles.
Existing recipient namespaces are `HERC02.BCPL.R4NT`
and `HERC02.BCPL.R4CB`. **Do not restore them again**.

The selected `native` group of RC4 manifest sequences
13–20 is eight separate PDSes:

| Sequence | Curated library | Required verification |
| --- | --- | --- |
| 13 | `BOOT_OBJ` | Core seven objects, `BLIB`, `BCPLCO`, `COROUTIN`; native linkage and provenance |
| 14 | `BOOT_ASM` | Nine assembler members, including generated `COROUTIN` |
| 15 | `BOOT_SOURCE` | `LIBHDR`, `BLIB`, `COROUTIN`, `COHDR` source lineage |
| 16 | `BOOT_JCL` | Curated MVS jobs `BLDBMAIN`, `BLDCORCO`, `BLDCORLB`, `BCPLDEMO`, `BCPLTIME`, `BCPLQSAM` |
| 17 | `EXT_OBJ` | Three accepted extension object members |
| 18 | `EXT_ASM` | Matching three assembler members |
| 19 | `EXT_SOURCE` | `DEMOHDR`, `TIMEHDR`, `QSAMHDR` |
| 20 | `EXT_MAC` | `BCXPRE`, `BCXCAT`, `BCXPOST` |

The complete NATIVE profile also includes COMMON and historical
Cambridge source distribution members. Those members do not
prove a runnable native Cambridge Compiler.

## Design choices requiring review before stateful execution

1. **Provenance first:** reconcile each preserved native object
   member with its selected source and already accepted MVS
   build/installation evidence. In particular, `BLIB`
   is BCPL-derived, `BOOT_ASM(COROUTIN)` is generated, and
   the release intentionally lacks the native-running compiler
   needed for independent BCPL-source rebuilding. Do not
   misclassify `BLIB` or `COROUTIN` as arbitrary assembler
   source or fabricate a new compiler gate.
2. **Actual native application execution:** build minimal
   release-namespace BCPL test objects from already accepted
   source/generator assets and link against **installed**
   `R4NT`/`R4CB` objects. Use fresh, isolated verification
   outputs and existing System/370 ABI rules. Reuse accepted
   native regression oracles, not invented functional expectations.
3. **Optional extension matrix:** demonstrate the known-package
   `BCEX/BCRG v1` selection behavior with `BCPLDEMO`,
   `BCPLTIME`, `BCPLQSAM` deliberately included/excluded.
   Do not require `BCPLDEC`; it is outside the RC4 manifest.
   Verify link maps, actual dispatch and negative conditions,
   and all supported selected packages' documented contracts.
4. **Consolidation and safety:** prefer a single consolidated
   source-controlled job campaign over repeated submissions
   when safe. Begin with Git/source and saved-evidence audit,
   then one read-only MVS catalog/member/DCB preflight.
   Only after major design approval, use new noncolliding
   DASD targets, a single explicit owner confirmation,
   complete JES/IFOX/IEWL/GO evidence and one-shot no-retry
   controls. Do not mutate installed libraries or accepted media.

## Entry boundary

This is **design preparation**, not TA.5 verification,
a fresh MVS preflight, a source/binary build receipt, or
authorization to submit JCL. TA.4's reported automatic PASS
does not pre-accept native link/execute behavior, clean-target
acceptance (TA.7), rights/provenance clearance (TA.8) or
release publication. The next action is design review and
read-only source/evidence planning, guided by the existing
MVS-native toolchain rather than host-only simulation.
