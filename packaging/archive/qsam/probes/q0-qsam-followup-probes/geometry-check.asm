***********************************************************************
* Q.0 TEST-ONLY: JFCB GEOMETRY PRECHECK. NEVER OPEN QGOOD/QBAD.
* JFCB OFFSETS +100 RECFM, +102 BLKSIZE, +104 LRECL TO VERIFY.
* EXPECT FB80/800 VALID AND FB80/801 REJECTED BEFORE OPEN.
***********************************************************************
Q0GEOM   CSECT
         STM   14,12,12(13)
         LR    12,15
         USING Q0GEOM,12
         LA    11,SAVREG
         ST    13,4(11)
         ST    11,8(13)
         LR    13,11
         LA    2,GDCB
         RDJFCB ((2))
         LTR   15,15
         BNZ   FAILED
         CLI   GJFCB+100,X'90'
         BNE   FAILED
         CLC   GJFCB+102(2),=H'800'
         BNE   FAILED
         CLC   GJFCB+104(2),=H'80'
         BNE   FAILED
         LA    2,BADDCB
         RDJFCB ((2))
         LTR   15,15
         BNZ   FAILED
         CLI   BJFCB+100,X'90'
         BNE   FAILED
         CLC   BJFCB+102(2),=H'801'
         BNE   FAILED
         CLC   BJFCB+104(2),=H'80'
         BNE   FAILED
* CHECK THE ACTUAL JFCB FIELD PAIR, NOT JUST A HARDCODED RESULT.
         LH    4,BJFCB+104
         LTR   4,4
         BZ    FAILED
         LH    3,BJFCB+102
         SR    2,2
         DR    2,4
         LTR   2,2
         BZ    FAILED
* A NONZERO REMAINDER MEANS REJECT; DO NOT OPEN BADDCB.
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
PASSREC  DC    CL80'Q0 JFCB FB80/800 OK FB80/801 REJECT PASS'
SAVREG   DS    18F
GDCB     DCB   DDNAME=QGOOD,DSORG=PS,MACRF=GM,EXLST=GEXL
BADDCB   DCB   DDNAME=QBAD,DSORG=PS,MACRF=GM,EXLST=BEXL
ODCB     DCB   DDNAME=QOUT,DSORG=PS,MACRF=PM
         DS    0F
GEXL     DC    X'87',AL3(GJFCB)
         DS    0F
GJFCB    DS    CL176
         DS    0F
BEXL     DC    X'87',AL3(BJFCB)
         DS    0F
BJFCB    DS    CL176
         LTORG
         END   Q0GEOM
