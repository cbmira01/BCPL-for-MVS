***********************************************************************
* Q.0 PROBE ONLY - READ ALL 23 LOGICAL FB80 RECORDS FROM DASD.
* CHECK EFFECTIVE DCB, BYTE CONTENTS, ORDER, COUNT AND EODAD.
* DCB FIELD OFFSETS FROM IFOX DCB EXPANSION IN JOB 2159.
***********************************************************************
Q0FBR    CSECT
         STM   14,12,12(13)
         LR    12,15
         USING Q0FBR,12
         LA    11,SAVREG
         ST    13,4(11)
         ST    11,8(13)
         LR    13,11
         XC    RECCNT(4),RECCNT
         OPEN  (QDCB,(INPUT))
         OPEN  (ODCB,(OUTPUT))
         CLI   QDCB+36,X'90'
         BNE   FAILED
         CLC   QDCB+62(2),=H'800'
         BNE   FAILED
         CLC   QDCB+82(2),=H'80'
         BNE   FAILED
RLOOP    GET   QDCB,AREA
         CLC   AREA(8),=CL8'Q0FBTEST'
         BNE   FAILED
         L     3,RECCNT
         SR    4,4
         IC    4,AREA+8
         CR    4,3
         BNE   FAILED
         CLC   AREA+9(70),BLANKS
         BNE   FAILED
         CLI   AREA+79,C'X'
         BNE   FAILED
         LA    3,1(3)
         ST    3,RECCNT
         C     3,=F'23'
         BH    FAILED
         B     RLOOP
ATEND    L     3,RECCNT
         C     3,=F'23'
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
BLANKS   DC    CL70' '
AREA     DS    CL80
PASSREC  DC    CL80'Q0 FB DASD 23 RECORDS PASS'
SAVREG   DS    18F
QDCB     DCB   DDNAME=QDISK,DSORG=PS,MACRF=GM,EODAD=ATEND
ODCB     DCB   DDNAME=QOUT,DSORG=PS,MACRF=PM
         LTORG
         END   Q0FBR
