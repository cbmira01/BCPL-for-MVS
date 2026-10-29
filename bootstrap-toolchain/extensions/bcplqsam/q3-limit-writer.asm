***********************************************************************
* Q.3 IFOX V/VB MAXIMUM-STAGE WRITER FOR BCPLQSAM READ.
* DATA BYTES: 0,1,12,1020,1020,0,1; TWO FULL LOGICAL RECORDS.
* THE 1024-BYTE STAGE INCLUDES THE FOUR-BYTE RDW, NOT THE BDW.
***********************************************************************
Q3LMW    CSECT
         STM   14,12,12(13)
         LR    12,15
         USING Q3LMW,12
         LA    11,SAVREG
         ST    13,4(11)
         ST    11,8(13)
         LR    13,11
         XC    RECCNT(4),RECCNT
         OPEN  (QDCB,(OUTPUT))
WLOOP    MVC   AREA(256),BLANKS
         MVC   AREA+256(256),BLANKS
         MVC   AREA+512(256),BLANKS
         MVC   AREA+768(256),BLANKS
         L     3,RECCNT
         LR    4,3
         SLL   4,1
         LA    5,LENTAB
         LH    2,0(4,5)
         STH   2,AREA
         XC    AREA+2(2),AREA+2
         CH    2,=H'4'
         BE    WRPUT
         STC   3,AREA+4
         MVI   AREA+5,X'00'
         MVI   AREA+6,X'FF'
         MVI   AREA+15,X'A5'
         MVI   AREA+35,X'7E'
         MVI   AREA+259,X'00'
         MVI   AREA+515,X'FF'
         MVI   AREA+771,X'00'
         MVI   AREA+1023,X'C3'
WRPUT    PUT   QDCB,AREA
         L     3,RECCNT
         LA    3,1(3)
         ST    3,RECCNT
         C     3,=F'7'
         BL    WLOOP
         CLOSE (QDCB)
         L     13,4(13)
         LM    14,12,12(13)
         SR    15,15
         BR    14
         DS    0F
RECCNT   DC    F'0'
BLANKS   DC    CL256' '
LENTAB   DC    H'4',H'5',H'16',H'1024',H'1024',H'4',H'5'
AREA     DS    CL1024
SAVREG   DS    18F
QDCB     DCB   DDNAME=QVDATA,DSORG=PS,MACRF=PM
         LTORG
         END   Q3LMW
