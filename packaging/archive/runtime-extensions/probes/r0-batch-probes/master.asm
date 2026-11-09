***********************************************************************
* R.0 TEST ONLY: INVOKE BOTH INDEPENDENT EVIDENCE SUBPROGRAMS.
***********************************************************************
R0BM     CSECT
         ENTRY R0BM
         EXTRN R0DCHK,R0FCHK
         STM   14,12,12(13)
         LR    12,15
         USING R0BM,12
         LA    11,SAVEA
         ST    13,4(11)
         ST    11,8(13)
         LR    13,11
         LA    11,CALLSV
         ST    13,4(11)
         ST    11,8(13)
         LR    13,11
         L     15,=A(R0DCHK)
         BALR  14,15
         ST    15,DEPSTAT
         L     15,=A(R0FCHK)
         BALR  14,15
         O     15,DEPSTAT
         L     13,4(13)
         L     13,4(13)
         LM    14,14,12(13)
         LM    0,12,20(13)
         BR    14
         DS    0F
DEPSTAT  DC    F'0'
SAVEA    DS    18F
CALLSV   DS    18F
         LTORG
         END   R0BM
