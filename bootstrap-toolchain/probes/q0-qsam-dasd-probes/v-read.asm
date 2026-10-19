***********************************************************************
* Q.0 PROBE ONLY - READ 15 VARIABLE LOGICAL RECORDS.
* VALIDATE RDW TOTAL LENGTH, RESERVED BYTES, PAYLOAD AND ORDER.
* TEST DOES NOT EXPORT RDW THROUGH THE BCPL API.
***********************************************************************
Q0VR     CSECT
         STM   14,12,12(13)
         LR    12,15
         USING Q0VR,12
         LA    11,SAVREG
         ST    13,4(11)
         ST    11,8(13)
         LR    13,11
         XC    RECCNT(4),RECCNT
         OPEN  (QDCB,(INPUT))
         OPEN  (ODCB,(OUTPUT))
         CLC   QDCB+82(2),=H'100'
         BNE   FAILED
RLOOP    GET   QDCB,AREA
         CLC   AREA+4(8),=CL8'Q0VRTST!'
         BNE   FAILED
         LH    2,AREA
         L     3,RECCNT
         LR    4,3
         SLL   4,1
         LA    5,LENTAB
         CH    2,0(4,5)
         BNE   FAILED
         CLC   AREA+2(2),ZERO2
         BNE   FAILED
         SR    4,4
         IC    4,AREA+12
         CR    4,3
         BNE   FAILED
         LA    3,1(3)
         ST    3,RECCNT
         C     3,=F'15'
         BH    FAILED
         B     RLOOP
ATEND    L     3,RECCNT
         C     3,=F'15'
         BNE   FAILED
         PUT   ODCB,PASSREC
         CLOSE (QDCB)
         CLOSE (ODCB)
         L     13,4(13)
         LM    14,12,12(13)
         SR    15,15
         BR    14
FAILED   CLOSE (QDCB)
         CLOSE (ODCB)
         L     13,4(13)
         LM    14,12,12(13)
         LA    15,8
         BR    14
         DS    0F
RECCNT   DC    F'0'
ZERO2    DC    H'0'
LENTAB   DC    H'16',H'36',H'100',H'16',H'36',H'100'
         DC    H'16',H'36',H'100',H'16',H'36',H'100'
         DC    H'16',H'36',H'100'
AREA     DS    CL100
PASSREC  DC    CL80'Q0 VARIABLE 15 RECORDS PASS'
SAVREG   DS    18F
QDCB     DCB   DDNAME=QDISK,DSORG=PS,MACRF=GM,EODAD=ATEND
ODCB     DCB   DDNAME=QOUT,DSORG=PS,MACRF=PM
         LTORG
         END   Q0VR
