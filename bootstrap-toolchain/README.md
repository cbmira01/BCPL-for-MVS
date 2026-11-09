# Bootstrap Toolchain — current source and build paths

This area contains the **interpreter-hosted demoted Cambridge compiler**
and the reconstructed System/370 Core Runtime and Base Library build sources.
The demoted compiler runs as INTCODE under `ICINT19` and generates native
System/370 assembler; the separately planned native-running compiler belongs
in [`cambridge-compiler/`](../cambridge-compiler/).

## Current owned directories

| Directory | Active responsibility |
| --- | --- |
| [`bootstrap-cambridge/`](bootstrap-cambridge/README.md) | Demotion generators, compiler inputs, options and reproducible bootstrap instructions |
| [`asm/`](asm/README.md) | Canonical Core Runtime assembler sources; historical material remains explicitly identified |
| [`jcl/`](jcl/README.md) | Canonical MVS build and installation job bodies |
| [`regression/`](regression/README.md) | Shared native regression runner and its implementation helpers; numbered cases live in `tests/` |
| [`library/`](library/README.md) | Staged, unpromoted native BCPL utility candidates |
| [`probes/`](probes/README.md) | Active and dependency-retained test fixtures; completed probe research is archived under `packaging/archive/` |

The authoritative [clean-room rebuild](../docs/Rebuild-BCPL-for-MVS-from-source.md)
and [repository map](../packaging/operations/repository-map.md) define current
usage. Bootstrap host-side tools live in [`tools/bootstrap/`](../tools/bootstrap/README.md).
No historical probe or archived note authorizes JES submission or resident
MVS dataset changes.

## Documentation boundaries

- [CG370 architecture discussion](../packaging/architecture/cg370-architecture-notes.md)
- [MR10 versus Cambridge runtime interfaces](../packaging/architecture/runtime-interface-conventions-and-contracts.md)
- [Early kit-compiler strategy](../packaging/archive/bootstrap/kit-compiler-strategy.md)
- [Historical BLIB object-library investigation](../packaging/archive/bootstrap/object-library/README.md)
- [Historical core-runtime investigations](../packaging/archive/core-runtime/README.md)
- [Historical bootstrap-source discussion](../packaging/archive/bootstrap/bootstrap-toolchain-legacy-readme.md)

GitHub `main` remains authoritative for source and documentation; MVS
execution and JES evidence are authoritative for target behavior.
