***********************************************************************
* Q.0 PROBE ONLY - WRITE 15 V OR VB LOGICAL RECORDS TO DASD.
* RDW: LENGTH (TWO BYTES), THEN TWO ZERO RESERVED BYTES.
* TOTAL RECORD LENGTHS: 16, 36, 100 REPEATED FIVE TIMES.
***********************************************************************
Q0VW     CSECT
         STM   14,12,12(13)
         LR    12,15
         USING Q0VW,12
         LA    11,SAVREG
         ST    13,4(11)
         ST    11,8(13)
         LR    13,11
         XC    RECCNT(4),RECCNT
         OPEN  (QDCB,(OUTPUT))
WLOOP    MVC   AREA(100),BLANKS
         MVC   AREA+4(8),=CL8'Q0VRTST!'
         L     3,RECCNT
         STC   3,AREA+12
         SLL   3,1
         LA    2,LENTAB
         LH    2,0(3,2)
         STH   2,AREA
         XC    AREA+2(2),AREA+2
         PUT   QDCB,AREA
         L     3,RECCNT
         LA    3,1(3)
         ST    3,RECCNT
         C     3,=F'15'
         BL    WLOOP
         CLOSE (QDCB)
         L     13,4(13)
         LM    14,12,12(13)
         SR    15,15
         BR    14
         DS    0F
RECCNT   DC    F'0'
BLANKS   DC    CL100' '
LENTAB   DC    H'16',H'36',H'100',H'16',H'36',H'100'
         DC    H'16',H'36',H'100',H'16',H'36',H'100'
         DC    H'16',H'36',H'100'
AREA     DS    CL100
SAVREG   DS    18F
QDCB     DCB   DDNAME=QDISK,DSORG=PS,MACRF=PM
         LTORG
         END   Q0VW
