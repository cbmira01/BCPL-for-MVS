# BCPL application discussions

This directory records research, feasibility assessments, and design discussions concerning **applications written in native BCPL** for IBM System/370 under MVS 3.8J.

It is separate from:
- `bootstrap-toolchain/` and `cambridge-compiler/`, which own compiler and bootstrap work;
- `packaging/`, which owns architectural contracts, milestones, acceptance and engineering records;
- `docs/`, which contains general reference and programming guides.

Discussions here are **exploratory**, not acceptance evidence, approved milestones, implementation specifications, or a claim of working MVS software. If an application is later approved for development, its actual source, JCL, test plan and MVS execution evidence must be given explicit ownership and tracked according to the existing project conventions. Existing Core Runtime, Base Library, Standard Library, System Extension, and User/Site Library terminology remains authoritative in [runtime-and-library nomenclature](../packaging/architecture/runtime-and-library-nomenclature.md).

## Discussions

- [LittleD-derived relational database in native BCPL](littled-feasibility-20261103.md) — feasibility, SQL subset, data types, I/O/storage design, virtual storage, TSO/STC options, evidence, and unresolved decisions (3 November 2026).

GitHub `main` remains the authoritative source. No application work is authorized merely by inclusion here.
