# Owner decision — Release without the native-running Cambridge Compiler

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release, TA.0–TA.8 unchanged  
**Decision:** Owner-approved 16 November 2026, following TA.0 briefing  
**State:** Design approval; no release candidate, Git tag, tape operation, MVS installation, march closure or publication authorized.

The owner approved the curated-member inventory, single canonical manifest, MR10-only/native-only/combined installation choices, conservative transport and immutable release identity **with one proviso: a tape release must be possible without the unfinished native-running Cambridge Compiler**. This revises the earlier unconditional native-compiler gate in the [milestone](../milestones/tape-artifact-release/milestone-tape-artifact-release.md). The complete two-compiler product remains a separate release configuration.

## Explicit candidate configurations

| Manifest capability | Required installed content | Permitted claims |
| --- | --- | --- |
| `native_compiler: absent` | Fully independent `ICINT19` MR10 Kit Compiler with `SYNI/TRNI/CGI/BLIBI/ICLIB`, 11 language and 17 BCPL demonstrations, standard 12-case `MRREGRES`; accepted native Core Runtime, historical `BLIB`, separate `BCPLCO`/`COROUTIN` Coroutine Support Library, `BCPLDEMO`, `BCPLTIME`, `BCPLQSAM`, source/object/JCL/documentation and test materials as qualified | **One BCPL source compiler: MR10.** The native runtime, accepted native objects and System Extensions are usable for linkage/execution, but no native-running BCPL source compiler or self-compilation is shipped or claimed. |
| `native_compiler: included` | All above plus verified native-running Cambridge Compiler executable, source, assembler/build/link JCL, examples and native self-compilation evidence | Complete two-compiler distribution after TA.6 proof on a recipient MVS. |

`CAMBCOMP` is interpreter-hosted under `ICINT19` and is **not a native compiler substitute**. Neither configuration includes it by default. Native BCPL-derived object sources and build provenance may be supplied when `native_compiler: absent`, but a recipient cannot be promised to rebuild them from BCPL source with a compiler that is absent.

## Installation profiles

- **MR10-only:** complete interpreted BCPL compilation/execution/demos/regressions; no dependence on native runtime/compiler.
- **Native-only:** accepted native Core Runtime, `BLIB`, Coroutine Support Library and all three installed System Extensions. When `native_compiler: absent`, advertise this as **native components only**, suitable for supported binary linkage/execution and qualified IFOX assembler rebuild, not independent BCPL source compilation.
- **Combined:** union of selected groups; with `absent`, still only one BCPL source compiler (MR10). When included, the native compiler remains an independent environment with a different binary ABI.

All three System Extensions are required **on the distribution tape** but optional **at application link time** (BCEX/BCRG v1). Coroutine Support is neither historical `BLIB` nor a System Extension.

## TA.0–TA.8 acceptance

TA.0–TA.3 architecture, tape tests, producer and installer requirements are unchanged. TA.4 full MR10 independent install, 11+17 demonstrations and all 12 cases with fixed `EXP:`, actual `RP:`, `TEST:`, interpreted `CODE=` and human per-case PASS/FAIL/identified sign-off remain mandatory; preserve the WSL automated runner. TA.5 accepted native runtime, `BLIB`, Coroutine Support and three extensions must restore/link/run and verify their link-time optionality.

**TA.6 is mandatory only if `native_compiler: included`.** When absent, record **not applicable to this candidate**, not a TA.6 PASS or formal march closure. If included, the genuine supplied native compiler must compile itself and the result must be assembled, linked, executed and verified using IFOX/IEWL. TA.7 clean-target acceptance checks MR10-only, native-only and combined profiles on the **declared configuration**, plus actual MVS/JES/IFOX/IEWL/GO and tape evidence. TA.8 may publish an accepted **scoped** release without TA.6 only after immutable artifact, provenance/redistribution, version/VOLSER, release-specific documentation and separate owner publication approval. All release titles and tape-resident documentation must disclose the omitted compiler.

Earlier documents' unconditional native self-compilation language is superseded for the scoped `absent` configuration, not for complete `included` releases. TA.0–TA.8 names/numbering, GitHub source authority, MVS execution authority, read-only `BCPL.BT0001` EBCDIC FB80 bootstrap, `BCPL.BT0002` installer PDS unload, continuous logical `BCPL.BTnnnn` labels, unique non-reusable six-character VOLSER and exact accepted AWS SHA-256 remain unchanged.

**Safety:** Single-dataset round trips do not prove multi-dataset or `RECFM=U` load-library tape correctness. TA.1 remains separately gated. No live MVS modification, tape initialization/write, Git tag or publication is authorized.
