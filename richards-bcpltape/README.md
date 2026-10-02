# Richards BCPL Tape

This directory contains the historical BCPL material that is the primary source for the BCPL-for-MVS reconstruction.

The files originate with a BCPL distribution associated with Martin Richards. This copy is Robert Nordier's reconstruction of the archive made available by Ken Yap: character-mapping problems were corrected and the original `f01` through `f75` names were replaced with meaningful Unix paths where the surviving information allowed it.

Start with [`INDEX`](INDEX). It is the map of the original distribution, showing the historical data-set/member names, their corresponding paths in this tree, and entries for files that did not survive. The index lists 75 original entries; 55 files are present in this recovered collection.

The most important areas for this project include:

| Area | Contents |
| --- | --- |
| [`bcplib/`](bcplib/) | Source for the native BCPL compiler and libraries, including `SYN`, `TRN`, `CG`, `BLIB`, `IOS`, and related build material. These sources are increasingly important as work moves from the interpreted bootstrap toward native System/370 code generation. |
| [`mr10/bcplkit/`](mr10/bcplkit/) | The portable BCPL/INTCODE kit: BCPL sources for `SYN`, `TRN`, `CG`, `BLIB`, and `ICINT`, together with preserved INTCODE compilations such as `SYNI`, `TRNI`, `CGI`, and `BLIBI`. This material supplied the working interpreted bootstrap used by the project. |
| [`mr10/`](mr10/) | Additional BCPL sources, compiler front ends, code generators, documentation, and bootstrap material associated with Martin Richards's files. |
| [`km10/`](km10/) | Supporting BCPL material, macros, coroutine support, tests, and documentation from the preserved distribution. |
| [`sys1/`](sys1/) and [`sys3/`](sys3/) | Material whose original organization corresponded to IBM-style system data sets, including procedures and BCPL headers. These areas are particularly relevant as the reconstruction begins exercising DASD-resident workflows. |
| [`tripos/`](tripos/) | TRIPOS-related documentation and material. |
| [`info/`](info/) | Historical change information and related notes. |

Two provenance files should also be retained with the archive:

- [`README.Nordier`](README.Nordier) explains Robert Nordier's recovery, renaming, and character-mapping work.
- [`README.orig.Yap`](README.orig.Yap) preserves the README distributed with Ken Yap's copy.

## How the archive is being used

Treat this tree primarily as historical evidence. Project-specific translations, extracted INTCODE files, tests, generated intermediates, and reconstructed MVS code belong elsewhere in the repository rather than being folded back into this archive.

The current System/370 translation of ICINT is developed under [`../asm/`](../asm/). Working copies of preserved INTCODE compiler/runtime components are kept under [`../intcode/`](../intcode/), and executable regression workloads are organized under [`../tests/`](../tests/).

The portable `mr10/bcplkit` path has now been demonstrated end-to-end under MVS: reconstructed ICINT hosts `SYNI`/`TRNI`, produces OCODE, `CGI` translates that OCODE to INTCODE, and the generated program runs with `BLIBI` and `ICLIB`. Separate BCPL source modules have also been compiled independently and linked through the common BCPL `GLOBAL` vector.

That successful interpreted path makes the archive useful in a second way: surviving native compiler sources and code-generator material can now be compared against a working behavioral reference while a System/370-native generator and runtime are reconstructed.

## Missing material and reconstruction targets

The archive is incomplete. The `INDEX` explicitly records missing files, including the original native `BCPLMAIN` assembler source and a number of object modules.

`BCPLMAIN` remains an important reconstruction target because it represented native runtime and MVS services, but its contract does not need to be guessed all at once. The project expects to recover more of that interface from surviving compiler/runtime clients, historical build material, experiments with MVS data handling, and especially the requirements exposed by native System/370 code generation.

Preserve the archive as evidence even when a project reconstruction differs from it. The point of this tree is to keep the surviving historical system available for comparison.
