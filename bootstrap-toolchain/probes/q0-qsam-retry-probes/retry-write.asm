***********************************************************************
* Q.0 TEST ONLY: TWO FB80 LOGICAL RECORDS; DISTINCT BINARY BYTES.
***********************************************************************
Q0PRW    CSECT
         STM   14,12,12(13)
         LR    12,15
         USING Q0PRW,12
         LA    11,SAVREG
         ST    13,4(11)
         ST    11,8(13)
         LR    13,11
         OPEN  (QDCB,(OUTPUT))
         MVC   AREA(80),BLANKS
         MVC   AREA(8),=CL8'Q0PND001'
         MVI   AREA+8,X'00'
         MVI   AREA+9,X'FF'
         MVI   AREA+79,X'5A'
         PUT   QDCB,AREA
         MVC   AREA(80),BLANKS
         MVC   AREA(8),=CL8'Q0PND002'
         MVI   AREA+8,X'FF'
         MVI   AREA+9,X'00'
         MVI   AREA+79,X'A5'
         PUT   QDCB,AREA
         CLOSE (QDCB)
         L     13,4(13)
         LM    14,12,12(13)
         SR    15,15
         BR    14
         DS    0F
BLANKS   DC    CL80' '
AREA     DS    CL80
SAVREG   DS    18F
QDCB     DCB   DDNAME=QDISK,DSORG=PS,MACRF=PM
         LTORG
         END   Q0PRW
