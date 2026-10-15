# M1.7 — Independent runtime component builds

Status: **ACCEPTED AND CLOSED — 13 October 2026 (Gates A–F)**.

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

## Gate B — corrected component build evidence (13 October 2026)

After the corrected JCL was staged as JOB 656 (BLDDEVB) and JOB 657
(BLDDEVA), authenticated launcher JOB 659 submitted **JOB 660**:
BCPLBYTE ASMCOMP IFOX00 RC=0000, PUTCOMP IEBGENER RC=0000,
zero flagged statements and assembler severity zero. Authenticated
launcher JOB 662 submitted **JOB 663**: BCPLAPT ASMCOMP IFOX00
RC=0000, PUTCOMP IEBGENER RC=0000, zero flagged statements and
assembler severity zero. Both jobs returned highest RC=0000.
Both jobs targeted DEVOBJ only. The previous JCL errors (JOBS 652
and 655) were resolved.

Four modules now have demonstrated individual DEVOBJ builds across
this and preceding marches: BCPLMAIN, BCPLMEM, BCPLBYTE, BCPLAPT.
**BLIB remains outstanding** for Gate B.

## Gate B — BLIB acceptance and complete inventory (13 October 2026)

Operator PUT JCL(BLDDEVL) in JOB 664, launcher JOB 666,
payload **JOB 667**. COMP ICINT19 RC=0000;
PREPASM IFOX00 RC=0000; PREPLK IEWL RC=0000;
FIXASM card-fix RC=0000; ASMBLIB IFOX00 RC=0000;
INSTALL IEBGENER RC=0000. Highest RC=0000,
zero flagged assembler statements, assembler severity zero.
The FIXASM program returns RC=0000 only if both required
CG370 substitutions occur exactly once.

`tools/datasets/dspal ls DEVOBJ` subsequently listed five members:
BCPLAPT, BCPLBYTE, BCPLMAIN, BCPLMEM, BLIB.
**Gate B accepted** for all five independent development builds.
No production OBJ write was requested.

## Gate C — focused independent object regression evidence (13 October 2026)

Operator pulled commit 00eb6cf and ran five individual regressions with
`BCPL_RUNTIME_PDS=1 BCPL_RUNTIME_LIBRARY=DEVOBJ`:

- 04 — string output: PASS 1/1
- 27 — GETVEC: PASS 1/1
- 069 — independent BLIB object: PASS 1/1
- 091 — nested APTOVEC: PASS 1/1
- 123 — automatic FREEBASE publication: PASS 1/1

Each run reported FAIL 0 and SKIP 0. **Gate C accepted.**
No complete 124-case panel was run as part of this gate.

## Gate D — installed-object regression preparation (candidate)

`tools/checks/prepare-runtime-pds-regression.py` now calls pure
application transformations from
`native-compiler/regression/prepare-native-global.py` and
`native-compiler/regression/combine-separate-bcpl.py`, rather than
executing those legacy scripts and discarding an appended
`asm/bcplmain-wip.asm` body. It inserts EXTRN BCPLMAIN and END on
the resulting application section and retains existing assembler card
validation. The legacy source-mode workflow is deliberately unchanged.

This source change is **not yet MVS-verified**. Gate D remains open
until focused installed-object regression cases prove native and
separately compiled BCPL module assembly/link/GO behavior. No full
regression panel at this point.

## Gate D — focused acceptance (13 October 2026)

Operator pulled commit fced635 and ran installed-object DEVOBJ focused
regressions **25** (separately compiled BCPL library) and **26**
(separately assembled native routine through G). Both reported
PASS 1, FAIL 0, SKIP 0, TOTAL 1.

Code audit confirms `run-test.sh` takes the installed-runtime
branch when `BCPL_RUNTIME_PDS=1` and does not execute its subsequent
source-runtime combination branch. In this mode,
`tools/checks/prepare-runtime-pds-regression.py` now prepares
both special application code forms directly, without referring to
`asm/bcplmain-wip.asm`. **Gate D accepted for the normal
installed-object DEVOBJ workflow.** Explicit source-runtime
compatibility and regression 083 remain separate Gate E concerns.
The historical source is retained at this checkpoint.

## Gate E — reclamation diagnostic contract and isolation

**Not equivalent:** production BCPLMEM `MEMSTAT` exposes live allocation
count, peak allocation count, current allocated bytes and peak bytes.
It can establish accounting invariants, but does not count returned
MVS FREEMAIN macro call sites. Regression 083 asserts something
stronger/different: after three GETVECs and one explicit FREEVEC,
FINISH must return from **two** `MEMDRAIN` vector FREEMAIN calls
and **one** BCPLMAIN final combined-storage FREEMAIN call.
Expected records are `42` and `V=2 M=1`. Even this proves
return from the macros, not independent success of MVS deallocation.

The maintained test-only check
`tools/checks/prepare-bcplmem-083-probe.py` instruments a temporary
copy of canonical `asm/bcplmem.asm` with private `MEMDCNT`, and a
corresponding temporary externalized BCPLMAIN copy with `TRM083`.
It does **not** write DEVOBJ or production OBJ. The source-only
regression runner selects this isolated probe using
`BCPL_RUNTIME_PDS=0 BCPLMEM_OBJECT=1`. Its existing generated
combined program still uses the archived WIP source as a **test
fixture**, which is outside the normal DEVOBJ run path accepted in
Gate D. Do not assert complete deletion of every historical WIP
consumer while this deliberate source-only probe remains.

The probe was updated for MEMBIND on 12 October; its regression
README explicitly says the previously accepted JOB 6295 predates
that change. Gate E therefore **requires a new focused MVS probe
run** rather than inferring acceptance from historical execution.
Run:

```sh
BCPL_RUNTIME_PDS=0 BCPLMEM_OBJECT=1 \
  tools/native/run-regression 83 --show-output
```

Accept only an actual PASS with both output records and verified
return-code results. Keep the explicit installed-object 083 exclusion:
`BCPL_RUNTIME_PDS=1` cannot observe internal call-site returns
without a new production diagnostic ABI. Gate F should continue to
expect 123 PASS, 0 FAIL, 1 justified SKIP out of 124. Any future
removal of the WIP fixture requires migration or replacement of
this isolated reclamation test and fresh MVS validation.

**Gate E status:** diagnostic distinction and test scope defined;
MVS revalidation pending.

## Gate E — focused MVS diagnostic acceptance (13 October 2026)

Operator ran `BCPL_RUNTIME_PDS=0 BCPLMEM_OBJECT=1
tools/native/run-regression 83 --show-output`. The runner reported
`PASS 1 / FAIL 0 / SKIP 0 / TOTAL 1` for
`083-instrumented-storage-reclamation`. This accepts the distinct,
test-only reclamation probe after the MEMBIND-compatible update.

The supplied runner summary does not include raw GO output or individual
step return codes; acceptance here is based on the regression harness
PASS, not an independently inspected `V=2 M=1` JES record.
Historical WIP remains an isolated source-only test fixture;
normal DEVOBJ execution does not need it. Gate F remains outstanding.

## Gate F — authoritative DEVOBJ panel (13 October 2026)

The operator pulled commit `8454442` and executed exactly one
complete `BCPL_RUNTIME_PDS=1 BCPL_RUNTIME_LIBRARY=DEVOBJ
tools/native/run-regression` panel covering 00–123 (124 cases).
Results: **123 PASS, 0 FAIL, 1 SKIP, TOTAL 124**.
The sole skip was **083-instrumented-storage-reclamation**
(source-only instrumentation), separately passed under Gate E.
All 123 executable installed-object regressions passed.

**M1.7 ACCEPTED AND CLOSED** — Gates A through F met.
Five independent runtime components have resident, controlled
DEVOBJ build routes and integrated execution evidence. Production
`HERC02.BCPL.OBJ` was not modified. Normal installed-object
regressions no longer depend on the monolithic BCPLMAIN WIP source.
The intentionally isolated source-only diagnostic 083 still relies
on the historical WIP fixture, so **do not delete WIP yet**.
Retirement requires an explicit separate diagnostic-source migration
and subsequent proof. No production promotion is authorized by
this gate.

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
tools/datasets/dspal put SOURCE BCPLBYTE asm/bcplbyte.asm
tools/datasets/dspal put SOURCE BCPLAPT asm/bcplapt.asm
tools/datasets/dspal put JCL BLDDEVB jcl/build-dev-bcplbyte.jcl
tools/datasets/dspal put JCL BLDDEVA jcl/build-dev-bcplapt.jcl
tools/datasets/dspal put JCL BLDDEVL jcl/build-dev-blib.jcl
tools/datasets/dspal submit JCL BLDDEVB --wait
tools/datasets/dspal submit JCL BLDDEVA --wait
tools/datasets/dspal submit JCL BLDDEVL --wait
tools/datasets/dspal ls DEVOBJ
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
