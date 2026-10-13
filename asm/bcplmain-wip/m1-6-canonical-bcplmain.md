# M1.6 — Canonical, independently assemblable BCPLMAIN

Status: **candidate staged, awaiting checks and MVS evidence**.

## Objective and non-goals

Make `asm/bcplmain.asm` the authoritative, production-compatible
assembler text of independently linked BCPLMAIN, rather than a
generated `workarea/runtime-object-candidates/bcplmain-pds.asm`.
No runtime behavior change, no BLIB/BCPLMEM modification, and no
production OBJ installation are authorized in this march.

The historical monolithic `asm/bcplmain-wip.asm` remains intact
as an input to existing source-only regressions. It is **not** the
canonical independently linked runtime source. It may be retired or
further refactored in a separately scoped effort.

The canonical module includes the already accepted transformations:
external BCPLMEM entry points and MEMBIND/MEMDRAIN lifecycle calls;
BLIB exported-global registration; and the external STKOVFL entry
needed by independent BCPLAPT. No repeated build-time rewriting is
required for normal BCPLMAIN assembly.

`config/dspal.yaml` now maps `SOURCE(BCPLMAIN)` to
`asm/bcplmain.asm`. Development job `JCL(BLDDEVN)` assembles that
member with IFOX00 and installs its FB80 relocatable object into
`DEVOBJ(BCPLMAIN)` through IEBGENER, only after assembly RC=0.

## Gates

* **A — Source equivalence.** Run the automated exact comparison of
  canonical BCPLMAIN against the established externalization, BLIB
  registration and STKOVFL-export staging recipe. This is a strict
  byte-for-byte comparison of assembler text, not binary-object
  equivalence or proof of execution.
* **B — MVS assembly and candidate installation.** PUT canonical text
  into SOURCE(BCPLMAIN), submit authenticated JCL(BLDDEVN), inspect
  ASMMMAIN IFOX00 RC, flagged statements and highest severity, and
  PUTMAIN IEBGENER RC. Confirm DEVOBJ inventory. Never write OBJ.
* **C — Focused independent linkage and execution.** Run selected
  native DEVOBJ regressions exercising startup, BLIB, BCPLAPT,
  BCPLMEM and stack high-water. Require expected GO behavior and
  no linkage failures.
* **D — One full authoritative panel.** Once candidate validation is
  complete, run the full 00–123 DEVOBJ panel **once**, expecting
  123 PASS, 0 FAIL, 1 expected source-only SKIP (083). Close only
  after actual operator evidence is received.

## Operator sequence for Gates A and B

```sh
git pull --ff-only
python3 tools/checks/check-bcplmain-canonical.py
tools/dspal put SOURCE BCPLMAIN asm/bcplmain.asm
tools/dspal put JCL BLDDEVN jcl/build-dev-bcplmain.jcl
tools/dspal submit JCL BLDDEVN --wait
tools/dspal ls DEVOBJ
```

Require source-equivalence PASS **before** the PUT steps.
The job is authenticated through dspal, not the bare card reader.
Do not claim Gate B based solely on a summary if assembler listing
contains nonzero severity or flagged cards.

Possible focused Gate C tests (do not run the full panel prematurely):

```sh
BCPL_RUNTIME_PDS=1 BCPL_RUNTIME_LIBRARY=DEVOBJ \
  tools/run-native-regression 00 --show-output
BCPL_RUNTIME_PDS=1 BCPL_RUNTIME_LIBRARY=DEVOBJ \
  tools/run-native-regression 69 --show-output
BCPL_RUNTIME_PDS=1 BCPL_RUNTIME_LIBRARY=DEVOBJ \
  tools/run-native-regression 91 --show-output
BCPL_RUNTIME_PDS=1 BCPL_RUNTIME_LIBRARY=DEVOBJ \
  tools/run-native-regression 120 --show-output
BCPL_RUNTIME_PDS=1 BCPL_RUNTIME_LIBRARY=DEVOBJ \
  tools/run-native-regression 123 --show-output
```

The development object library was seeded from the Gate F1
accepted production library and its independently assembled BCPLMEM
already passed the complete 123/0/1 panel in the preceding march.

Production `HERC02.BCPL.OBJ` remains an accepted immutable baseline;
promotion is a separate future march, not an implicit step of M1.6.
