# TA.0 — Member provenance and recipient-JCL dependency audit

**Milestone:** Tape artifact release; **march:** TA.0 — Release Architecture, Inventory, and Manifest  
**Status:** Read-only design audit, **TA.0 IN PROGRESS**; no release acceptance, candidate or publication  
**Evidence basis:** GitHub `main` at `c65cae8f34a404d8913f9b4fe84bc1a10142ade1`, the 29-dataset `config/dspal.yaml` development map, the selected design inventory and Git object tree

This document reviews **the one design inventory**, [`ta0-inventory.yaml`](ta0-inventory.yaml); it does not create another member selection or second manifest. The read-only [`validate-manifest.py`](../../../tools/distribution/validate-manifest.py) `--audit-json` mode derives the current per-member worksheet from that inventory and `config/dspal.yaml`. Its source hints are **not** proven binary ancestry or redistribution permissions.

## 1. Selection and Git source-path verification

| Selected content | Git-backed members | Generated, MVS source provenance pending | Resident object/load binary evidence pending | Total |
| --- | ---: | ---: | ---: | ---: |
| Distribution documentation PDS | 7 | 0 | 0 | 7 |
| Nine MR10 Kit Compiler PDSes | 77 | 0 | 2 | 79 |
| Eight native Core Runtime/Base/Coroutine/Extensions PDSes | 26 | 2 | 13 | 41 |
| **Total (18 PDSes)** | **110** | **2** | **15** | **127** |

Together with the two reserved bootstrap positions, this is the proposed **20 logical MVS tape dataset** layout. Only `BCPL.BT0001` and `BCPL.BT0002` have approved fixed roles; proposed subsequent sequence assignments are not frozen release identities.

A read-only scan of the full Git tree (2,742 entries) and `dspal.yaml` found **zero missing paths among all 110 selected Git-backed members**. This checks path existence only—not file-to-MVS record equivalence, licensing, source semantics, generated outputs or accepted binaries. The source revision above is the audit input snapshot, **not** a reserved release source SHA.

## 2. Generated source and resident binary gaps

| Members | Derivation known from the development map | Evidence still required |
| --- | --- | --- |
| `BOOT_SOURCE(BLIB)` | Generated `workarea/bootstrap-cambridge/demoted/blib`; not a tracked file in `config/dspal.yaml` | Historical/input provenance, exact generation recipe and source verification; no claim of a recipient BCPL-source rebuild with the absent native compiler |
| `BOOT_ASM(COROUTIN)` | Generated from maintained `BOOT_SOURCE(COROUTIN)` for the accepted Coroutine Support Library | Compiler/generator inputs, actual assembled source, producer receipt and source-to-object correspondence; preserve its separate identity from `BLIB` |
| `MR10_OBJ(ICINT19)` and `MR10_LOAD(ICINT19)` | Source candidate `MR10_ASM(ICINT19)` | Read-only source/target DCB and object/load inventories, actual IFOX/IEWL job evidence, member content readback, load-library restore and executable use |
| Ten `BOOT_OBJ` members | Core seven, historical `BLIB`, and separate Coroutine Support `BCPLCO`/`COROUTIN` | Per-member correct assembler/BCPL generation chain, accepted MVS object inventory/readback and usable IEWL linkage/GO |
| Three `EXT_OBJ` members | `EXT_ASM(BCPLDEMO/BCPLTIME/BCPLQSAM)` source candidates | Accepted object provenance and build receipts; prove extensions are present on tape but optional at application link time |

The JSON worksheet deliberately reports **127/127 redistribution reviews as `UNREVIEWED`** and **0 MVS build receipts recorded**. These values are *audit placeholders*, not findings that historical materials are unlicensable or that accepted programs failed. An actual reviewer must record author/source lineage, rights basis, notices, transformation and accepted binary evidence **before** any production candidate may be declared distributable.

The source-to-object hints in the report are investigation pointers. A source path, compilation job name or accepted regression history alone does **not** prove that a particular resident binary was built from those exact source bytes.

## 3. Recipient JCL dependency and independence review

All ten provisionally selected JCL members were read from Git at the audit revision. Each contains literal `HERC02` development-site references and lacks a standalone JCL `JOB` card. Literal counts reflect simple text matches and may include comments; they do not alone establish which substitutions or new JOB statements are safe.

| Selected release member | Mapped source path (under repository) | `HERC02` literal count |
| --- | --- | ---: |
| `MR10_JCL(IC19BLD)` | `mr10-kit-compiler/jcl/build-icintv19.jcl` | 6 |
| `MR10_JCL(MRLANGDM)` | `mr10-kit-compiler/jcl/run-language-demos.jcl` | 49 |
| `MR10_JCL(MRBCDEMO)` | `mr10-kit-compiler/jcl/run-bcpl-demos.jcl` | 90 |
| `MR10_JCL(MRREGRES)` | `mr10-kit-compiler/jcl/run-regression-tests.jcl` | 89 |
| `BOOT_JCL(BLDBMAIN)` | `bootstrap-toolchain/jcl/bldbmain.jcl` | 16 |
| `BOOT_JCL(BLDCORCO)` | `bootstrap-toolchain/jcl/bldcorco.jcl` | 3 |
| `BOOT_JCL(BLDCORLB)` | `bootstrap-toolchain/jcl/bldcorlb.jcl` | 3 |
| `BOOT_JCL(BCPLDEMO)` | `bootstrap-toolchain/jcl/bcpldemo.jcl` | 3 |
| `BOOT_JCL(BCPLTIME)` | `bootstrap-toolchain/jcl/bcpltime.jcl` | 3 |
| `BOOT_JCL(BCPLQSAM)` | `bootstrap-toolchain/jcl/bcplqsam.jcl` | 3 |

Release-adapted jobs must obtain authorized recipient HLQ/JOB/UNIT/SPACE details through the MVS-only installer and work without the developer's `dspal` or resident `HERC02`. Verify actual job syntax, required components and controlled no-overwrite behavior on MVS before claiming any installation procedure works. Some native *source rebuilds* still depend on the development `CAMBCOMP` pipeline; without the native-running Cambridge Compiler, **native-only means accepted native components for linkage/execution, not BCPL source compilation**. `MR10-only` must stay independently runnable, and the combined profile must not invent a second compiler.

## 4. Reproducible read-only audit and gate separation

On an ordinary Git checkout with PyYAML:

```sh
python3 -B tools/distribution/validate-manifest.py
python3 -B tools/distribution/validate-manifest.py --audit-json
python3 -B -m unittest discover -s packaging/distribution/manifest/tests -p 'test_*.py' -v
```

The JSON contains an ordered entry for each selected PDS member, its logical owner, source class/reference, and **unreviewed** rights/MVS evidence slots. It is derived output, **not** a second release manifest. The existing design file must fail `--release` preflight. Offline tests use synthetic MVS mapping fixtures; they **do not** constitute live-MVS inventory proof.

Remaining TA.0 review includes the exact native source/JCL dependency closure, per-member attribution/rights methodology, DCB/transfer requirements and owner acceptance of the proposed order after `BT0002`. TA.1 must separately prove multi-dataset tape sequencing and `RECFM=U` executable load-library restore; TA.3 must prove the recipient installer; TA.4/TA.5 and TA.7–TA.8 own their respective MVS acceptance/publication evidence. **No tape operation, production release identity, VOLSER reservation, MVS dataset modification or march closure is authorized by this audit.**
