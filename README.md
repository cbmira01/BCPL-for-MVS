# BCPL reconstruction for IBM MVS 3.8

This project is a reconstruction of a BCPL development environment for IBM MVS 3.8, using the historical BCPL transport tape associated with Martin Richards as its primary source. Development and testing use Hercules.

The repository contains historical source material, reconstruction work, tests, and tools. The intended product is a virtual tape that installs BCPL on an existing MVS 3.8 system.

## Status

The native compiler and much of its supporting source survive on the transport tape. A key missing component is `BCPLMAIN`, which provided the native runtime and MVS services. It should be possible to reconstruct a runtime library for the BCPL compiler, from documentation and from client code.

Current work focuses on the tape's `ICINT` interpreter and the preserved compiler bootstrap stages.

## Where to start

- [`richards-bcpltape/README.md`](richards-bcpltape/README.md) — introduction to the historical BCPL transport-tape material and its provenance
- [`richards-bcpltape/INDEX`](richards-bcpltape/INDEX) — detailed map of the surviving files in the historical distribution
- [`docker/README.md`](docker/README.md) — Hercules/TK5 development environment
- [`docs/README.md`](docs/README.md) — programmer orientation briefings for System/370, MVS 3.8J, Hercules, and the development toolchain
- [`tools/README.md`](tools/README.md) — host-side build, submission, job-reporting, and INTCODE tools

## BCPL documentation online

Useful historical and modern BCPL references include:

- [History of BCPL — Software Preservation Group](https://softwarepreservation.computerhistory.org/BCPL/) — an extensive index of historical BCPL documentation, source code, INTCODE material, and implementations.
- [The BCPL Reference Manual (1967)](https://www.nokia.com/bell-labs/about/dennis-m-ritchie/bcpl.html) — Martin Richards's original Project MAC reference manual, preserved by Dennis Ritchie.
- [The BCPL Programming Manual (1974)](https://softwarepreservation.computerhistory.org/BCPL/cambridge/richards-manual-1974.pdf) — Martin Richards's Cambridge programming manual, close in date to the BCPL system reconstructed here.
- [The BCPL Cintsys and Cintpos User Guide](https://www.cl.cam.ac.uk/~mr10/bcplman.pdf) — Martin Richards's modern BCPL manual and system documentation. Modern BCPL includes extensions not necessarily present in the historical compiler.

The Software Preservation Group's BCPL collection is particularly useful
for locating historical documents concerning INTCODE, compiler
bootstrapping, and early BCPL implementations.
