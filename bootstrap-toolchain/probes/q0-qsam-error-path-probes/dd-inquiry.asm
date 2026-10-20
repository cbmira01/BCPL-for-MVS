***********************************************************************
* MILESTONE QSAM, MARCH Q.0 - TEST-ONLY DD ALLOCATION INQUIRY.
* RDJFCB DOES NOT OPEN EITHER DD. QPRES MUST EXIST IN THIS STEP;
* QMISS MUST BE ABSENT. EXPECT R15=0 AND R15=4, RESPECTIVELY.
* A MISSING DD IS NEVER PASSED TO OPEN IN THIS EXPERIMENT.
***********************************************************************
Q0DDCK   CSECT
         STM   14,12,12(13)
         LR    12,15
         USING Q0DDCK,12
         LA    11,SAVREG
         ST    13,4(11)
         ST    11,8(13)
         LR    13,11
         LA    2,PDCB
         RDJFCB ((2))
         LTR   15,15
         BNZ   FAILED
         LA    2,MDCB
         RDJFCB ((2))
         C     15,=F'4'
         BNE   FAILED
         OPEN  (ODCB,(OUTPUT))
         PUT   ODCB,PASSREC
         CLOSE (ODCB)
         L     13,4(13)
         LM    14,12,12(13)
         SR    15,15
         BR    14
FAILED   L     13,4(13)
         LM    14,12,12(13)
         LA    15,8
         BR    14
         DS    0F
PASSREC  DC    CL80'Q0 DD RDJFCB PRESENT=0 MISSING=4 PASS'
SAVREG   DS    18F
PDCB     DCB   DDNAME=QPRES,DSORG=PS,MACRF=GM,EXLST=PEXL
MDCB     DCB   DDNAME=QMISS,DSORG=PS,MACRF=GM,EXLST=MEXL
ODCB     DCB   DDNAME=QOUT,DSORG=PS,MACRF=PM
         DS    0F
PEXL     DC    X'87',AL3(PJFCB)
         DS    0F
PJFCB    DS    CL176
         DS    0F
MEXL     DC    X'87',AL3(MJFCB)
         DS    0F
MJFCB    DS    CL176
         LTORG
         END   Q0DDCK
