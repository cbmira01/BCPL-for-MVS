# M1.7 — Independent runtime component builds

Status: **Gate A inventory complete; Gate B build jobs staged, not MVS accepted**.

## Gate A — component inventory

| Component | Canonical source | Resident source | Candidate build |
| --- | --- | --- | --- |
| BCPLMAIN | asm/bcplmain.asm | SOURCE(BCPLMAIN) | JCL(BLDDEVN), IFOX00 |
| BCPLMEM | asm/bcplmem.asm | SOURCE(BCPLMEM) | JCL(BLDDEVM), IFOX00 |
| BCPLBYTE | asm/bcplbyte.asm | SOURCE(BCPLBYTE) | JCL(BLDDEVB), IFOX00 |
| BCPLAPT | asm/bcplapt.asm | SOURCE(BCPLAPT) | JCL(BLDDEVA), IFOX00 |
| BLIB | workarea/bootstrap-cambridge/demoted/blib | SOURCE(BLIB) | JCL(BLDDEVL), resident Cambridge/CG370, card-fix, IFOX00 |

Only development `HERC02.BCPL.DEVOBJ` is written by these jobs.
Production `HERC02.BCPL.OBJ` is not a build target.

Contract observations: BCPLMAIN imports BLIB and BCPLMEM services;
BCPLAPT imports STKOVFL from BCPLMAIN; BCPLBYTE publishes GETBYTE
and PUTBYTE. The BLIB build is **not** assembler-only: it uses resident
ICINT19/CAMBCOMP and a strict two-card CG370 repair before IFOX assembly.
BCPLAPT already existed as `asm/bcplapt.asm`; its probe counterpart
`tools/checks/bcplapt-linkage-probe.asm` is not the canonical source.

## Existing active WIP dependency

Source-runtime mode and several source-only combination helpers continue
to use `asm/bcplmain-wip.asm`. In particular,
`tools/checks/prepare-runtime-pds-regression.py` calls legacy
combiners for application/native-library global preparations, then
discards their appended BCPLMAIN source. That is still a **real
toolchain dependency** despite installed-object linkage.

M1.7 Gate D must replace that preparation dependency without changing
application-generated assembler semantics, and isolate or retire
source-mode assembly paths. Do not delete the WIP file prematurely.
Regression 083's FREEMAIN instrumentation remains specialized and
is addressed in Gate E.

## Initial Gate B JCL failure and repair (13 October 2026)

The operator submitted BLDDEVB payload JOB 652 and BLDDEVA payload
JOB 655. Both were rejected as JCL errors before any steps executed.
Review of the committed decks revealed the common defect: the
`PUTCOMP EXEC` statement lacked its required leading `//`.
This is the likely cause; the complete JES messages were not supplied,
so the exact JES diagnostic is not independently confirmed.

Both JCL bodies have been corrected to `//PUTCOMP EXEC` and checked
locally for card length and statement prefixes. Re-stage only these
two corrected JCL members; the already staged assembler SOURCE
members do not require another PUT. No successful install is claimed.

## Acceptance gates

* A: inventory and contracts (documented).
* B: independent DEVOBJ build of each runtime component, zero
  significant assembler diagnostics, and controlled binary installation.
* C: focused link/GO tests against the complete candidate set.
* D: remove normal production/development regression dependence on WIP.
* E: retain meaningful storage-release diagnostic coverage, including 083.
* F: one final DEVOBJ full regression panel; no acceptance without MVS evidence.

## First operator build sequence (Gate B)

The old M1.6 final Gate D evidence has not yet been supplied in this
conversation; do not infer its acceptance from the five passing focused
tests. In M1.7, begin with newly added BCPLBYTE, BCPLAPT and BLIB
builds; BCPLMAIN and BCPLMEM already have separate proven DEVOBJ jobs.

```sh
git pull --ff-only
tools/dspal put SOURCE BCPLBYTE asm/bcplbyte.asm
tools/dspal put SOURCE BCPLAPT asm/bcplapt.asm
tools/dspal put JCL BLDDEVB jcl/build-dev-bcplbyte.jcl
tools/dspal put JCL BLDDEVA jcl/build-dev-bcplapt.jcl
tools/dspal put JCL BLDDEVL jcl/build-dev-blib.jcl
tools/dspal submit JCL BLDDEVB --wait
tools/dspal submit JCL BLDDEVA --wait
tools/dspal submit JCL BLDDEVL --wait
tools/dspal ls DEVOBJ
```

BLIB source is the existing managed `SOURCE(BLIB)` member. Before
BLDDEVL execution, verify its present source is the accepted version
used for the production object; this initial preparation does **not**
automatically repopulate BLIB source. Evaluate all COMP, PREPASM,
PREPLK, FIXASM, ASMBLIB and INSTALL return codes, including card-fix
count assertions. A job-step RC of zero alone is not a semantic
compatibility guarantee. Save assembler and linker evidence.

At the end of the march, run only one authoritative full panel, after
focused validation. The pre-existing regression 083 skip must not
disappear without replacement diagnostic coverage or explicit
acceptance of a separately retained source-only check.
