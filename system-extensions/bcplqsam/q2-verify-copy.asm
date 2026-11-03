***********************************************************************
* Q.2 TEST ONLY: INDEPENDENT MVS READBACK OF 23 FB80 COPIED RECORDS.
* EXPECT EACH BYTE, INCLUDING 00, FF AND TRAILING EBCDIC BLANK.
* NO BCPLQSAM CALLS HERE; NO PERMANENT DATASET MODIFICATION.
***********************************************************************
Q2VFY    CSECT
         ENTRY Q2VFY
         STM   14,12,12(13)
         LR    12,15
         USING Q2VFY,12
         LA    11,SAVREG
         ST    13,4(11)
         ST    11,8(13)
         LR    13,11
         XC    RECCNT(4),RECCNT
         OPEN  (IDC,(INPUT))
         OPEN  (ODC,(OUTPUT))
* GENERATE EXPECTED 80 BYTES: N,00,FF,03..4E,40.
         MVI   EXPECT+1,X'00'
         MVI   EXPECT+2,X'FF'
         MVI   EXPECT+79,X'40'
         LA    5,EXPECT+3
         LA    6,3
         LA    7,76
BTLOOP   STC   6,0(5)
         LA    5,1(5)
         LA    6,1(6)
         BCT   7,BTLOOP
VLOOP    GET   IDC,AREA
         L     3,RECCNT
         STC   3,EXPECT
         CLC   AREA(80),EXPECT
         BNE   FAILED
         LA    3,1(3)
         ST    3,RECCNT
         C     3,=F'23'
         BH    FAILED
         B     VLOOP
ATEND    CLC   RECCNT(4),=F'23'
         BNE   FAILED
         PUT   ODC,PASSREC
         CLOSE (IDC)
         CLOSE (ODC)
         L     13,4(13)
         LM    14,12,12(13)
         SR    15,15
         BR    14
FAILED   CLOSE (IDC)
         CLOSE (ODC)
         L     13,4(13)
         LM    14,12,12(13)
         LA    15,8
         BR    14
         DS    0F
RECCNT   DC    F'0'
EXPECT   DS    CL80
AREA     DS    CL80
PASSREC  DC    CL80'BCPLQSAM Q2 COPY 23 FB80 EXACT PASS'
SAVREG   DS    18F
IDC      DCB   DDNAME=QBCOPY,DSORG=PS,MACRF=GM,EODAD=ATEND
ODC      DCB   DDNAME=QOUT,DSORG=PS,MACRF=PM
         LTORG
         END   Q2VFY
