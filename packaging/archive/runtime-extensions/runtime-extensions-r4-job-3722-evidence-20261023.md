# Milestone Runtime Extensions — R.4 — JOB 3722 Integrated BCPL Evidence

**Date:** 23 October 2026
**System:** Hercules / MVS 3.8J TK5, IFOX, IEWL, ICINT19
**Tested revision:** 40655b004c027f82c5eab6d6fb9d182e013c6128
**Job:** R4BCXINT, JOB 3722
**Disposition:** PASS — integrated known-package BCXREQ BCPLDEMO acceptance.
**R.4 status:** OPEN pending owner disposition.

## Execution

The owner pulled revision 40655b0 and submitted the committed
bootstrap-toolchain/probes/r4-bcx-macros/r4-bcx-integrated-mvs.jcl.
The supplied JES report confirms all eleven EXEC steps completed
RC=0000:

| EXEC steps | Program | Actual |
| --- | --- | --- |
| COMP | ICINT19, resident demoted Cambridge compiler | RC=0000; COMPILATION SUCCESSFUL |
| PREP, CATP, POSTP | IEBGENER | RC=0000 each |
| ASMA, ASMN, ASMR, ASMP, ASMG | IFOX00 | RC=0000 each |
| LINK | IEWL | RC=0000 |
| GO | Native compiled BCPL | RC=0000 |

The actual BCPL output was: **R4 BCX BCPL START PASS**.
The compiled START calls DEMOSVC(0,0,0) at G!203 and requires
return value 6 before printing the marker. An incorrect value
would have invoked STOP(8). Normal FINISH followed.

## IFOX and IEWL evidence

- IFOX ASMA exported LD R4APP at offset 000000 in the unnamed
  client CSECT. The label is defined by a zero-length assembler
  prefix concatenated before the unchanged compiler output.
- IEWL processed the macro-punched INCLUDE PKGA and an explicit
  ENTRY R4APP, and reported ENTRY ADDRESS 00.
- The map shows $PRIVATE/R4APP at 000000, BCPLMAIN at 0000B0,
  RGINIT at 0010F8, RGFINI at 001B18, DMODESC/DMOBEG at
  001C18, DMODISP/DMOEND at 001C50, and BCPLREG at 001D18.
  BCRGBEG is 001D18; BCRGEND is 001D44.
- ASMG expanded one BCXREQ BCPLDEMO and emitted a 44-byte BCRG
  version-1 table: 28-byte header, one selected descriptor pair
  A(DMOBEG),A(DMOEND), and one CL8 BCPLDEMO required ID. Its
  header reports version 1, header size 28, total 44, N=1, M=1.
- IEWL resolved the real package descriptor and dispatcher
  addresses, and the compiled BCPL client successfully used the
  registered G!203 service at execution time.

## R.4 sequence

JOB 3719 exposed illegal assembler macro declaration placement.
JOB 3720 passed all five IFOX macro/PUNCH/IEWL selection cases.
JOB 3721 compiled and linked but GO ABEND S0C1 because IEWL
started BCPLMAIN rather than the private compiled client prefix.
JOB 3722 corrected this with explicit R4APP and passed all steps.

## Limits

This proves a **known-package** BCXREQ integration with a real
compiled BCPL application and the accepted BCPLMAIN/BCPLRGS.
It does not establish arbitrary extension discovery, automatic
transitive selection of dependencies, negative/failure behavior of
macro-generated registries, or independently packaged site libraries.
The prior R.0–R.3 acceptance is unchanged.

All new object and load datasets were temporary, and BOOT.OBJ was
read-only. No production compiler, runtime, accepted ABI, or
persistent MVS object library was altered.
R.4 is not formally closed without an owner decision.
