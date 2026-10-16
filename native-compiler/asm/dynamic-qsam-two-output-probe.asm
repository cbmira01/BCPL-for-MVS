***********************************************************************
* DQ2PRB - PRIVATE TWO-INDEPENDENT-QSAM-OUTPUT PROBE.
* Each GETMAIN block 288 bytes:
* +0..31 private descriptor, +32..163 FB132 record buffer,
* +164..259 private 96-byte DCB, +260 OPEN list, +264 CLOSE.
* Initial DCB template is the unopened IFOX-generated DCB.
* Source/JCL test only; public BCPLIO is not modified.
***********************************************************************
DQ2PRB   CSECT
         ENTRY DQ2PRB
         STM   14,12,12(13)
         LR    12,15
         USING DQ2PRB,12
         ST    13,OLDSAVE+4
         LA    13,NEWSAVE
         GETMAIN RC,LV=288
         LTR   15,15
         BNZ   FAIL8
         ST    1,PD1
         LR    6,1
         BAL   14,INITREG
         MVC   8(8,6),NAME1
         GETMAIN RC,LV=288
         LTR   15,15
         BNZ   FAIL12
         ST    1,PD2
         LR    6,1
         BAL   14,INITREG
         MVC   8(8,6),NAME2
* Both DCBs are live simultaneously.
         L     6,PD1
         BAL   14,DOPEN
         L     6,PD2
         BAL   14,DOPEN
         L     6,PD1
         MVC   32(132,6),REC1A
         BAL   14,DPUT
         L     6,PD2
         MVC   32(132,6),REC2A
         BAL   14,DPUT
         L     6,PD1
         MVC   32(132,6),REC1B
         BAL   14,DPUT
* Close first DD, while second remains OPEN and writable.
         L     6,PD1
         BAL   14,DCLOSE
         L     6,PD2
         MVC   32(132,6),REC2B
         BAL   14,DPUT
         BAL   14,DCLOSE
         L     1,PD2
         FREEMAIN R,LV=288,A=(1)
         L     1,PD1
         FREEMAIN R,LV=288,A=(1)
         SR    8,8
         B     FINISH
FAIL8    LA    8,8
         B     FINISH
FAIL12   L     1,PD1
         FREEMAIN R,LV=288,A=(1)
         LA    8,12
FINISH   ST    8,RESULT
         L     13,OLDSAVE+4
         L     15,RESULT
         ST    15,16(13)
         LM    14,12,12(13)
         BR    14
* R6 is private region pointer. +28 stores caller R14.
INITREG  XC    0(288,6),0(6)
         MVC   164(96,6),TEMPLATE
         LA    7,164(6)
         ST    7,20(6)
         LA    7,32(6)
         ST    7,16(6)
         LA    7,164(6)
         STCM  7,7,261(6)
         STCM  7,7,265(6)
         MVI   260(6),X'8F'
         MVI   264(6),X'80'
         BR    14
DOPEN    ST    14,28(6)
         MVC   204(8,6),8(6)
         LA    1,260(6)
         SVC   19
         LA    1,164(6)
         L     15,48(1)
         LTR   15,15
         BZ    ABEND8
         L     14,28(6)
         BR    14
DPUT     ST    14,28(6)
         LA    1,164(6)
         LA    0,32(6)
         L     15,48(1)
         BALR  14,15
         L     14,28(6)
         BR    14
DCLOSE   ST    14,28(6)
         LA    1,264(6)
         SVC   20
         L     14,28(6)
         BR    14
ABEND8   ABEND 8
         BR    14
         LTORG
PD1      DC    F'0'
PD2      DC    F'0'
RESULT   DC    F'0'
NAME1    DC    CL8'REPORT'
NAME2    DC    CL8'REPORT2'
REC1A    DC    CL132'REPORT RECORD ONE'
REC1B    DC    CL132'REPORT RECORD TWO'
REC2A    DC    CL132'REPORT2 RECORD ONE'
REC2B    DC    CL132'REPORT2 RECORD TWO'
OLDSAVE  DS    18F
NEWSAVE  DS    18F
TEMPLATE DCB   DDNAME=DUMMY,DSORG=PS,MACRF=PM
         END   DQ2PRB
