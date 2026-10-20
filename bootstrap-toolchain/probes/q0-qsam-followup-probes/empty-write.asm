***********************************************************************
* Q.0 TEST-ONLY: CREATE EMPTY FB80 DISK FILE WITH OPEN/CLOSE ONLY.
***********************************************************************
Q0EMW    CSECT
         STM   14,12,12(13)
         LR    12,15
         USING Q0EMW,12
         LA    11,SAVREG
         ST    13,4(11)
         ST    11,8(13)
         LR    13,11
         OPEN  (QDCB,(OUTPUT))
         CLOSE (QDCB)
         L     13,4(13)
         LM    14,12,12(13)
         SR    15,15
         BR    14
SAVREG   DS    18F
QDCB     DCB   DDNAME=QDISK,DSORG=PS,MACRF=PM
         LTORG
         END   Q0EMW
