

# BCPL reconstruction for IBM MVS 3.8 

This project is a reconstruction of a BCPL development environment for IBM MVS 3.8, using the historical BCPL transport tape associated with Martin Richards as its primary source. Development and testing use Hercules.

The repository contains historical source material, reconstruction work, tests, and tools. The intended product is a virtual tape that installs BCPL on an existing MVS 3.8 system.

## Status

The native compiler and much of its supporting source survive on the transport tape. A key missing component is `BCPLMAIN`, which provided the native runtime and MVS services. It should be possible to reconstruct a runtime library for the BCPL compiler, from documentation and from client code.

Current work focuses on the tape’s `ICINT` interpreter and the preserved compiler bootstrap stages.

## Where to start

- [`richards-bcpltape/INDEX`](richards-bcpltape/INDEX) — historical source inventory
- [`docker/README.md`](docker/README.md) — development environment

## Links to BCPL documentaiton online

- TODO
