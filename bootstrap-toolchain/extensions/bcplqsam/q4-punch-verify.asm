***********************************************************************
* Q.4 INDEPENDENT IFOX FB80 VERIFIER OF THREE TEMP QSAM RECORDS.
* CHECKS ALL 80 EBCDIC BYTES, TRAILING BLANKS, COLUMN 80, AND EOF.
* DOES NOT READ FROM JES2 OR THE HERCULES ASCII PUNCH CAPTURE.
***********************************************************************
Q4VFY    CSECT
         ENTRY Q4VFY
         STM   14,12,12(13)
         LR    12,15
         USING Q4VFY,12
         LA    11,SAVREG
         ST    13,4(11)
         ST    11,8(13)
         LR    13,11
         XC    RECCNT(4),RECCNT
         OPEN  (IDC,(INPUT))
         OPEN  (ODC,(OUTPUT))
         CLI   IDC+36,X'90'
         BNE   FAILED
         CLC   IDC+82(2),=H'80'
         BNE   FAILED
         CLC   IDC+62(2),=H'800'
         BNE   FAILED
VLOOP    GET   IDC,AREA
         L     3,RECCNT
         C     3,=F'3'
         BNL   FAILED
         MVC   EXPECT(80),BLANKS
         MVC   EXPECT(7),PREFIX
         LA    4,241(3)
         STC   4,EXPECT+7
         C     3,=F'1'
         BNE   CHKTHRD
         MVI   EXPECT+79,X'E7'
CHKTHRD  C     3,=F'2'
         BNE   CHKREC
         MVI   EXPECT+79,X'E8'
CHKREC   CLC   AREA(80),EXPECT
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
BLANKS   DC    80X'40'
PREFIX   DC    CL7'Q4CARD0'
EXPECT   DS    CL80
AREA     DS    CL80
PASSREC  DC    CL80'BCPLQSAM Q4 FB80 TEMP EXACT 3 PASS'
SAVREG   DS    18F
IDC      DCB   DDNAME=Q4TEMP,DSORG=PS,MACRF=GM,EODAD=ATEND
ODC      DCB   DDNAME=QOUT,DSORG=PS,MACRF=PM
         LTORG
         END   Q4VFY
