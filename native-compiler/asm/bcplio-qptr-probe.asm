***********************************************************************
* IO2DPRB - M1 QSAM SECONDARY PUT POINTER BEFORE/AFTER OPEN.
* RETURN: 0 changed to nonzero, 4 unchanged, 8 zero,
*         12 known observed bad pointer D01407FE, 16 IOSEL failed.
* No IOFIN: avoid CLOSE while diagnosing OPEN; MVS step cleanup.
***********************************************************************
IO2DPRB  CSECT
         ENTRY IO2DPRB
         EXTRN IOINIT,IOSEL,IO2PTR
         STM   14,12,12(13)
         LR    12,15
         USING IO2DPRB,12
         ST    13,OLDSAVE+4
         LA    13,NEWSAVE
         L     15,=A(IO2PTR)
         BALR  14,15
         ST    15,BEFORE
         SR    1,1
         L     15,=A(IOINIT)
         BALR  14,15
         LA    1,2
         L     15,=A(IOSEL)
         BALR  14,15
         LTR   15,15
         BNZ   BADOPEN
         L     15,=A(IO2PTR)
         BALR  14,15
         ST    15,AFTER
         LTR   15,15
         BZ    ZEROPTR
         C     15,=X'D01407FE'
         BE    BADPTR
         C     15,BEFORE
         BE    SAMEPTR
         SR    8,8
         B     FINISH
SAMEPTR  LA    8,4
         B     FINISH
ZEROPTR  LA    8,8
         B     FINISH
BADPTR   LA    8,12
         B     FINISH
BADOPEN  LA    8,16
FINISH   ST    8,RESULT
         L     13,OLDSAVE+4
         LM    14,12,12(13)
         L     15,RESULT
         BR    14
         LTORG
BEFORE   DS    F
AFTER    DS    F
RESULT   DS    F
OLDSAVE  DS    18F
NEWSAVE  DS    18F
         END   IO2DPRB
