# M3 — Native Compiler and Runtime Reconstruction Acceptance

**Status: ACCEPTED — 15 October 2026 (MVS/TK5 job date).**

## Boundary

This records restoration of the **existing** native-compiler toolchain and its native application regression panel after repository and dataset refactoring. It is **not** acceptance of a native-implemented Cambridge compiler, and does **not** authorize M4 use of `CAMB_*` datasets.

- Git is canonical for source and JCL; `config/dspal.yaml` defines the MVS dataset layout.
- Runtime assembler source is installed in `NATIVE_ASM`; BCPL compiler sources and headers in `NATIVE_SOURCE`; authoritative MVS build procedures in `NATIVE_JCL`.
- Compiled interpreter and compiler INTCODE and all runtime objects were **rebuilt** rather than migrated from the retired datasets.
- Accepted runtime objects in `NATIVE_OBJ` and candidate service modules in `NATIVE_DEVOBJ` remain distinct. This acceptance does not promote candidates.

## Operator-provided MVS evidence

| Evidence | Result |
| --- | --- |
| MR10 interpreter build, payload JOB 4965 | `MR10_LOAD(ICINT19)` installed, assembler/link/run steps successful |
| Large translator, JOB 4971; installed JOB 4972 | `NATIVE_INTCODE(TRNILRG)`; fetched copy matched staged input |
| Resident compiler image build, payload JOB 4994 | 22 ICINT19 compile/codegen steps and PACKCOMP RC=0000; `NATIVE_INTCODE(CAMBCOMP)` present |
| Resident compiler smoke compile, JOB 4996 | Generated System/370 assembler source from regression 00 |
| Runtime source population, JOBs 4998–5005 | Eight `NATIVE_ASM` members installed |
| `BLDBMAIN`, payload JOB 5012 | BCPLMAIN and BCPLMEM: IFOX/IEBGENER RC=0000; `NATIVE_OBJ` members verified |
| `BLIBBLD`, payload JOB 5019 | Compiler, card fix, IFOX and IEBGENER RC=0000; `NATIVE_OBJ(BLIB)` verified |
| `BLDDEVA`, payload JOB 5047 | `NATIVE_DEVOBJ(BCPLAPT)` rebuilt |
| `BLDDEVB`, payload JOB 5050 | `NATIVE_DEVOBJ(BCPLBYTE)` rebuilt |
| `BLDDEVI`, payload JOB 5030 | `NATIVE_DEVOBJ(BCPLIO)` rebuilt |
| Native regression 00 | PASS, 0 FAIL |
| Native regressions 00–09 | 10 PASS, 0 FAIL |
| **Full native regression 00–123** | **123 PASS; 0 FAIL; 1 expected SKIP (083); 124 total** |

Regressions 075 and 076 report PASS against their existing fixtures; this does not imply all historical WRITEF limitations have been repaired. Regression 083 remains intentionally omitted in the installed-object mode because its reclamation counters need source-level instrumentation.

## Reconstructed object library state

- `HERC02.BCPL.NATIVE.OBJ`: `BCPLMAIN`, `BCPLMEM`, `BLIB`.
- `HERC02.BCPL.NATIVE.DEVOBJ`: `BCPLAPT`, `BCPLBYTE`, `BCPLIO`.
- Default native regression link-edit reads both libraries, without promoting candidate objects.
- The regression driver is `tools/native/run-regression`; its current default is the installed-object route.

## Lessons preserved

- Updating tracked JCL does not update installed PDS members: install changed JCL with `dspal put` or repopulate `NATIVE_JCL` before execution. Earlier JOB 5037 used old `HERC02.BCPL.SOURCE/DEVOBJ` references despite RC=0000. After corrected JCL deployment, the expected `NATIVE_DEVOBJ` directory appeared.
- The retired `tools/native/build-cambridge` and `tools/native/build-blib` duplicated MVS build responsibility; authoritative build jobs live under `native-compiler/jcl/`.
- Generated compiler INTCODE and binary objects are rebuildable deliverables, not migration inputs.

## Acceptance scope and follow-on

The full native application regression panel demonstrates restoration of the pre-M3 executable pipeline in the new datasets. Remaining M3 closure work, if any, is repository documentation/manifest hygiene and validation of rebuild instructions; **no native compiler or runtime semantic changes are indicated by the panel**. Future native Cambridge compiler work must be separately scoped and use the reserved M4 resources only after authorization.

Evidence is based on operator-submitted JES summaries, verified member inventories, and full regression output in the project conversation; the GitHub-connected assistant did not itself run jobs on Hercules.
