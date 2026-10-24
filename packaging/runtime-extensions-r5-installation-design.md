# R.5 — Optional-extension PDS installation and reconstruction

**Project:** BCPL for MVS 3.8 Reconstruction
**Milestone:** Runtime Extensions
**March:** R.5 — Optional Extension Packaging and Regression (**IN PROGRESS**)
**Design:** Owner approved 23 October 2026
**Execution authority:** No permanent MVS PDS creation, population, replacement, or installation authorized by the design approval.
**Official source:** GitHub main; package binaries on MVS are disposable, rebuildable products.

## Allocation design

The manifest is config/dspal.yaml. The resolved MVS names use the current HERC02 HLQ.

| Alias | Resolved dataset | Attributes | Initial members |
|---|---|---|---|
| EXT_OBJ | HERC02.BCPL.EXT.OBJ | PDS FB80/800; 15+5 tracks, 10 directory blocks; object, populate false | None automatically; install BCPLDEMO after authorized IFOX build |
| EXT_MAC | HERC02.BCPL.EXT.MAC | PDS FB80/800; 10+5 tracks, 5 directory blocks; text-populated | BCXPRE, BCXCAT, BCXPOST |
| EXT_ASM | HERC02.BCPL.EXT.ASM | PDS FB80/800; 10+5 tracks, 5 directory blocks; text-populated | BCPLDEMO |
| EXT_SOURCE | HERC02.BCPL.EXT.SOURCE | PDS FB80/800; 10+5 tracks, 5 directory blocks; text-populated | DEMOHDR |

Text population does not authorize running dspal against permanent MVS datasets.
EXT_OBJ must be assembled on MVS from Git-backed EXT_ASM(BCPLDEMO), never
copied from prebuilt Git binary records. BCPLDEMO has one FB80 relocatable
object containing DMODESC and DMODISP, with exported DMOBEG, DMOEND, and
DMODISP. Its public dispatcher is DEMOSVC at G!203. BCEX/BCRG v1 is unchanged.

## Native build and installation (separate authorization required)

1. Record the Git revision. After explicit authorization create the four
   manifest-managed PDSes and populate their Git-backed text members.
   Verify member names, 80-column cards and EBCDIC conversion.
2. Verify that `BOOT_JCL(R5DINST)` was populated from
   `bootstrap-toolchain/jcl/r5dinst.jcl`. After separate installation
   authorization, run `tools/datasets/dspal submit BOOT_JCL R5DINST`.
   `dspal submit` generates the authenticated JOB card from the local
   configuration and submits the resident body through JES INTRDR.
   Never commit authenticated JOB credentials.
3. ASMDEMO runs IFOX on EXT_ASM(BCPLDEMO), writes its binary object
   through SYSGO to a temporary FB80 sequential dataset, and must return 0000.
4. PUTDEMO (IEBGENER) installs the temporary binary records without text
   conversion into EXT_OBJ(BCPLDEMO) using DISP=OLD. It is the only persistent
   write step in the supplied job. A PDS member update is not atomic.
5. READBACK copies the installed binary member to a temporary dataset.
   VERIFY compares the assembled records and read-back records with
   IEBCOMPR. Require successful real MVS return codes and matching bytes.
6. Independently link and run an application in read-only installed mode.
   Confirm IEWL MAP/XREF, relocated BCEX/BCRG v1 descriptors, G!203
   registration, and absence of BCPLDEMO when unselected.

Failed installation recovery means reconstructing optional-extension
datasets from a known GitHub revision: recreate as needed, repopulate
text sources, reassemble, reinstall, compare, link, and retest.
There is no backup PDS or member-level rollback requirement.
Never destroy unrelated BOOT_OBJ, BOOT_DEVOBJ, CAMB_* or site datasets.

## Installed IFOX and IEWL convention

Use the R.4 IFOX source-concatenation model, with MVS PDS sources
replacing embedded macro definitions:

    //SYSIN    DD  DSN=HERC02.BCPL.EXT.MAC(BCXPRE),DISP=SHR
    //         DD  DSN=HERC02.BCPL.EXT.MAC(BCXCAT),DISP=SHR
    //         DD  *
             BCXREQ BCPLDEMO
    /*
    //         DD  DSN=HERC02.BCPL.EXT.MAC(BCXPOST),DISP=SHR

The catalog emits the IEWL statement INCLUDE EXTLIB(BCPLDEMO).
The EXTLIB DD names the complete read-only object library:
HERC02.BCPL.EXT.OBJ. Core Runtime/Base Library use the ordinary OBJ DD.
The SYSLIN stream contains application/runtime/registry object input,
the punched INCLUDE, and explicit ENTRY/NAME controls.
A package is selected at link-edit, not at runtime. No transitive
dependency discovery is claimed.

## Regression requirements and acceptance

Source mode is unchanged: BCPL_R5_EXTENSION_MODE=source continues to
assemble BCPLDEMO and embed the tested R.4 macro fixture definitions
into temporary objects.

Installed mode requires all three settings:

    BCPL_R5_EXTENSION_MODE=installed
    BCPL_R5_EXTENSION_DSN=HERC02.BCPL.EXT.OBJ
    BCPL_R5_MACRO_DSN=HERC02.BCPL.EXT.MAC

The generator validates manifest identity and builds IFOX SYSIN from
resident BCXPRE, BCXCAT and BCXPOST members, without embedding their
host source. Installed-mode object PDS input uses DISP=SHR. Numbered
single-case and contiguous-range invocation remain supported.

Test 146 and 158 must exclude the extension object; 147–157 must
demonstrate inclusion and behavior. Verify real IEWL MAP/XREF shows
DMODESC, DMODISP, DMOBEG, DMOEND, RGINIT and BCPLREG as applicable,
correct entry address, and the expected native BCPL output. Once
installed 146–158 pass, run the full 00–158 panel (expected 158 PASS,
0 FAIL, one expected SKIP 083, contingent upon MVS evidence).
Then rebuild from fresh Git and document the real JES/IFOX/IEWL/GO
evidence and recovery procedure.

**Owner-reported source-mode result, 23 October 2026:** 146–158
returned 13 PASS, 0 FAIL, 0 SKIP. Preserve the earlier verifier
false negatives for JOBs 3724/3726 and the correction/revalidation.
The operator subsequently reported a successful full clean-room
00–158 panel on 23 October 2026: **158 PASS, 0 FAIL, 1 expected SKIP
083**. This is documented in the
[R.5 evidence receipt](runtime-extensions-r5-clean-room-acceptance-evidence-20261023.md).
Individual `R5DINST` job steps, PDS inventories and actual MAP/XREF/GO
reports have not yet been provided for independent review.
R.4 formal closure is pending; R.5 remains **IN PROGRESS**.

## Installation and owner acceptance — 24 October 2026

The *design-only/no-installation-authority* status above describes the
23 October proposal, not the subsequent MVS reconstruction. The
owner's original full clean-room transcript establishes installed
`EXT_OBJ(BCPLDEMO)`, submitted via `BOOT_JCL(R5DINST)`:

- Payload JOB 5108: ASMDEMO, PUTDEMO, READBACK and VERIFY each
  RC=0000; ten object records independently compared by IEBCOMPR.
- The installed-mode 00–158 native panel: 158 PASS, 0 FAIL,
  one expected SKIP 083, including automated IEWL MAP checks.
- The final extension PDS membership matched the manifest.
- The revision transition 7fff89f -> 00379e0 was documented.

R.5 was **CLOSED by explicit owner approval**. See the
[formal closure record](runtime-extensions-r5-closure-20261024.md).
This does not imply permission for further permanent writes.
R.4 formal closure remains pending.
