# BCPL for MVS — current repository map

**Scope:** source and documentation navigation, 17 October 2026.
For project status, see [root README](../README.md); for an ordered
clean-room rebuild, see
[reconstruction runbook](clean-room-mvs-reconstruction.md).

| Repository area | Purpose and source authority |
|---|---|
| [`richards-bcpltape/`](../richards-bcpltape/) | Preserved historical BCPL source; primary evidence, not reconstructed code |
| [`mr10-kit-compiler/`](../mr10-kit-compiler/) | MR10 INTCODE compiler phases, ICINT19, interpreted tests and demos, build JCL |
| [`bootstrap-toolchain/`](../bootstrap-toolchain/) | Cambridge source bootstrap, System/370 runtime assembler and JCL, native regression cases; see [canonical module sources](../bootstrap-toolchain/asm/README.md) |
| [`cambridge-compiler/`](../cambridge-compiler/) | Historical Cambridge BCPL sources and independent runtime for building a compiler that itself executes natively under MVS |
| [`config/dspal.yaml`](../config/dspal.yaml) | Canonical inventory and Git-to-MVS dataset/member mappings |
| [`tools/datasets/`](../tools/datasets/) | Manifest-driven `dspal` dataset management and text deployment |
| [`tools/mr10/`](../tools/mr10/) | Interpreted compiler, demos and test runners |
| [`tools/native/`](../tools/native/) | Demotion/bootstrap, resident compilation and native regression runner |
| [`tools/mvs/`](../tools/mvs/) | JES reader, print reports, TK5/Hercules and assembler job operations |
| [`tools/checks/`](../tools/checks/) | Static validation, evidence checks and focused research probes |
| [`docker/`](../docker/) | Hercules/TK5 container setup; MVS remains the target operating system |
| [`docs/`](../docs/) | Human-readable briefings and programming background only |
| [`packaging/`](./) | Runtime contracts, engineering decisions, historical acceptance, rebuild procedures, audits |
| `workarea/` | Ignored, disposable *generated host output*; preserve valuable evidence in Git before clearing |
| `mvs-state/` | Persistent guest DASD, printers and TK5 state; **never** treat as disposable host scratch |

## Current build path

1. The reconstructed **ICINT19** interpreter is assembler code running
   on MVS; the demoted Cambridge compiler is **INTCODE executed under
   ICINT19**, not an S/370 native load module.
2. `NATIVE_INTCODE(CAMBCOMP)` generates S/370 assembly for native BCPL
   applications. IFOX assembles it, IEWL links it with runtime objects,
   and a GO step executes it under MVS.
3. The current clean-room target rebuilds all five canonical runtime
   assembler modules **plus BLIB** into `NATIVE_OBJ`, and runs all
   146 numbered regression cases using the OBJ-only linker profile.
   This new production configuration is not yet MVS-validated.
4. The previously accepted historical milestone used
   `DEVOBJ(BCPLM6)` and `DEVOBJ(BCPLIO)`. See [the DEVOBJ runtime contract](bcplio-dynamic-stream/BCPLIO-dynamic-runtime-contract.md)
   and [accepted milestone record](bcplio-dynamic-stream/Milestone-BCPLIO-dynamic-stream-final-acceptance.md).
   The final candidate native panel was 145 PASS, 0 FAIL, expected SKIP 083.

## Development and evidence conventions

- Keep historical source intact; explain deviations rather than silently
  modernizing the evidence.
- Develop in small units and inspect actual MVS assembly, link-edit and
  GO results. Host tooling is not a substitute for guest behavior.
- Keep BCPL GLOBAL assignments stable; see
  [runtime and library naming](runtime-and-library-nomenclature.md).
- Commit source, tracked test fixtures and human-readable evidence.
  Rebuild binary object decks, INTCODE images and scratch outputs rather
  than copying them from a prior MVS system.
- For current tool entry points use [root README](../README.md) and
  [clean-room reconstruction](clean-room-mvs-reconstruction.md),
  not pre-M3 root paths such as `asm/`, `intcode/`, `library/`,
  `tests/`, `suite/`, or `jcl/`.
- Protect `config/dspal.local.yaml` credentials and avoid copying
  authenticated generated JCL into tracked documentation.

## Documentation scope

- [`docs/README.md`](../docs/README.md) indexes human-oriented
  System/370, MVS, Hercules, BCPL, JCL and IFOX briefings.
- [`packaging/README.md`](README.md) indexes operational procedures,
  runtime contracts, audits, and accepted engineering evidence.
- The [BCPLIO milestone index](bcplio-dynamic-stream/README.md) separates
  current contract/acceptance from dated historical investigations.
