# Milestone BCPLTIME — T.1 packaging and installation design

**Project:** BCPL for MVS 3.8 Reconstruction  
**March:** **T.1 — Packaging and Acceptance (CLOSED 24 October 2026)**  
**Owner design approval:** 24 October 2026  
**Authority chronology:** Design approved, then five specific permanent
member writes separately authorized and completed 24 October 2026.
**No further permanent PDS writes are authorized by this record.**  
**Acceptance:** [T.1 owner closure](bcpltime-t1-closure-20261024.md)  
**Official source:** GitHub `main`; resident MVS objects are rebuildable products, not canonical sources.

## Package and exact member mapping

BCPLTIME is a project-created optional System Extension with BCEX/BCRG v1
descriptor `TIMDESC`, dispatcher `TIMDISP`, exported descriptor extent
`TIMBEG`/`TIMEND`, and BCPL `TIMESVC:201`. The approved version-1
operations remain QUERY, raw STCK and raw MVS TIME DEC; its STCK scratch
area remains **non-reentrant**. It has no dependency on BCPLDEMO.

| Managed PDS alias | Member | Git source or role |
| --- | --- | --- |
| `EXT_ASM` | `BCPLTIME` | `bootstrap-toolchain/extensions/bcpltime/bcpltime.asm` |
| `EXT_SOURCE` | `TIMEHDR` | `bootstrap-toolchain/extensions/bcpltime/bcpltime.h` |
| `BOOT_JCL` | `T1TINST` | `bootstrap-toolchain/jcl/t1tinst.jcl` |
| `EXT_OBJ` | `BCPLTIME` | FB80 binary relocatable object assembled on **MVS** |
| `EXT_MAC` | existing `BCXCAT` | Production known-package selection catalog |

No new PDS allocation is required. Retain `EXT_ASM(BCPLDEMO)`,
`EXT_SOURCE(DEMOHDR)`, `EXT_OBJ(BCPLDEMO)`, `BCXPRE`, `BCXPOST`,
and `BOOT_JCL(R5DINST)`. `EXT_OBJ` remains `populate: false`.
Never transfer binary object records with a text-oriented `dspal put`.

Production `BCXCAT` recognizes both `BCPLDEMO` and `BCPLTIME`,
emitting `INCLUDE EXTLIB(BCPLDEMO)` with `DMOBEG`/`DMOEND`
or `INCLUDE EXTLIB(BCPLTIME)` with `TIMBEG`/`TIMEND`.
`BCXPRE`, `BCXPOST`, BCPLMAIN, BCPLRGS, the demoted Cambridge
compiler, and BCEX/BCRG v1 are **unchanged**. The source-mode
`t1-catalog.asm` is a test fixture, never an installed macro member.

## Safe offline preflight — no resident writes

Record the exact Git revision and check the manifest/source and job:

```sh
python3 -m unittest discover -s tools/checks -p 'test_*t1_time*.py' -v
python3 -m unittest discover -s tools/checks -p 'test_t1_install_packaging.py' -v
python3 -m unittest discover -s tools/checks -p 'test_r5_time_absence.py' -v
tools/bootstrap/run-regression --check-numbering
tools/datasets/dspal populate EXT_ASM --dry-run
tools/datasets/dspal populate EXT_SOURCE --dry-run
tools/datasets/dspal populate EXT_MAC --dry-run
tools/datasets/dspal populate BOOT_JCL --dry-run
tools/datasets/dspal info
```

The tracked `T1TINST` job body is explicitly configured for the
R.5 site's `HERC02.BCPL.*` datasets. Stop if the effective local
configuration resolves other names. These checks do not submit any
installation job. **Incremental installation must not use
`dspal populate EXT_ASM`**, because population rewrites every mapped
member, including BCPLDEMO. Use member-level `dspal put` only after
separate approval.

## Live incremental installation — requires separate owner approval for any future run

**The owner separately authorized this exact installation on 24 October
2026; it completed successfully. These commands are a repeatable
operator procedure, not standing authority for a future MVS write.**
Before any future run, obtain explicit approval and confirm the existing
`EXT_*`, `BOOT_JCL` and `BOOT_OBJ` inventories; save the accepted
resident `BCXCAT` contents and the source revision for recovery.

1. Stage **only the three new** tracked text members:

   ```sh
   tools/datasets/dspal put EXT_ASM BCPLTIME \
     bootstrap-toolchain/extensions/bcpltime/bcpltime.asm
   tools/datasets/dspal put EXT_SOURCE TIMEHDR \
     bootstrap-toolchain/extensions/bcpltime/bcpltime.h
   tools/datasets/dspal put BOOT_JCL T1TINST \
     bootstrap-toolchain/jcl/t1tinst.jcl
   ```

2. Verify the resident members, then submit the approved install job:

   ```sh
   tools/datasets/dspal submit BOOT_JCL T1TINST
   ```

   `dspal submit` supplies the authenticated JOB card. Retain both
   launcher and payload JOB numbers. The JCL has exactly four steps:

   | Step | Program | Required evidence |
   | --- | --- | --- |
   | `ASMTIME` | `IFOX00` | `EXT_ASM(BCPLTIME)` to temporary FB80 object; RC=0000 and no flagged statements |
   | `PUTTIME` | `IEBGENER` | **Only binary PDS write**: `EXT_OBJ(BCPLTIME)`; RC=0000 |
   | `READBACK` | `IEBGENER` | Installed binary object copied to temporary sequential FB80; RC=0000 |
   | `VERIFY` | `IEBCOMPR` | Original and read-back records equal; RC=0000 |

   Each downstream step is conditional on the prior step's RC.
   Review the actual JES/IFOX listing and IEBCOMPR record counts.
   The job does not update BCPLDEMO, `BOOT_OBJ`, or `BOOT_DEVOBJ`.

3. Check `tools/datasets/dspal ls EXT_OBJ`: both `BCPLDEMO` and
   `BCPLTIME` must exist. **Only after a successful binary comparison**,
   publish the updated existing production catalog:

   ```sh
   tools/datasets/dspal put EXT_MAC BCXCAT \
     bootstrap-toolchain/extensions/bcx/BCXCAT.asm
   tools/datasets/dspal cat EXT_MAC BCXCAT
   ```

   Do not rewrite BCXPRE or BCXPOST. Publishing the catalog last
   avoids advertising an unavailable object during a live upgrade.

4. Run installed-mode tests with both optional packages read-only:

   ```sh
   export BCPL_RUNTIME_PDS=1
   export BCPL_RUNTIME_LIBRARY=OBJ
   export BCPL_RUNTIME_CANDIDATE=0
   export BCPL_R5_EXTENSION_MODE=installed
   export BCPL_R5_EXTENSION_DSN=HERC02.BCPL.EXT.OBJ
   export BCPL_R5_MACRO_DSN=HERC02.BCPL.EXT.MAC
   export BCPL_T1_EXTENSION_MODE=installed
   export BCPL_T1_EXTENSION_DSN=HERC02.BCPL.EXT.OBJ
   export BCPL_T1_MACRO_DSN=HERC02.BCPL.EXT.MAC
   tools/bootstrap/run-production-regression 159 162 --show-output
   tools/bootstrap/run-production-regression 0 162
   ```

   The full acceptance target is **162 PASS, 0 FAIL, one expected
   SKIP 083 (163 total cases)**. Cases 146 and 158 must exclude *both*
   extension CSECT pairs; R.5 cases 147–157 must continue including
   BCPLDEMO without BCPLTIME. Cases 159–162 must verify installed
   BCPLTIME alone and alongside BCPLDEMO, selection order and
   request deduplication with real IEWL maps and native GO results.
   Retain detailed operator-local JES reports, step RCs, IFOX messages,
   installed PDS inventory and verified regression tally.

## Clean-room rebuild and recovery

A fresh clean-room `dspal populate all` installs the Git-controlled
source, header, job and updated BCXCAT **before** building binary
members. Do not run the optional-extension panel until **both**
`R5DINST` and `T1TINST` have completed with verified readbacks.
The accepted R.5 binary build must not be displaced by T.1.

An object-member update is not atomic. If `ASMTIME`, `PUTTIME`,
`READBACK` or `VERIFY` fails, **do not publish BCXCAT**. Diagnose
and rebuild `EXT_OBJ(BCPLTIME)` from the pinned Git revision.
If a catalog already published during a failed regression must be
reverted, restore the previously accepted BCPLDEMO-only `BCXCAT`
from Git with a controlled member-level put after review. No backup
PDS, binary-versioning facility or wholesale Core Runtime rebuild is
required. Do not purge unrelated datasets as a recovery shortcut.

## Completed installation and owner acceptance — 24 October 2026

The owner approved the design, then separately approved the specified
live incremental installation. Staging JOBs **5446–5448** installed
the BCPLTIME source, header and job body; launcher **5454** submitted
payload **5455**. The four `ASMTIME`/`PUTTIME`/`READBACK`/
`VERIFY` steps all returned **RC=0000**, with zero flagged
assembler statements, 12 object records punched and 12 records
compared. `EXT_OBJ` held both BCPLDEMO and BCPLTIME. JOB **5457**
published the revised `BCXCAT`, whose resident readback confirmed
both independent package mappings.

Focused installed-mode 159–162: **4 PASS, 0 FAIL, 0 SKIP**.
Full production 00–162: **162 PASS, 0 FAIL, 1 expected SKIP 083**,
TOTAL 163. The owner explicitly approved **T.1 closure** after
reviewing this evidence. See the [formal acceptance record]
(bcpltime-t1-closure-20261024.md) for tested revision, jobs and
limitations. **No new resident PDS writes are authorized by closure.**
