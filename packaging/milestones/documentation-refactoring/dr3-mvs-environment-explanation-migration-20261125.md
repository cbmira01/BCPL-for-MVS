# DR.3 — MVS programming environment: migration and evidence

**Date:** 25 November 2026 EST  
**Baseline:** `f111b92ff7fb8805c4f62bde46d8249752b5740b`  
**Status:** Twelve-chapter working explanation; owner commit authorization pending. DR.3 remains IN PROGRESS.

Destination: [Explanation of the MVS Programming Environment](../../../docs/project/Explanation-of-the-MVS-Programming-Environment.md). Retain original briefings and normative sources.

| Existing source | Chapters | Reconciliation / qualifications |
| --- | --- | --- |
| [System/370](../../../docs/System_370-briefing.md), [IBM data](../../../docs/IBM-data-representation.md) | 1–2 | 24-bit address vs 32-bit register, zero base/index, PSW/CC, byte order, decimal/floating and EBCDIC/raw distinction. |
| [MVS overview](../../../docs/MVS-3_8-briefing.md), [storage](../../../docs/MVS-storage-and-addressing.md), [interfaces](../../../docs/MVS-system-programming-interfaces.md) | 3–4, 9 | Address space vs task, DAT, protection, macros vs SVC, service lifetime, WAIT/POST and ENQ/DEQ. |
| [Access methods](../../../docs/MVS-access-methods.md), [QSAM specification](../qsam/bcplqsam-public-interface.md), [BLIBBLD](../../../bootstrap-toolchain/jcl/blibbld.jcl) | 5 | DCB, PS/PDS, RDW/BDW, QSAM/BSAM/BPAM, actual EODAD helper, project-specific ceiling. |
| [JCL](../../../docs/JCL-for-the-programmer.md), [BLDCORCO](../../../bootstrap-toolchain/jcl/bldcorco.jcl) | 6 | JOB/EXEC/DD, spool, DISP/COND, temporary binary deck vs persistent gated installation. |
| [IFOX](../../../docs/IFOX-assembler-toolchain-briefing.md), [objects/load modules](../../../docs/S370-object-and-load-modules.md), [historical paired promotion](../../operations/runtime-object-promotion.md) | 7–8 | Actual assembler options, USING vs runtime base, ESD/TXT/RLD/END, DD and symbol resolution, maps. |
| [Execution](../../../docs/MVS-program-execution.md), [debugging](../../../docs/MVS-debugging.md), [case 075](../../../tests/bootstrap/075-blib-writef-mixed-object/README.md), [CO.6 closure](../coroutines/co6-formal-acceptance-and-closure-20261116.md) | 9–10 | Save-area chain and actual entry/exit; distinguish PSW, RC, CODE and oracle, S0C4 vs S0C5 and old PSW caveat. |
| [Hercules](../../../docs/Hercules-briefing.md), [Compose](../../../docker/compose.yaml), [console guide](../../../tools/mvs/mvs-console-README.md) | 11 | Emulator/guest/host boundary, tracked ports/binds not live inventory, IPL and media/output distinction. |
| [BCPL history](../../../docs/BCPL-history-and-porting.md), [memory](../../../docs/BCPL-memory-management.md), [BCPLMAIN](../../../bootstrap-toolchain/asm/bcplmain.asm), [BCPLBYTE](../../../bootstrap-toolchain/asm/bcplbyte.asm), [BCPLMEM](../../../bootstrap-toolchain/asm/bcplmem.asm), [nomenclature](../../architecture/runtime-and-library-nomenclature.md) | 2–4, 12 | Interpreted vs native compiler/output, real byte bridge, allocation, global registration, qualified coroutine scope; original sources retained. |

## Primary-source review

Selected indexed primary-source extracts were inspected: IBM GA22-7000-4 (1975) for base/index/displacement formation; GC26-3783-5 (1975) for organization and RDW/BDW; GC33-4010-5 (1979) for USING/DROP; GC28-0683-3 (1983) for conventional save-area chaining and return. Actual publication links are in the manual. Editions and dialects are not assumed identical to the installed target. Modern IBM record-format text was consulted only for corroboration, not for importing later extended formats. Upstream Hercules references were identified for further study; tracked Compose supplies project mappings.

The PDF screenshot requests failed with cache misses. Indexed text was available, but scanned-page validation and comprehensive instruction, macro and operating-system edition review were not completed. Other manuals named for further study are not represented as fully inspected. DR.5 must verify consequential details against applicable historical manuals and actual target evidence where needed.

## Disposition

- Clarify address range versus region availability, addressability versus allocation, machine condition code versus job RC, and S0C4 versus S0C5. Distinguish text from binary records and the ordinary RDW/BDW model from the restricted BCPLQSAM contract.
- Actual source/JCL excerpts are not complete executable templates. Worked addresses/record descriptors are explanatory calculations, not fresh MVS tests.
- Retain original briefings and earlier failures, historical evidence, configuration, contracts and product references. No existing path is retired. DR.0 dependency qualification and DR.5 integrated reconciliation remain.
- No new MVS execution, repository unit tests, raw private report reopening, exhaustive primary-source or full historical compatibility verification. No code, JCL, registry, configuration, manifest or accepted historical evidence changed.
