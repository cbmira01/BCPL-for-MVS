***********************************************************************
* BCDIPRB - D3 BCPLIO PRIMARY DIAGNOSTIC APPEND PROBE
* Isolated DEVOBJ(BCPLIO), no BCPLMAIN/global-vector changes.
***********************************************************************
BCDIPRB  CSECT
         ENTRY BCDIPRB
         EXTRN IOINIT,IOFIN,IODIAG,IOSTAT,IOSEL
         STM   14,12,12(13)
         LR    12,15
         USING BCDIPRB,12
         ST    13,OLDSAVE+4
         LA    13,NEWSAVE
         L     15,=A(IOINIT)
         BALR  14,15
* Try alternate selection to prove diagnostic bypasses selection.
* JCL provides BCPALT.
         LA    1,2
         L     15,=A(IOSEL)
         BALR  14,15
         LTR   15,15
         BNZ   FAIL
         LA    1,MSG
         LA    2,MSGE-MSG
         L     15,=A(IODIAG)
         BALR  14,15
         LTR   15,15
         BNZ   FAIL
* Fill remaining record exactly using 112 spaces.
         LA    1,SPACES
         LA    2,132-(MSGE-MSG)
         L     15,=A(IODIAG)
         BALR  14,15
         LTR   15,15
         BNZ   FAIL
* One more character must latch 12, without PUT or callback.
         LA    1,EXTRA
         LA    2,1
         L     15,=A(IODIAG)
         BALR  14,15
         C     15,=F'12'
         BNE   FAIL
         L     15,=A(IOSTAT)
         BALR  14,15
         C     15,=F'12'
         BNE   FAIL
         L     15,=A(IOFIN)
         BALR  14,15
         L     13,OLDSAVE+4
         LM    14,12,12(13)
         SR    15,15
         BR    14
FAIL     L     15,=A(IOFIN)
         BALR  14,15
         L     13,OLDSAVE+4
         LM    14,12,12(13)
         LA    15,8
         BR    14
         LTORG
MSG      DC    C'BCPLIO DIAG PRIMARY'
MSGE     EQU   *
SPACES   DC    CL132' '
EXTRA    DC    C'Z'
         DS    0F
OLDSAVE  DS    18F
NEWSAVE  DS    18F
         END   BCDIPRB
