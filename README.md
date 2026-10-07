# BCPL for MVS 3.8J

This repository reconstructs a usable BCPL environment for IBM System/370 under MVS 3.8J. Development uses Hercules and the TK5 distribution, but the compiler and runtime work is aimed at ordinary MVS mechanisms: IFOX assembly, the linkage editor, JCL, data sets, and BCPL's historical bootstrap model.

The primary historical evidence is the Martin Richards BCPL transport-tape material preserved by Ken Yap and Robert Nordier. The project adds an MVS-hosted INTCODE interpreter, host-side build and data-set tools, reconstructed runtime pieces, tests, and demonstrations.

This project appears to be one of the few modern efforts to reconstruct a historical BCPL system for IBM System/370 from surviving compiler and bootstrap materials.

## Compatibility scope

The goal is to reconstruct a usable BCPL compiler and runtime for MVS 3.8J from the surviving historical evidence. Success does **not** by itself establish complete compatibility with the original System/370 BCPL implementation.

In particular, even a compiler that successfully compiles itself and passes this project's regression suite is not guaranteed to compile or run every historical BCPL program that worked with the original compiler. Such programs may depend on undocumented or unrecovered runtime conventions, library routines, stream and data-set behavior, host interfaces, implementation-defined semantics, or other properties of the original environment.

The regression suite therefore demonstrates the behavior explicitly tested by the project; it is not a certification of full historical source, binary, or runtime compatibility.

## Current state

The interpreted bootstrap path works. The promoted interpreter is selected by `config/CURRENT` and currently resolves to `asm/icintv17.asm`.

Using `tools/compile-and-run`, the preserved kit compiler can:

- run `SYNI` and `TRNI` to translate BCPL source to OCODE;
- run `CGI` to translate OCODE to INTCODE;
- execute generated INTCODE under the reconstructed System/370 ICINT;
- compile separate BCPL modules and link them through the `GLOBAL` vector;
- use named MVS input streams;
- exercise reconstructed allocation and coroutine support; and
- preserve OCODE and INTCODE as inspectable intermediate results.

The MVS-side project data-set lifecycle is also reproducible. `dspal` can create, inspect, populate, read, update, compress, and purge the managed `HERC02.BCPL.*` libraries. Git is the source of truth; the MVS libraries are deployed/build state.

The next compiler step is **not** to invent a new System/370 code generator from scratch. A historical System/370 BCPL code generator has been found in the surviving material. Current work is to host, understand, adapt where necessary, and connect that generator to the kit compiler's OCODE stream so it can emit assembler for the MVS toolchain. Native runtime services, including the surviving `BCPLMAIN` contract, still require reconstruction.

See [`native-compiler/README.md`](native-compiler/README.md) for that work.

## What is in this repository

Three kinds of material are deliberately kept together:

**Historical material.** `richards-bcpltape/` is preserved third-party source and documentation. Several files in `intcode/` are byte-for-byte working copies of compiler/runtime files from that archive. These files are not relicensed by this project.

**Reconstruction work.** The System/370 ICINT sources in `asm/`, host tools in `tools/`, project runtime modules in `library/`, tests, most demonstrations, Docker integration, and project documentation are reconstruction or support work developed for this repository.

**Experimental work.** Native code generation, the eventual native MVS runtime, parts of the BCPL library, and some compiler/runtime probes are still under active reconstruction. Passing a probe establishes the behavior tested by that probe; it does not imply that the native compiler is finished.

For detailed provenance and licensing boundaries, read [`THIRD-PARTY-NOTICES.md`](THIRD-PARTY-NOTICES.md). The public-release review is recorded in [`PUBLIC-RELEASE-AUDIT.md`](PUBLIC-RELEASE-AUDIT.md).

## Quick start for the current interpreted system

Start the local TK5/Hercules system, then create and populate the managed MVS libraries:

```sh
tools/start-tk5 --detached
tools/dspal initbcpl
tools/dspal populate all
```

Run a BCPL program through the preserved compiler phases and ICINT:

```sh
tools/compile-and-run --results \
    "$(tools/current-icint)" \
    suite/richards-factorial/richards-factorial.bcpl
```

Run the durable regression panel:

```sh
tools/run-regression-panel
```

Run the demonstration suite:

```sh
tools/run-demo-suite.sh
```

## Repository guide

- [`asm/README.md`](asm/README.md) — reconstructed System/370 ICINT and assembler work
- [`intcode/README.md`](intcode/README.md) — preserved kit compiler/runtime INTCODE and project additions
- [`native-compiler/README.md`](native-compiler/README.md) — kit compiler and native System/370 code-generation work
- [`library/README.md`](library/README.md) — portable BCPL runtime/library modules
- [`tests/README.md`](tests/README.md) — regression cases and reconstruction probes
- [`suite/README.md`](suite/README.md) — readable BCPL demonstrations
- [`tools/README.md`](tools/README.md) — host-side build, JES, compiler, regression, and `dspal` tools
- [`config/README.md`](config/README.md) — checked-in configuration and local overrides
- [`docker/README.md`](docker/README.md) — Hercules/TK5 container environment
- [`docs/README.md`](docs/README.md) — System/370, MVS, IFOX, JCL, and BCPL orientation notes
- [`richards-bcpltape/README.md`](richards-bcpltape/README.md) — historical tape provenance and contents

[`docs/project-map.md`](docs/project-map.md) gives a broader contributor-oriented map of the repository.

## Historical references

Useful external references include:

- [BCPL History Collection](https://softwarepreservation.computerhistory.org/BCPL/) — historical source, manuals, papers, and implementation notes
- [Martin Richards' BCPL page](https://www.cl.cam.ac.uk/~mr10/BCPL.html) — present-day BCPL distribution and documentation
- [Robert Nordier's Classic BCPL page](https://www.nordier.com/) — `bcplkit` and the curated `bcpltape` archive used as provenance for this repository

## License

Original project work is MIT licensed unless a file says otherwise. Historical BCPL material and other third-party components retain their own copyright and licensing status. See [`LICENSE.md`](LICENSE.md) and [`THIRD-PARTY-NOTICES.md`](THIRD-PARTY-NOTICES.md).