# Richards BCPL Tape

This directory contains the historical BCPL material that is the primary
source for the BCPL-for-MVS reconstruction.

The files originate with a BCPL distribution associated with Martin
Richards. This copy is Robert Nordier's reconstruction of the archive
made available by Ken Yap: character-mapping problems were corrected and
the original `f01` through `f75` names were replaced with meaningful
Unix paths where the surviving information allowed it.

Start with [`INDEX`](INDEX). It is the map of the original distribution,
showing the historical data-set/member names, their corresponding paths
in this tree, and entries for files that did not survive. The index lists
75 original entries; 55 files are present in this recovered collection.

The most important areas for this project include:

| Area | Contents |
| --- | --- |
| [`bcplib/`](bcplib/) | Source for the native BCPL compiler and libraries, including `SYN`, `TRN`, `CG`, `BLIB`, `IOS`, and related build material. |
| [`mr10/bcplkit/`](mr10/bcplkit/) | The portable BCPL/INTCODE kit: BCPL sources for `SYN`, `TRN`, `CG`, `BLIB`, and `ICINT`, together with preserved INTCODE compilations such as `SYNI`, `TRNI`, `CGI`, and `BLIBI`. This material is central to the current bootstrap work. |
| [`mr10/`](mr10/) | Additional BCPL sources, compiler front ends, code generators, documentation, and bootstrap material associated with Martin Richards's files. |
| [`km10/`](km10/) | Supporting BCPL material, macros, coroutine support, tests, and documentation from the preserved distribution. |
| [`sys1/`](sys1/) and [`sys3/`](sys3/) | Material whose original organization corresponded to IBM-style system data sets, including procedures and BCPL headers. |
| [`tripos/`](tripos/) | TRIPOS-related documentation and material. |
| [`info/`](info/) | Historical change information and related notes. |

Two provenance files should also be retained with the archive:

- [`README.Nordier`](README.Nordier) explains Robert Nordier's recovery,
  renaming, and character-mapping work.
- [`README.orig.Yap`](README.orig.Yap) preserves the README distributed
  with Ken Yap's copy.

## Preservation and project use

Treat this tree primarily as historical evidence. Project-specific
translations, extracted INTCODE files, tests, and reconstructed MVS code
belong elsewhere in the repository rather than being folded back into
this archive.

In particular, the current System/370 translation of ICINT is developed
under [`../asm/`](../asm/), while working copies of preserved INTCODE
components are kept under [`../intcode/`](../intcode/).

The archive is incomplete: the `INDEX` explicitly records missing files,
including the original native `BCPLMAIN` assembler source and a number of
object modules. Recovering the behavior represented by those missing
pieces is one of the purposes of this reconstruction project.
