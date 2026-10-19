***********************************************************************
* Q.0 PROBE ONLY - WRITE 23 FB80 LOGICAL RECORDS TO A DASD DATA SET.
* THE RECORD ID AND THE BYTE AT +8 IDENTIFY THE RECORD SEQUENCE.
***********************************************************************
Q0FBW    CSECT
         STM   14,12,12(13)
         LR    12,15
         USING Q0FBW,12
         LA    11,SAVREG
         ST    13,4(11)
         ST    11,8(13)
         LR    13,11
         XC    RECCNT(4),RECCNT
         OPEN  (QDCB,(OUTPUT))
WLOOP    MVC   AREA(80),BLANKS
         MVC   AREA(8),=CL8'Q0FBTEST'
         L     3,RECCNT
         STC   3,AREA+8
         MVI   AREA+79,C'X'
         PUT   QDCB,AREA
         L     3,RECCNT
         LA    3,1(3)
         ST    3,RECCNT
         C     3,=F'23'
         BL    WLOOP
         CLOSE (QDCB)
         L     13,4(13)
         LM    14,12,12(13)
         SR    15,15
         BR    14
         DS    0F
RECCNT   DC    F'0'
BLANKS   DC    CL80' '
AREA     DS    CL80
SAVREG   DS    18F
QDCB     DCB   DDNAME=QDISK,DSORG=PS,MACRF=PM
         LTORG
         END   Q0FBW
