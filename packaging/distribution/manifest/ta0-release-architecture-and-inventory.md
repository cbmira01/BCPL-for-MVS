# TA.0 — Release architecture, inventory and manifest mapping

**March:** TA.0 — Release Architecture, Inventory, and Manifest
**Status:** TA.0 CLOSED (qualified) by owner direction 17 November 2026; this remains a design inventory, not a frozen release candidate
**Source inspected:** GitHub `main` at `624f70d331b1e7c0bc9a26a946b8b07d23799875`
**Controlling:** [Milestone](../../milestones/tape-artifact-release/milestone-tape-artifact-release.md), [scoped release](../release-without-native-compiler-decision-20261116.md), [nomenclature](../../architecture/runtime-and-library-nomenclature.md), [manifest schema](schema-v1-design.md).

`config/dspal.yaml` currently defines **29 managed development datasets**, not 29 automatically selected release datasets. The canonical per-release manifest explicitly selects members; each physical dataset has one group/target, each member one logical owner, one source lineage and one redistribution disposition. Unselected development candidates must never leak into the release.

## MR10 Kit Compiler — 9 selected PDSes / 79 members

`HERC02` is the present development HLQ; all targets are `{HLQ}.<suffix>`. Exact proposed selected member list:

| `dspal` key / target suffix | Members | Count |
| --- | --- | ---: |
| `MR10_SOURCE` / `BCPL.MR10KIT.SOURCE` | `SYNI TRNI CGI BLIBI ICLIB` | 5 |
| `MR10_ASM` / `BCPL.MR10KIT.ASM` | `ICINT19` | 1 |
| `MR10_JCL` / `BCPL.MR10KIT.JCL` | `IC19BLD MRLANGDM MRBCDEMO MRREGRES` | 4 |
| `MR10_LIBRARY` / `BCPL.MR10KIT.LIBRARY` | `CHARUTIL COROUTIN GETVEC INTUTIL LINEIO MEMUTIL NUMCONV RANDOM STRUTIL` | 9 |
| `MR10_LANGDEMO` / `BCPL.MR10KIT.LANGDEMO` | `BOOLOPS DECLS FUNCVAL MANIGLOB PTRIDIOM REPEAT STRBYTES SWITCHON TABVECT TESTTHEN VALOFRES` | 11 |
| `MR10_BCPLDEMO` / `BCPL.MR10KIT.BCPLDEMO` | `RFACT QUEENS KNIGHT HANOI SIEVE GCD QUICKSRT BSEARCH LINKLIST BINTREE HASHTABL WORDCNT RPNCALC EXPRPARS MAZE STRMFANO COROUTIN WORDIN FANAIN FANBIN FANCIN` | 21 |
| `MR10_TESTS` / `BCPL.MR10KIT.TESTS` | Exact 26 below | 26 |
| `MR10_OBJ` / `BCPL.MR10KIT.OBJ` | Relocatable object `ICINT19` | 1 |
| `MR10_LOAD` / `BCPL.MR10KIT.LOAD` | Executable load module `ICINT19` | 1 |
| **Total** | | **79** |

`MR10_TESTS`: 12 case sources plus companion `MODHELP` — `SCALVEC BYTES INTARITH BRANCHES NESTREC MODMAIN BASLIB RANDCHAR STRMEM LINEIO GETVEC BASICCO MODHELP`; 12 expected results — `SCAVEXP BYTESEXP INTAREXP BRANEXP NESTREXP MODEXP BASLEXP RANDEXP STRMEXP LINEEXP GETVEXP BASCOEXP`; input fixture `LINEIN`. The authoritative case manifest is `mr10-kit-compiler/tests/00-regression-panel/manifest.tsv` with twelve interpreted expected `CODE=0` cases.

**Exclude** `MR10_SOURCE(ICLIBC)`, `MR10_LIBRARY(COCAND)`, earlier `ICINT12`–`ICINT18`/trace members, experimental/coroutine-candidate JCL, and all probes outside the standard 12-case panel. Preserve known probe failures separately. Existing `MRREGRES` and demo jobs hardcode `HERC02` and lack site JOB cards; TA.4 must adapt them and add literal `EXP:` to all 12 BCPL programs while preserving `RP:` and WSL checks.

## Accepted native Core Runtime, Base Library and Coroutine Support

| Dataset key | Proposed member selection | Owner and limitation |
| --- | --- | --- |
| `BOOT_OBJ` | Exactly **10**: `BCPLMAIN BCPLMEM BCPLBYTE BCPLAPT BCPLIO BCPLRGS BCPLREG BLIB BCPLCO COROUTIN` | First 7 Core Runtime/registration, `BLIB` historical Base Library, `BCPLCO` bridge and `COROUTIN` separate Coroutine Support. Accepted production inventory, recheck MVS binaries for candidate. |
| `BOOT_ASM` | `BCPLMAIN BCPLIO BCPLMEM BCPLBYTE BCPLAPT BCPLRGS BCPLREG BCPLCO` (8 Git-backed) plus generated `COROUTIN` (1) after source/build verification | `BCPLCO` Git origin: `bootstrap-toolchain/asm/bcplco-production.asm`; `COROUTIN` assembler derives from maintained BCPL source. |
| `BOOT_SOURCE` | Provisional minimum `LIBHDR BLIB COROUTIN COHDR` | Historical `LIBHDR` and `BLIB` (generated), plus separate coroutine source/header; complete dependency audit still required. |
| `BOOT_JCL` | Provisional release-adapted `BLDBMAIN BLDCORCO BLDCORLB BCPLDEMO BCPLTIME BCPLQSAM` | Not yet site-independent. Check executable dependencies; `BLIBBLD` needs development `CAMBCOMP` and cannot be promised runnable on a no-native-compiler recipient. |

In the scoped configuration, approved objects and their Git/historical source, binary provenance, and applicable assembler rebuild/link procedures ship, **without asserting BCPL-source rebuild under a missing native compiler**. `BOOT_DEVOBJ` and `BOOT_INTCODE(CAMBCOMP)` are not release products.

## Required System Extensions

| Dataset key | Exact members |
| --- | --- |
| `EXT_OBJ` | `BCPLDEMO BCPLTIME BCPLQSAM` — accepted relocatable objects |
| `EXT_ASM` | `BCPLDEMO BCPLTIME BCPLQSAM` — Git-backed assembly |
| `EXT_SOURCE` | `DEMOHDR TIMEHDR QSAMHDR` — headers |
| `EXT_MAC` | `BCXPRE BCXCAT BCXPOST` — BCEX/BCRG v1 selection |

All are **present on release tape** and **optional in individual IEWL application linkage**. `BCPLDEC` and Standard Library are excluded. `COROUTIN` is not `BLIB` and not a System Extension.

## Documentation, installer, native compiler

- `DIST_DOCS`: `README INSTALL DATASETS COMPILE VERIFY RELEASE LICENSE` (7 FB80 members); current drafts have development-specific wording, so release-specific documents must be generated from the manifest with truthful capability and checksum references.
- `BCPL.BT0001`: reserved sequential read-only EBCDIC FB80 bootstrap. `BCPL.BT0002`: reserved IEBCOPY unload of **generated MVS-only installation PDS**; its actual member inventory is **not yet implemented**.
- `CAMB_SOURCE`, `CAMB_ASM`, `CAMB_JCL`, `CAMB_LIBRARY`, `CAMB_BCPLDEMO`, `CAMB_LANGDEMO`, `CAMB_TESTS`, `CAMB_OBJ`, `CAMB_LOAD`: development placeholders (`populate: false`) with **no certified native-running compiler inventory**. Historical `cambridge-compiler/jcl/makeobj.jcl`/`makelib.jcl` are `BCPLIB.*` historical jobs, not functioning native compiler build products. **Select none when `native_compiler: absent`.** Include only after exact real source/object/load/JCL evidence and native self-compilation acceptance. `CAMBCOMP` is not interchangeable.

## Proposed logical tape ordering

**Only BT0001 and BT0002 roles are binding.** Other positions below are **unassigned proposals**, not a frozen release:

| Logical dataset sequence | Contents |
| --- | --- |
| 1 | `BCPL.BT0001` read-only bootstrap |
| 2 | `BCPL.BT0002` installer PDS unload |
| 3 | `DIST_DOCS` |
| 4–12 | Nine MR10 PDSes in table order |
| 13–16 | Four `BOOT_*` PDSes in table order |
| 17–20 | Four `EXT_*` PDSes in table order |
| 21 onward, only if included | Verified native Cambridge compiler dataset inventory |

Every alias `BCPL.BTnnnn` is derived from 1-based **logical MVS tape dataset sequence** and must agree with `LABEL=(n,SL)`; Hercules physical `hetmap` file numbers do not equal these positions.

## DCB/transport and source-to-recipient mapping

| Kind | Source/restored `DSORG/RECFM/LRECL/BLKSIZE` | Transport |
| --- | --- | --- |
| Bootstrap | `PS/FB/80/800` proposed | Sequential EBCDIC SL |
| Source, JCL, demo, test, docs PDS | `PO/FB/80/800` | IEBCOPY unload/restore |
| Relocatable object PDS | `PO/FB/80/800` | Binary-preserving IEBCOPY |
| Executable load library | `PO/U/0/6144` | IEBCOPY; **TA.1 executable round-trip unverified** |

The accepted **single** object-PDS tape round trip observed **sequential unload** `RECFM=V/LRECL=816/BLKSIZE=820`, distinct from PDS DCB and **not** a universal unload setting. Record separate source PDS DCB, tape unload DCB and recipient restored PDS DCB. Source `HERC02.BCPL.MR10KIT.SOURCE` becomes `{HLQ}.BCPL.MR10KIT.SOURCE` only after legal, authorized HLQ substitution; no operational `HERC02` DSNs may remain in recipient JCL.

**Profiles:** MR10-only = nine MR10 PDSes plus common materials; native-only = four `BOOT_*` + four `EXT_*` plus common materials, and `CAMB_*` only when included; combined = deduplicated union. No MR10 dependency is permitted for native-only linking/execution. With no compiler, native-only is **native components**, not an independent source compiler. The complete configuration additionally needs TA.6 genuine native self-compilation.

## Validation/provenance acceptance

Static: exact member lists, one primary logical owner per member, source path/generator, legal member and DSN, no extra/candidate objects, no missing dependencies, expected group/profile closure, `native_compiler` gate, contiguous aliases and unique VOLSER. Pre-tape MVS: actual PDS DCB/member inventories, binary source/build evidence for 10 accepted `BOOT_OBJ` and three `EXT_OBJ`, `ICINT19` object/load and `COROUTIN` derivation. Tape: `VOL1/HDR1/HDR2/EOF1/EOF2`, data/filemarks, logical sequencing, readback and immutable AWS SHA-256. Clean target: all three profile paths; 11+17 MR10 demos; 12 literal `EXP:` vs computed `RP:` and `CODE=` checked by human with per-case PASS/FAIL/sign-off, unchanged automated WSL runner; native Core Runtime/`BLIB`/Coroutine Support/Extension/link/execution tests; self-compilation only if compiler included.

Each member's source-to-MVS record must identify project-original, preserved historical, derived or MVS-generated status, Git input, source rights and required attribution, transformation/encoding, IFOX/IEWL/JES build receipts and redistribution disposition. Public historical source is not automatically licensed by the project's MIT license. Uncertain rights or provenance are a release gate.

**Remaining:** exact final native source/JCL dependencies, source-vs-object provenance, safe recipient installer, manifest parser, immutable version/VOLSER registry, TA.1 multi-dataset and `RECFM=U` experiments, MR10 `EXP:` modification and clean-target tests. TA.0 remains open and TA.1 writing separately gated.

## Subsequent TA.0 static audit

The [derived member provenance and recipient-JCL dependency audit](ta0-provenance-and-dependency-audit.md) checks this one design selection against Git and `dspal` mappings: 110 Git-backed paths, two generated members, fifteen MVS object/load members, and ten JCL site-adaptation blockers. It is **not** a second release manifest, a rights approval, MVS acceptance or a permit to write tape.

## Qualified TA.0 closure — 17 November 2026

The owner formally directed TA.0 closure. The
[formal acceptance and TA.1 transition](../../milestones/tape-artifact-release/ta0-formal-acceptance-and-ta1-transition-20261117.md)
accepts this design baseline with explicit qualifications: the development
14-object printer readback (902 FB80 records / 72,160 bytes), JOB 9060
`ICINT19` directory and JOB 9061 development execution are verified in
the stated scope; exact resident source lineage, complete build receipts,
`RECFM=U` tape restoration, manifest freeze, rights and recipient
installation are not. These remaining obligations are preserved in the
governing milestone's existing later marches. No tape write or release
publication is authorized by closure.
