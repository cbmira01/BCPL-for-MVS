# BCPL for MVS 3.8J

This repository reconstructs a usable BCPL environment for IBM System/370 under MVS 3.8J. Development uses Hercules and the TK5 distribution, but the compiler and runtime work is aimed at ordinary MVS mechanisms: IFOX assembly, the linkage editor, JCL, data sets, and BCPL's historical bootstrap model.

The primary historical evidence is the Martin Richards BCPL transport-tape material preserved by Ken Yap and Robert Nordier. The project adds an MVS-hosted INTCODE interpreter, host-side build and data-set tools, reconstructed runtime pieces, tests, and demonstrations.

This project appears to be one of the few modern efforts to reconstruct a historical BCPL system for IBM System/370 from surviving compiler and bootstrap materials.

## Public release and compiler environments

The first public prerelease, [Cambridge BCPL Programming System for MVS 3.8J — 0.1.0-rc4](https://github.com/cbmira01/BCPL-for-MVS/releases/tag/v0.1.0-rc4), was published on 24 November 2026. Start with the [RC4 companion installation and usage guide](packaging/distribution/publication/RC4-README.md). It supersedes the draft documentation in BT0003.

| Environment | Status and purpose |
| --- | --- |
| [MR10 Kit Compiler](mr10-kit-compiler/) | Independently usable on MVS through ICINT19; included and functionally verified in RC4. |
| [Bootstrap toolchain](bootstrap-toolchain/) | Development toolchain: interpreter-hosted demoted Cambridge Compiler and CG370 generate native System/370 applications. The compiler itself runs as INTCODE. CAMBCOMP is not included in RC4. |
| [Cambridge Compiler](cambridge-compiler/) | Native-running MVS compiler reconstruction is unfinished. Historical Cambridge sources, native runtime, libraries and System Extensions are distributed in RC4 as work in progress. |

All three installation profiles passed on actual MVS 3.8J in fresh namespaces on the existing system. MR10 and COMBINED passed 80 functional cases in total. Independent IPL, alternate HLQ/site verification and native functional certification were not established.

The [Tape artifact release closure](packaging/milestones/tape-artifact-release/ta8-formal-qualified-closure-and-milestone-completion-20261124.md) records scope and qualifications. TA.5 is closed (qualified); TA.6 is N/A for RC4. Historical redistribution rights remain unresolved under the preservation-first policy. See [third-party notices](THIRD-PARTY-NOTICES.md).

## Compatibility scope

The goal is to reconstruct a usable BCPL compiler and runtime for MVS 3.8J from the surviving historical evidence. Success does **not** by itself establish complete compatibility with the original System/370 BCPL implementation.

In particular, even a compiler that successfully compiles itself and passes this project's regression suite is not guaranteed to compile or run every historical BCPL program that worked with the original compiler. Such programs may depend on undocumented or unrecovered runtime conventions, library routines, stream and data-set behavior, host interfaces, implementation-defined semantics, or other properties of the original environment.

The regression suite therefore demonstrates the behavior explicitly tested by the project; it is not a certification of full historical source, binary, or runtime compatibility.

## Development and reconstruction

The established development bootstrap runs under ICINT19 and generates native code using the demoted Cambridge Compiler. This is not a native-running compiler.

For reconstruction from source, follow the [canonical clean-room runbook](docs/Rebuild-BCPL-for-MVS-from-source.md). For current architecture and accepted interfaces, see [architecture and contracts](packaging/architecture/README.md); for milestone status, see the [milestone index](packaging/milestones/README.md). Historical native development results remain in the accepted milestone records and [earlier README](https://github.com/cbmira01/BCPL-for-MVS/blob/9f382203fcd6a5424cd916f304e3210c0f650212/README.md); they are not RC4 functional certification.

## Repository organization

| Directory | Purpose |
| --- | --- |
| `mr10-kit-compiler/` | ICINT19 assembler, preserved compiler phases, test panels, interpreted demos, and MVS JCL |
| `bootstrap-toolchain/` | Demoted Cambridge source machinery, S/370 runtime ASM, authoritative native build JCL, native regressions |
| `system-extensions/` | Optional System/370 and MVS services and shared extension selection assets; Git-backed source/headers |
| `standard-library/` | Proposed BCPL Standard Library (BSL); design-only placeholder, no modules implemented |
| `tools/datasets/` | `dspal` manifest-driven MVS PDS access and lifecycle |
| `tools/mr10/` | MR10 interpreter, interpreted compiler, demos, and regression runners |
| `tools/bootstrap/` | Native bootstrap preparation, deployment, compilation, and regression runner |
| `tools/mvs/` | TK5/Hercules, JES and assembler job tools |
| `tools/checks/` | Repository-owned static and acceptance diagnostics |
| `tools/distribution/` | Release manifest and evidence inspection tools |
| `tools/reconstruction/` | Clean-room reconstruction tooling |
| `config/` | `dspal.yaml` and ignored machine-local overrides |
| `docs/` | Human-readable educational briefings on BCPL, System/370, MVS, Hercules, IFOX and JCL |
| `packaging/` | Architecture, engineering contracts, acceptance records, audits, and rebuild procedures; [index](packaging/README.md) |
| `richards-bcpltape/` | Historical reference sources; third-party rights preserved |
| `workarea/` | Derived host output; preserve accepted private release receipts and no-retry markers separately before any cleanup |

The managed development dataset inventory is defined by [config/dspal.yaml](config/dspal.yaml). Git is authoritative for source and JCL; MVS establishes target execution evidence. Release selection and installed namespaces are defined separately by the [distribution manifest](packaging/distribution/manifest/README.md).

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

For the initial Docker Compose build, TK5 startup/shutdown, logs, image
updates and persistent-state precautions, see the
[Hercules/TK5 Docker Compose operations guide](docker/README.md).

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
