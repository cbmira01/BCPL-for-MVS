***********************************************************************
* Q.0 TEST-ONLY MVS QSAM PROBE. NOT THE BCPLQSAM SYSTEM EXTENSION.
* FB80 MOVE-MODE GET/PUT; VERIFY TWO RECORDS AND EODAD.
* NO PRODUCTION OBJECT PDS UPDATE. IEWL LOAD MODULE IS TEMPORARY.
***********************************************************************
Q0FBPRB  CSECT
         STM   14,12,12(13)
         LR    12,15
         USING Q0FBPRB,12
         LA    11,SAVEAREA
         ST    13,4(11)
         ST    11,8(13)
         LR    13,11
         XC    RECCOUNT(4),RECCOUNT
         OPEN  (INDCB,(INPUT))
         OPEN  (OUTDCB,(OUTPUT))
QAGAIN   GET   INDCB,RECAREA
         L     3,RECCOUNT
         LTR   3,3
         BZ    QFIRST
         C     3,=F'1'
         BE    QSECOND
         B     QFAILED
QFIRST   CLC   RECAREA(8),=CL8'Q0FIX001'
         BNE   QFAILED
         CLI   RECAREA+79,C'X'
         BNE   QFAILED
         B     QCHECK
QSECOND  CLC   RECAREA(8),=CL8'Q0FIX002'
         BNE   QFAILED
         CLI   RECAREA+79,C'Y'
         BNE   QFAILED
QCHECK   CLC   RECAREA+8(71),BLANKS
         BNE   QFAILED
         PUT   OUTDCB,RECAREA
         L     3,RECCOUNT
         LA    3,1(3)
         ST    3,RECCOUNT
         B     QAGAIN
QEOD     L     3,RECCOUNT
         C     3,=F'2'
         BNE   QFAILED
         CLOSE (INDCB)
         CLOSE (OUTDCB)
         L     13,4(13)
         LM    14,12,12(13)
         SR    15,15
         BR    14
QFAILED  CLOSE (INDCB)
         CLOSE (OUTDCB)
         L     13,4(13)
         LM    14,12,12(13)
         LA    15,8
         BR    14
         DS    0F
RECCOUNT DC    F'0'
BLANKS   DC    CL71' '
RECAREA  DS    CL80
SAVEAREA DS    18F
INDCB    DCB   DDNAME=QIN,DSORG=PS,MACRF=GM,EODAD=QEOD
OUTDCB   DCB   DDNAME=QOUT,DSORG=PS,MACRF=PM
         LTORG
         END   Q0FBPRB
