# Canonical native System/370 Core Runtime sources

These are maintained assembler sources for the **native BCPL application
runtime used with the demoted Cambridge bootstrap compiler**. The demoted
compiler executes under `ICINT19`; its compiled applications execute as
native System/370 code. This is distinct from the separate native
Cambridge compiler reconstruction.

| Canonical Git source | Module | Responsibility |
| --- | --- | --- |
| `bcplmain.asm` | `BCPLMAIN` | Startup, global/system vectors, Base Library imports, registration and termination |
| `bcplio.asm` | `BCPLIO` | BCPL character streams implemented using MVS QSAM |
| `bcplmem.asm` | `BCPLMEM` | BCPL vector allocation and cleanup |
| `bcplbyte.asm` | `BCPLBYTE` | Byte-access primitives |
| `bcplapt.asm` | `BCPLAPT` | Argument-vector and workspace-limit service |
| `bcplrgs.asm` | `RGINIT` / `RGFINI` | Optional package registration and finalization |
| `bcplreg-empty.asm` | `BCPLREG` | Empty, application-specific registration table |

## Shared runtime and application-selected table

The five established modules plus `BCPLRGS` form the **Core Runtime**
source set. The **Base Library** `BLIB` is separately compiled BCPL.
Every application linking the registration-enabled Core Runtime must
select **exactly one** `BCPLREG` table: the empty table, or a table
naming selected optional packages. The selected table is application
data, not the generic registrar itself.

Optional System Extensions are separate packages under
`bootstrap-toolchain/extensions/`. The maintained reference example
`BCPLDEMO` uses G!203. It is not a mandatory Core Runtime module.

## Acceptance versus installed objects

Milestone Runtime Extensions R.0-R.3 closed on 22 October 2026.
Registration integration and selective extension linkage were tested
with **temporary** MVS objects. The owner explicitly deferred
installation to `BOOT_OBJ` and `BOOT_DEVOBJ`. Incorporating the accepted
R.1 integration into this canonical source does not promote any object.

**INSTALLATION HOLD:** `BOOT_JCL(BLDBMAIN)` is still the legacy
five-module production object-PDS writer and does not prepare the
complete registration-enabled runtime. Do not submit it until the
installation procedure and object membership are separately approved.
`BOOT_JCL(BLDRGCHK)` is a non-installing IFOX check of the canonical
BCPLMAIN, BCPLRGS and empty BCPLREG sources; it creates only
temporary object datasets and does not link or execute an application.

## Source layout and checks

Use ASCII IFOX source records with text in columns 1-71, asterisks
for comments in column 1, no tabs, and symbols of at most eight
characters. Historical sources remain under `history/`; working
fragments remain under `bcplmain-wip/` for reference only.

Host verification (no MVS installation):

```sh
python3 tools/checks/check-bcplmain-canonical.py
python3 tools/checks/check-native-jcl-manifest.py
python3 tools/checks/r1_prepare_candidate.py --check
python3 -m unittest discover -s tools/checks -p 'test_r1*.py' -v
```

Consult `packaging/milestone-runtime-extensions.md`,
`packaging/runtime-extensions-r3-closure-20261022.md`, and
`packaging/runtime-and-library-nomenclature.md` for the accepted
architecture and nomenclature.
