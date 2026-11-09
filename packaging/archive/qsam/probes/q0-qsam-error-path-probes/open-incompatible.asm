***********************************************************************
* MILESTONE QSAM Q.0: ISOLATED INVALID DCB OPEN EXPERIMENT.
* INTENDED OUTPUT DATA SET: FB, LRECL=80, BLKSIZE=801 (INVALID).
* QSAM MAY ABEND THE STEP AT OPEN. NO INPUT OR PDS IS AT RISK.
* IF OPEN RETURNS, REPORT A DIAGNOSTIC RC=12: INVESTIGATE RESULT.
***********************************************************************
Q0BADOP  CSECT
         STM   14,12,12(13)
         LR    12,15
         USING Q0BADOP,12
         LA    11,SAVREG
         ST    13,4(11)
         ST    11,8(13)
         LR    13,11
         OPEN  (QDCB,(OUTPUT))
* RETURNING FROM OPEN IS NOT PROOF OF A SUCCESSFUL OPEN.
* LEAVE CLOSE/PUT OUT OF THIS PROBE: A FAILED OPEN MAY NOT OWN DCB.
         L     13,4(13)
         LM    14,12,12(13)
         LA    15,12
         BR    14
         DS    0F
SAVREG   DS    18F
QDCB     DCB   DDNAME=QBAD,DSORG=PS,MACRF=PM
         LTORG
         END   Q0BADOP
