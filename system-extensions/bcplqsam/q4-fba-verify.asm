***********************************************************************
* Q.4 INDEPENDENT IFOX FBA133 VERIFIER OF THREE TEMP QSAM RECORDS.
* CHECK ALL 133 EBCDIC BYTES, INCLUDING ASA AND FINAL DATA COLUMN.
* JES2 PRINTER CARRIAGE CONTROL IS A SEPARATE OUTPUT ASSERTION.
***********************************************************************
Q4FAV    CSECT
         ENTRY Q4FAV
         STM   14,12,12(13)
         LR    12,15
         USING Q4FAV,12
         LA    11,SAVREG
         ST    13,4(11)
         ST    11,8(13)
         LR    13,11
         XC    RECCNT(4),RECCNT
         OPEN  (IDC,(INPUT))
         OPEN  (ODC,(OUTPUT))
         CLI   IDC+36,X'94'
         BNE   FAILED
         CLC   IDC+82(2),=H'133'
         BNE   FAILED
         CLC   IDC+62(2),=H'133'
         BNE   FAILED
VLOOP    GET   IDC,AREA
         L     3,RECCNT
         C     3,=F'3'
         BNL   FAILED
         MVC   EXPECT(133),BLANKS
         MVC   EXPECT+1(7),PREFIX
         LA    4,241(3)
         STC   4,EXPECT+8
         C     3,=F'1'
         BNE   CHKTHRD
         MVI   EXPECT,X'F0'
         MVI   EXPECT+132,X'E7'
CHKTHRD  C     3,=F'2'
         BNE   CHKREC
         MVI   EXPECT,X'F1'
         MVI   EXPECT+132,X'E8'
CHKREC   CLC   AREA(133),EXPECT
         BNE   FAILED
         LA    3,1(3)
         ST    3,RECCNT
         B     VLOOP
ATEND    CLC   RECCNT(4),=F'3'
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
BLANKS   DC    133X'40'
PREFIX   DC    CL7'Q4FBA00'
EXPECT   DS    CL133
AREA     DS    CL133
PASSREC  DC    CL80'BCPLQSAM Q4 FBA133 TEMP EXACT 3 PASS'
SAVREG   DS    18F
IDC      DCB   DDNAME=Q4TEMP,DSORG=PS,MACRF=GM,EODAD=ATEND
ODC      DCB   DDNAME=QOUT,DSORG=PS,MACRF=PM
         LTORG
         END   Q4FAV
