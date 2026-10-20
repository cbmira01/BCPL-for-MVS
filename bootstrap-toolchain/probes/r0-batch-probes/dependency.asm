***********************************************************************
* R.0 TEST ONLY: LINKED DESCRIPTORS, DEPENDENCY/OWNER VALIDATION.
* FIXTURES ARE LINKED DATA; NOTHING IS PUBLISHED INTO BCPL GLOBALS.
***********************************************************************
R0DCHK   CSECT
         ENTRY R0DCHK
         EXTRN R0TBL
         STM   14,12,12(13)
         LR    12,15
         USING R0DCHK,12
         LA    11,SAVREG
         ST    13,4(11)
         ST    11,8(13)
         LR    13,11
         XC    FLAG(4),FLAG
         OPEN  (ODCB,(OUTPUT))
         L     10,=A(R0TBL)
         L     5,0(10)
         LA    10,4(10)
SCNLOOP  ST    10,CURSC
         ST    5,LEFT
         LR    1,10
         BAL   14,CHECK
         L     10,CURSC
         C     15,0(10)
         BNE   FAILONE
         MVC   OUTBUF(80),20(10)
         B     PRINT
FAILONE  LA    0,8
         ST    0,FLAG
         MVC   OUTBUF(80),=CL80'R0 DEP BATCH CASE FAILED'
PRINT    PUT   ODCB,OUTBUF
         L     10,CURSC
         LA    10,100(10)
         L     5,LEFT
         BCT   5,SCNLOOP
         CLOSE (ODCB)
         L     15,FLAG
         L     13,4(13)
         LM    14,14,12(13)
         LM    0,12,20(13)
         BR    14
*
* CHECK ONE BOUNDED TEST-SCENARIO RECORD, RESULT STATUS IN R15.
* SCENARIO +0 EXPECTED, +4 COUNT, +8 REQUIRED COUNT,
* +12 PAIR-LIST ADDRESS, +16 REQUIRED-ID ADDRESS, +20 TEXT.
*
CHECK    ST    14,CKRET
         L     6,4(1)
         L     7,8(1)
         C     6,=F'3'
         BH    BADSPAN
         C     7,=F'1'
         BH    BADSPAN
         ST    6,CTN
         ST    7,REQCNT
         L     2,12(1)
         ST    2,SELBASE
         L     2,16(1)
         ST    2,REQPTR
         XC    IDX(4),IDX
         L     6,CTN
         LTR   6,6
         BZ    REQCHECK
PKLOOP   L     3,IDX
         SLL   3,3
         A     3,SELBASE
         L     8,0(3)
         L     9,4(3)
         LR    0,8
         N     0,=F'3'
         BNZ   BADSPAN
         LR    0,9
         N     0,=F'3'
         BNZ   BADSPAN
         CR    9,8
         BNH   BADSPAN
         LR    0,9
         SR    0,8
         C     0,=F'56'
         BL    BADSPAN
         C     0,=F'128'
         BH    BADSPAN
         C     0,12(8)
         BNE   BADSPAN
         CLC   0(4,8),=CL4'BCEX'
         BNE   BADSPAN
         CLC   4(4,8),=F'1'
         BNE   BADSPAN
         CLC   8(4,8),=F'48'
         BNE   BADSPAN
         CLC   32(4,8),=F'1'
         BNE   BADSPAN
         L     7,40(8)
         C     7,=F'1'
         BH    BADSPAN
         SLL   7,4
         A     7,=F'56'
         CR    7,0
         BNE   BADSPAN
         L     0,48(8)
         C     0,=F'14'
         BE    BADCORE
         C     0,=F'200'
         BE    BADCORE
         C     0,=F'299'
         BL    BADCORE
         C     0,=F'305'
         BH    BADCORE
* COMPARE WITH ALL EARLIER PACKAGE IDS AND EXPORTED GLOBALS.
         L     7,IDX
         L     2,SELBASE
PRIOR    LTR   7,7
         BZ    DEPCHECK
         L     5,0(2)
         CLC   16(8,8),16(5)
         BE    DUPID
         L     0,48(8)
         C     0,48(5)
         BE    DUPGLOB
         LA    2,8(2)
         BCT   7,PRIOR
DEPCHECK L     7,40(8)
         LTR   7,7
         BZ    NEXTPK
         L     7,CTN
         L     2,SELBASE
         SR    3,3
FINDDEP  L     5,0(2)
         CLC   56(8,8),16(5)
         BE    GOTDEP
         LA    2,8(2)
         LA    3,1(3)
         BCT   7,FINDDEP
         B     MISSDEP
GOTDEP   L     0,64(8)
         C     0,24(5)
         BNE   BADVERS
         L     0,68(8)
         C     0,28(5)
         BH    BADVERS
         C     3,IDX
         BNL   BADORDER
NEXTPK   L     0,IDX
         A     0,=F'1'
         ST    0,IDX
         C     0,CTN
         BL    PKLOOP
REQCHECK L     7,REQCNT
         LTR   7,7
         BZ    GOOD
         L     9,REQPTR
         L     7,CTN
         LTR   7,7
         BZ    BADREQ
         L     2,SELBASE
REQLOOP  L     5,0(2)
         CLC   0(8,9),16(5)
         BE    GOOD
         LA    2,8(2)
         BCT   7,REQLOOP
         B     BADREQ
GOOD     SR    15,15
         B     RETCHECK
BADSPAN  LA    15,4
         B     RETCHECK
MISSDEP  LA    15,12
         B     RETCHECK
BADVERS  LA    15,16
         B     RETCHECK
BADORDER LA    15,20
         B     RETCHECK
DUPID    LA    15,28
         B     RETCHECK
DUPGLOB LA   15,32
         B     RETCHECK
BADREQ   LA    15,36
         B     RETCHECK
BADCORE  LA    15,40
RETCHECK L     14,CKRET
         BR    14
         DS    0F
CURSC    DC    F'0'
LEFT     DC    F'0'
FLAG     DC    F'0'
CKRET    DC    F'0'
CTN      DC    F'0'
REQCNT   DC    F'0'
REQPTR   DC    F'0'
SELBASE  DC    F'0'
IDX      DC    F'0'
OUTBUF   DS    CL80
SAVREG   DS    18F
ODCB     DCB   DDNAME=QOUT,DSORG=PS,MACRF=PM
         LTORG
         END   R0DCHK
