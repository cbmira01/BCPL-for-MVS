***********************************************************************
* Q.0 TEST ONLY: V/VB 1024-BYTE LOGICAL RECORD CEILING ON TK5.
* FIFTEEN RECORDS: RDW LENGTHS 4,16,1024 REPEATED FIVE TIMES.
* WRITE TRUE RDW-ONLY RECORDS AND LONG BINARY SENTINELS.
* NO PUBLIC BCPLQSAM, NO PERMANENT DATA SETS.
***********************************************************************
Q0CVW    CSECT
         STM   14,12,12(13)
         LR    12,15
         USING Q0CVW,12
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
         LA    2,LENTAB
         LH    2,0(4,2)
         STH   2,AREA
         XC    AREA+2(2),AREA+2
         CH    2,=H'4'
         BE    WRPUT
         CH    2,=H'16'
         BE    WRSML
         CH    2,=H'1024'
         BNE   FAILED
* FULL DATA AREA: DISTINCT X'00'/X'FF' AT BOUNDARIES.
         MVI   AREA+4,X'00'
         STC   3,AREA+12
         MVI   AREA+255,X'FF'
         MVI   AREA+511,X'00'
         MVI   AREA+767,X'FF'
         MVI   AREA+1023,X'00'
         B     WRPUT
WRSML    MVC   AREA+4(8),=CL8'Q0VRTST!'
         STC   3,AREA+12
WRPUT    PUT   QDCB,AREA
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
FAILED   CLOSE (QDCB)
         L     13,4(13)
         LM    14,12,12(13)
         LA    15,8
         BR    14
         DS    0F
RECCNT   DC    F'0'
BLANKS   DC    CL256' '
LENTAB   DC    H'4',H'16',H'1024',H'4',H'16',H'1024'
         DC    H'4',H'16',H'1024',H'4',H'16',H'1024'
         DC    H'4',H'16',H'1024'
AREA     DS    CL1024
SAVREG   DS    18F
QDCB     DCB   DDNAME=QDISK,DSORG=PS,MACRF=PM
         LTORG
         END   Q0CVW
