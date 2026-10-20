***********************************************************************
* Q.0 TEST-ONLY: EMPTY FB80 EODAD; APPLICATION READ TWICE.
* A SECOND APPLICATION READ MUST NOT ISSUE A SECOND QSAM GET.
***********************************************************************
Q0EMR    CSECT
         STM   14,12,12(13)
         LR    12,15
         USING Q0EMR,12
         LA    11,SAVREG
         ST    13,4(11)
         ST    11,8(13)
         LR    13,11
         XC    EOCOUNT(4),EOCOUNT
         XC    RDCNT(4),RDCNT
         MVI   EOFLAG,X'00'
         OPEN  (QDCB,(INPUT))
         OPEN  (ODCB,(OUTPUT))
         LA    7,AFTER1
         B     READONE
AFTER1   CLC   EOCOUNT(4),=F'1'
         BNE   FAILED
         CLC   RDCNT(4),=F'1'
         BNE   FAILED
         CLI   EOFLAG,X'01'
         BNE   FAILED
         LA    7,AFTER2
         B     READONE
AFTER2   CLC   EOCOUNT(4),=F'1'
         BNE   FAILED
         CLC   RDCNT(4),=F'2'
         BNE   FAILED
         PUT   ODCB,PASSREC
         CLOSE (QDCB)
         CLOSE (ODCB)
         L     13,4(13)
         LM    14,12,12(13)
         SR    15,15
         BR    14
READONE  CLI   EOFLAG,X'01'
         BE    EOFRET
         GET   QDCB,AREA
* NO DATA RECORD IS EXPECTED. GET ON NONEMPTY FILE IS FAILURE.
         B     FAILED
ATEND    L     3,EOCOUNT
         LA    3,1(3)
         ST    3,EOCOUNT
         MVI   EOFLAG,X'01'
EOFRET   L     3,RDCNT
         LA    3,1(3)
         ST    3,RDCNT
         BR    7
FAILED   CLOSE (QDCB)
         CLOSE (ODCB)
         L     13,4(13)
         LM    14,12,12(13)
         LA    15,8
         BR    14
         DS    0F
EOCOUNT  DC    F'0'
RDCNT    DC    F'0'
EOFLAG   DC    X'00'
AREA     DS    CL80
PASSREC  DC    CL80'Q0 EMPTY FB EOF2 EODAD1 PASS'
SAVREG   DS    18F
QDCB     DCB   DDNAME=QDISK,DSORG=PS,MACRF=GM,EODAD=ATEND
ODCB     DCB   DDNAME=QOUT,DSORG=PS,MACRF=PM
         LTORG
         END   Q0EMR
