***********************************************************************
* Q.2 INDEPENDENT CHECK OF STOP(8) FINALIZER FB80 PHYSICAL FLUSH.
* QPOST MUST HOLD EXACTLY ONE 80-BYTE RECORD AFTER BCPL STOP(8).
***********************************************************************
Q2STVF   CSECT
         ENTRY Q2STVF
         STM   14,12,12(13)
         LR    12,15
         USING Q2STVF,12
         LA    11,SAVREG
         ST    13,4(11)
         ST    11,8(13)
         LR    13,11
         XC    RECCNT(4),RECCNT
         MVI   EXPECT,X'AD'
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
         OPEN  (IDC,(INPUT))
         OPEN  (ODC,(OUTPUT))
NEXT     GET   IDC,AREA
         L     3,RECCNT
         LTR   3,3
         BNZ   FAILED
         CLC   AREA(80),EXPECT
         BNE   FAILED
         LA    3,1
         ST    3,RECCNT
         B     NEXT
ATEND    CLC   RECCNT(4),=F'1'
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
PASSREC  DC    CL80'BCPLQSAM Q2 STOP FLUSH FB80 EXACT PASS'
SAVREG   DS    18F
IDC      DCB   DDNAME=QPOST,DSORG=PS,MACRF=GM,EODAD=ATEND
ODC      DCB   DDNAME=QOUT,DSORG=PS,MACRF=PM
         LTORG
         END   Q2STVF
