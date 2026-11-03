# BCPL application discussions

This directory preserves **exploratory discussions** about possible applications written in native BCPL for IBM System/370 under MVS 3.8J. The BCPL for MVS 3.8 Reconstruction project is **not undertaking application delivery**; these notes are retained as reference material only.

These records sit under `packaging/` because they document discussion and research, **not** an application source tree. Compiler work remains in `bootstrap-toolchain/` and `cambridge-compiler/`; general programming guides remain in `docs/`.

Discussions here are **exploratory**, not acceptance evidence, approved milestones, implementation specifications, or a claim of working MVS software. If an application is later approved for development, its actual source, JCL, test plan and MVS execution evidence must be given explicit ownership and tracked according to the existing project conventions. Existing Core Runtime, Base Library, Standard Library, System Extension, and User/Site Library terminology remains authoritative in [runtime-and-library nomenclature](../architecture/runtime-and-library-nomenclature.md).

## Discussions

- [LittleD-derived relational database in native BCPL](littled-feasibility-20261103.md) — feasibility, SQL subset, data types, I/O/storage design, virtual storage, TSO/STC options, evidence, and unresolved decisions (3 November 2026).

GitHub `main` remains the authoritative source. No application work is authorized merely by inclusion here.
