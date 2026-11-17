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

## 5. Native/MR10 release JCL dependency closure — 17 November 2026 checkpoint

A separate [read-only dependency scanner](../../../tools/distribution/audit-jcl-dependencies.py) now inspects the ten **selected Git JCL source members** using the one TA.0 design inventory and `config/dspal.yaml`. The scan classifies active `//` JCL `DSN=/DSNAME=` references (not comments or in-stream input), verifies that referenced PDS members are selected, identifies `EXEC PGM=` dependencies, rejects undeclared permanent datasets/programs and rejects MR10/native cross-profile dependencies. It **does not** parse all possible JCL constructs or prove that JES will accept generated recipient jobs.

**Independent read-only GitHub source review at `012fc467f274c682c8380b8992ee66fc157bed21`:**

| Finding | Count / result |
| --- | --- |
| Selected source JCL | 10 total: 4 `MR10_JCL`, 6 `BOOT_JCL` |
| Active selected permanent-dataset DSN references | 260 occurrences (111 with an explicit member qualifier); **zero** unselected dataset/member or MR10/native cross-profile references |
| Source jobs requiring recipient adaptation | **10/10** use literal `HERC02` and lack a standalone `JOB` card |
| Jobs requiring `SYS1.MACLIB` | **7/10** (IFOX assembler); a target MVS-system prerequisite, **not** tape content |
| Native JCL `CAMBCOMP` execution references | **0** among the six selected native JCL jobs |
| Active source JCL records longer than 80 columns | **0** in the ten inspected Git sources |

**Dependency interpretation:** `MR10_JCL(IC19BLD)` uses IFOX/IEWL/IEBGENER to build `ICINT19`, and the other three MR10 jobs run `ICINT19` with selected MR10 source/load/demo/test members. The six selected native jobs use IFOX/IEBGENER/IEBCOMPR with selected `BOOT_ASM`/`BOOT_OBJ` or `EXT_ASM`/`EXT_OBJ`. There is no direct `CAMBCOMP` program dependency in those six JCL bodies. However, `BOOT_JCL(BLDCORLB)` **assumes the generated assembler member** `BOOT_ASM(COROUTIN)` already exists, and no independently operable BCPL-source rebuild of historical `BLIB` is demonstrated without a native-running compiler. A no-native-compiler release may truthfully provide accepted objects and qualified assembler-source rebuilds, **not** native BCPL source compilation.

**Repeatability on an actual checkout (development host, PyYAML):**

```sh
python3 -B tools/distribution/audit-jcl-dependencies.py
python3 -B tools/distribution/audit-jcl-dependencies.py --json
python3 -B tools/distribution/audit-jcl-dependencies.py --strict
python3 -B -m unittest discover -s packaging/distribution/manifest/tests -p 'test_*.py' -v
```

The design-source `--strict` check is **expected to fail** because jobs still require `JOB` cards and `HERC02` substitution. For separately staged adapted JCL, the audit supports `--hlq SITEABC --strict` with an explicit `--dspal` mapping pointing to those staged Git-derived job files; the scanner performs **no adaptation**, writes no jobs and never submits them. Offline tests exercise synthetic fixtures (40 total manifest + JCL tests passed); a parallel read-only GitHub analysis independently checked the ten actual source JCL bodies. A static reference match is **not** MVS compilation, target installation or acceptance of job semantics.

**Still open:** define deterministic generated recipient JCL, site JOB/HLQ/UNIT/SPACE and no-overwrite policy, prove IFOX/IEWL/JES execution, establish exact MVS object/load inventory with source-to-binary receipts, generated `COROUTIN` provenance, historical redistribution permissions, and TA.1 tape mechanics. No VOLSER or release identity is reserved and no TA.0 march closure is claimed.

## 6. Binary source-to-build chain and saved-inventory checks — 17 November 2026

The read-only [binary build-chain auditor](../../../tools/distribution/audit-binary-build-chain.py) derives its fifteen selected MVS binary members from the *same* `ta0-inventory.yaml`. It statically parses `tools/reconstruction/verify.py` (without importing or executing it), checks accepted `RUNTIME_MEMBERS` and `EXTENSION_MEMBERS`, and verifies the selected Git-backed build JCL `EXEC` step sequence against the reconstruction `EXPECTED_STEPS` contract.

**Source and build map (Git source, not target binary proof):**

| Binary member(s) selected | Selected source member(s) | Reconstruction build job | Count |
| --- | --- | --- | ---: |
| `MR10_OBJ(ICINT19)`, `MR10_LOAD(ICINT19)` | `MR10_ASM(ICINT19)` | `MR10_JCL(IC19BLD)` — IFOX, IEWL and object save | 2 |
| `BOOT_OBJ(BCPLMAIN/BCPLMEM/BCPLBYTE/BCPLAPT/BCPLIO/BCPLRGS/BCPLREG)` | Corresponding `BOOT_ASM` members | `BOOT_JCL(BLDBMAIN)` — seven independent assemblies and seven installation steps | 7 |
| `BOOT_OBJ(BLIB)` | Generated `BOOT_SOURCE(BLIB)` | `BOOT_JCL(BLIBBLD)` — **development-only, not selected on tape**; uses the interpreter-hosted compiler | 1 |
| `BOOT_OBJ(BCPLCO)` | `BOOT_ASM(BCPLCO)` | `BOOT_JCL(BLDCORCO)` | 1 |
| `BOOT_OBJ(COROUTIN)` | Maintained `BOOT_SOURCE(COROUTIN)` and **generated** `BOOT_ASM(COROUTIN)` | `BOOT_JCL(BLDCORLB)` — assembler build requires the generated member already staged | 1 |
| `EXT_OBJ(BCPLDEMO/BCPLTIME/BCPLQSAM)` | Corresponding `EXT_ASM` members | Three separate `BOOT_JCL(BCPLDEMO/BCPLTIME/BCPLQSAM)` jobs | 3 |
| **Total** | | | **15** |

**Evidence qualification:** The established reconstruction/CO.5 records document accepted BOOT_OBJ inventories and production coroutine results (see [CO.5 qualified closure](../../milestones/coroutines/co5-formal-acceptance-and-closure-20261116.md)), but the original `mvs-state/reconstruction-evidence/` receipts and current MVS dataset bytes are **not in GitHub**. This audit therefore does not assign **any** of the fifteen members a candidate-specific MVS receipt, source revision binding, binary readback comparison or redistribution approval. It does not downgrade the historical qualified acceptance; it refuses to reuse it as unexamined **new tape candidate** evidence.

In particular, **both `BLIB` and `COROUTIN` are BCPL-derived**. Their installed object decks may be usable as accepted components without shipping the native-running Cambridge Compiler, but distributing `BOOT_SOURCE(BLIB)` or `BOOT_SOURCE(COROUTIN)` does not make a recipient BCPL-source rebuild possible. `BLIBBLD` is deliberately absent from the curated release JCL inventory because its `CAMBCOMP` dependency is not supplied. `BLDCORLB` is only independently usable after its generated IFOX assembler input is supplied.

**Local read-only commands on a real checkout (PyYAML on development host):**

```sh
python3 -B tools/distribution/audit-binary-build-chain.py
python3 -B tools/distribution/audit-binary-build-chain.py --json
python3 -B tools/distribution/audit-binary-build-chain.py --strict
python3 -B -m unittest discover -s packaging/distribution/manifest/tests -p 'test_*.py' -v
```

`--json` produces fifteen explicit *requirements* with MVS receipt fields `null` and rights `false`; it does not confer evidence or issue acceptance. The `--strict` exit is **expected nonzero**, even after a mere inventory match, until an independently designed candidate-specific evidence/rights acceptance mechanism exists.

The optional `--inventory-dir <directory>` reads four saved, standard `dspal ls` outputs (`MR10_OBJ.txt`, `MR10_LOAD.txt`, `BOOT_OBJ.txt`, `EXT_OBJ.txt`) and checks exact member equality and the development HLQ heading. It does **not** connect to MVS or produce those reports. Comparing directory member names is only one of many required checks: full member record bytes, DCB, job identity/RC/severity, restoration and executable linkage/GO remain necessary.

**Independent GitHub cross-check at `bb4a88d76dfbda91eacc7dda6cb196a3747534b2`:** all eight relevant IFOX/IEWL/IEBGENER build JCL step sequences matched `verify.py` expectations, including the unshipped `BLIBBLD` development job. The fifteen offline test cases added in this checkpoint are synthetic; with existing 40 TA.0 cases, **55 offline tests passed**. This is build-contract consistency evidence, **not** a resident MVS readback, legal redistribution determination, or TA.0 closure. No MVS or tape writes occurred.

## 7. Read-only retained MVS evidence preflight — 17 November 2026

The [operator-supplied evidence index contract](ta0-mvs-build-evidence-intake.md)
specifies eight JES job summary/full-report pairs and four saved object/load
directory listings with SHA-256 attachment integrity. The
[read-only inspector](../../../tools/distribution/audit-mvs-build-evidence.py)
uses existing reconstruction verification rules and rejects inconsistent
source claims, malformed job IDs, missing/duplicated members, unsafe paths,
symlinks, changed attachments, job failures, nonzero RCs, and absent CODE=0.

18 new synthetic tests pass, bringing the TA.0 offline suite to **73/73**.
No real JES output, MVS binary record readback, actual DCB proof or historical
redistribution acceptance is present in this checkpoint. Existing CO.5
qualification remains unchanged; no new tape-candidate evidence is claimed.

