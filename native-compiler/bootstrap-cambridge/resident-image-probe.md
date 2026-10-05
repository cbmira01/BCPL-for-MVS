# Cambridge resident interpreted image probe

## Purpose

All ten Cambridge compiler implementation units have individually crossed the
MR10 bootstrap path to generated INTCODE.  The next boundary is architectural,
not source-language compatibility: prove that those generated modules can be
loaded together under ICINT V19 and rendezvous through one shared global vector.

Do not use JES job numbers as durable project state.  A spool job number is
useful only while examining a particular local run.  Reconstruct progress from
repository artifacts, the command used, and the observed compiler/runtime
state.

## Tool support

`tools/compile-and-run` accepts:

```text
--trni PATH
```

The option selects an alternate MR10 translator image for the compilation
phases without replacing the tracked `intcode/trni.int`.  The normal default is
unchanged.

The bootstrap probe is:

```sh
bash native-compiler/bootstrap-cambridge/probe-resident-image.sh
```

It deterministically regenerates the demoted Cambridge source units.  If local
cleanup removed generated `asm/icintv19.asm` or
`trni-large-names.int`, it recreates them using their committed generators.

The final resident load order is intentional:

```text
BCPL
SYN
LEX
TRNA
TRNB
CGA
CGB
CGC
CGD
CGE
BLIBI
ICLIB
```

`BCPL` is first so the historical master is the image entry.  BLIBI and ICLIB
are appended by `compile-and-run`.

Every Cambridge compile unit is given the bootstrap options plus LIBHDR,
SYNHDR, TRNHDR, and CGHDR.  The large-name MR10 translator is used explicitly
through `--trni`; no tracked compiler phase is swapped or promoted.

## First success criterion

This experiment is not yet required to compile a user BCPL program to native
S/370.  Its first purpose is to establish a coherent resident image.

Inspect the final ICINT result and MAPSTORE.  At minimum, the global rendezvous
should simultaneously contain nonzero addresses for representative entry
points from every layer, including:

```text
G!1    Cambridge master entry
G!150  FORMTREE
G!245  COMPILEAE
G!390  CODEGEN
G!450  CG370
G!520  CGSTIND
G!580  COMPILE
G!622  CGSTART
G!645  WRCARD
G!692  LOCKED
```

The exact addresses are run-dependent and are not durable state.  Presence,
coherence, and absence of loader/global-range failures are what matter.

The historical master may then expose the next host-runtime dependency while it
begins execution.  Such a failure is useful evidence; it should be diagnosed
before adding runtime services or changing compiler semantics.

## V19 status

V19 remains a promotion candidate under review.  This probe does not promote
V19 and does not modify `config/CURRENT`.  Promotion waits for explicit review
and requested changes.
