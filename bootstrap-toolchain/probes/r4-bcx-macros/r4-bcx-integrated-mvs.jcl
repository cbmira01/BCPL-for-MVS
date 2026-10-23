//R4BCXINT JOB (BCPL),'R4 BCPL INTEG',CLASS=A,MSGCLASS=A,
//             MSGLEVEL=(1,1)
//* R.4 INTEGRATED BCPL: CAMBCOMP/IFOX/IEWL/BCPLMAIN/BCPLRGS.
//* BOOT.OBJ READ-ONLY; ALL NEW OBJECTS AND LOADS TEMPORARY.
//* COMPILER EXECUTES AS INTCODE UNDER ICINT19 ON MVS.
//* APP IN UNNAMED CSECT: EXPORT R4APP AND LINK ENTRY R4APP.
//COMP     EXEC PGM=ICINT19,REGION=256K,TIME=(,30)
//STEPLIB  DD  DSN=HERC02.BCPL.MR10KIT.LOAD,DISP=SHR
//SYSPRINT DD  SYSOUT=*,DCB=(RECFM=FB,LRECL=132,BLKSIZE=132)
//INTIN    DD  DSN=HERC02.BCPL.BOOT.INTCODE(CAMBCOMP),DISP=SHR
//SYSIN    DD  DATA,DLM=Z9
// INTEGRATED COMPILED BCPL: DIRECT G!203 QUERY.
GLOBAL $( START:1; STOP:30; WRITES:60; NEWLINE:63;
          DEMOSVC:203 $)
LET START() BE
$(1
    IF DEMOSVC(0,0,0) NE 6 DO STOP(8)
    WRITES("R4 BCX BCPL START PASS")
    NEWLINE()
    FINISH
$)1
Z9
//OPTIONS  DD  DSN=HERC02.BCPL.BOOT.SOURCE(OPTIONS),DISP=SHR
//CAMBPARM DD  DSN=HERC02.BCPL.BOOT.SOURCE(CAMBPARM),DISP=SHR
//LIBHDR   DD  DSN=HERC02.BCPL.BOOT.SOURCE(LIBHDR),DISP=SHR
//SYNHDR   DD  DSN=HERC02.BCPL.BOOT.SOURCE(SYNHDR),DISP=SHR
//TRNHDR   DD  DSN=HERC02.BCPL.BOOT.SOURCE(TRNHDR),DISP=SHR
//CGHDR    DD  DSN=HERC02.BCPL.BOOT.SOURCE(CGHDR),DISP=SHR
//CODE     DD  DSN=&&R4CODE,UNIT=SYSDA,
//             SPACE=(80,(1000,500)),
//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=80),
//             DISP=(NEW,PASS)
//SYSGO    DD  DUMMY
//SYSUDUMP DD  SYSOUT=*
//PREP     EXEC PGM=IEBGENER
//SYSPRINT DD  SYSOUT=*
//SYSUT1   DD  *
* R.4 IFOX MACRO PROBE. TWO KNOWN TEST CATALOG ENTRIES ONLY.
* NO CSECT IS EMITTED UNTIL BCXEND IN BCXPOST.
* BCXSEL SELECTS AN OPTIONAL PACKAGE; BCXREQ ALSO REQUIRES IT.
* ALL IEWL PUNCH CARDS PRECEDE THE FIRST OBJECT CSECT.
         MACRO
         BCXSEL &PKG
         BCXADD &PKG,0
         MEND
         MACRO
         BCXREQ &PKG
         BCXADD &PKG,1
         MEND
         MACRO
         BCXADD &PKG,&REQ
         GBLA  &BXN,&BXM,&BXR(32),&BXGOOD
         GBLC  &BXID(32),&BXBEG(32),&BXFIN(32)
         GBLC  &BXCLIB,&BXCBEG,&BXCFIN
         LCLA  &I
&BXGOOD SETA  0
         BCXCAT &PKG
         AIF   (&BXGOOD EQ 0).EXIT
&I       SETA  1
.FIND    AIF   (&I GT &BXN).NEW
         AIF   ('&BXID(&I)' EQ '&PKG').FOUND
&I       SETA  &I+1
         AGO   .FIND
.FOUND   AIF   (&REQ EQ 0).EXIT
         AIF   (&BXR(&I) EQ 1).EXIT
&BXR(&I) SETA  1
&BXM     SETA  &BXM+1
         AGO   .EXIT
.NEW     AIF   (&BXN GE 32).FULL
&BXN     SETA  &BXN+1
&BXID(&BXN)  SETC '&PKG'
&BXBEG(&BXN) SETC '&BXCBEG'
&BXFIN(&BXN) SETC '&BXCFIN'
         AIF   (&REQ EQ 0).SEL
&BXR(&BXN) SETA  1
&BXM     SETA  &BXM+1
.SEL     ANOP
         PUNCH ' INCLUDE &BXCLIB'
         AGO   .EXIT
.FULL    MNOTE 8,'BCX SELECTED PACKAGE LIMIT 32'
.EXIT    ANOP
         MEND
         MACRO
         BCXEND
         GBLA  &BXN,&BXM,&BXR(32)
         GBLC  &BXID(32),&BXBEG(32),&BXFIN(32)
         LCLA  &I,&BYTES
&BYTES   SETA  28+8*(&BXN+&BXM)
BCPLREG  CSECT
         ENTRY BCRGBEG,BCRGEND
BCRGBEG  DS    0F
         DC    CL4'BCRG'
         DC    F'1',F'28',F'&BYTES',F'&BXN',F'&BXM',F'0'
&I       SETA  1
.DESC    AIF   (&I GT &BXN).REQS
         EXTRN &BXBEG(&I),&BXFIN(&I)
         DC    A(&BXBEG(&I)),A(&BXFIN(&I))
&I       SETA  &I+1
         AGO   .DESC
.REQS    ANOP
&I       SETA  1
.REQLOOP AIF   (&I GT &BXN).DONE
         AIF   (&BXR(&I) EQ 0).NEXT
         DC    CL8'&BXID(&I)'
.NEXT    ANOP
&I       SETA  &I+1
         AGO   .REQLOOP
.DONE    ANOP
BCRGEND  EQU   *
         MEND
/*
//SYSUT2   DD  DSN=&&BCXPRE,UNIT=SYSDA,
//             SPACE=(80,(60,20)),DISP=(NEW,PASS),
//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)
//SYSIN    DD  DUMMY
//CATP     EXEC PGM=IEBGENER
//SYSPRINT DD  SYSOUT=*
//SYSUT1   DD  *
* R.4 MVS RESIDENT PACKAGE CATALOG. TWO TEST ENTRIES ONLY.
* PKGA/PKGB ARE IEWL DD NAMES FOR TEMPORARY OBJECT DATASETS.
         MACRO
         BCXCAT &PKG
         GBLA  &BXGOOD
         GBLC  &BXCLIB,&BXCBEG,&BXCFIN
         AIF   ('&PKG' EQ 'BCPLDEMO').PA
         AIF   ('&PKG' EQ 'R2TESTB').PB
         MNOTE 8,'UNKNOWN BCX PACKAGE: &PKG'
         AGO   .EXIT
.PA      ANOP
&BXCLIB  SETC  'PKGA'
&BXCBEG  SETC  'DMOBEG'
&BXCFIN  SETC  'DMOEND'
         AGO   .GOOD
.PB      ANOP
&BXCLIB  SETC  'PKGB'
&BXCBEG  SETC  'R2BBEG'
&BXCFIN  SETC  'R2BEND'
.GOOD    ANOP
&BXGOOD  SETA  1
.EXIT    ANOP
         MEND
/*
//SYSUT2   DD  DSN=&&BCXCAT,UNIT=SYSDA,
//             SPACE=(80,(60,20)),DISP=(NEW,PASS),
//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)
//SYSIN    DD  DUMMY
//POSTP    EXEC PGM=IEBGENER
//SYSPRINT DD  SYSOUT=*
//SYSUT1   DD  *
* BCPLREG CSECT AND ASSEMBLER END STAY OUT OF APPLICATION SELECTION.
         BCXEND
         END   BCPLREG
/*
//SYSUT2   DD  DSN=&&BCXPOST,UNIT=SYSDA,
//             SPACE=(80,(60,20)),DISP=(NEW,PASS),
//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)
//SYSIN    DD  DUMMY
//ASMA     EXEC PGM=IFOX00,REGION=256K,
//             PARM='OBJECT,NODECK,LIST,XREF(FULL),ESD,RLD',
//             COND=(0,NE,COMP)
//SYSLIB   DD  DSN=SYS1.MACLIB,DISP=SHR
//SYSUT1   DD  UNIT=SYSDA,SPACE=(1700,(600,100))
//SYSUT2   DD  UNIT=SYSDA,SPACE=(1700,(300,50))
//SYSUT3   DD  UNIT=SYSDA,SPACE=(1700,(300,50))
//SYSPRINT DD  SYSOUT=*
//SYSPUNCH DD  DUMMY
//SYSGO    DD  DSN=&&R4AOBJ,UNIT=SYSDA,
//             SPACE=(80,(300,100)),DISP=(NEW,PASS),
//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)
//SYSIN    DD  *
         CSECT
         ENTRY R4APP
R4APP    EQU   *
/*
//         DD  DSN=&&R4CODE,DISP=(OLD,PASS)
//ASMN     EXEC PGM=IFOX00,REGION=256K,
//             PARM='OBJECT,NODECK,LIST,XREF(FULL),ESD,RLD',
//             COND=(0,NE,COMP)
//SYSLIB   DD  DSN=SYS1.MACLIB,DISP=SHR
//SYSUT1   DD  UNIT=SYSDA,SPACE=(1700,(600,100))
//SYSUT2   DD  UNIT=SYSDA,SPACE=(1700,(300,50))
//SYSUT3   DD  UNIT=SYSDA,SPACE=(1700,(300,50))
//SYSPRINT DD  SYSOUT=*
//SYSPUNCH DD  DUMMY
//SYSGO    DD  DSN=&&R4NOBJ,UNIT=SYSDA,
//             SPACE=(80,(300,100)),DISP=(NEW,PASS),
//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)
//SYSIN    DD  *
***********************************************************************
* BCPL FOR MVS 3.8 RECONSTRUCTION - BCPLMAIN
*
* Core Runtime coordinator for generated native BCPL applications.
* Creates global/system vectors, binds core services and imports
* application/Base Library exports before entering START.
*
* REGISTRATION:
* RGINIT validates and registers selected optional packages
* before START; RGFINI runs before stream/memory cleanup.
* Exactly one application BCPLREG table is required at link-edit.
*
* LINKAGE:
* Requires BLIB, BCPLIO, BCPLMEM, BCPLBYTE, BCPLAPT,
* and the generic registrar BCPLRGS (RGINIT/RGFINI).
* Preserves the accepted native System/370 BCPL register ABI.
*
* STATUS:
* Accepted R.1-R.3 behavior was tested with temporary MVS
* objects; no BOOT_OBJ or BOOT_DEVOBJ installation is implied.
* A reconstruction, not authenticated historical machine code.
***********************************************************************

BCPLMAIN CSECT
         ENTRY STKOVFL
         EXTRN BLIB
         EXTRN RGINIT,RGFINI
         EXTRN GETVEC,FREEVEC,MEMDRAIN,MEMBIND
         EXTRN GETBYTE,PUTBYTE
         EXTRN APTOVEC,APLIMIT
         EXTRN IOINIT,IOFIN,IOWRCH,IOBIND,IODIAG,IOREPL,IOPMGET
         EXTRN IOFOUT,IOSOUT,IOOUT,IOWRAP,IOENDW
         EXTRN IOSELIN,IOINP,IOPARMST,IORDCH,IOUNRD,IOFINDIN
         EXTRN IOENDRD
*
* Preserve the compiled-module base before R3 is repurposed as R.K12.
*
         LR    3,15
         LR    9,1
         BALR  10,0
         USING *,10
*
* Establish a private MVS save area before any service call.
* The generated module prefix already saved the caller's R14..R12.
*
         L     1,=A(MSVSAVE)
         ST    13,4(1)
         ST    1,8(13)
         LR    13,1
         USING MSVSAVE,13
         ST    9,PARMLIST
         ST    3,MODBASE
*
* Locate L998 = module base + unsigned positive halfword at module+10.
* CG370 limits a generated section to less than 16K bytes, so LH is
* safe.
*
         LH    0,10(3)
         LR    2,3
         AR    2,0
         ST    2,MODEND
*
* Acquire one MVS allocation for G!0..G!699, 16384 usable stack
* words and a provisional 256-byte stack clearance. Preserve the
* tested safe limit while retaining physical headroom above it.
* GETMAIN EC reports failure through R15.
* through R15.  Store base and length for subsequent FREEMAIN R.
*
         L     9,DYNLEN
         GETMAIN EC,LV=(9),A=DYNBASE,SP=0
         LTR   15,15
         BNZ   GNOCORE
         L     12,DYNBASE
         LA    1,GVBYTES(12)
         ST    1,DYNWORK
         A     1,=F'65536'
         ST    1,STKLIM
         A     1,=F'256'
         ST    1,DYNEND
*
* G56 STACKHWM in historical BLIB scans alternating word markers.
* Paint the safe 16384-word stack before the first BCPL frame.
* The final 256-byte clearance stays outside the working stack.
*
         L     2,DYNWORK
         L     3,=X'5C40E2E3'
         L     4,=X'C3D2405C'
         L     0,=F'8192'
STKPAINT ST    3,0(2)
         ST    4,4(2)
         LA    2,8(2)
         BCT   0,STKPAINT
*
* STACKEND-2 is the guard; STACKEND-1 records the highest
* initialized even-marker word as a BCPL word pointer.
* These two fullwords reside in the reserved clearance.
*
         L     2,DYNEND
         AH    2,=H'-8'
         ST    3,0(2)
         L     1,STKLIM
         AH    1,=H'-8'
         SRL   1,2
         ST    1,4(2)
         LA    11,SYSV
*
* Initialize the dynamic global vector with the historical sentinel.
*
         LA    1,GLOBCNT
         ST    1,0(12)
         LA    2,4(12)
         L     3,=X'C7D3F004'
GINIT    ST    3,0(2)
         A     3,=F'4'
         LA    2,4(2)
         BCT   1,GINIT
* CLEAR PER-GLOBAL OWNER LEDGER BEFORE IMPORTS.
         L     4,=A(R1OWNB)
         XC    0(256,4),0(4)
         XC    256(256,4),256(4)
         XC    512(188,4),512(4)
*
* Find the trailer sentinel by scanning backward in two-word units.
* A pair whose second word is zero is treated as [4*MAXGN,0].
*
         L     8,MODEND
GSCAN    AH    8,=H'-8'
         L     9,4(8)
         LTR   9,9
         BC    7,GSCAN
*
* Reject modules requiring more globals than this static WIP provides.
*
         L     0,0(8)
         C     0,=F'2796'
         BC    2,GTOOBIG
         ST    8,TRAILER
*
* Re-scan from the module end and install each exported global.
*
         L     8,MODEND
GINST    AH    8,=H'-8'
         L     9,4(8)
         LTR   9,9
         BC    8,GIDONE
         L     1,0(8)
         C     1,=F'2796'
         BC    2,GTOOBIG
         LR    2,12
         AR    2,1
         ST    9,0(2)
         LR    4,1
         SRL   4,2
         L     2,=A(R1OWNB)
         AR    2,4
         OI    0(2),X'01'
         BC    15,GINST
*
* G!1 must now contain START rather than the unset sentinel.
*
GIDONE   L     8,=A(BLIB)
* IMPORT BLIB EXPORTED GLOBALS BY EXPLICIT MODULE REGISTRATION.
* THE RELOCATED BLIB ENTRY POINT NAMES THE PREFIX AT OFFSET ZERO.
         LH    0,10(8)
         AR    8,0
BLIMP    AH    8,=H'-8'
         L     9,4(8)
         LTR   9,9
         BZ    BLIDONE
         L     1,0(8)
         C     1,=F'800'
         BH    GTOOBIG
         LR    2,12
         AR    2,1
         ST    9,0(2)
         LR    4,1
         SRL   4,2
         L     2,=A(R1OWNB)
         AR    2,4
         OI    0(2),X'02'
         B     BLIMP
BLIDONE  L     4,4(12)
         C     4,=X'C7D3F004'
         BC    8,NOSTART
*
* Publish the subset of runtime globals whose representation is
* supported strongly enough for this WIP.
*
* G!6 = provisional BCPL word pointer for the current MVS save area.
*
         LR    1,13
         SRL   1,2
         ST    1,24(12)
         L     8,=A(R1OWNB)
         OI    6(8),X'04'
*
* G!52/G!53 = provisional main-program word-address extent.
*
         L     1,MODBASE
         SRL   1,2
         ST    1,208(12)
         L     8,=A(R1OWNB)
         OI    52(8),X'04'
         L     1,MODEND
         SRL   1,2
         ST    1,212(12)
         L     8,=A(R1OWNB)
         OI    53(8),X'04'
*
* G!54/G!55 = BCPL word pointers for the allocated stack extent.
* G!55 includes the reserved clearance; STKLIM is the safe limit.
*
         L     1,DYNWORK
         SRL   1,2
         ST    1,216(12)
         L     8,=A(R1OWNB)
         OI    54(8),X'04'
         L     1,DYNEND
         SRL   1,2
         ST    1,220(12)
         L     8,=A(R1OWNB)
         OI    55(8),X'04'
*
* G!14 = first narrow native WRCH implementation for Regression 03.
* G!76 = bootstrap WRITEF, extended through Regression 058.
* G!85/G!86 = machine-dependent byte primitives required by BLIB.
* G!87/G!88 = first WIP GETVEC/FREEVEC dynamic-storage services.
* G!150 = provisional DEBUGINT bootstrap diagnostic service.
*
         L     1,=A(IOSELIN)
         ST    1,44(12)
         L     8,=A(R1OWNB)
         OI    11(8),X'04'
         L     1,=A(IOINP)
         ST    1,64(12)
         L     8,=A(R1OWNB)
         OI    16(8),X'04'
         L     1,=A(IOOUT)
         ST    1,68(12)
         L     8,=A(R1OWNB)
         OI    17(8),X'04'
         L     1,=A(IOPARMST)
         ST    1,156(12)
         L     8,=A(R1OWNB)
         OI    39(8),X'04'
         L     1,=A(IOWRAP)
         ST    1,132(12)
         L     8,=A(R1OWNB)
         OI    33(8),X'04'
         L     1,=A(IORDCH)
         ST    1,52(12)
         L     8,=A(R1OWNB)
         OI    13(8),X'04'
         L     1,=A(IOUNRD)
         ST    1,60(12)
         L     8,=A(R1OWNB)
         OI    15(8),X'04'
         L     1,=A(IOFINDIN)
         ST    1,168(12)
         L     8,=A(R1OWNB)
         OI    42(8),X'04'
         L     1,=A(IOFOUT)
         ST    1,164(12)
         L     8,=A(R1OWNB)
         OI    41(8),X'04'
         L     1,=A(IOSOUT)
         ST    1,48(12)
         L     8,=A(R1OWNB)
         OI    12(8),X'04'
         L     1,=A(IOENDW)
         ST    1,188(12)
         L     8,=A(R1OWNB)
         OI    47(8),X'04'
         L     1,=A(IOENDRD)
         ST    1,184(12)
         L     8,=A(R1OWNB)
         OI    46(8),X'04'
         L     1,=A(IOWRCH)
         ST    1,56(12)
         L     8,=A(R1OWNB)
         OI    14(8),X'04'
* Keep BLIB's G!76 WRITEF when its export has been imported.
* Install provisional WRITEST only if G!76 retains the unset sentinel.
         L     1,304(12)
         C     1,=X'C7D3F130'
         BNE   WFHAS76
         LA    1,WRITEST
         ST    1,304(12)
         L     8,=A(R1OWNB)
         OI    76(8),X'04'
WFHAS76  EQU   *
         L     1,=A(GETBYTE)
         ST    1,340(12)
         L     8,=A(R1OWNB)
         OI    85(8),X'04'
         L     1,=A(PUTBYTE)
         ST    1,344(12)
         L     8,=A(R1OWNB)
         OI    86(8),X'04'
         L     1,=A(GETVEC)
         ST    1,348(12)
         L     8,=A(R1OWNB)
         OI    87(8),X'04'
         L     1,=A(FREEVEC)
         ST    1,352(12)
         L     8,=A(R1OWNB)
         OI    88(8),X'04'
         ST    10,MBRT10
         L     1,=A(MSVFREE)
         L     9,=A(MEMBIND)
         BALR  14,9
         L     10,MBRT10
         L     1,=A(DEBUGINT)
         ST    1,600(12)
         L     8,=A(R1OWNB)
         OI    150(8),X'04'
* Install independent BCPLAPT G40 entry and its safe stack limit.
         L     1,=A(APLIMIT)
         L     2,STKLIM
         ST    2,0(1)
         L     1,=A(APTOVEC)
         ST    1,160(12)
         L     8,=A(R1OWNB)
         OI    40(8),X'04'
         LA    1,STOPENT
         ST    1,120(12)
         L     8,=A(R1OWNB)
         OI    30(8),X'04'
*
* Regression 03 output is deliberately narrow: one buffered SYSPRINT
* record.  This borrows the proven QSAM shape used by ICINT V19.
*
         LR    9,10
         L     1,PARMLIST
         L     15,=A(IOINIT)
         BALR  14,15
         LR    10,9
         LR    9,10
         LA    1,IOSTOP
         L     15,=A(IOBIND)
         BALR  14,15
         LR    10,9
*
* Establish S, initial P/W, and the absolute-base constants required by
* generated USING 4096,1,2,3 code.
*
* REGISTER OPTIONALS AFTER CORE AND BLIB IMPORTS.
         ST    12,R1GVEC
         LA    1,R1GVEC
         L     15,=A(RGINIT)
         BALR  14,15
         LTR   15,15
         BNZ   R1BAD
         LA    11,SYSV
         L     15,DYNWORK
         LR    5,15
         L     1,=F'4096'
         L     2,=F'8192'
         L     3,=F'12288'
*
* START receives no arguments.  Clear argument registers and linkage.
* R10 has served as our assembler base and must cease being one now.
*
         SR    6,6
         SR    7,7
         SR    8,8
         SR    9,9
         SR    10,10
*
* Job 943 makes this initialization a required runtime invariant.
*
         SR    0,0
         BCR   15,4
*
* START is expected to terminate through S.FIN.  Returning here is
* treated as a WIP runtime failure.
*
* REGISTRATION REJECTION BEFORE APPLICATION START.
* IOFIN USES R10 AS A PRIVATE BASE. PRESERVE OUR BASE IN R9.
R1BAD    LR    9,10
         L     15,=A(IOFIN)
         BALR  14,15
         LR    10,9
         BAL   14,RELMEM
         L     13,4(13)
         LM    14,12,12(13)
         LA    15,12
         BR    14
BADRETN  BAL   14,RELMEM
         L     13,4(13)
         LM    14,12,12(13)
         LA    15,36
         BR    14
*
* Bootstrap failures before START.
*
GTOOBIG  BAL   14,RELMEM
         L     13,4(13)
         LM    14,12,12(13)
         LA    15,16
         BR    14
NOSTART  BAL   14,RELMEM
         L     13,4(13)
         LM    14,12,12(13)
         LA    15,20
         BR    14
*
* Failure before allocation: no storage to release.
GNOCORE  L     13,4(13)
         LM    14,12,12(13)
         LA    15,24
         BR    14
*
* Put literals used by startup inside the startup base-register region.
*
         LTORG
*
* From here on R10 is not a runtime base.  Executable system-vector
* services use R11, whose value is SYSV in generated BCPL code.
*
         DROP  10
*
***********************************************************************
* SYSTEM VECTOR
*
* Each public offset is a four-byte branch followed by padding to the
* next 20-byte slot.  This layout is a reconstruction proposal matching
* the offsets in CGHDR; the historical instruction sequence is unknown.
***********************************************************************
SYSV     EQU   *
         USING SYSV,11
         BC    15,RETIMPL
         DS    8H
*
* S.COUNT = 20
*
SYSCOUNT BC    15,CNTIMPL
         DS    8H
*
* S.FIN = 40
*
SYSFIN   BC    15,FINIMPL
         DS    8H
*
* S.STKCK = 60
*
SYSSTK   BC    15,STKIMPL
         DS    8H
*
* S.STKCKCOUNT = 80
*
SYSSTKC  BC    15,STKCIMP
         DS    8H
*
* Runtime-local byte limit and controlled-overflow message.
* Historical BCPLMAC distinguishes STKLIM (safe limit) from STKHIGH.
* This WIP reserves 256 extra bytes above the tested 16KB safe
* limit.  The exact historical INUM interpretation remains unknown.
*
STKLIM   DC    F'0'
STKMSG   DC    CL14'STACK OVERFLOW'
         DS    0H
*
***********************************************************************
* PROCEDURE RETURN
*
* Restore linkage from the callee frame, then restore the caller's P
* before reloading R4 from the caller frame.  Test 32 showed why R4
* cannot be restored from 0(current P): that word names the callee.
***********************************************************************
RETIMPL  L     6,8(5)
         L     5,4(5)
         L     4,0(5)
         BCR   15,6
*
***********************************************************************
* CALL-COUNT SERVICE -- STUB
*
* CG370 emits BAL R14,S.COUNT(R11) followed by an inline fullword.
* A minimally non-destructive stub must skip that word on return.
* Actual counter semantics remain to be reconstructed.
***********************************************************************
CNTIMPL  LA    14,4(14)
         BR    14
*
***********************************************************************
* FINISH
*
* Restore the MVS registers saved by the generated module prefix.
* FINISH selects RC=0; STOP(N) selects the requested step code.
* Both share the output and storage reclamation path.
***********************************************************************
FINIMPL  XC    STOPRC(4),STOPRC
         XC    R1REAS(4),R1REAS
         XC    R1CODE(4),R1CODE
         B     FINEXIT
STOPENT  ST    7,STOPRC
         ST    7,R1CODE
         LA    1,1
         ST    1,R1REAS
FINEXIT  LR    9,10
* FINALIZERS RUN BEFORE IOFIN AND MEMDRAIN.
         LA    1,R1REAS
         L     15,=A(RGFINI)
         BALR  14,15
         LTR   15,15
         BZ    R1FINOK
         L     1,R1REAS
         LTR   1,1
         BNZ   R1FINOK
         LA    1,8
         ST    1,STOPRC
R1FINOK  L     15,=A(IOFIN)
         BALR  14,15
         LR    10,9
FINNOO2  EQU   *
* BCPLIO IOFIN closes lazily opened BCPIN and BCPINB.
         BAL   14,RELMEM
         L     15,STOPRC
         L     13,4(13)
         LM    14,14,12(13)
         LM    0,12,20(13)
         BR    14
*
* Drain live GETVEC allocations before freeing global/stack memory.
* Each record holds its own byte length and next record address.
* Detach the head before FREEMAIN; never read a released record.
* Save the BAL return across MVS services that may modify R14.
***********************************************************************
RELMEM   ST    14,RELRET
         L     1,=A(MEMDRAIN)
         BALR  14,1
         SR    1,1
         L     9,=A(MEMBIND)
         BALR  14,9
RELMAIN  L     1,DYNBASE
         LTR   1,1
         BZ    RELDONE
         L     10,DYNLEN
         FREEMAIN R,LV=(10),A=(1)
         XC    DYNBASE(4),DYNBASE
RELDONE  L     14,RELRET
         BR    14
         LTORG
*
***********************************************************************
* STACK CHECK -- FRAME-SIZE CONTRACT
*
* Tests 48-49 established the checked-entry sequence and proved that
* this path must perform the LR 5,15 omitted by CG370.
*
* R14 addresses an inline fullword containing the generated frame size
* in bytes.  CG370 has already saved R4-R6 at 0(R15), so R4 is safe as
* a temporary here and can be restored before returning to generated
* code.
*
* Test 50 added structural validation of the inline value.  Test 52
* adds the first WIP limit check: W plus required frame bytes must not
* exceed STKLIM.  BCPLMAC proves that the historical runtime maintained
* a safe stack limit distinct from the byte beyond allocated stack.
* The missing machine-code STKCK body leaves exact clearance semantics
* unrecovered. The provisional boundary remains 16KB from stack base.
***********************************************************************
STKIMPL  LR    5,15
         L     4,0(14)
         LTR   4,4
         BC    12,STKFORM
         TM    3(14),X'03'
         BC    7,STKFORM
         AR    4,15
         C     4,STKLIM
         BH    STKOVFL
         L     4,0(15)
         LA    14,4(14)
         BR    14
STKOVFL  LR    9,10
         LA    1,STKMSG
         LA    2,14
         L     15,=A(IOREPL)
         BALR  14,15
         LR    10,9
         B     FINIMPL
IOSTOP   LA    7,12
         B     STOPENT
STKFORM  L     4,0(15)
         L     13,4(13)
         LM    14,12,12(13)
         LA    15,36
         BR    14
*
***********************************************************************
* STACK CHECK + CALL COUNT -- STUB
*
* CG370 places an inline fullword after this BAL form, so skip it.
***********************************************************************
STKCIMP  LA    14,4(14)
         BR    14
*
***********************************************************************
* Independent BCPLAPT supplies G40; bootstrap sets APLIMIT.
*
***********************************************************************
* INPUT STREAM RUNG 094 -- SINGLE NAMED QSAM STREAM BCPIN
*
* FINDINPUT accepts the EBCDIC BCPL string "BCPIN", lazily opens
* its DCB and returns a word-address stream handle. Other DDs fail
* with zero. SELECTINPUT retains that handle. RDCH reads characters
* from an 80-byte fixed QSAM record; end-of-data yields -1.
* This is a bootstrap subset, not multi-stream historical BCPL I/O.
***********************************************************************
* D4 input handlers now reside in BCPLIO.

*
***********************************************************************
* BCPL output services and both QSAM DCBs are owned by BCPLIO.
* G14/G12/G16/G17/G41/G47 point to independent entries.
***********************************************************************
*
* WRITEF -- LITERAL + %N/%C/%S/%I/%X/%O BOOTSTRAP
*
* Regression 053 established literal-string output through G76.
* Regression 054 adds the historical BLIB %N case: decimal output of
* the next argument with no width field.  Regression 055 adds %C and
* %S and proves sequential consumption of R8 then R9. Regression 056
* adds the historical %I width path; Test 060 adds A-F width digits.
*
* BCPL strings use a length byte at byte offset zero followed by data
* Literal bytes use the BCPL output service. '%' followed by 'N'
* emits signed decimal; %C emits one character; %S emits a BCPL
* string; %I consumes one width character and emits signed decimal
* right-justified in that field. %X and %O consume one width
* character and emit exactly that many zero-filled hexadecimal or
* octal digits respectively.
*
* This is bootstrap machinery, not a reconstruction of BLIB's BCPL
* WRITEF body.  R0 and R1-R3 remain permanent generated-code registers.
***********************************************************************
WRITEST  STM   2,6,WFREGSV
         ST    8,WFARGS
         ST    9,WFARGS+4
         XC    WFARGIX(4),WFARGIX
         LR    14,7
         SLL   14,2
         SR    8,8
         IC    8,0(14)
         LA    14,1(14)
         SR    9,9
WFLITLP  LTR   8,8
         BZ    WFLITDN
         SR    7,7
         IC    7,0(14)
         CLI   0(14),C'%'
         BNE   WFLITCP
         LA    4,2
         CR    8,4
         BL    WFLITCP
         CLI   1(14),C'N'
         BE    WFNSEL
         CLI   1(14),C'C'
         BE    WFCSEL
         CLI   1(14),C'I'
         BE    WFISEL
         CLI   1(14),C'X'
         BE    WFXSEL
         CLI   1(14),C'O'
         BE    WFOSEL
         CLI   1(14),C'S'
         BE    WFSTSEL
         CLI   1(14),C'$'
         BE    WFSKARG
         B     WFUNK
WFSTSEL  EQU   *
         LA    14,2(14)
         SR    8,4
         BAL   10,WFNEXT
         B     WFSTR
*
* Historical BLIB default emits the unknown conversion character
* without the '%' and without advancing the argument cursor.
*
*
* Historical BLIB percent-dollar skips one argument; emits nothing.
*
WFSKARG  L     6,WFARGIX
         LA    6,1(6)
         ST    6,WFARGIX
         LA    14,2(14)
         SR    8,4
         B     WFLITLP
WFUNK    SR    7,7
         IC    7,1(14)
         LA    14,2(14)
         SR    8,4
         BAL   10,WFPUTC
         B     WFLITLP
WFNSEL   XC    WFWIDTH(4),WFWIDTH
         LA    14,2(14)
         SR    8,4
         BAL   10,WFNEXT
         B     WFNUM
WFISEL  LA    5,3
         CR    8,5
         BL    WFLITCP
         SR    6,6
         IC    6,2(14)
         CLI   2(14),C'A'
         BL    WFIDEC
         CLI   2(14),C'F'
         BH    WFIDEC
         S     6,WFHEXAO
         B     WFISTOR
WFIDEC   S     6,WFZERO
WFISTOR  ST    6,WFWIDTH
         LA    14,3(14)
         SR    8,5
         BAL   10,WFNEXT
         B     WFNUM
WFXSEL   LA    5,3
         CR    8,5
         BL    WFLITCP
         SR    6,6
         IC    6,2(14)
         CLI   2(14),C'A'
         BL    WFXDEC
         CLI   2(14),C'F'
         BH    WFXDEC
         S     6,WFHEXAO
         B     WFXSTOR
WFXDEC   S     6,WFZERO
WFXSTOR  ST    6,WFWIDTH
         LA    14,3(14)
         SR    8,5
         BAL   10,WFNEXT
         B     WFHEX
WFOSEL   LA    5,3
         CR    8,5
         BL    WFLITCP
         SR    6,6
         IC    6,2(14)
         CLI   2(14),C'A'
         BL    WFODEC
         CLI   2(14),C'F'
         BH    WFODEC
         S     6,WFHEXAO
         B     WFOSTOR
WFODEC   S     6,WFZERO
WFOSTOR  ST    6,WFWIDTH
         LA    14,3(14)
         SR    8,5
         BAL   10,WFNEXT
         B     WFOCT
WFCSEL   LA    14,2(14)
         SR    8,4
         BAL   10,WFNEXT
         BAL   10,WFPUTC
         B     WFLITLP
WFLITCP  LA    14,1(14)
         BCTR  8,0
         BAL   10,WFPUTC
         B     WFLITLP
*
* Emit the current signed integer using the proven CVD/UNPK shape
* used by DEBUGINT, then copy digits through the common byte appender.
*
WFNUM    ST    8,WFREM
         ST    14,WFFMTP
         XC    WFSIGN(4),WFSIGN
         LTR   7,7
         BNM   WFCVT
         LA    6,1
         ST    6,WFSIGN
WFCVT    CVD   7,WFDECPK
         UNPK  WFDECZN(15),WFDECPK(8)
         OI    WFDECZN+14,X'F0'
         LA    4,WFDECZN
         LA    5,15
WFSKIP   CLI   0(4),C'0'
         BNE   WFPAD
         LA    6,1
         CR    5,6
         BE    WFPAD
         LA    4,1(4)
         BCT   5,WFSKIP
*
* R5 is now the digit count.  Pad on the left to WFWIDTH, counting a
* minus sign as part of the field.  A width of zero is the %N case.
*
WFPAD    L     2,WFWIDTH
         LTR   2,2
         BZ    WFSIGNO
         SR    2,5
         S     2,WFSIGN
         BNP   WFSIGNO
WFPADLP  LA    7,64
         BAL   10,WFPUTC
         BCT   2,WFPADLP
WFSIGNO  L     6,WFSIGN
         LTR   6,6
         BZ    WFDCOPY
         LA    7,96
         BAL   10,WFPUTC
WFDCOPY  SR    7,7
         IC    7,0(4)
         BAL   10,WFPUTC
         LA    4,1(4)
         BCT   5,WFDCOPY
         L     8,WFREM
         L     14,WFFMTP
         B     WFLITLP
*
* Emit exactly WFWIDTH hexadecimal digits from the current argument.
* This mirrors historical WRITEHEX: fixed width, zero filled, high
* nibbles first. Regression 057 establishes width 4.
*
WFHEX    ST    8,WFREM
         ST    14,WFFMTP
         ST    7,WFHEXVAL
         L     5,WFWIDTH
         LTR   5,5
         BZ    WFHEXDN
         LR    2,5
         BCTR  2,0
         SLL   2,2
WFHEXLP  L     7,WFHEXVAL
         SRL   7,0(2)
         N     7,WFHEXMSK
         C     7,WFHEXNIN
         BL    WFHEXDIG
         A     7,WFHEXAO
         B     WFHEXOUT
WFHEXDIG A     7,WFHEXZO
WFHEXOUT BAL   10,WFPUTC
         SH    2,WFHXFOUR
         BCT   5,WFHEXLP
WFHEXDN  L     8,WFREM
         L     14,WFFMTP
         B     WFLITLP
*
* Emit exactly WFWIDTH octal digits from the current argument.
* This mirrors historical WRITEOCT: fixed width, zero filled, high
* 3-bit groups first. Regression 058 establishes width 4.
*
WFOCT    ST    8,WFREM
         ST    14,WFFMTP
         ST    7,WFOCTVAL
         L     5,WFWIDTH
         LTR   5,5
         BZ    WFOCTDN
         LR    2,5
         BCTR  2,0
         LR    6,2
         SLL   2,1
         AR    2,6
WFOCTLP  L     7,WFOCTVAL
         SRL   7,0(2)
         N     7,WFOCTMSK
         A     7,WFHEXZO
         BAL   10,WFPUTC
         SH    2,WFOCTTHR
         BCT   5,WFOCTLP
WFOCTDN  L     8,WFREM
         L     14,WFFMTP
         B     WFLITLP
*
* Emit a BCPL string argument in R7.  Preserve the format cursor and
* remaining format length in R14/R8 while the string bytes are copied.
*
WFSTR    LR    4,7
         SLL   4,2
         SR    5,5
         IC    5,0(4)
         LA    4,1(4)
WFSTRLP  LTR   5,5
         BZ    WFLITLP
         SR    7,7
         IC    7,0(4)
         BAL   10,WFPUTC
         LA    4,1(4)
         BCTR  5,0
         B     WFSTRLP
*
* Fetch the next saved formatting argument into R7 and advance the
* bootstrap argument cursor.  Test 055 exercises R8 then R9.
*
WFNEXT   L     6,WFARGIX
         SLL   6,2
         LA    4,WFARGS
         AR    4,6
         L     7,0(4)
         L     6,WFARGIX
         LA    6,1(6)
         ST    6,WFARGIX
         BR    10
*
* Reload the argument most recently returned by WFNEXT.  The negative
* sign append in WFNUM temporarily consumes R7.
*
WFLAST   L     6,WFARGIX
         BCTR  6,0
         SLL   6,2
         LA    4,WFARGS
         AR    4,6
         L     7,0(4)
         BR    10
*
* Append R7 low byte through the installed BCPL output service.
* Return through R10, which is scratch for this bootstrap WRITEF.
*
WFPUTC   LA    6,132
         CR    9,6
         BNL   WFPUTRT
         LA    6,WFBUF
         AR    6,9
         STC   7,0(6)
         LA    9,1(9)
WFPUTRT  BR    10
WFLITDN  ST    9,WFLEN
         LM    2,6,WFREGSV
         STM   0,15,WFALLSV
         LR    8,10
         LA    1,WFBUF
         L     2,WFLEN
         L     9,=A(IODIAG)
         BALR  14,9
         LR    10,8
         LM    0,15,WFALLSV
         L     4,0(5)
         BCR   15,6
*
WFALLSV  DS    16F
WFLEN    DC    F'0'
WFBUF    DS    CL132
WFREGSV  DS    5F
WFARGS   DS    2F
WFARGIX  DC    F'0'
WFWIDTH  DC    F'0'
WFSIGN   DC    F'0'
WFZERO   DC    X'000000F0'
WFHEXMSK DC    F'15'
WFHEXNIN DC    F'10'
WFHEXAO  DC    F'183'
WFHEXZO  DC    F'240'
WFHXFOUR DC   H'4'
WFHEXVAL DC    F'0'
WFOCTMSK DC    F'7'
WFOCTTHR DC    H'3'
WFOCTVAL DC    F'0'
WFREM    DC    F'0'
WFFMTP   DC    A(0)
WFDECPK  DS    D
WFDECZN  DS    CL15
*
***********************************************************************
* G85/G86 are supplied by separate BCPLBYTE CSECT.
*
***********************************************************************
* GETVEC(N) -> R7 -- WIP DYNAMIC STORAGE
*
* Regression 27 success-path implementation.
*
* BCPL VEC N has indices 0..N, so GETVEC(N) supplies N+1 payload
* fullwords.  Twelve private bytes precede the payload and mirror the
* historical VECAREA fields VECBASE, VECLEN, and VECNEXT.
*
* Regression 30 changes allocation to conditional GETMAIN EC.
* GETVEC returns zero for a negative or overlarge size, or an MVS
* allocation failure.  N<=4194299 keeps the byte count within 24 bits.
*
* GETMAIN EC returns its address through A= and completion in R15.
* Generated BCPL requires R0=0 and R1-R3 to hold permanent constants,
* R5 to remain P, R6 to remain L, and R15 to remain W.  Preserve them
* explicitly across the MVS service as defensive runtime discipline.
* Test 32 ultimately identified a separate RETIMPL error, not GETMAIN
* register corruption.
***********************************************************************
* BCPLMEM external allocator routines.
*
***********************************************************************
DEBUGINT XC    DBGPOS(4),DBGPOS
         LTR   7,7
         BNM   DBGCVT
         LA    10,C'-'
         BAL   14,DBGAPND
DBGCVT   CVD   7,DECPACK
         UNPK  DECZON(15),DECPACK(8)
         OI    DECZON+14,X'F0'
         LA    8,DECZON
         LA    9,15
DBGSKIP  CLI   0(8),C'0'
         BNE   DBGOUT
         LA    4,1
         CR    9,4
         BE    DBGOUT
         LA    8,1(8)
         BCT   9,DBGSKIP
DBGOUT   SR    10,10
         IC    10,0(8)
         BAL   14,DBGAPND
         LA    8,1(8)
         BCT   9,DBGOUT
         STM   0,15,DBGSV
         LR    8,10
         LA    1,DBGBUF
         L     2,DBGPOS
         L     9,=A(IODIAG)
         BALR  14,9
         LR    10,8
         LM    0,15,DBGSV
         L     4,0(5)
         BCR   15,6
*
* Append one EBCDIC byte from R10.  R14 is local linkage.
*
DBGAPND  L     4,DBGPOS
         LA    7,132
         CR    4,7
         BNL   DBGARET
         LA    7,DBGBUF
         AR    7,4
         STC   10,0(7)
         LA    4,1(4)
         ST    4,DBGPOS
DBGARET  BR    14
*
***********************************************************************
***********************************************************************
* WIP DATA
***********************************************************************
         DS    0F
MSVSAVE  DS    18F
* Historical USERSAVE-compatible G6 list-head positions.
* The leading 18 words remain the ordinary MVS save area (R13).
* Unimplemented intervening fields are reserved, not emulated.
         DS    11F
MSVLOAD  DC    F'0'              G6!29, byte-pointer load-list head
         DS    18F
MSVFREE  DC    F'0'              G6!48, byte-pointer free-area head
MBRT10   DC    F'0'
* Original MVS EXEC parameter list (R1), retained at entry.
PARMLIST DC    F'0'
MODBASE  DC    F'0'
MODEND   DC    F'0'
TRAILER  DC    F'0'
*
* GETVEC WIP allocation state.
* VECLIST is a byte pointer to the first three-word control record.
*
* Allocator state moved to BCPLMEM.
*
* R13 save area precedes the data controls.
*
* Contiguous GETMAIN layout: 700 global fullwords, 16384 stack
* fullwords, and 256 bytes of provisional clearance.  Dynamic backing
* addresses are saved in static controls.
* The GETMAIN block is released as a unit during FINISH/error exit.
*
GLOBCNT  EQU   699
GVBYTES  EQU   (GLOBCNT+1)*4
DYNLEN   DC    F'68592'
DYNBASE  DC    F'0'
DYNWORK  DC    F'0'
DYNEND   DC    F'0'
RELRET   DC    F'0'
STOPRC   DC    F'0'
R1GVEC   DC    F'0'
R1OWNP   DC    A(R1OWNB)
R1REAS   DC    F'0'
R1CODE   DC    F'0'
         DS    0F
R1OWNB   DS    CL700
*
* DEBUGINT state remains local; QSAM stream state belongs to BCPLIO.
*
DBGSV    DS    16F
DBGPOS   DC    F'0'
DBGBUF   DS    CL132
DECPACK  DS    D
DECZON   DS    CL15
* Retired obsolete local output DCBs, buffers, and stream handles.

*
* MVS EXEC PARM pseudo-stream: independently selectable via FINDPARM.
* No DCB/GET: PARM bytes are held by MVS for this task step.
         DS    0F
* Input/PARM state, DCBs and EODAD are BCPLIO-owned.

*
* Stack marker initialization and historical clearance remain separate
* work.  No static workspace is reserved in this CSECT.
*
         END   BCPLMAIN
/*
//ASMR     EXEC PGM=IFOX00,REGION=256K,
//             PARM='OBJECT,NODECK,LIST,XREF(FULL),ESD,RLD',
//             COND=(0,NE,COMP)
//SYSLIB   DD  DSN=SYS1.MACLIB,DISP=SHR
//SYSUT1   DD  UNIT=SYSDA,SPACE=(1700,(600,100))
//SYSUT2   DD  UNIT=SYSDA,SPACE=(1700,(300,50))
//SYSUT3   DD  UNIT=SYSDA,SPACE=(1700,(300,50))
//SYSPRINT DD  SYSOUT=*
//SYSPUNCH DD  DUMMY
//SYSGO    DD  DSN=&&R4ROBJ,UNIT=SYSDA,
//             SPACE=(80,(300,100)),DISP=(NEW,PASS),
//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)
//SYSIN    DD  *
***********************************************************************
* BCPL FOR MVS 3.8 RECONSTRUCTION - BCPLRGS
*
* Generic optional package registrar and finalizer.
* RGINIT checks selected BCRG/BCEX descriptors and publishes
* optional globals only after complete validation.
*
* INTERFACE:
* RGINIT runs before START; detects descriptor, ownership,
* version, and dependency errors.
* RGFINI runs finalizers in reverse order before IOFIN.
* Uses approved BCRG/BCEX version 1 and R.0 A-H ABI.
*
* LIMITATIONS:
* Selected package linker addresses require source review;
* the registrar does not protect against malicious pointers.
* Accepted MVS evidence used temporary objects.
***********************************************************************

RGINIT   CSECT
         ENTRY RGINIT,REGCOUNT,REGFINTB
         EXTRN BCRGBEG,BCRGEND
         STM   14,12,12(13)
         LR    12,15
         USING RGINIT,12
         LA    11,4095(12)
         LA    11,1(11)
         USING RGINIT+4096,11
         LA    2,RSAVE
         ST    13,4(2)
         ST    2,8(13)
         LR    13,2
         XC    REGCOUNT(4),REGCOUNT
         XC    RGONCE(4),RGONCE
         XC    RGERR(4),RGERR
         L     10,0(1)
         ST    10,RGGBASE
         L     2,4(1)
         ST    2,RGOWNER
         L     9,=A(BCRGBEG)
         L     4,=A(BCRGEND)
* BOUNDS FIRST; NEVER READ AN INVALID FIXED HEADER.
         LR    0,9
         N     0,=F'3'
         BNZ   ERR1001
         LR    0,4
         N     0,=F'3'
         BNZ   ERR1001
         LTR   9,9
         BNP   ERR1001
         LTR   4,4
         BNP   ERR1001
         CR    4,9
         BNH   ERR1001
         LR    3,4
         SR    3,9
         C     3,=F'28'
         BL    ERR1001
         C     3,=F'540'
         BH    ERR1001
         CLC   0(4,9),=CL4'BCRG'
         BNE   ERR1002
         CLC   4(4,9),=F'1'
         BNE   ERR1002
         CLC   8(4,9),=F'28'
         BNE   ERR1002
         CLC   24(4,9),=F'0'
         BNE   ERR1002
         L     7,16(9)
         L     6,20(9)
         LTR   7,7
         BM    ERR1003
         LTR   6,6
         BM    ERR1003
         C     7,=F'32'
         BH    ERR1003
         C     6,=F'32'
         BH    ERR1003
         ST    7,RGCNT
         ST    6,RGREQN
         SLL   7,3
         SLL   6,3
         AR    7,6
         A     7,=F'28'
         CR    7,3
         BNE   ERR1003
         C     7,12(9)
         BNE   ERR1003
         LA    8,28(9)
         ST    8,RGSELECT
         L     1,RGCNT
         SLL   1,3
         AR    1,8
         ST    1,RGREQP
         XC    RGIDX(4),RGIDX
PKNEXT   L     6,RGIDX
         C     6,RGCNT
         BNL   REQLIST
         L     8,RGSELECT
         SLL   6,3
         AR    8,6
         L     5,0(8)
         L     4,4(8)
         ST    5,RGPKG
         ST    4,RGPKEND
         LR    0,5
         N     0,=F'3'
         BNZ   ERR1004
         LR    0,4
         N     0,=F'3'
         BNZ   ERR1004
         LTR   5,5
         BNP   ERR1004
         LTR   4,4
         BNP   ERR1004
         CR    4,5
         BNH   ERR1004
         LR    3,4
         SR    3,5
         C     3,=F'56'
         BL    ERR1004
         C     3,=F'368'
         BH    ERR1004
         CLC   0(4,5),=CL4'BCEX'
         BNE   ERR1005
         CLC   4(4,5),=F'1'
         BNE   ERR1005
         CLC   8(4,5),=F'48'
         BNE   ERR1005
         CLC   44(4,5),=F'0'
         BNE   ERR1005
         L     6,32(5)
         L     7,40(5)
         LTR   6,6
         BNP   ERR1006
         LTR   7,7
         BM    ERR1006
         C     6,=F'8'
         BH    ERR1006
         C     7,=F'16'
         BH    ERR1006
         ST    6,RGK
         ST    7,RGD
         L     0,24(5)
         LTR   0,0
         BNP   ERR1005
         L     0,28(5)
         LTR   0,0
         BM    ERR1005
         SLL   6,3
         SLL   7,4
         AR    6,7
         A     6,=F'48'
         CR    6,3
         BNE   ERR1006
         C     6,12(5)
         BNE   ERR1006
         CLC   16(8,5),=CL8' '
         BE    ERR1007
* ALREADY VALIDATED PACKAGE IDS MUST BE UNIQUE.
         XC    RGSCAN(4),RGSCAN
IDPRIOR  L     4,RGSCAN
         C     4,RGIDX
         BNL   EXBEGIN
         L     8,RGSELECT
         SLL   4,3
         AR    8,4
         L     8,0(8)
         CLC   16(8,8),16(5)
         BE    ERR1007
         LA    4,1(4)
         ST    4,RGSCAN
         B     IDPRIOR
EXBEGIN  XC    RGEXI(4),RGEXI
EXNEXT   L     6,RGEXI
         C     6,RGK
         BNL   DEBEGIN
         L     3,RGPKG
         SLL   6,3
         LA    3,48(3)
         AR    3,6
         L     1,0(3)
         LTR   1,1
         BNP   ERR1008
         C     1,=F'699'
         BH    ERR1008
         L     2,4(3)
         LTR   2,2
         BNP   ERR1008
         LR    0,2
         N     0,=F'1'
         BNZ   ERR1008
* TEST CURRENT EFFECTIVE G SLOT, INCLUDING ACTUAL APP/BLIB/CORE.
         SLL   1,2
         LR    4,10
         AR    4,1
         L     2,0(4)
         L     4,=X'C7D3F000'
         AR    4,1
         CR    2,4
         BNE   ERR1009
* VERIFY THE PRIVATE PRIOR-WRITER LEDGER, NOT ONLY LAST G VALUE.
         L     4,RGOWNER
         LTR   4,4
         BZ    ERR1009
         SRL   1,2
         AR    4,1
         CLI   0(4),X'00'
         BNE   ERR1009
* CHECK EARLIER EXPORTS IN THIS DESCRIPTOR.
         XC    RGSCAN(4),RGSCAN
EXSAME   L     4,RGSCAN
         C     4,RGEXI
         BNL   EXOTHER
         SLL   4,3
         LA    8,48(5)
         AR    8,4
         L     2,0(3)
         C     2,0(8)
         BE    ERR1008
         L     2,4(3)
         C     2,4(8)
         BE    ERR1008
         L     4,RGSCAN
         LA    4,1(4)
         ST    4,RGSCAN
         B     EXSAME
EXOTHER  XC    RGSCAN(4),RGSCAN
EXOPKG  L     4,RGSCAN
         C     4,RGIDX
         BNL   EXDONE
         L     8,RGSELECT
         SLL   4,3
         AR    8,4
         L     8,0(8)
         L     7,32(8)
         LA    8,48(8)
         L     2,0(3)
EXPLOOK  C     2,0(8)
         BE    ERR1008
         L     0,4(3)
         C     0,4(8)
         BE    ERR1008
         LA    8,8(8)
         BCT   7,EXPLOOK
         L     4,RGSCAN
         LA    4,1(4)
         ST    4,RGSCAN
         B     EXOPKG
EXDONE   L     6,RGEXI
         LA    6,1(6)
         ST    6,RGEXI
         B     EXNEXT
* DEPENDENCIES MUST ALREADY HAVE BEEN SELECTED (AND VALIDATED).
DEBEGIN  XC    RGDEPI(4),RGDEPI
DENEXT   L     6,RGDEPI
         C     6,RGD
         BNL   PKDONE
         SLL   6,4
         L     8,RGK
         SLL   8,3
         A     8,=F'48'
         AR    8,5
         AR    8,6
         ST    8,RGDEPTR
         CLC   0(8,8),=CL8' '
         BE    ERR1014
         CLC   0(8,8),16(5)
         BE    ERR1014
* DO NOT ACCEPT DUPLICATED REQUIREMENTS FROM THIS PACKAGE.
         XC    RGSCAN(4),RGSCAN
DEDUPE   L     4,RGSCAN
         C     4,RGDEPI
         BNL   DEFIND
         SLL   4,4
         L     8,RGDEPTR
         SR    8,4
         L     1,RGDEPTR
         CLC   0(8,8),0(1)
         BE    ERR1014
         L     8,RGDEPTR
         L     4,RGSCAN
         LA    4,1(4)
         ST    4,RGSCAN
         B     DEDUPE
DEFIND   XC    RGSCAN(4),RGSCAN
DEPKGLP  L     4,RGSCAN
         C     4,RGCNT
         BNL   ERR1010
         L     8,RGSELECT
         SLL   4,3
         AR    8,4
         L     8,0(8)
         L     1,RGDEPTR
         CLC   0(8,1),16(8)
         BE    DEPMATCH
         L     4,RGSCAN
         LA    4,1(4)
         ST    4,RGSCAN
         B     DEPKGLP
DEPMATCH C     4,RGIDX
         BNL   ERR1012
         L     1,RGDEPTR
         L     2,8(1)
         C     2,24(8)
         BNE   ERR1011
         L     2,12(1)
         C     2,28(8)
         BH    ERR1011
         L     6,RGDEPI
         LA    6,1(6)
         ST    6,RGDEPI
         B     DENEXT
PKDONE   L     6,RGIDX
         L     8,RGPKG
         L     1,36(8)
* SOURCE-TRUSTED LINKER ADDRESS; RUNTIME CAN CHECK ALIGNMENT.
         LTR   1,1
         BZ    FINSTORE
         BM    ERR1013
         LR    0,1
         N     0,=F'1'
         BNZ   ERR1013
FINSTORE L     8,=A(REGFINTB)
         SLL   6,2
         AR    8,6
         ST    1,0(8)
         L     6,RGIDX
         LA    6,1(6)
         ST    6,RGIDX
         B     PKNEXT
* APPLICATION REQUIRED IDS MAY NOT REFER TO AN UNSELECTED PACKAGE.
REQLIST  XC    RGREQI(4),RGREQI
REQNEXT  L     6,RGREQI
         C     6,RGREQN
         BNL   PUBLISH
         SLL   6,3
         L     9,RGREQP
         AR    9,6
         CLC   0(8,9),=CL8' '
         BE    ERR1007
         XC    RGSCAN(4),RGSCAN
REQDUPE  L     4,RGSCAN
         C     4,RGREQI
         BNL   REQFIND
         SLL   4,3
         L     1,RGREQP
         AR    1,4
         CLC   0(8,1),0(9)
         BE    ERR1007
         L     4,RGSCAN
         LA    4,1(4)
         ST    4,RGSCAN
         B     REQDUPE
REQFIND  XC    RGSCAN(4),RGSCAN
REQLOOK  L     4,RGSCAN
         C     4,RGCNT
         BNL   ERR1010
         L     8,RGSELECT
         SLL   4,3
         AR    8,4
         L     8,0(8)
         CLC   0(8,9),16(8)
         BE    REQFOUND
         L     4,RGSCAN
         LA    4,1(4)
         ST    4,RGSCAN
         B     REQLOOK
REQFOUND L     6,RGREQI
         LA    6,1(6)
         ST    6,RGREQI
         B     REQNEXT
* ONLY NOW CAN OPTIONAL GLOBALS BECOME VISIBLE TO START.
PUBLISH  XC    RGIDX(4),RGIDX
PUBPKG   L     6,RGIDX
         C     6,RGCNT
         BNL   ALLDONE
         SLL   6,3
         L     8,RGSELECT
         AR    8,6
         L     5,0(8)
         L     7,32(5)
         LA    5,48(5)
PUBENT   L     1,0(5)
         SLL   1,2
         AR    1,10
         L     2,4(5)
         ST    2,0(1)
         LA    5,8(5)
         BCT   7,PUBENT
         L     6,RGIDX
         LA    6,1(6)
         ST    6,RGIDX
         B     PUBPKG
ALLDONE  L     0,RGCNT
         ST    0,REGCOUNT
         XC    RGERR(4),RGERR
         B     REGRET
ERR1001  WTO   'BCPLREG 1001 INVALID REGISTRY EXTENT'
         LA    15,1001
         B     REGFAIL
ERR1002  WTO   'BCPLREG 1002 INVALID REGISTRY HEADER'
         LA    15,1002
         B     REGFAIL
ERR1003  WTO   'BCPLREG 1003 INVALID REGISTRY COUNTS'
         LA    15,1003
         B     REGFAIL
ERR1004  WTO   'BCPLREG 1004 INVALID PACKAGE EXTENT'
         LA    15,1004
         B     REGFAIL
ERR1005  WTO   'BCPLREG 1005 INVALID PACKAGE HEADER'
         LA    15,1005
         B     REGFAIL
ERR1006  WTO   'BCPLREG 1006 INVALID PACKAGE COUNTS'
         LA    15,1006
         B     REGFAIL
ERR1007  WTO   'BCPLREG 1007 INVALID PACKAGE IDENTIFIER'
         LA    15,1007
         B     REGFAIL
ERR1008  WTO   'BCPLREG 1008 INVALID EXPORT ENTRY'
         LA    15,1008
         B     REGFAIL
ERR1009  WTO   'BCPLREG 1009 GLOBAL OWNERSHIP COLLISION'
         LA    15,1009
         B     REGFAIL
ERR1010  WTO   'BCPLREG 1010 MISSING PACKAGE REQUIREMENT'
         LA    15,1010
         B     REGFAIL
ERR1011  WTO   'BCPLREG 1011 INCOMPATIBLE PACKAGE VERSION'
         LA    15,1011
         B     REGFAIL
ERR1012  WTO   'BCPLREG 1012 DEPENDENCY ORDER FAILURE'
         LA    15,1012
         B     REGFAIL
ERR1013  WTO   'BCPLREG 1013 INVALID FINALIZER ADDRESS'
         LA    15,1013
         B     REGFAIL
ERR1014  WTO   'BCPLREG 1014 INVALID DEPENDENCY RECORD'
         LA    15,1014
REGFAIL  ST    15,RGERR
         XC    REGCOUNT(4),REGCOUNT
REGRET   L     15,RGERR
         L     13,4(13)
         LM    14,14,12(13)
         LM    0,12,20(13)
         BR    14
         DS    0F
RSAVE    DS    18F
RGGBASE  DC    F'0'
RGOWNER  DC    F'0'
RGSELECT DC    F'0'
RGCNT    DC    F'0'
RGREQN   DC    F'0'
RGREQP   DC    F'0'
RGIDX    DC    F'0'
RGPKG    DC    F'0'
RGPKEND  DC    F'0'
RGK      DC    F'0'
RGD      DC    F'0'
RGEXI    DC    F'0'
RGDEPI   DC    F'0'
RGDEPTR  DC    F'0'
RGREQI   DC    F'0'
RGSCAN   DC    F'0'
RGONCE   DC    F'0'
RGERR    DC    F'0'
REGCOUNT DC    F'0'
REGFINTB DS    32F
         LTORG
***********************************************************************
* GENERIC FINALIZER: REVERSE SELECTED ORDER, EXACTLY ONCE.
* R1 -> TWO FULLWORDS REASON (0 FINISH,1 STOP), REQUESTED STOP CODE.
* STATUS 8 MEANS AT LEAST ONE FINALIZER RETURNED NONZERO.
***********************************************************************
RGFINI   CSECT
         ENTRY RGFINI
         STM   14,12,12(13)
         LR    12,15
         USING RGFINI,12
         LA    2,FSAVE
         ST    13,4(2)
         ST    2,8(13)
         LR    13,2
         ST    1,FPARAM
         XC    FERROR(4),FERROR
         L     5,=A(REGCOUNT)
         L     6,0(5)
         XC    0(4,5),0(5)
         LTR   6,6
         BZ    FRETURN
         L     4,=A(REGFINTB)
FINLOOP  LR    3,6
         BCTR  3,0
         SLL   3,2
         AR    3,4
         L     15,0(3)
         LTR   15,15
         BZ    FINNEXT
         L     1,FPARAM
         BALR  14,15
         LTR   15,15
         BZ    FINNEXT
         LA    0,8
         ST    0,FERROR
         WTO   'BCPLREG 2001 FINALIZER RETURNED NONZERO'
FINNEXT  BCT   6,FINLOOP
FRETURN  L     15,FERROR
         L     13,4(13)
         LM    14,14,12(13)
         LM    0,12,20(13)
         BR    14
         DS    0F
FSAVE    DS    18F
FPARAM   DC    F'0'
FERROR   DC    F'0'
         LTORG
         END   RGINIT
/*
//ASMP     EXEC PGM=IFOX00,REGION=256K,
//             PARM='OBJECT,NODECK,LIST,XREF(FULL),ESD,RLD',
//             COND=(0,NE,COMP)
//SYSLIB   DD  DSN=SYS1.MACLIB,DISP=SHR
//SYSUT1   DD  UNIT=SYSDA,SPACE=(1700,(600,100))
//SYSUT2   DD  UNIT=SYSDA,SPACE=(1700,(300,50))
//SYSUT3   DD  UNIT=SYSDA,SPACE=(1700,(300,50))
//SYSPRINT DD  SYSOUT=*
//SYSPUNCH DD  DUMMY
//SYSGO    DD  DSN=&&R4POBJ,UNIT=SYSDA,
//             SPACE=(80,(300,100)),DISP=(NEW,PASS),
//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)
//SYSIN    DD  *
***********************************************************************
* BCPLDEMO BCEX V1: 48-BYTE HEADER + ONE 8-BYTE DISPATCHER EXPORT.
* NO DEPENDENCIES AND NO FINALIZER.  IEWL RELOCATES DMODISP.
***********************************************************************
DMODESC  CSECT
         ENTRY DMOBEG,DMOEND
DMOBEG   DS    0F
         DC    CL4'BCEX'
         DC    F'1',F'48',F'56'
         DC    CL8'BCPLDEMO'
         DC    F'1',F'0',F'1',F'0',F'0',F'0'
         DC    F'203',A(DMODISP)
DMOEND   EQU   *
***********************************************************************
* BCPLDEMO: PERMANENT OPTIONAL PACKAGE, PUBLIC DISPATCHER G!203.
* DEMOSVC IS THE BCPL GLOBAL NAME; DMODISP IS THE IEWL ENTRY SYMBOL.
* NATIVE BCPL ABI: R7 OPCODE/RESULT; R8 VECTOR; R9 WORD CAPACITY.
* BCPL POINTERS ARE WORD ADDRESSES; SHIFT BY 2 ONLY AFTER VALIDATION.
* EXAMPLE IS STATELESS: NO INIT AND NO FINALIZER.
***********************************************************************
DMODISP  CSECT
         ENTRY DMODISP
         USING DMODISP,4
         STM   4,9,0(15)
         LR    5,15
         LTR   7,7
         BNZ   OTHEROP
*
* OPCODE 0: SHARED QUERY V1.  (0,0,0) IS THE SIZE INQUIRY.
* REJECT BAD PAIRS BEFORE CAPACITY CHECK; NEVER PARTIALLY WRITE.
*
         LTR   8,8
         BNZ   QPTR
         LTR   9,9
         BNZ   BADARG
         LA    7,6
         BCR   15,11
QPTR     LTR   9,9
         BM    BADARG
         C     9,=F'6'
         BL    SHORT
         SLL   8,2
         LA    14,1
         ST    14,0(8)
         ST    14,4(8)
         SR    14,14
         ST    14,8(8)
         LA    14,6
         ST    14,12(8)
         LA    14,1
         ST    14,16(8)
         SR    14,14
         ST    14,20(8)
         LA    7,6
         BCR   15,11
*
* OPCODE 1: GETVALUES(VEC, CAPACITY); THREE BCPL FULLWORDS.
* RESULT IS 3 OR -1 TOO SMALL OR -3 BAD ARGUMENT.
* CONTENTS 10,20,30 ARE FIXED SAMPLE DATA, NOT POINTERS.
*
OTHEROP  C     7,=F'1'
         BNE   BADOP
         LTR   8,8
         BZ    BADARG
         LTR   9,9
         BM    BADARG
         C     9,=F'3'
         BL    SHORT
         SLL   8,2
         LA    14,10
         ST    14,0(8)
         LA    14,20
         ST    14,4(8)
         LA    14,30
         ST    14,8(8)
         LA    7,3
         BCR   15,11
BADOP    L     7,=F'-2'
         BCR   15,11
SHORT    L     7,=F'-1'
         BCR   15,11
BADARG   L     7,=F'-3'
         BCR   15,11
         LTORG
         END   DMODISP
/*
//ASMG     EXEC PGM=IFOX00,REGION=256K,
//             PARM='OBJECT,DECK,LIST,XREF(FULL),ESD,RLD',
//             COND=(0,NE,COMP)
//SYSLIB   DD  DSN=SYS1.MACLIB,DISP=SHR
//SYSUT1   DD  UNIT=SYSDA,SPACE=(1700,(600,100))
//SYSUT2   DD  UNIT=SYSDA,SPACE=(1700,(300,50))
//SYSUT3   DD  UNIT=SYSDA,SPACE=(1700,(300,50))
//SYSPRINT DD  SYSOUT=*
//SYSPUNCH DD  DSN=&&REGD,UNIT=SYSDA,
//             SPACE=(80,(100,20)),DISP=(NEW,PASS),
//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)
//SYSGO    DD  DUMMY
//SYSIN    DD  DSN=&&BCXPRE,DISP=(OLD,PASS)
//         DD  DSN=&&BCXCAT,DISP=(OLD,PASS)
//         DD  *
         BCXREQ BCPLDEMO
/*
//         DD  DSN=&&BCXPOST,DISP=(OLD,PASS)
//LINK     EXEC PGM=IEWL,REGION=256K,
//             PARM='NCAL,LIST,XREF,MAP',
//             COND=(0,NE)
//OBJ      DD  DSN=HERC02.BCPL.BOOT.OBJ,DISP=SHR
//PKGA     DD  DSN=&&R4POBJ,DISP=(OLD,PASS)
//SYSLIN   DD  DSN=&&R4AOBJ,DISP=(OLD,PASS)
//         DD  DSN=&&R4NOBJ,DISP=(OLD,PASS)
//         DD  DSN=&&R4ROBJ,DISP=(OLD,PASS)
//         DD  DSN=&&REGD,DISP=(OLD,PASS)
//         DD  *
 INCLUDE OBJ(BCPLIO)
 INCLUDE OBJ(BCPLMEM)
 INCLUDE OBJ(BCPLBYTE)
 INCLUDE OBJ(BCPLAPT)
 INCLUDE OBJ(BLIB)
 ENTRY R4APP
 NAME R4BCXIN(R)
/*
//SYSLMOD  DD  DSN=&&R4LOAD(R4BCXIN),
//             UNIT=SYSDA,SPACE=(1024,(50,20,1)),
//             DISP=(NEW,PASS)
//SYSUT1   DD  UNIT=SYSDA,SPACE=(1024,(50,20))
//SYSPRINT DD  SYSOUT=*
//GO       EXEC PGM=*.LINK.SYSLMOD,REGION=256K,
//             TIME=(,2),COND=(0,NE,LINK)
//SYSPRINT DD  SYSOUT=*,DCB=(RECFM=FB,LRECL=132,
//             BLKSIZE=132)
//SYSUDUMP DD  SYSOUT=*
//
