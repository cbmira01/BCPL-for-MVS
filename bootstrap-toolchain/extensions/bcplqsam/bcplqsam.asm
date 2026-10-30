***********************************************************************
* BCPLQSAM Q.3 V READ/WRITE VERIFIED; VB NATIVE CANDIDATE.
* ONE RELOCATABLE ASSEMBLY: BCEX + DISPATCHER + FINALIZER + QSAM.
* OWNER: BCPL FOR MVS 3.8 RECONSTRUCTION; G!200 QSAMSVC.
* OPERATIONS: QUERY=0 OPEN=1 READ=2 WRITE=3 CLOSE=4 INFO=5.
* REQUIRES IFOX / SYS1.MACLIB AND R.1 GENERIC BCPLREG.
* NONREENTRANT, SINGLE-TASK; Q.2 CLOSED; Q.3 IN PROGRESS.
***********************************************************************
QSMDESC  CSECT
         ENTRY QSMBEG,QSMEND
QSMBEG   DS    0F
         DC    CL4'BCEX'
         DC    F'1',F'48',F'56'
         DC    CL8'BCPLQSAM'
         DC    F'1',F'0',F'1',A(QSMFIN),F'0',F'0'
         DC    F'200',A(QSMDISP)
QSMEND   EQU   *
***********************************************************************
* NATIVE BCPL ENTRY. R7 OP/RESULT, R8/R9 WORD POINTERS.
* R11 RETURN, R4 EXECUTION BASE, R15 CALLER WORKSPACE.
* PRESERVE R0/R1 THROUGH MVS MACROS (CG370 PERMANENT REGISTERS).
***********************************************************************
QSMDISP  CSECT
         ENTRY QSMDISP
         USING QSMDISP,4
         STM   4,9,0(15)
         LR    5,15
         STM   0,1,24(5)
         LTR   7,7
         BZ    QSQUERY
         C     7,=F'1'
         BE    QSORD
         C     7,=F'2'
         BE    QSORD
         C     7,=F'3'
         BE    QSORD
         C     7,=F'4'
         BE    QSORD
         C     7,=F'5'
         BNE   QSBADOP
QSORD    LTR   8,8
         BNP   QSBADARG
         LTR   9,9
         BNP   QSBADARG
         SLL   8,2
         SLL   9,2
         XC    0(32,9),0(9)
         L     15,=A(QSMCORE)
         BALR  14,15
         LR    7,15
         ST    7,0(9)
         LM    0,1,24(5)
         BCR   15,11
* QUERY: FIVE OPERATIONS; F/FB AND V/VB CAPABILITIES.
QSQUERY  LTR   8,8
         BNZ   QSQPTR
         LTR   9,9
         BNZ   QSBADARG
         LA    7,6
         B     QSRET
QSQPTR   LTR   9,9
         BM    QSBADARG
         C     9,=F'6'
         BL    QSSHORT
         SLL   8,2
         LA    14,1
         ST    14,0(8)
         ST    14,4(8)
         SR    14,14
         ST    14,8(8)
         LA    14,6
         ST    14,12(8)
         LA    14,31
         ST    14,16(8)
         LA    14,3
         ST    14,20(8)
         LA    7,6
         B     QSRET
QSBADOP  L     7,=F'-2'
         B     QSRET
QSSHORT  L     7,=F'-1'
         B     QSRET
QSBADARG L     7,=F'-3'
QSRET    LM    0,1,24(5)
         BCR   15,11
         LTORG
***********************************************************************
* PRIVATE CONVENTIONAL-MVS CORE. R7=OP; R8 REQUEST BYTE PTR;
* R9 RESULT BYTE PTR; R15 RETURNS STATUS. ALL R2-R12 PRESERVED.
* SAVE AREA IS PACKAGE PRIVATE; THIS MODULE IS NOT REENTRANT.
***********************************************************************
QSMCORE  CSECT
         STM   14,12,12(13)
         LR    12,15
         USING QSMCORE,12
         LA    10,4095(12)
         LA    10,1(10)
         USING QSMCORE+4096,10
         LA    2,QCSSAVE
         ST    13,4(2)
         ST    2,8(13)
         LR    13,2
         L     11,=A(QSMCTRL)
         USING QSMCTRL,11
         ST    8,QCREQ
         ST    9,QCRES
         C     7,=F'1'
         BE    QCOPEN
         C     7,=F'2'
         BE    QCIORD
         C     7,=F'3'
         BE    QCIOWRT
         C     7,=F'4'
         BE    QCCLOSE
         C     7,=F'5'
         BE    QCINFO
         L     15,=F'-2'
         B     QCRET
* Q.2 HANDLE LOOKUP: ONLY WORD 3 MUST BE RESERVED ZERO.
QCIORD   LA    6,2
         B     QCIOENT
QCIOWRT  LA    6,3
QCIOENT  BAL   14,QCIOLKP
         LTR   15,15
         BNZ   QCRET
         L     8,QCREQ
         L     9,QCRES
         LR    7,6
         L     15,=A(QSMIO)
         BALR  14,15
         B     QCRET
QCIOLKP  L     8,QCREQ
         L     7,12(8)
         LTR   7,7
         BNZ   QCIOARG
         L     7,0(8)
         LTR   7,7
         BNP   QCIOBAD
         LA    4,QSSLOTS
         LA    3,16
QCIOLOOP CLC   0(4,4),=F'2'
         BNE   QCIONXT
         CLC   4(4,4),0(8)
         BE    QCIOOK
QCIONXT  LA    4,44(4)
         BCT   3,QCIOLOOP
QCIOBAD  L     15,=F'-7'
         BR    14
QCIOARG  L     15,=F'-3'
         BR    14
QCIOOK   SR    15,15
         BR    14
* CHECK RESERVED WORDS FOR OPEN.
QCOPEN   L     8,QCREQ
         L     7,12(8)
         LTR   7,7
         BNZ   QCARG
         L     7,8(8)
         LTR   7,7
         BNZ   QCARG
         L     7,4(8)
         C     7,=F'1'
         BE    QCMODE
         C     7,=F'2'
         BNE   QCARG
QCMODE   ST    7,QCMOD
         L     7,0(8)
         LTR   7,7
         BNP   QCARG
         SLL   7,2
* FORMAT NORMALIZED EBCDIC DDNAME IN PRIVATE EIGHT-BYTE SCRATCH.
         SR    3,3
         IC    3,0(7)
         LTR   3,3
         BZ    QCNAMEER
         C     3,=F'8'
         BH    QCNAMEER
         MVI   QCNAME,C' '
         MVC   QCNAME+1(7),QCNAME
         LA    7,1(7)
         LA    5,QCNAME
         SR    6,6
QNLOOP   SR    0,0
         IC    0,0(7)
         CLI   0(7),X'81'
         BL    QNUP
         CLI   0(7),X'89'
         BNH   QNLOW
         CLI   0(7),X'91'
         BL    QNUP
         CLI   0(7),X'99'
         BNH   QNLOW
         CLI   0(7),X'A2'
         BL    QNUP
         CLI   0(7),X'A9'
         BH    QNUP
QNLOW    O     0,=X'00000040'
QNUP     STC   0,0(5)
         CLI   0(5),X'C1'
         BL    QNSPEC
         CLI   0(5),X'C9'
         BNH   QNOK
         CLI   0(5),X'D1'
         BL    QNSPEC
         CLI   0(5),X'D9'
         BNH   QNOK
         CLI   0(5),X'E2'
         BL    QNSPEC
         CLI   0(5),X'E9'
         BNH   QNOK
QNSPEC   CLI   0(5),X'7C'
         BE    QNOK
         CLI   0(5),X'7B'
         BE    QNOK
         CLI   0(5),X'5B'
         BE    QNOK
         LTR   6,6
         BZ    QCNAMEER
         CLI   0(5),X'F0'
         BL    QCNAMEER
         CLI   0(5),X'F9'
         BH    QCNAMEER
QNOK     LA    6,1(6)
         LA    5,1(5)
         LA    7,1(7)
         CR    6,3
         BL    QNLOOP
* NONRECYCLED SIGNED HANDLE COUNTER: NEGATIVE MEANS EXHAUSTED.
         L     7,QSNEXT
         LTR   7,7
         BNP   QCRESERR
         LA    4,QSSLOTS
         LA    3,16
QCFREE   L     0,0(4)
         LTR   0,0
         BZ    QCRESERV
         LA    4,44(4)
         BCT   3,QCFREE
         B     QCRESERR
QCRESERV LA    0,1
         ST    0,0(4)
         L     0,QSLIVE
         A     0,=F'1'
         ST    0,QSLIVE
         ST    4,QCCUR
         L     7,QCMOD
         ST    7,8(4)
         C     7,=F'1'
         BE    QCIN
         L     2,20(4)
         B     QCSETDC
QCIN     L     2,16(4)
QCSETDC  ST    2,QCDC
* STATIC DCBs ARE REUSED; RESTORE THE PRE-OPEN DCB IMAGE EACH TIME.
* ONE SAVED 96-BYTE TEMPLATE PER SLOT PER MODE, LAZILY SNAPSHOTTED.
* THIS PRESERVES PER-SLOT EXLST RELOCATION THROUGH QSAM CLOSE/OPEN.
         BAL   14,QCDBCOPY
         MVC   40(8,2),QCNAME
         L     5,24(4)
         ST    5,QCJFCB
* RDJFCB PRECHECK: R15 4 DENOTES CONFIRMED MISSING DD.
         RDJFCB ((2))
         C     15,=F'4'
         BE    QCNOTDD
         LTR   15,15
         BNZ   QCNOPEN
         L     5,QCJFCB
         SR    3,3
         IC    3,100(5)
         LH    5,104(5)
         L     2,QCJFCB
         LH    6,102(2)
         BAL   14,QCVFORM
         LTR   15,15
         BNZ   QCPREBAD
         L     2,QCDC
         L     7,QCMOD
         C     7,=F'1'
         BE    QCOPENIN
         OPEN  ((2),(OUTPUT))
         B     QCOPENCK
QCOPENIN OPEN  ((2),(INPUT))
QCOPENCK ST    15,QCOSRC
         L     2,QCDC
* DCB +48 IS THE QSAM ACCESS-METHOD ENTRY, NOT AN OPEN BIT.
* USE THE ACCEPTED BCPLIO POST-OPEN NONZERO POINTER CHECK.
* R15 OPEN-MACRO RETURN SEMANTICS NEED TARGET MVS VALIDATION.
         L     0,48(2)
         LTR   0,0
         BZ    QCNOPEN
         L     4,QCCUR
         LA    0,2
         ST    0,0(4)
         L     0,QSDCBS
         A     0,=F'1'
         ST    0,QSDCBS
* CHECK EFFECTIVE DCB FIELDS AGAINST PREFLIGHT AND CEILING.
         SR    3,3
         IC    3,36(2)
         LH    5,82(2)
         LH    6,62(2)
         BAL   14,QCVFORM
         LTR   15,15
         BNZ   QCPOSTER
         L     4,QCCUR
         ST    0,28(4)
         ST    5,32(4)
         ST    6,36(4)
         ST    1,40(4)
* ONE INDEPENDENT, CONDITIONALLY CHECKED 1024-BYTE STAGE.
         GETMAIN RC,LV=1024
         LTR   15,15
         BNZ   QCSTFAIL
         L     4,QCCUR
         ST    1,12(4)
         L     0,QSSTAGES
         A     0,=F'1'
         ST    0,QSSTAGES
* INITIALIZE PRIVATE READ STATE BEFORE PUBLISH.
         LR    3,4
         LA    6,QSSLOTS
         SR    3,6
         SR    2,2
         D     2,=F'44'
         LA    6,QISTATES
         AR    6,3
         MVI   0(6),X'00'
         SLL   3,2
         LA    6,QIPENDS
         AR    6,3
         XC    0(4,6),0(6)
* PUBLIC HANDLE IS ISSUED ONLY AFTER ALL ACQUISITIONS SUCCEED.
         L     7,QSNEXT
         ST    7,4(4)
         L     8,QCRES
         ST    7,4(8)
* ISSUE THE FINAL POSITIVE ID WITHOUT SIGNED ADD OVERFLOW.
* ZERO IS A PERMANENT EXHAUSTION SENTINEL, NEVER RECYCLED.
         C     7,=X'7FFFFFFF'
         BE    QCEXHAUS
         A     7,=F'1'
         ST    7,QSNEXT
         B     QCHDONE
QCEXHAUS XC    QSNEXT(4),QSNEXT
QCHDONE  SR    15,15
         B     QCRET
QCNOTDD L   7,=F'-5'
         B     QCROLL
QCNOPEN  L     7,=F'-6'
         B     QCROLL
QCPREBAD LR    7,15
         B     QCROLL
* Q.1 CLEANUP ERROR PRECEDENCE NOT OWNER-APPROVED.
* RETAIN THE ORIGINAL PRIMARY ERROR FOR THE OFFLINE CANDIDATE.
* ANY FAILED ROLLBACK CLOSE IS QUARANTINED; MVS GATE REQUIRED.
QCPOSTER LR    7,15
         LTR   7,7
         BM    QCCLEAN
         L     7,=F'-6'
         B     QCCLEAN
QCSTFAIL L     7,=F'-11'
QCCLEAN  ST    7,QCERRPRI
         L     4,QCCUR
         L     15,=A(QSMCLS1)
         BALR  14,15
         L     7,QCERRPRI
QCROLL   L     4,QCCUR
         CLC   0(4,4),=F'1'
         BNE   QCROLLRT
         XC    0(16,4),0(4)
         XC    28(16,4),28(4)
         L     0,QSLIVE
         BCTR  0,0
         ST    0,QSLIVE
QCROLLRT LR    15,7
         B     QCRET
* CLOSE / INFO REQUIRE A LIVE, POSITIVE, EXACT HANDLE MATCH.
QCCLOSE  BAL   14,QCFIND
         LTR   15,15
         BNZ   QCRET
         L     15,=A(QSMCLS1)
         BALR  14,15
         B     QCRET
QCINFO   BAL   14,QCFIND
         LTR   15,15
         BNZ   QCRET
         L     8,QCRES
         L     0,28(4)
         ST    0,16(8)
         L     0,32(4)
         ST    0,20(8)
         L     0,36(4)
         ST    0,24(8)
         L     0,40(4)
         ST    0,28(8)
         SR    15,15
         B     QCRET
QCFIND   L     8,QCREQ
         L     7,12(8)
         LTR   7,7
         BNZ   QCFARG
         L     7,4(8)
         LTR   7,7
         BNZ   QCFARG
         L     7,8(8)
         LTR   7,7
         BNZ   QCFARG
         L     7,0(8)
         LTR   7,7
         BNP   QCFBAD
         LA    4,QSSLOTS
         LA    3,16
QCFLOOP  CLC   0(4,4),=F'2'
         BNE   QCFNEXT
         CLC   4(4,4),0(8)
         BE    QCFGOOD
QCFNEXT  LA    4,44(4)
         BCT   3,QCFLOOP
QCFBAD   L     15,=F'-7'
         BR    14
QCFGOOD  SR    15,15
         BR    14
QCFARG   L     15,=F'-3'
         BR    14
* ONE PRIVATE PRISTINE 96-BYTE DCB IMAGE PER SLOT AND MODE.
* ON FIRST OPEN SNAPSHOT STATIC IFOX-INITIALIZED DCB; ON REUSE
* RESTORE IT BEFORE PLACING THE NEW DDNAME. R4/R2 REMAIN INTACT.
QCDBCOPY LR    7,4
         LA    6,QSSLOTS
         SR    7,6
         SR    6,6
         D     6,=F'44'
* R7 IS ZERO-BASED SLOT INDEX; TWO COPIES PER SLOT.
         SLL   7,1
         L     6,QCMOD
         BCTR  6,0
         AR    7,6
* SAVED IMAGE OFFSET = 96 * (2*SLOT + MODE-1).
         LR    6,7
         SLL   6,6
         SLL   7,5
         AR    6,7
         LA    5,QSDCOPY
         AR    5,6
* EACH SAVED IMAGE STARTS ZERO; TEST ONLY ITS FIRST-USE FLAG.
         LR    7,4
         LA    6,QSSLOTS
         SR    7,6
         SR    6,6
         D     6,=F'44'
         SLL   7,1
         L     6,QCMOD
         BCTR  6,0
         AR    7,6
         LA    6,QSFIRST
         AR    6,7
         CLI   0(6),X'00'
         BNE   QCDREST
         MVC   0(96,5),0(2)
         MVI   0(6),X'01'
         BR    14
QCDREST  MVC   0(96,2),0(5)
         BR    14
* INPUTS R3=RAW RECFM, R5=LRECL, R6=BLKSIZE.
* OUTPUT R15 STATUS, R0 ENUM, R1 MAX APPLICATION DATA.
QCVFORM  LTR   5,5
         BNP   QCVSIZE
         C     5,=F'1024'
         BH    QCVSIZE
         LTR   6,6
         BNP   QCVSIZE
         C     6,=F'32760'
         BH    QCVSIZE
         C     3,=F'128'
         BE    QCVFIX
         C     3,=F'144'
         BE    QCVFB
         C     3,=F'148'
         BE    QCVFBA
         C     3,=F'64'
         BE    QCVVAR
         C     3,=F'80'
         BE    QCVVB
         L     15,=F'-9'
         BR    14
QCVFIX   CR    6,5
         BNE   QCVSIZE
         LA    0,1
         LR    1,5
         B     QCVOK
QCVFB    CR    6,5
         BL    QCVSIZE
         SR    0,0
         LR    1,6
         DR    0,5
         LTR   0,0
         BNZ   QCVSIZE
         LA    0,2
         LR    1,5
         B     QCVOK
* FBA IS FIXED ASA: BCPL OWNS BYTE ZERO, INCLUDED IN LRECL.
QCVFBA   CR    6,5
         BL    QCVSIZE
         SR    0,0
         LR    1,6
         DR    0,5
         LTR   0,0
         BNZ   QCVSIZE
         LA    0,5
         LR    1,5
         B     QCVOK
QCVVAR   LA    0,3
         B     QCVVCK
QCVVB    LA    0,4
QCVVCK   C     5,=F'4'
         BL    QCVSIZE
         LR    1,5
         LA    1,4(1)
         CR    6,1
         BL    QCVSIZE
         LR    1,5
         BCTR  1,0
         BCTR  1,0
         BCTR  1,0
         BCTR  1,0
QCVOK    SR    15,15
         BR    14
QCVSIZE  L     15,=F'-6'
         BR    14
QCNAMEER L     15,=F'-4'
         B     QCRET
QCRESERR L   15,=F'-11'
         B     QCRET
QCARG    L     15,=F'-3'
QCRET    ST    15,QCSTATUS
         L     13,4(13)
         LM    14,14,12(13)
         L     15,QCSTATUS
         LM    0,12,20(13)
         BR    14
         LTORG
* PRIVATE CORE FIELDS (NO OS-MODULE WRITE OWNERSHIP).
QCSSAVE  DS    18F
QCSTATUS DC    F'0'
QCNAME   DC    CL8' '
QCREQ    DC    F'0'
QCRES    DC    F'0'
QCMOD    DC    F'0'
QCCUR    DC    F'0'
QCDC     DC    F'0'
QCJFCB   DC    F'0'
QCOSRC   DC    F'0'
QCERRPRI DC   F'0'
***********************************************************************
* PER-HANDLE SAFE CLOSE. CALLED BY QSMCORE AND QSMFIN.
* R4 -> SLOT; R15=0 OR -14. NEVER RETRIES AN UNCERTAIN CLOSE.
* RETURNED-CLOSE TEST PATH REQUIRES SEPARATE OWNER GATE REVIEW.
***********************************************************************
QSMCLS1  CSECT
         USING QSMCLS1,12
         STM   14,12,12(13)
         LR    12,15
         LA    2,QSCSAVE
         ST    13,4(2)
         ST    2,8(13)
         LR    13,2
         L     11,=A(QSMCTRL)
         USING QSMCTRL,11
         ST    4,QSCCUR
         CLC   0(4,4),=F'2'
         BNE   QSCBAD
         LA    0,3
         ST    0,0(4)
         L     0,8(4)
         C     0,=F'1'
         BE    QSCIND
         L     2,20(4)
         B     QSCEXEC
QSCIND   L     2,16(4)
QSCEXEC  ST    2,QSCDCB
         CLOSE ((2))
* Q.1 PROVISIONAL RETURNED-CLOSE RULE; MVS GATE STILL OPEN.
* DCB +48 IS NOT A TESTED POST-CLOSE OWNERSHIP/OPEN BIT.
         LTR   15,15
         BNZ   QSCQUAR
         L     4,QSCCUR
         L     1,12(4)
         LTR   1,1
         BZ    QSCFREE
         FREEMAIN R,LV=1024,A=(1)
         L     0,QSSTAGES
         BCTR  0,0
         ST    0,QSSTAGES
QSCFREE  L     4,QSCCUR
* DISCARD PENDING/EOF STATE AFTER SAFE CLOSE.
         LR    3,4
         LA    6,QSSLOTS
         SR    3,6
         SR    2,2
         D     2,=F'44'
         LA    6,QISTATES
         AR    6,3
         MVI   0(6),X'00'
         SLL   3,2
         LA    6,QIPENDS
         AR    6,3
         XC    0(4,6),0(6)
         XC    0(16,4),0(4)
         XC    28(16,4),28(4)
         L     0,QSDCBS
         BCTR  0,0
         ST    0,QSDCBS
         L     0,QSLIVE
         BCTR  0,0
         ST    0,QSLIVE
         SR    15,15
         B     QSCRET
QSCQUAR  L     4,QSCCUR
         LA    0,4
         ST    0,0(4)
         XC    4(4,4),4(4)
         L     0,QSQUAR
         A     0,=F'1'
         ST    0,QSQUAR
QSCBAD   L     15,=F'-14'
QSCRET   ST    15,QSCSTAT
         L     13,4(13)
         LM    14,14,12(13)
         L     15,QSCSTAT
         LM    0,12,20(13)
         BR    14
         LTORG
QSCSAVE  DS    18F
QSCSTAT  DC    F'0'
QSCCUR   DC    F'0'
QSCDCB   DC    F'0'
***********************************************************************
* Q.3 V/VB MOVE-MODE RECORD I/O; Q.2 FIXED PRESERVED.
* R7 OP, R8 REQUEST, R9 RESULT, R4 LIVE SLOT; RETURN R15.
* EODAD/SYNAD EXIT THROUGH THIS NONREENTRANT ACTIVE FRAME.
***********************************************************************
QSMIO    CSECT
         USING QSMIO,12
         STM   14,12,12(13)
         LR    12,15
         LA    2,QISAVE
         ST    13,4(2)
         ST    2,8(13)
         LR    13,2
         L     11,=A(QSMCTRL)
         USING QSMCTRL,11
         ST    7,QIOOP
         ST    8,QIOREQ
         ST    9,QIORES
         ST    4,QIOCUR
         L     2,8(4)
         C     7,=F'2'
         BE    QIRDCHK
         C     2,=F'2'
         BNE   QIODIR
         B     QIFMTCHK
QIRDCHK  C     2,=F'1'
         BNE   QIODIR
QIFMTCHK L     2,28(4)
         C     2,=F'1'
         BE    QIPTRCHK
         C     2,=F'2'
         BE    QIPTRCHK
* V/VB SHARE RDW-BASED PRIVATE RECORD STAGING.
         C     2,=F'3'
         BE    QIPTRCHK
         C     2,=F'4'
         BE    QIPTRCHK
* FBA USES EXACT FIXED RECORD BYTES INCLUDING ASA CONTROL BYTE.
         C     2,=F'5'
         BNE   QIOFORM
QIPTRCHK L     8,QIOREQ
         L     7,4(8)
         LTR   7,7
         BNP   QIOARG
         SLL   7,2
         ST    7,QIOBUF
         L     7,8(8)
         LTR   7,7
         BM    QIOARG
         ST    7,QIOCNT
         L     1,12(4)
         LTR   1,1
         BZ    QIORESER
         L     7,QIOOP
         C     7,=F'3'
         BE    QIWRITE
* INDEPENDENT READY/PENDING/EOF STATE FOR EACH SLOT.
         LR    3,4
         LA    6,QSSLOTS
         SR    3,6
         SR    2,2
         D     2,=F'44'
         LA    6,QISTATES
         AR    6,3
         ST    6,QISTPTR
         SLL   3,2
         LA    6,QIPENDS
         AR    6,3
         ST    6,QIPNPTR
         L     6,QISTPTR
         CLI   0(6),X'02'
         BE    QIOEOF
         CLI   0(6),X'01'
         BE    QICAPCK
         CLI   0(6),X'00'
         BNE   QIOREADR
* USE SEPARATE DCB/RECORD REGISTERS: GET SETS R1 BEFORE R0.
         L     2,16(4)
         L     3,12(4)
         GET   (2),(3)
* MOVE-MODE V RECORD: PRIVATE STAGE HOLDS RDW + DATA.
         L     4,QIOCUR
         L     0,28(4)
         C     0,=F'3'
         BE    QIRVAR
         C     0,=F'4'
         BNE   QIRDFIX
QIRVAR   L     3,12(4)
         CLC   2(2,3),=H'0'
         BNE   QIRDBAD
         LH    0,0(3)
         C     0,=F'4'
         BL    QIRDBAD
         C     0,32(4)
         BH    QIRDBAD
         S     0,=F'4'
         B     QIRDSET
QIRDFIX  L     0,32(4)
QIRDSET  L     6,QIPNPTR
         ST    0,0(6)
         L     6,QISTPTR
         MVI   0(6),X'01'
QICAPCK  L     6,QIPNPTR
         L     5,0(6)
         L     3,QIOCNT
         CR    3,5
         BL    QIOSHORT
* R4/R5 DEST; R6/R7 SOURCE; MVCL COPIES EXACT BYTE LENGTH.
         L     4,QIOCUR
         L     6,12(4)
         CLC   28(4,4),=F'3'
         BE    QICOPYV
         CLC   28(4,4),=F'4'
         BNE   QICOPY
QICOPYV  LA    6,4(6)
QICOPY   L     4,QIOBUF
         LR    7,5
         MVCL  4,6
         L     6,QISTPTR
         MVI   0(6),X'00'
         L     6,QIPNPTR
         L     0,0(6)
         XC    0(4,6),0(6)
         L     8,QIORES
         ST    0,4(8)
         SR    15,15
         B     QIOEXIT
QIOSHORT L     8,QIORES
         ST    5,4(8)
         L     15,=F'-1'
         B     QIOEXIT
* MALFORMED RDW: LOCK THIS HANDLE INTO READ ERROR UNTIL CLOSE.
QIRDBAD  L     6,QISTPTR
         MVI   0(6),X'03'
         L     6,QIPNPTR
         XC    0(4,6),0(6)
         B     QIOREADR
* FIXED OUTPUT REQUIRES EXACT LRECL; VARIABLE OUTPUT ALLOWS 0..MAX.
QIWRITE  CLC   28(4,4),=F'3'
         BE    QIWVAR
         CLC   28(4,4),=F'4'
         BE    QIWVAR
         L     5,32(4)
         L     3,QIOCNT
         CR    3,5
         BNE   QIOLEN
         L     6,QIOBUF
         L     4,12(4)
         LR    7,5
         MVCL  4,6
         B     QIPUT
* QSAM V MOVE-MODE STAGE: RDW IN PRIVATE BYTES 0..3, DATA AT +4.
QIWVAR   L     5,QIOCNT
         C     5,40(4)
         BH    QIOLEN
         L     4,12(4)
         LA    4,4(4)
         L     6,QIOBUF
         LR    7,5
         MVCL  4,6
         L     4,QIOCUR
         L     6,12(4)
         L     0,QIOCNT
* R0 IS NOT A VALID LA BASE ON SYSTEM/370: ADD EXPLICITLY.
         A     0,=F'4'
         STH   0,0(6)
         XC    2(2,6),2(6)
QIPUT    L     4,QIOCUR
* PUT ALSO REQUIRES A SEPARATE RECORD-ADDRESS REGISTER.
         L     2,20(4)
         L     3,12(4)
         PUT   (2),(3)
         L     0,QIOCNT
         L     8,QIORES
         ST    0,4(8)
         SR    15,15
         B     QIOEXIT
* EODAD IS CONTROL TRANSFER, NEVER AN R15 STATUS.
E        DS    0H
QIOEOD   L     6,QISTPTR
         MVI   0(6),X'02'
         L     6,QIPNPTR
         XC    0(4,6),0(6)
QIOEOF   LA    15,1
         B     QIOEXIT
* RECOGNIZED SYNAD PATH; UNRECOVERED ABENDS ARE NOT CAUGHT.
QS       DS    0H
QIOSYN   L     0,QIOOP
         C     0,=F'2'
         BE    QIOREADR
         L     15,=F'-13'
         B     QIOEXIT
QIOREADR L     15,=F'-12'
         B     QIOEXIT
QIODIR   L     15,=F'-8'
         B     QIOEXIT
QIOFORM  L     15,=F'-9'
         B     QIOEXIT
QIOLEN   L     15,=F'-10'
         B     QIOEXIT
QIOARG   L     15,=F'-3'
         B     QIOEXIT
QIORESER L     15,=F'-11'
QIOEXIT  ST    15,QIOSTAT
         L     13,4(13)
         LM    14,14,12(13)
         L     15,QIOSTAT
         LM    0,12,20(13)
         BR    14
         LTORG
QISAVE   DS    18F
QIOSTAT  DC    F'0'
QIOOP    DC    F'0'
QIOREQ   DC    F'0'
QIORES   DC    F'0'
QIOCUR   DC    F'0'
QIOBUF   DC    F'0'
QIOCNT   DC    F'0'
QISTPTR  DC    F'0'
QIPNPTR  DC    F'0'
***********************************************************************
* R.0-FINALIZER ABI. R1 -> TWO WORDS REASON / STOP CODE.
* R15 RETURNS ZERO OR NONZERO. R2-R12/R13 PRESERVED.
* REGISTRAR HANDLES BCPLREG 2001 / FINISH 8 / STOP(n).
***********************************************************************
QSMFIN   CSECT
         ENTRY QSMFIN
         USING QSMFIN,12
         STM   14,12,12(13)
         LR    12,15
         LA    2,QFSAVE
         ST    13,4(2)
         ST    2,8(13)
         LR    13,2
         L     11,=A(QSMCTRL)
         USING QSMCTRL,11
         XC    QFSTAT(4),QFSTAT
         XC    QFCOUNT(4),QFCOUNT
         LTR   1,1
         BZ    QFFAIL
         L     0,0(1)
         LTR   0,0
         BZ    QFSTART
         C     0,=F'1'
         BNE   QFFAIL
QFSTART  LA    4,QSSLOTS
         LA    5,16
QFNEXT   CLC   0(4,4),=F'2'
         BNE   QFOTHER
         L     15,=A(QSMCLS1)
         BALR  14,15
         LTR   15,15
         BNZ   QFMARK
         L     0,QFCOUNT
         A     0,=F'1'
         ST    0,QFCOUNT
         B     QFSTEP
QFOTHER  L     0,0(4)
         LTR   0,0
         BZ    QFSTEP
QFMARK   LA    0,8
         ST    0,QFSTAT
QFSTEP   LA    4,44(4)
         BCT   5,QFNEXT
         B     QFRET
QFFAIL   LA    0,8
         ST    0,QFSTAT
QFRET    L     0,QFCOUNT
         C     0,=F'16'
         BNE   QFEXIT
         CLC   QFSTAT(4),=F'0'
         BNE   QFEXIT
         CLC   QSLIVE(4),=F'0'
         BNE   QFEXIT
         CLC   QSDCBS(4),=F'0'
         BNE   QFEXIT
         CLC   QSSTAGES(4),=F'0'
         BNE   QFEXIT
* TEST-ONLY TRACE, NOT A VERSION-1 PUBLIC INTERFACE GUARANTEE.
         WTO   'BCPLQSAM Q1 FINALIZER 16 CLOSE PASS'
QFEXIT   L     15,QFSTAT
         L     13,4(13)
         LM    14,14,12(13)
         LM    0,12,20(13)
         BR    14
         LTORG
QFSAVE   DS    18F
QFSTAT   DC    F'0'
QFCOUNT  DC    F'0'
***********************************************************************
* PRIVATE NONREENTRANT HANDLE TABLE; 16 INDEPENDENT PER-SLOT DCBs
* IN THE SAME RELOCATABLE OBJECT. JFCBs ARE 176 BYTES EACH.
* SLOT: STATE,ID,MODE,STAGE,INPUT_DCB,OUTPUT_DCB,JFCB,
*       FORMAT,LRECL,BLKSIZE,DATA_MAX (44 BYTES).
* STATES: 0 FREE; 1 RESERVED; 2 OPEN; 3 CLOSING; 4 QUARANTINE.
***********************************************************************
QSMCTRL  CSECT
QSNEXT   DC    F'1'
QSLIVE   DC    F'0'
QSDCBS   DC    F'0'
QSSTAGES DC    F'0'
QSQUAR   DC    F'0'
* Q.2: 00 READY, 01 PENDING, 02 EOF; 16 INDEPENDENT SLOTS.
QISTATES DC    16X'00'
QIPENDS  DC    16F'0'
QSSLOTS  DS    0F
QS00     DC    F'0',F'0',F'0',F'0'
         DC    A(QI00),A(QO00),A(QJ00)
         DC    F'0',F'0',F'0',F'0'
QS01     DC    F'0',F'0',F'0',F'0'
         DC    A(QI01),A(QO01),A(QJ01)
         DC    F'0',F'0',F'0',F'0'
QS02     DC    F'0',F'0',F'0',F'0'
         DC    A(QI02),A(QO02),A(QJ02)
         DC    F'0',F'0',F'0',F'0'
QS03     DC    F'0',F'0',F'0',F'0'
         DC    A(QI03),A(QO03),A(QJ03)
         DC    F'0',F'0',F'0',F'0'
QS04     DC    F'0',F'0',F'0',F'0'
         DC    A(QI04),A(QO04),A(QJ04)
         DC    F'0',F'0',F'0',F'0'
QS05     DC    F'0',F'0',F'0',F'0'
         DC    A(QI05),A(QO05),A(QJ05)
         DC    F'0',F'0',F'0',F'0'
QS06     DC    F'0',F'0',F'0',F'0'
         DC    A(QI06),A(QO06),A(QJ06)
         DC    F'0',F'0',F'0',F'0'
QS07     DC    F'0',F'0',F'0',F'0'
         DC    A(QI07),A(QO07),A(QJ07)
         DC    F'0',F'0',F'0',F'0'
QS08     DC    F'0',F'0',F'0',F'0'
         DC    A(QI08),A(QO08),A(QJ08)
         DC    F'0',F'0',F'0',F'0'
QS09     DC    F'0',F'0',F'0',F'0'
         DC    A(QI09),A(QO09),A(QJ09)
         DC    F'0',F'0',F'0',F'0'
QS10     DC    F'0',F'0',F'0',F'0'
         DC    A(QI10),A(QO10),A(QJ10)
         DC    F'0',F'0',F'0',F'0'
QS11     DC    F'0',F'0',F'0',F'0'
         DC    A(QI11),A(QO11),A(QJ11)
         DC    F'0',F'0',F'0',F'0'
QS12     DC    F'0',F'0',F'0',F'0'
         DC    A(QI12),A(QO12),A(QJ12)
         DC    F'0',F'0',F'0',F'0'
QS13     DC    F'0',F'0',F'0',F'0'
         DC    A(QI13),A(QO13),A(QJ13)
         DC    F'0',F'0',F'0',F'0'
QS14     DC    F'0',F'0',F'0',F'0'
         DC    A(QI14),A(QO14),A(QJ14)
         DC    F'0',F'0',F'0',F'0'
QS15     DC    F'0',F'0',F'0',F'0'
         DC    A(QI15),A(QO15),A(QJ15)
         DC    F'0',F'0',F'0',F'0'
         DS    0F
QJ00     DS    CL176
QJ01     DS    CL176
QJ02     DS    CL176
QJ03     DS    CL176
QJ04     DS    CL176
QJ05     DS    CL176
QJ06     DS    CL176
QJ07     DS    CL176
QJ08     DS    CL176
QJ09     DS    CL176
QJ10     DS    CL176
QJ11     DS    CL176
QJ12     DS    CL176
QJ13     DS    CL176
QJ14     DS    CL176
QJ15     DS    CL176
* LAZY SNAPSHOTS: TWO DCBs PER SLOT, EACH 96 BYTES.
* THE FIRST-USE FLAGS AND COPIES MUST NOT BE RESET ON CLOSE.
QSFIRST  DC    32X'00'
QSDCOPY  DS    CL3072
***********************************************************************
* PHYSICAL QSAM DCBs: ONE INPUT AND ONE OUTPUT TEMPLATE PER SLOT.
* ONLY ONE MODE MAY BE OPEN IN A SLOT AT ANY TIME.
* DCB +40 DDNAME, +36 RECFM, +62 BLKSIZE, +82 LRECL:
* KEEP Q.1 DDNAME TEMPLATES; SHORT EXIT ALIASES FIT 71 COLS.
***********************************************************************
QSMDCBS  CSECT
QI00     DCB   DDNAME=Q00,DSORG=PS,MACRF=GM,EXLST=QE00,EODAD=E,SYNAD=QS
QO00     DCB   DDNAME=Q00,DSORG=PS,MACRF=PM,EXLST=QE00,SYNAD=QS
         DS    0F
QE00     DC    X'87',AL3(QJ00)
QI01     DCB   DDNAME=Q01,DSORG=PS,MACRF=GM,EXLST=QE01,EODAD=E,SYNAD=QS
QO01     DCB   DDNAME=Q01,DSORG=PS,MACRF=PM,EXLST=QE01,SYNAD=QS
         DS    0F
QE01     DC    X'87',AL3(QJ01)
QI02     DCB   DDNAME=Q02,DSORG=PS,MACRF=GM,EXLST=QE02,EODAD=E,SYNAD=QS
QO02     DCB   DDNAME=Q02,DSORG=PS,MACRF=PM,EXLST=QE02,SYNAD=QS
         DS    0F
QE02     DC    X'87',AL3(QJ02)
QI03     DCB   DDNAME=Q03,DSORG=PS,MACRF=GM,EXLST=QE03,EODAD=E,SYNAD=QS
QO03     DCB   DDNAME=Q03,DSORG=PS,MACRF=PM,EXLST=QE03,SYNAD=QS
         DS    0F
QE03     DC    X'87',AL3(QJ03)
QI04     DCB   DDNAME=Q04,DSORG=PS,MACRF=GM,EXLST=QE04,EODAD=E,SYNAD=QS
QO04     DCB   DDNAME=Q04,DSORG=PS,MACRF=PM,EXLST=QE04,SYNAD=QS
         DS    0F
QE04     DC    X'87',AL3(QJ04)
QI05     DCB   DDNAME=Q05,DSORG=PS,MACRF=GM,EXLST=QE05,EODAD=E,SYNAD=QS
QO05     DCB   DDNAME=Q05,DSORG=PS,MACRF=PM,EXLST=QE05,SYNAD=QS
         DS    0F
QE05     DC    X'87',AL3(QJ05)
QI06     DCB   DDNAME=Q06,DSORG=PS,MACRF=GM,EXLST=QE06,EODAD=E,SYNAD=QS
QO06     DCB   DDNAME=Q06,DSORG=PS,MACRF=PM,EXLST=QE06,SYNAD=QS
         DS    0F
QE06     DC    X'87',AL3(QJ06)
QI07     DCB   DDNAME=Q07,DSORG=PS,MACRF=GM,EXLST=QE07,EODAD=E,SYNAD=QS
QO07     DCB   DDNAME=Q07,DSORG=PS,MACRF=PM,EXLST=QE07,SYNAD=QS
         DS    0F
QE07     DC    X'87',AL3(QJ07)
QI08     DCB   DDNAME=Q08,DSORG=PS,MACRF=GM,EXLST=QE08,EODAD=E,SYNAD=QS
QO08     DCB   DDNAME=Q08,DSORG=PS,MACRF=PM,EXLST=QE08,SYNAD=QS
         DS    0F
QE08     DC    X'87',AL3(QJ08)
QI09     DCB   DDNAME=Q09,DSORG=PS,MACRF=GM,EXLST=QE09,EODAD=E,SYNAD=QS
QO09     DCB   DDNAME=Q09,DSORG=PS,MACRF=PM,EXLST=QE09,SYNAD=QS
         DS    0F
QE09     DC    X'87',AL3(QJ09)
QI10     DCB   DDNAME=Q10,DSORG=PS,MACRF=GM,EXLST=QE10,EODAD=E,SYNAD=QS
QO10     DCB   DDNAME=Q10,DSORG=PS,MACRF=PM,EXLST=QE10,SYNAD=QS
         DS    0F
QE10     DC    X'87',AL3(QJ10)
QI11     DCB   DDNAME=Q11,DSORG=PS,MACRF=GM,EXLST=QE11,EODAD=E,SYNAD=QS
QO11     DCB   DDNAME=Q11,DSORG=PS,MACRF=PM,EXLST=QE11,SYNAD=QS
         DS    0F
QE11     DC    X'87',AL3(QJ11)
QI12     DCB   DDNAME=Q12,DSORG=PS,MACRF=GM,EXLST=QE12,EODAD=E,SYNAD=QS
QO12     DCB   DDNAME=Q12,DSORG=PS,MACRF=PM,EXLST=QE12,SYNAD=QS
         DS    0F
QE12     DC    X'87',AL3(QJ12)
QI13     DCB   DDNAME=Q13,DSORG=PS,MACRF=GM,EXLST=QE13,EODAD=E,SYNAD=QS
QO13     DCB   DDNAME=Q13,DSORG=PS,MACRF=PM,EXLST=QE13,SYNAD=QS
         DS    0F
QE13     DC    X'87',AL3(QJ13)
QI14     DCB   DDNAME=Q14,DSORG=PS,MACRF=GM,EXLST=QE14,EODAD=E,SYNAD=QS
QO14     DCB   DDNAME=Q14,DSORG=PS,MACRF=PM,EXLST=QE14,SYNAD=QS
         DS    0F
QE14     DC    X'87',AL3(QJ14)
QI15     DCB   DDNAME=Q15,DSORG=PS,MACRF=GM,EXLST=QE15,EODAD=E,SYNAD=QS
QO15     DCB   DDNAME=Q15,DSORG=PS,MACRF=PM,EXLST=QE15,SYNAD=QS
         DS    0F
QE15     DC    X'87',AL3(QJ15)
         END
