# System/370 assembler sources

This directory contains native MVS 3.8J assembler and runtime development sources. ICINT interpreter sources have moved to `mr10-kit-compiler/asm/` during M3 restructuring.

## Relocated ICINT line (historical notes)

The current promoted interpreter is selected by `mr10-kit-compiler/asm/CURRENT`; `tools/mr10/current-icint` resolves that selection for scripts and users. At the time of this README the promoted source is `mr10-kit-compiler/asm/icintv17.asm`.

The numbered ICINT files are retained because each is a useful reconstruction milestone rather than an arbitrary backup:

- V12 established the main historical instruction model and basic execution path;
- V13 added map/store work used by later diagnostics;
- V14/V14-trace developed tracing and reporting;
- V15 expanded hosted stream support;
- V16 moved generic streams to dynamic MVS-managed storage and established character translation behavior;
- V17 is the current baseline, retaining the V16 stream work while adding recent-instruction diagnostics and guarded store handling.

The interpreter is based closely on `richards-bcpltape/mr10/bcplkit/icint`. The reconstruction rule is to stay close to that historical implementation and depart only where MVS hosting, diagnostics, or demonstrated correctness requires it.

## Building

For direct assembler work, generate a self-contained IFOX job with:

```sh
tools/mvs/make-asm-job asm/program.asm --output-dir jcl --listing heavy
```

For ICINT workloads, use `tools/mr10/run-intcode` or `tools/mr10/compile-and-run`; they generate the necessary assembly/link/run jobs automatically.

`hello-world.asm` is a small IFOX example retained as a toolchain sanity check.

## Native direction

ICINT is the bootstrap host, not the end product. The native compiler work now starts from a surviving historical System/370 BCPL code generator. The assembler work ahead is therefore centered on validating generated S/370 code and reconstructing the native runtime/MVS service layer, not on inventing a backend without historical reference.

The **accepted M2.0 Gate D development candidate** is `asm/bcplmain-d6-candidate.asm`, installed as `HERC02.BCPL.DEVOBJ(BCPLM6)`. Its independently assembled partners are `asm/bcplio.asm` (BCPLIO), `asm/bcplapt.asm` (BCPLAPT), `asm/bcplbyte.asm` (BCPLBYTE), `asm/bcplmem.asm` (BCPLMEM), plus the BLIB object. `asm/bcplmain.asm` is a separately maintained canonical/pre-D6 source, **not** the accepted D6 candidate; `bcplmain-wip.asm` retains historical WIP context. Do not substitute either into a D6 validation build.

For the module contracts, independently linked objects and acceptance evidence, start at [`packaging/m2-0-runtime-modularity-architecture.md`](../packaging/m2-0-runtime-modularity-architecture.md), [`packaging/m2-0-gate-e-maintainability-review.md`](../packaging/m2-0-gate-e-maintainability-review.md), and the Gate D extraction record. The validated D6 build uses `jcl/build-dev-bcplmain-d6.jcl` and `jcl/bcplio-d6-integration-link.jcl`. Native PDS regressions require explicit `BCPL_RUNTIME_LIBRARY=DEVOBJ BCPL_RUNTIME_CANDIDATE=1 BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6` with `BCPL_RUNTIME_PDS=1`. These jobs do not promote `HERC02.BCPL.OBJ`.\n\nSee `native-compiler/README.md` for the current compiler direction and `THIRD-PARTY-NOTICES.md` for historical provenance.