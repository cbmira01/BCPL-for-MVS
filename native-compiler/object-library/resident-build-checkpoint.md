# Resident BLIB object build — successful acceptance checkpoint

**Date:** 2026-10-08  
**Repository branch:** `experiment/blib-object-pds`  
**Evidence:** user-executed Hercules MVS 3.8J TK5, **JOB 2413** (`BLIBBLD`)  
**Status:** **VERIFIED — MVS-resident compilation, source-card correction, assembly and binary object-member installation.**

## Acceptance execution

The user updated the experiment branch to the fix recorded in commit
`6b74360`. The local Python packaging tests returned **6 tests, OK**.
The revised JCL was installed with:

```sh
tools/dspal put JCL BLIBBLD jcl/build-blib-object.jcl
```

This completed as **JOB 2410**, installing the job body in
`HERC02.BCPL.JCL(BLIBBLD)`. `HERC02.BCPL.SOURCE(BLIB)` had already
been deployed successfully in **JOB 2404** by the normal `dspal put`
operation. The user submitted:

```sh
tools/dspal submit JCL BLIBBLD --wait
```

JES assigned launcher **JOB 2412** and payload **JOB 2413**. The
reported payload summary was:

```text
JOB 2413  BLIBBLD
08 OCT 26  20.50.47 - 20.50.51

STEP       PROGRAM      RESULT
COMP       ICINT19      RC=0000
PREPASM    IFOX00       RC=0000
PREPLK     IEWL         RC=0000
FIXASM     PGM=*.DD     RC=0000
ASMBLIB    IFOX00       RC=0000
INSTALL    IEBGENER     RC=0000

JOB RESULT: SUCCESS
HIGHEST RC: 0000

Assembler:
  Statements flagged: 0
  Highest severity:   0
```

## What this proves

1. The demoted whole historical Cambridge BLIB in the persistent
   `SOURCE(BLIB)` member was accepted by the resident Cambridge image
   `INTCODE(CAMBCOMP)` via `ICINT19`.
2. The temporary assembler utility assembled (`PREPASM`, RC=0), linked
   (`PREPLK`, RC=0), and **ran** (`FIXASM`, RC=0) entirely on MVS.
   Its success return requires exactly one unnamed-CSECT correction and one
   signed-minimum-constant correction.
3. `ASMBLIB` assembled the resulting named BLIB control section into
   MVS FB/80 relocatable object records with zero flagged statements.
4. `INSTALL` completed at RC=0, copying the generated binary object
   stream to `HERC02.BCPL.OBJ(BLIB)` using IEBGENER on MVS, not the
   text-oriented `dspal put` path.
5. The build depends on no host-recovered assembly, static regression
   combiner, or host binary-object transfer. The host's responsibility
   is limited to demotion, `dspal` deployment of SOURCE and JCL, and
   job submission.

The object PDS had already been allocated and inspected during Stage A;
it was **not** reallocated or purged for JOB 2413.

## Preceding failure and correction

First resident build attempt **JOB 2408** completed COMP, PREPASM and
PREPLK at RC=0, then failed at FIXASM with `S806-4` and
`IEA703I ... MODULE ACCESSED PREP`. PREPLK linked a module named
`BLIBPREP` but the temporary `SYSLMOD` DD named member `PREP`.
Changing the DD to `&&PREPLD(BLIBPREP)` resolved the loader name
mismatch. The successful FIXASM step in JOB 2413 is the direct
confirmation of that correction. The offline packaging suite gained
a regression check that IEWL `NAME` and SYSLMOD member agree.

## Relationship to independent object linkage

The earlier Stage A **JOB 2396** verified *independent* BLIB assembly,
FB/80 object PDS member installation, and explicit IEWL
`INCLUDE OBJ(BLIB)` with a separately assembled BCPLMAIN module
and a resolved external BCPLMAIN relocation (link RC=0). JOB 2413
verifies the **normal MVS-resident rebuild** from positioned BCPL
source. Together they establish the object-library build and
link-edit foundation.

**Not yet established:** runtime execution of a BCPL application
with separately assembled and linked application/BLIB/BCPLMAIN sections;
BCPLMAIN's exported-global-vector initialization remains Stage B.
The historically passing 69-test static-combination native regression
suite was not rerun in this build-only checkpoint.

The user ran the two `dspal put` and `dspal submit` commands directly
for acceptance. The convenience wrapper `tools/build-blib-object`
has passing offline checks and dry-run, but has **not yet been separately
run to completion** as a single command. A direct member listing after
JOB 2413 was not included in this report; INSTALL RC=0 is the reported
object installation evidence.

## Separate-job consumer probe: JOB 2418 (2026-10-08)

**Verified from user-provided `dspal submit --wait` summary:**
- Offline packaging suite: **7 tests, OK**.
- **JOB 2414:** deployed `asm/bcplmain-wip.asm` to
  `HERC02.BCPL.ASM(BCMWIP)`.
- **JOB 2415:** deployed `jcl/probe-blib-object-consumer.jcl` to
  `HERC02.BCPL.JCL(BLIBLINK)`.
- Launcher **JOB 2417** submitted payload **JOB 2418** (`BLIBLINK`).
- `ASMRUN` IFOX00 **RC=0000**; `LKED` IEWL **RC=0000**.
- `JOB RESULT: SUCCESS`, highest RC 0000; no flagged assembler
  statements; highest severity zero.

The stored `BLIBLINK` JCL assembles only BCPLMAIN-wip from the ASM PDS,
then issues explicit `INCLUDE OBJ(BLIB)` with read-only
`HERC02.BCPL.OBJ`. It does **not** compile, assemble, reinstall, or
execute BLIB, nor does it contain a GO step. This establishes that the
persistent `OBJ(BLIB)` installed by the separate resident-build
**JOB 2413** is accepted by the linkage editor in another job.

**Evidence boundary:** The user has supplied the job summary, but
not yet the IEWL link map and XREF listing from JOB 2418. The exact
CSECT lengths, resolved BCPLMAIN relocation and control-card echo
remain to be explicitly checked from that report. IEWL RC=0 alone is
not a substitute for recording those details. No independently linked
BCPL application was executed; Stage B remains open.

