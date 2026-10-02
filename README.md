# BCPL reconstruction for IBM MVS 3.8

This project is a reconstruction of a BCPL development environment for IBM MVS 3.8, using the historical BCPL transport tape associated with Martin Richards as its primary source. Development and testing use Hercules and the MVS 3.8J Turnkey/TK5 environment.

The repository contains historical source material, reconstructed System/370 code, compiler and runtime components, tests, JCL, and host-side tools. The long-term deliverable is a native BCPL system that can be installed and used on an existing MVS 3.8 system, ultimately packaged in a form suitable for archival distribution such as virtual tape.

## Current status

The interpreted bootstrap path is working.

The reconstructed System/370 `ICINT` interpreter can execute the preserved BCPL compiler and runtime components. Using `asm/icintv15.asm` and the host-side `tools/compile-and-run` driver, the project has demonstrated:

- BCPL source compiled by the preserved `SYNI` and `TRNI` phases into OCODE;
- OCODE translated by preserved `CGI` into INTCODE;
- generated INTCODE executed under ICINT with `BLIBI` and `ICLIB`;
- saved OCODE and INTCODE intermediate files;
- separate compilation of multiple BCPL source modules; and
- cross-module linkage through the BCPL `GLOBAL` vector.

The Richards factorial example is used as a compact regression workload for both single-module and separate-module compilation. See [`tests/README.md`](tests/README.md).

The native compiler and much of its supporting source survive on the transport tape. A major missing native component is `BCPLMAIN`, which supplied runtime and MVS services. Rather than reconstructing that contract in isolation, the project expects to recover more of it experimentally as native code generation and MVS-resident workloads are developed.

## Near-term direction

Current priorities are:

1. strengthen host-to-MVS data handling, including convenient named-DD input for BCPL programs and compiler phases;
2. exercise ordinary MVS data sets and DASD-resident workflows rather than relying only on in-stream temporary data;
3. reconstruct a System/370 BCPL code generator capable of translating compiler OCODE into native assembler;
4. use that code generator to clarify the runtime services and calling conventions required from the eventual `BCPLMAIN` replacement;
5. bootstrap a native compiler that can compile and maintain itself on MVS; and
6. build a small suite of BCPL example programs that exercise the language and reconstructed runtime in practical ways.

A later milestone will be an annotated "compile the compiler and compare the results" job stream that rebuilds the native compiler from BCPL sources and makes the bootstrap reproducible and inspectable.

## Repository map

- [`richards-bcpltape/README.md`](richards-bcpltape/README.md) — introduction to the historical BCPL transport-tape material and its provenance
- [`asm/README.md`](asm/README.md) — reconstructed System/370 assembler sources, especially ICINT
- [`intcode/README.md`](intcode/README.md) — preserved INTCODE compiler and runtime components
- [`tests/README.md`](tests/README.md) — interpreter, compiler-pipeline, and separate-module regression tests
- [`tools/README.md`](tools/README.md) — host-side build, submission, job-reporting, INTCODE, and BCPL compile/run tools
- [`jcl/README.md`](jcl/README.md) — retained JCL examples and historical development decks
- [`docker/README.md`](docker/README.md) — Hercules/TK5 development environment
- [`docs/README.md`](docs/README.md) — programmer orientation briefings for System/370, MVS 3.8J, Hercules, and the development toolchain

## BCPL documentation online

Useful historical and modern BCPL references include:

- [History of BCPL — Software Preservation Group](https://softwarepreservation.computerhistory.org/BCPL/) — an extensive index of historical BCPL documentation, source code, INTCODE material, and implementations.
- [The BCPL Reference Manual (1967)](https://www.nokia.com/bell-labs/about/dennis-m-ritchie/bcpl.html) — Martin Richards's original Project MAC reference manual, preserved by Dennis Ritchie.
- [The BCPL Programming Manual (1974)](https://softwarepreservation.computerhistory.org/BCPL/cambridge/richards-manual-1974.pdf) — Martin Richards's Cambridge programming manual, close in date to the BCPL system reconstructed here.
- [The BCPL Cintsys and Cintpos User Guide](https://www.cl.cam.ac.uk/~mr10/bcplman.pdf) — Martin Richards's modern BCPL manual and system documentation. Modern BCPL includes extensions not necessarily present in the historical compiler.

The Software Preservation Group's BCPL collection is particularly useful for locating historical documents concerning INTCODE, compiler bootstrapping, runtime conventions, and early BCPL implementations.
