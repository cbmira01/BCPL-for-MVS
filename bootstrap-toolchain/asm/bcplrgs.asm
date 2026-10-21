***********************************************************************
* R.1 GENERIC REGISTRATION FOUNDATION - DEVELOPMENT CANDIDATE.
* RGINIT: R1 -> F'G BASE' (MVS BYTE POINTER), RETURN R15=ID/0.
* RGFINI: R1 -> REASON,STOPCODE; R15=0 OR 8 ON RETURNED FAILURE.
* VERSION 1 BCRG/BCEX. NEVER PUBLISH BEFORE FULL VALIDATION.
* LINK A REAL BCPLREG OBJECT FOR EVERY APPLICATION.
* LINK TRUST: EACH PAIR MUST COME FROM DC A(BEGIN),A(END) IN
* SOURCE-REVIEWED REGISTRY; IEWL MAP/XREF MUST VERIFY REFERENCES.
* A BOGUS RELOCATABLE POINTER IS NOT GENERAL MEMORY PROTECTION.
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
         LA    0,RSAVE
         ST    13,4(0)
         ST    0,8(13)
         LR    13,0
         XC    REGCOUNT(4),REGCOUNT
         XC    RGONCE(4),RGONCE
         XC    RGERR(4),RGERR
         L     10,0(1)
         ST    10,RGGBASE
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
         LR    0,10
         AR    0,1
         L     2,0(0)
         L     4,=X'C7D3F000'
         AR    4,1
         CR    2,4
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
EXOPKG   L     4,RGSCAN
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
         EXTRN REGCOUNT,REGFINTB
         STM   14,12,12(13)
         LR    12,15
         USING RGFINI,12
         LA    0,FSAVE
         ST    13,4(0)
         ST    0,8(13)
         LR    13,0
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
