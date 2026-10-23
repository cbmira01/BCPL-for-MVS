# R.4 — MVS-native BCXSEL / BCXREQ assembler macro probe

**Status:** Test-only source candidate; static source/JCL inspection done;
**IFOX, IEWL, and GO have NOT yet been run for this candidate.**
This is **R.4 — IEWL-Driven Extension Selection**, not a new march.

## Purpose and boundary

Establish whether an *MVS-only* build can use brief assembler statements
inside JCL to select optional packages, produce the existing `BCPLREG`
**BCRG version-1** registration object, and `PUNCH` matching IEWL
`INCLUDE` control statements into the **same** FB80 object deck.
No application-build work depends on WSL, Python, or repository scripts.
The job is submitted to the MVS reader unchanged except for a
site-specific JOB card if security requires one.

The selected extension and required package counts are different:

- `BCXSEL BCPLDEMO`: include and register `BCPLDEMO`; **not** a direct
  application-required package ID.
- `BCXREQ R2TESTB`: include and register `R2TESTB` **and** add it to the
  direct application-required ID list.
- A later `BCXREQ` of an already selected package upgrades it from
  selected-only to selected-and-required without a second INCLUDE or
  descriptor entry.

The prototype **does not infer dependencies**, register packages with
`BCPLRGS` in a real BCPL program, or handle arbitrary unknown
package names. Selection is dependency-first, under the established
BCRG contract. `BCXCAT` maps **only two test names** to their
link-editor DD names and independently relocated BCEX symbols:

| BCX name | Test IEWL DD | Begin/end | Public global |
| --- | --- | --- | --- |
| BCPLDEMO | `PKGA` | `DMOBEG` / `DMOEND` | G!203 (permanent) |
| R2TESTB | `PKGB` | `R2BBEG` / `R2BEND` | G!299 (**test-only**) |

A general User/Site Library would require an **MVS-resident** catalog
entry and corresponding IEWL DD/object member. No central host-side
registry-generation tool is part of this design. The fixture objects
are deliberately minimal BCEX v1 descriptors plus stub dispatchers;
they are **not replacements** for the maintained BCPLDEMO or R2TESTB
implementations.

## Files

- `BCXPRE.asm` — assembler globals, `BCXSEL`, `BCXREQ`, internal
  `BCXADD`, and `BCXEND` macros; emits no CSECT until closure.
- `BCXCAT.asm` — IFOX macro definition for the two known test packages.
- `BCXPOST.asm` — expands `BCXEND` and supplies assembler `END`.
- `r4-bcx-macro-mvs.jcl` — standalone MVS-only executable *candidate*.

The standalone test JCL contains an exact, deliberately embedded copy
of the three `.asm` sources. Its `PREP`, `CATP`, and `POSTP` **MVS
IEBGENER** steps write them to temporary FB80 source datasets. Each
`ASMREG` step reads them as `SYSIN` concatenation with only the
programmer's selections in the middle `DD *`. In a later installed
version these same three sources can be MVS PDS members; that
installation **has not been authorized or performed**.

## MVS execution

Send **only the tracked JCL deck** to JES using the normal MVS job
reader. No JCL generation, Python, or host-side build script is needed.
The checked-in JOB statement deliberately contains no credentials;
use your ordinary site-approved JOB card if required. Do not commit
passwords or an authenticated local deck.

The job executes:

1. `PREP`, `CATP`, `POSTP` — IEBGENER creates three temporary assembler
   source datasets containing the reusable prefix/catalog/postfix.
2. `ASMPA`, `ASMPB` — IFOX assembles two tiny, **test-only** BCEX objects.
3. `ASMOBS` — IFOX assembles one unchanged generic observer.
4. `ASMR0`, `ASMRA`, `ASMRB`, `ASMRS`, `ASMRX` — IFOX assembles five
   selection forms with `OBJECT,DECK` and `SYSPUNCH=&&REG*`.
5. `L0/G0`, `LA/GA`, `LB/GB`, `LS/GS`, `LX/GX` — IEWL links each
   punched control/object deck and executes the unchanged observer.

| Profile | Inline selections | `N` selected | `M` required | Expected GO RC |
| --- | --- | ---: | ---: | ---: |
| 0 | none | 0 | 0 | **0028** |
| A | `BCXREQ BCPLDEMO` | 1 | 1 | **0044** |
| B | `BCXREQ R2TESTB` | 1 | 1 | **0044** |
| S | `BCXSEL BCPLDEMO`; `BCXREQ R2TESTB` | 2 | 1 | **0052** |
| X | preceding two plus `BCXREQ BCPLDEMO` | 2 | 2 | **0060** |

The **GO return codes intentionally equal the BCRG byte length** and
are not errors. The 3 IEBGENER, 3 initial IFOX, 5 registry IFOX and 5
IEWL steps are expected to return **0000**. Link-step COND clauses
refer to their own assemblies, preventing earlier nonzero GO
measurements from bypassing subsequent cases. The generic observer
reads relocated `BCRGBEG`/`BCRGEND` and returns their difference.

In the assembler listings and IEWL MAP/XREF, verify that the selected
objects match the profile, no extension object leaks into the zero
case, the punched `INCLUDE PKGA/PKGB` records precede `BCPLREG` object
records, the descriptor symbol relocations are valid, and BCRG IDs
are exactly in the expected required list. The observer tests length;
**length alone does not prove all header and registration semantics**.
If any stage fails, capture the full assembler diagnostics, IEWL maps,
JES return codes and the exact failing statements. Do not report this
candidate as accepted until MVS evidence has been reviewed.

All datasets are temporary `&&` datasets. No writes to `BOOT_OBJ`,
`BOOT_DEVOBJ`, compiler, `BCPLMAIN`, `BCPLRGS`, or accepted runtime
objects. R.0–R.3 closure remains intact. R.4 remains open.

## Period-correct basis

IBM *OS Assembler Language*, Release 21, GC28-6514-9, documents
assembler macros, global `SET` variables, and `PUNCH` control cards.
PUNCH output before the first CSECT precedes the object module's
records. This is a **historical language rule**, not yet a test result
for our MVS 3.8J TK5 IFOX/IEWL pairing.
