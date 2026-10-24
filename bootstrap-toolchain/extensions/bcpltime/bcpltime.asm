***********************************************************************
* BCPLTIME V1: TWO CSECTS, ONE OPTIONAL RELOCATABLE OBJECT.
* DESC BCEX V1 EXPORTS G!201; DISPATCH OPERATIONS 0,1,2.
* BCPL CALL ABI: R7 OP/RETURN, R8 WORD PTR, R9 CAPACITY WORDS.
* R11 RETURN, R4 BASE; USES NORMAL BCPL FRAME AT R15.
* NON-REENTRANT: PRIVATE ALIGNED CLOCK SCRATCH AREA.
***********************************************************************
TIMDESC  CSECT
         ENTRY TIMBEG,TIMEND
TIMBEG   DS    0F
         DC    CL4'BCEX'
         DC    F'1',F'48',F'56'
         DC    CL8'BCPLTIME'
         DC    F'1',F'0',F'1',F'0',F'0',F'0'
         DC    F'201',A(TIMDISP)
TIMEND   EQU   *
***********************************************************************
* DIRECT DISPATCH: NO WRAPPER, DATE LIBRARY, INIT OR FINALIZER.
* RESULTS ARE COUNTS OF WRITTEN WORDS OR -1/-2/-3.
***********************************************************************
TIMDISP  CSECT
         ENTRY TIMDISP
         USING TIMDISP,4
         STM   4,9,0(15)
         LR    5,15
         LTR   7,7
         BZ    DOQUERY
         C     7,=F'1'
         BE    DOCLOCK
         C     7,=F'2'
         BE    DOTIME
         B     BADOP
*
* OP 0 - SHARED SIX-WORD QUERY.  (0,0,0) RETURNS REQUIRED SIZE.
*
DOQUERY  LTR   8,8
         BNZ   QCHECK
         LTR   9,9
         BNZ   BADARG
         LA    7,6
         BCR   15,11
QCHECK   LTR   9,9
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
         LA    14,3
         ST    14,16(8)
         SR    14,14
         ST    14,20(8)
         LA    7,6
         BCR   15,11
*
* OP 1 - RAW STCK: HIGH WORD, LOW WORD, INSTRUCTION CC.
* ALIGNED SCRATCH AVOIDS PROMISING DOUBLEWORD ALIGNMENT OF VEC.
* CAPTURE THE CC IMMEDIATELY WITH MASKED CONDITIONAL BRANCHES.
*
DOCLOCK  LTR   8,8
         BZ    BADARG
         LTR   9,9
         BM    BADARG
         C     9,=F'3'
         BL    SHORT
         SLL   8,2
         XC    CLKBUF(8),CLKBUF
         STCK  CLKBUF
         BC    8,CCZERO
         BC    4,CCONE
         BC    2,CCTWO
         LA    14,3
         B     SAVETOD
CCZERO   SR    14,14
         B     SAVETOD
CCONE    LA    14,1
         B     SAVETOD
CCTWO    LA    14,2
SAVETOD  ST    14,8(8)
         L     14,CLKBUF
         ST    14,0(8)
         L     14,CLKBUF+4
         ST    14,4(8)
         LA    7,3
         BCR   15,11
*
* OP 2 - RAW MVS TIME DEC: STORE RETURNED R0/R1 FULLWORDS.
* R0 AND R1 ARE PERMANENT CG370 REGISTERS; PRESERVE BOTH.
* CALL FRAME +24,+28 FOLLOW THE SAVED R4-R9 AT +0..+23.
* SYS1.MACLIB TIME MACRO REQUIRED; EXPANSION VERIFIED ON MVS.
*
DOTIME   LTR   8,8
         BZ    BADARG
         LTR   9,9
         BM    BADARG
         C     9,=F'2'
         BL    SHORT
         SLL   8,2
         STM   0,1,24(5)
         TIME  DEC
         ST    0,0(8)
         ST    1,4(8)
         LM    0,1,24(5)
         LA    7,2
         BCR   15,11
*
BADOP    L     7,=F'-2'
         BCR   15,11
SHORT    L     7,=F'-1'
         BCR   15,11
BADARG   L     7,=F'-3'
         BCR   15,11
         LTORG
CLKBUF   DS    0D
         DS    D
         END
