# Runtime Extensions — R.4 — JOB 3720 IFOX macro/PUNCH/IEWL evidence

**Date:** 23 October 2026  
**MVS:** Hercules / MVS 3.8J TK5, IFOX00, IEWL  
**Tested Git revision:** `b2a1411bd05c4c60e96185f459bcc7ffbaabf8b3`  
**JES:** `R4BCXMAC`, **JOB 3720**  
**Disposition:** **PASS** for the *test-only MVS-native macro/PUNCH/IEWL mechanism*. **R.4 remains OPEN**; this is not BCPL startup registration acceptance.

## Operator report reviewed

The owner supplied the full `tools/mvs/dump-report-for-job 3720` output after pulling Git revision `b2a1411`. All 21 JCL EXEC steps ran. The 3 IEBGENER preparation steps, the 3 fixture/observer IFOX assemblies, the 5 registration IFOX assemblies, and all 5 IEWL steps returned **RC=0000**. The 5 GO steps returned exactly the intended BCRG byte lengths:

| Profile | Selection | IFOX | IEWL | GO expected | GO observed |
| --- | --- | --- | --- | ---: | ---: |
| 0 | none | 0000 | 0000 | 0028 | 0028 |
| A | `BCXREQ BCPLDEMO` | 0000 | 0000 | 0044 | 0044 |
| B | `BCXREQ R2TESTB` | 0000 | 0000 | 0044 | 0044 |
| S | `BCXSEL BCPLDEMO`, `BCXREQ R2TESTB` | 0000 | 0000 | 0052 | 0052 |
| X | S plus `BCXREQ BCPLDEMO` | 0000 | 0000 | 0060 | 0060 |

The nonzero GO codes are *expected size measurements*, not failure conditions.

## Evidence beyond condition codes

- IFOX macro expansion shows `PUNCH ' INCLUDE PKGA'` and `PUNCH ' INCLUDE PKGB'` for selected packages.
- IEWL `LIST/XREF/MAP` reports `INCLUDE PKGA` and/or `INCLUDE PKGB`, with absent packages excluded from the zero and single-package load modules.
- One package: BCRG length 44, `N=1`, `M=1`. Selected A, required B: length 52, `N=2`, `M=1`. Upgraded A and required B: length 60, `N=2`, `M=2`.
- The `GX` case emits exactly two `INCLUDE` cards and two relocated descriptor begin/end pairs; upgrading `BCXSEL` to `BCXREQ` does not duplicate a selected package.
- IEWL XREF confirms descriptor begin/end relocation; GO reads the linked `BCRGBEG/BCRGEND` extent.
- Each registration assembly reports zero flagged statements and highest severity 0.

The JES statistic `0 SYSOUT PUNCH RECORDS` is consistent with the test: `SYSPUNCH` wrote **temporary MVS datasets**, not a JES SYSOUT punch class.

## Boundaries and next gate

JOB 3720 did **not** exercise `BCPLMAIN` or `BCPLRGS` in a compiled BCPL application. Length and relocation do not alone prove registrar acceptance, validated dependencies, lifecycle, missing-package rejection, or real extension dispatch. The package catalog has only two known test entries and does not discover arbitrary packages.

The next isolated probe uses the resident demoted Cambridge compiler under MVS `ICINT19` to compile a BCPL client, assembles the accepted `BCPLMAIN` and `BCPLRGS`, links a real BCPLDEMO dispatcher with the generated BCRG/IEWL deck, and requires the BCPL `START` marker. No production objects, runtime ABI, compiler or package PDS are changed.
