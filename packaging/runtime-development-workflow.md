# Unified MVS runtime development — candidate object march

Status: **staged, awaiting operator MVS evidence** (13 October 2026).

Gate F1 production baseline remains accepted and untouched: HERC02.BCPL.OBJ
contains BCPLMAIN, BCPLMEM, BCPLBYTE, BCPLAPT and BLIB. Gate F1's installed
panel was 123 PASS, 0 FAIL, 1 expected SKIP (083).

## Library ownership

* Git-tracked assembler is authoritative source. HERC02.BCPL.SOURCE stores
  the synchronized FB80 assembler texts; it is not the Git authority.
* HERC02.BCPL.OBJ is the **accepted production** binary FB80 object PDS.
  The development jobs in this march do not write it.
* HERC02.BCPL.DEVOBJ is a separately allocated **candidate** binary FB80
  object PDS, initially copied as a complete five-member set from production.
  Never use `dspal put` on OBJ or DEVOBJ: it converts text encodings.
* HERC02.BCPL.JCL is the resident job-body library; `dspal submit` supplies
  an authenticated HERC02 job card using the ignored local private config.

Do not implicitly fallback from DEVOBJ to production OBJ. A candidate run
must explicitly use the five DEVOBJ members; if any are missing, linkage
must fail. Re-seeding is a deliberate destructive candidate reset, not an
automatic response to a missing member.

## Initial operator sequence (once)

Update the local checkout, then inspect the intended dataset and member
inventories:

```sh
git pull --ff-only
tools/datasets/dspal stat OBJ
tools/datasets/dspal stat DEVOBJ
tools/datasets/dspal ls OBJ
tools/datasets/dspal ls DEVOBJ
```

Use `tools/datasets/dspal initbcpl` only after reviewing its allocation preflight.
The newly registered DEVOBJ is a PO/FB/LRECL=80/BLKSIZE=800 library.
**Do not submit SEEDDEV unless DEVOBJ exists and is empty.** Review the
effective allocation report and ensure no other managed dataset is at risk.
Confirm production OBJ has all five accepted members.

Install the two new job bodies, *as text*:

```sh
tools/datasets/dspal put JCL SEEDDEV jcl/seed-devobj.jcl
tools/datasets/dspal put JCL BLDDEVM jcl/build-dev-bcplmem.jcl
```

Seed the empty candidate library with one MVS-native binary IEBCOPY:

```sh
tools/datasets/dspal submit JCL SEEDDEV --wait
tools/datasets/dspal ls DEVOBJ
```

Require IEBCOPY RC=0000 and exactly the five expected object members.
The seeding job does **not** assemble any source and does not alter OBJ.
Save the payload JES report and the five-member inventory as evidence.

## Initial allocation and seed evidence — accepted (13 October 2026)

Operator evidence: `dspal initbcpl` preflight JOBs 354–365;
allocation JOB 366 created `HERC02.BCPL.DEVOBJ`, with all prior
datasets reported existing and compatible. JOB 367 verified volume
TSO002, DSORG=PO, RECFM=FB, LRECL=80, BLKSIZE=800, with an empty
member directory.

The operator staged `JCL(SEEDDEV)` in JOB 369. Authenticated launcher
JOB 371 submitted payload JOB 372, whose COPYOBJ IEBCOPY step completed
RC=0000 (highest RC=0000). Subsequent `dspal ls` inventories showed
the same five member names in DEVOBJ and production OBJ: BCPLAPT,
BCPLBYTE, BCPLMAIN, BCPLMEM, BLIB. This establishes successful
initial binary seeding and member inventory; bytewise equality has not
been independently checked. No candidate reassembly or regression
execution is yet accepted.

## Focused component development and verification

An individual BCPLMEM candidate build is:

```sh
tools/datasets/dspal put SOURCE BCPLMEM asm/bcplmem.asm
tools/datasets/dspal submit JCL BLDDEVM --wait
tools/datasets/dspal ls DEVOBJ
```

Inspect the payload JES listing. Require IFOX ASMMEM RC=0000, highest
assembler severity 0 and no flagged statements, followed by IEBGENER
PUTMEM RC=0000. The JCL condition protects installation on nonzero
assembler return code, **not** against zero-RC assembler warning text;
review diagnostics before accepting the candidate.

Test explicitly against candidates, not production:

```sh
BCPL_RUNTIME_PDS=1 BCPL_RUNTIME_LIBRARY=DEVOBJ \
  tools/native/run-regression 27 --show-output
```

The regression generator validates that the logical library is a managed
binary FB80 PDS and generates explicit `INCLUDE OBJ(...)` statements
against the chosen DD dataset. It accepts only `OBJ` or `DEVOBJ`.
`BCPL_RUNTIME_LIBRARY` defaults to `OBJ`, preserving production mode.
The command above is a **focused** test only, not a march acceptance panel.
Job-link reports should confirm member resolution from DEVOBJ.

## Independent BCPLMEM candidate build — accepted (13 October 2026)

Operator synchronized `JCL(BLDDEVM)` in JOB 375 and canonical
`SOURCE(BCPLMEM)` from `asm/bcplmem.asm` in JOB 376.
Authenticated launcher JOB 378 submitted payload JOB 379.
JOB 379 completed: ASMMEM (IFOX00) RC=0000 and PUTMEM
(IEBGENER) RC=0000; highest job RC=0000, zero flagged
assembler statements, and highest assembler severity zero.

This accepts independent source synchronization, MVS assembly and
binary-safe candidate installation to DEVOBJ(BCPLMEM). Runtime linkage
and execution remain to be verified; no full regression has run in
this march.

## Focused DEVOBJ execution — accepted (13 October 2026)

After pulling commit d3c5947, operator invoked
`BCPL_RUNTIME_PDS=1 BCPL_RUNTIME_LIBRARY=DEVOBJ` on native
regression 27 (`27-getvec`) and regression 122
(`122-freebase-vector-list-experiment`), each with
`--show-output`. Both individually completed PASS 1, FAIL 0,
SKIP 0, TOTAL 1. This validates the selected candidate-linkage
path and successful application behavior for these tests; these
console summaries do not independently document the complete
IEWL map or prove object-byte identity with production.

The one full DEVOBJ panel is now the remaining acceptance step.
Do not run a second full source-mode or production-object panel.

## One authoritative full panel at march conclusion

After assembly, installation, source synchronization, linkage, and focused
execution have been demonstrated, run the full panel **once**:

```sh
BCPL_RUNTIME_PDS=1 BCPL_RUNTIME_LIBRARY=DEVOBJ \
  tools/native/run-regression
```

Expected baseline is 123 PASS / 0 FAIL / 1 expected SKIP (083).
No acceptance is claimed until actual operator JES results support it.
Regression 083 retains its source-only FREEMAIN instrumentation and is
not reclassified.

## Failure, promotion, rollback

A failed build or link must not trigger a production OBJ update. Freeze
candidate changes, inspect the corresponding JES report, and repair
the isolated DEVOBJ candidate. IEBCOPY seeding is intended only for an
empty DEVOBJ: to reset an existing candidate library, first plan a
controlled deletion/reallocation or explicit safe member replacement.
IEBGENER installation to an existing DEVOBJ member is not atomic.

Production promotion remains a **separate explicitly authorized operation**
after acceptance. There is no automatic promotion or binary backup claim;
exact incumbent object rollback is not guaranteed without saved artifacts.
Preserve Git commit, source hashes, MVS job numbers, assembler severity,
IEBCOPY/IEBGENER return codes, link-editor report, and regression totals.

## March acceptance — CLOSED (13 October 2026)

The operator ran the sole full panel for this development march with
`BCPL_RUNTIME_PDS=1 BCPL_RUNTIME_LIBRARY=DEVOBJ tools/native/run-regression`
after pulling commit 6529fcb. All numbered cases 00–123 were evaluated:
**123 PASS, 0 FAIL, 1 expected SKIP, TOTAL 124**. Case 083 was skipped
because it requires source-only FREEMAIN instrumentation. The operator's
console transcript confirms the result; no additional production-mode or
source-mode full panel is required for this march.

Accepted evidence chain: DEVOBJ creation JOB 366, metadata JOB 367;
seeding COPYOBJ IEBCOPY JOB 372 RC=0000; isolated BCPLMEM candidate
assembly and installation JOB 379 (ASMMEM IFOX00 RC=0000, PUTMEM
IEBGENER RC=0000, no flagged statements or severity); focused
DEVOBJ regressions 27 and 122 PASS; full DEVOBJ panel 123/0/1.
Production OBJ was not an installation target in the new jobs.

This closes the **development-object foundation** milestone, not the
entire component canonicalization effort: independently assembling
BCPLMAIN and the other three component/library members requires later
bounded work. The production promotion policy remains unchanged.

## Remaining work

The first working candidate installer targets BCPLMEM only. Extend the same
MVS-native individual build mechanism to BCPLMAIN, BCPLBYTE, BCPLAPT,
and BLIB as needed, first resolving canonical independently assemblable
BCPLMAIN source. Currently SOURCE(BCPLMAIN) is generated by
`tools/checks/stage-bldbmain.py` from `asm/bcplmain-wip.asm` via
externalization and BLIB-registration transformations. Do not replace
it with the raw monolith. Avoid expanding runtime features during this
workflow march.
