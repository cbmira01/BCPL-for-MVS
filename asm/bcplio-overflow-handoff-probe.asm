***********************************************************************
* BCOVPRB - D3 NONRETURNING BCPLIO OVERFLOW/STOP HANDOFF PROBE
* GO should terminate RC=12 and emit exactly 132 X characters.
* Self-contained caller owns termination and IOFIN, no BCPLMAIN.
***********************************************************************
BCOVPRB  CSECT
         ENTRY BCOVPRB
         EXTRN IOINIT,IOWRCH,IOFIN,IOBIND,IOSTAT
         STM   14,12,12(13)
         LR    12,15
         USING BCOVPRB,12
         ST    13,OLDSAVE+4
         LA    13,NEWSAVE
         LA    5,FRAME
         XC    FRAME(4),FRAME
         L     15,=A(IOINIT)
         BALR  14,15
* Install caller-owned, nonreturning STOP exit.
         LA    1,OVEXIT
         L     15,=A(IOBIND)
         BALR  14,15
         LA    9,133
OVLOOP   LA    7,231
         L     15,=A(IOWRCH)
         BALR  6,15
         BCT   9,OVLOOP
* A return from the 133rd write is a test failure.
         B     RETBAD
* Callback sees R7=12; it owns IOFIN/STOP and does not return.
OVEXIT   C     7,=F'12'
         BNE   FAILED
         L     15,=A(IOSTAT)
         BALR  14,15
         C     15,=F'12'
         BNE   FAILED
         L     15,=A(IOFIN)
         BALR  14,15
         B     RETGOOD
FAILED   L     15,=A(IOFIN)
         BALR  14,15
RETBAD   L     13,OLDSAVE+4
         LM    14,12,12(13)
         LA    15,8
         BR    14
RETGOOD  L     13,OLDSAVE+4
         LM    14,12,12(13)
         LA    15,12
         BR    14
         LTORG
         DS    0F
FRAME    DC    F'0'
OLDSAVE  DS    18F
NEWSAVE  DS    18F
         END   BCOVPRB
