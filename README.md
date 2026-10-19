# BCPL for MVS 3.8J

This repository reconstructs a usable BCPL environment for IBM System/370 under MVS 3.8J. Development uses Hercules and the TK5 distribution, but the compiler and runtime work is aimed at ordinary MVS mechanisms: IFOX assembly, the linkage editor, JCL, data sets, and BCPL's historical bootstrap model.

The primary historical evidence is the Martin Richards BCPL transport-tape material preserved by Ken Yap and Robert Nordier. The project adds an MVS-hosted INTCODE interpreter, host-side build and data-set tools, reconstructed runtime pieces, tests, and demonstrations.

This project appears to be one of the few modern efforts to reconstruct a historical BCPL system for IBM System/370 from surviving compiler and bootstrap materials.

## The two compiler environments

| Directory | Compiler execution | Purpose |
| --- | --- | --- |
| [`bootstrap-toolchain/`](bootstrap-toolchain/) | Interpreter-hosted under `ICINT19` | Runs the demoted Cambridge compiler and CG370 to produce native System/370 code, and holds the established runtime, build inputs and native regression suite. |
| [`cambridge-compiler/`](cambridge-compiler/) | Native MVS executable (the new build target) | Holds the historical Cambridge compiler sources, its own runtime copies and the work to assemble, link, run and eventually self-compile the real compiler on MVS. |

**Important:** The bootstrap toolchain *generates* native code but its
compiler does **not** run natively. The native Cambridge compiler is a
separate deliverable. `tools/bootstrap/` operates the bootstrap toolchain; the MVS
`BOOT_*` dataset aliases are its established interfaces.

## Compatibility scope

The goal is to reconstruct a usable BCPL compiler and runtime for MVS 3.8J from the surviving historical evidence. Success does **not** by itself establish complete compatibility with the original System/370 BCPL implementation.

In particular, even a compiler that successfully compiles itself and passes this project's regression suite is not guaranteed to compile or run every historical BCPL program that worked with the original compiler. Such programs may depend on undocumented or unrecovered runtime conventions, library routines, stream and data-set behavior, host interfaces, implementation-defined semantics, or other properties of the original environment.

The regression suite therefore demonstrates the behavior explicitly tested by the project; it is not a certification of full historical source, binary, or runtime compatibility.

## Reconstruction status (17 October 2026)

The historical MR10 kit compiler runs under reconstructed System/370 ICINT19,
which is built on MVS as `MR10_LOAD(ICINT19)`. The resident demoted Cambridge
compiler image is reconstructed into `BOOT_INTCODE(CAMBCOMP)` and generates
System/370 assembler code; **the compiler itself still runs as INTCODE**.
Applications are assembled, link-edited, and executed natively on MVS.

The complete native panel spanning 00–123 passed with **123 PASS, 0 FAIL,
1 expected SKIP (083)** using rebuilt objects in `BOOT_OBJ` and
`BOOT_DEVOBJ`. This is not a claim of full historical BCPL compatibility.
The separate native Cambridge compiler is developed under
`cambridge-compiler/` using the reserved `CAMB_*` dataset namespace.

**Current native-stream milestone:** BCPLIO dynamic stream
**formally CLOSED** 17 October 2026 with owner acceptance of
the candidate `BOOT_DEVOBJ(BCPLM6+BCPLIO)` under the documented
QSAM stream contract. A fresh `00..145` native regression
at Git `57c7354` returned **145 PASS, zero FAIL,
one expected SKIP 083**, with independent audit
of **145/145 fresh per-case logs**. JES/QSAM physical
evidence is recorded for JOBS 8184–8186.
The accepted DEVOBJ candidate has **not** been promoted
to production `BOOT_OBJ`; the Cambridge compiler still
executes as INTCODE under ICINT19. The earlier
00–123 acceptance above is the M3 *historical* baseline.

Read the [formal BCPLIO milestone sign-off]
(packaging/bcplio-dynamic-stream/Milestone-BCPLIO-dynamic-stream-final-acceptance.md),
[current runtime contract]
(packaging/bcplio-dynamic-stream/BCPLIO-dynamic-runtime-contract.md), and
[handoff for repository cleanup and regression-runner review]
(packaging/maintenance/Handoff-repository-cleanup-regression-runner.md).

**Start here:** [Clean-room reconstruction of the entire MVS PDS
environment](packaging/clean-room-mvs-reconstruction.md). The consolidated
procedure includes source demotion, managed PDS purge/init/population,
ICINT19 rebuilding, the MR10 interpreter suites, resident compiler
reconstruction, runtime objects, and the native regression panel. For
the previously observed acceptance evidence see [M3 reconstruction acceptance](packaging/m3-native-reconstruction-acceptance-20261015.md).

## Repository organization

| Directory | Purpose |
| --- | --- |
| `mr10-kit-compiler/` | ICINT19 assembler, preserved compiler phases, test panels, interpreted demos, and MVS JCL |
| `bootstrap-toolchain/` | Demoted Cambridge source machinery, S/370 runtime ASM, authoritative native build JCL, native regressions |
| `tools/datasets/` | `dspal` manifest-driven MVS PDS access and lifecycle |
| `tools/mr10/` | MR10 interpreter, interpreted compiler, demos, and regression runners |
| `tools/bootstrap/` | Native bootstrap preparation, deployment, compilation, and regression runner |
| `tools/mvs/` | TK5/Hercules, JES and assembler job tools |
| `tools/checks/` | Repository-owned static and acceptance diagnostics |
| `config/` | `dspal.yaml` and ignored machine-local overrides |
| `docs/` | Human-readable educational briefings on BCPL, System/370, MVS, Hercules, IFOX and JCL |
| `packaging/` | Architecture, engineering contracts, acceptance records, audits, and rebuild procedures; [index](packaging/README.md) |
| `richards-bcpltape/` | Historical reference sources; third-party rights preserved |
| `workarea/` | Disposable derived host output, never source authority |

The M3 manifest has 24 managed datasets (9 MR10, 9 reserved CAMB,
6 NATIVE). Source code and JCL are authoritative in Git; resident MVS
datasets are deployed source, rebuildable generated artifacts, and MVS
execution evidence. Do not migrate INTCODE or object modules from earlier
libraries to reconstruct M3.

## Common operator entry points

```sh
tools/mvs/start-tk5 --detached
tools/datasets/dspal status --probe
tools/datasets/dspal info
tools/datasets/dspal ls
tools/mr10/run-regression-panel
tools/mr10/run-demo-suite
tools/mr10/run-language-demos
tools/bootstrap/run-regression
```

These commands assume the environment has already been rebuilt. For a new
system or after `purgebcpl`, **first follow the clean-room reconstruction
runbook**, rather than attempting native tests against missing object modules.

## Provenance and compatibility

The primary historical evidence is Martin Richards' BCPL transport-tape
material preserved by Ken Yap and Robert Nordier. Original
project-developed files are MIT licensed unless otherwise stated; historical
and other third-party materials retain their own licenses. See
[THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md),
[PUBLIC-RELEASE-AUDIT.md](PUBLIC-RELEASE-AUDIT.md), and [LICENSE.md](LICENSE.md).

Passing the current regression panel proves only its explicit tested
contracts; it does not guarantee support for every original compiler,
library, stream, operating-system, or undocumented runtime behavior.

## Historical references

Useful external references include:

- [BCPL History Collection](https://softwarepreservation.computerhistory.org/BCPL/) — historical source, manuals, papers, and implementation notes
- [Martin Richards' BCPL page](https://www.cl.cam.ac.uk/~mr10/BCPL.html) — present-day BCPL distribution and documentation
- [Robert Nordier's Classic BCPL page](https://www.nordier.com/) — `bcplkit` and the curated `bcpltape` archive used as provenance for this repository

## License

Original project work is MIT licensed unless a file says otherwise. Historical BCPL material and other third-party components retain their own copyright and licensing status. See [`LICENSE.md`](LICENSE.md) and [`THIRD-PARTY-NOTICES.md`](THIRD-PARTY-NOTICES.md).