# Milestone Runtime Extensions — R.2 BCPLDEMO JOB 3075 evidence

**March:** R.2 — Selective interoperability (ACTIVE)  
**Scope:** Extension A only — the project-maintained `BCPLDEMO` / `DEMOSVC:203` reference package  
**Evidence disposition:** First real MVS end-to-end demonstration **PASS**; approved for permanent documentation by the owner, 22 October 2026. **Not R.2 acceptance or closure.**  
**Git source baseline:** [`997ba4a`](https://github.com/cbmira01/BCPL-for-MVS/commit/997ba4a157127d30ae955621331f6a7c646df536)  
**Environment:** IBM System/370 under Hercules, MVS 3.8J TK5; demoted Cambridge compiler via the interpreter-hosted bootstrap toolchain; IFOX00 and IEWL.

## Operator procedure and provenance

From the repository root, the operator ran:

```sh
tools/bootstrap/compile-mvs \
  bootstrap-toolchain/probes/r2-interoperability/demo.bcpl \
  --job-name R2DCOMP \
  --output workarea/r2-demo.s370.asm

python3 bootstrap-toolchain/probes/r2-interoperability/make-job.py \
  --generated workarea/r2-demo.s370.asm

bash tools/mvs/submit-jcl workarea/runtime-extensions-r2/r2-demo.jcl
tools/mvs/dump-report-for-job 3075
```

The compiler command reported **JOB 3074** and saved `workarea/r2-demo.s370.asm`. The generated candidate deck was submitted as **JOB 3075 / R2DEMO**. The supplied `dump-report-for-job 3075` transcript is the reviewed primary JES, IFOX, IEWL, and GO evidence. The independent JOB 3074 JES report was **not** supplied, so its individual MVS step condition codes are not independently asserted here.

Host preflight at this source revision also reported **4 unit tests PASS** and **`CHECK R2DEMO: 2383 JCL cards`** (synthetic, in-memory preflight). Actual JOB 3075 reports **2,679 JES input cards** and **4,031 SYSOUT print records**; these are separate observations, not interchangeable deck counts.

## Actual MVS execution — 22 October 2026, 14:40:43 JES time

| JOB 3075 step | Program | Observed return code |
| --- | --- | --- |
| ASMA | IFOX00 | 0000 |
| ASMN | IFOX00 | 0000 |
| ASMR | IFOX00 | 0000 |
| ASMG | IFOX00 | 0000 |
| ASMD | IFOX00 | 0000 |
| ASMS | IFOX00 | 0000 |
| LKED | IEWL | 0000 |
| GO | `PGM=*.LKED.SYSLMOD` | 0000 |

The JES log records `$HASP373 R2DEMO STARTED` and `$HASP395 R2DEMO ENDED`. The GO output contains **exactly one** occurrence of the actual application success marker:

```text
R2 BCPLDEMO G203 PASS
```

In `demo.bcpl`, failed QUERY, buffer-guard, GETVALUES, and unsupported-opcode assertions invoke `STOP(8)`; the observed GO RC=0000 and success marker support PASS for those tested paths.

## Actual IEWL MAP/XREF evidence

IEWL ran with `NCAL,LIST,XREF,MAP`, with RC=0000. The cross-reference table identifies these linked control sections and entries (hexadecimal origins/lengths):

| CSECT | Origin | Length | Related entries |
| --- | --- | --- | --- |
| `R0APP` | `000000` | `0003C0` | Application entry |
| `BCPLMAIN` | `0003C0` | `001048` | Temporary R.1 startup adaptation |
| `RGINIT` | `001408` | `000A20` | Generic registration initializer |
| `RGFINI` | `001E28` | `000100` | Generic finalizer path |
| `BCPLREG` | `001F28` | `00002C` | `BCRGBEG=001F28`, `BCRGEND=001F54` |
| `DMODESC` | `001F58` | `000038` | `DMOBEG=001F58`, `DMOEND=001F90` |
| `DMODISP` | `001F90` | `0000C8` | Dispatcher entry at `001F90` |

The map also reports `ENTRY ADDRESS 00` and `TOTAL LENGTH 5F08`. Its XREF references to `DMOBEG`, `DMOEND`, and `DMODISP` are linker reference locations, **not** alternate symbol definitions; use the CSECT/ENTRY table above for symbol addresses.

The `BCPLREG` source names the relocated `DMOBEG`/`DMOEND` descriptor span and requires package `BCPLDEMO`. `DMODESC` exports global **G!203** through `F'203',A(DMODISP)`. The compiled application's trailer exports its own `START` global, rather than registering `DEMOSVC` by application-trailer binding; this example exercises real `BCPLREG` selection.

## Exercised dispatcher contract

Actual BCPL caller assertions test:

- `DEMOSVC(0,0,0)` returns required descriptor size **6**.
- Short QUERY capacity returns **-1** without changing checked sentinel words; invalid null/negative argument combinations return **-3**.
- Six-word QUERY reports format **1**, API **1.0**, required size **6**, opcode bitmap **1**, capability flags **0**; the adjacent canary is unchanged.
- Opcode 1 `GETVALUES` rejects short capacity (**-1**) and null vector (**-3**), then returns **3** with fullwords **10, 20, 30** and no checked canary overwrite.
- Unsupported opcode 2 returns **-2**.

These assertions are verified as a combined successful GO path, not as independently logged per-assertion markers. They do **not** establish exhaustive arbitrary-pointer protection, all failure combinations, or a two-extension interoperability gate.

## Resource boundaries and remaining R.2 work

The six candidate assembler object datasets and the `R2DEMO` load module used temporary `&&` datasets. `HERC02.BCPL.BOOT.OBJ` was linked with `DISP=SHR`; the transcript shows it **KEPT**. No `BOOT_DEVOBJ` allocation or persistent object promotion was performed by this job. The generated authenticated deck and full JES transcript remain local operator artifacts; neither credentials nor raw spool output are committed here.

**Established:** One genuine project-assigned, separately compiled BCPL caller successfully invoked the independently assembled `BCPLDEMO` dispatcher at G!203 after R.1 generic registration, with actual IEWL relocation evidence.

**Not yet established:** independent extension B, 0/A/B/A+B selection matrix, collision/malformed-descriptor/missing-dependency/absent-module rejection matrix, cross-package QUERY behavior, or R.2 closure. R.2 remains **ACTIVE**. R.3 has not started. `BOOT_OBJ` and `BOOT_DEVOBJ` accepted contents are unchanged, and G!150 FORMTREE/DEBUGINT remains a separate unresolved issue.

## Reproduction sources

- [BCPLDEMO example and execution procedure](../bootstrap-toolchain/extensions/bcpldemo/README.md)
- [R.2 interoperability probe](../bootstrap-toolchain/probes/r2-interoperability/README.md)
- [R.2 BCPLDEMO design decision](runtime-extensions-r2-bcpldemo-decision-20261022.md)
- [Milestone Runtime Extensions](milestone-runtime-extensions.md)
