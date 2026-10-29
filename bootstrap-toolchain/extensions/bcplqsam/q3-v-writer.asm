***********************************************************************
* Q.3 NATIVE V READ TEST: INDEPENDENT IFOX QSAM DATASET WRITER.
* SIX RDW-INCLUSIVE LENGTHS: 5,16,36,100,4,5 (DATA 1,12,32,96,0,1).
* QSAM MOVE MODE, RECFM=V, LRECL=100, BLKSIZE=104.
***********************************************************************
Q3VWRT   CSECT
         STM   14,12,12(13)
         LR    12,15
         USING Q3VWRT,12
         LA    11,SAVREG
         ST    13,4(11)
         ST    11,8(13)
         LR    13,11
         XC    RECCNT(4),RECCNT
         OPEN  (QDCB,(OUTPUT))
WLOOP    MVC   AREA(100),BLANKS
         L     3,RECCNT
         STC   3,AREA+4
         MVI   AREA+5,X'00'
         MVI   AREA+6,X'FF'
         MVI   AREA+15,X'A5'
         MVI   AREA+35,X'7E'
         MVI   AREA+99,X'C3'
         SLL   3,1
         LA    2,LENTAB
         LH    2,0(3,2)
         STH   2,AREA
         XC    AREA+2(2),AREA+2
         PUT   QDCB,AREA
         L     3,RECCNT
         LA    3,1(3)
         ST    3,RECCNT
         C     3,=F'6'
         BL    WLOOP
         CLOSE (QDCB)
         L     13,4(13)
         LM    14,12,12(13)
         SR    15,15
         BR    14
         DS    0F
RECCNT   DC    F'0'
BLANKS   DC    CL100' '
LENTAB   DC    H'5',H'16',H'36',H'100',H'4',H'5'
AREA     DS    CL100
SAVREG   DS    18F
QDCB     DCB   DDNAME=QVDATA,DSORG=PS,MACRF=PM
         LTORG
         END   Q3VWRT
