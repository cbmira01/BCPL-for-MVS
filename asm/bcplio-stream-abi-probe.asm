***********************************************************************
* BCSTRPB - D3 BCPL OUTPUT HANDLE/SELECTION/WRAP/ENDWRITE PROBE
* Independent BCPLIO DEVOBJ linkage, no BCPLMAIN.
***********************************************************************
BCSTRPB  CSECT
         ENTRY BCSTRPB
         EXTRN IOINIT,IOFIN,IOFOUT,IOSOUT,IOOUT
         EXTRN IOWRAP,IOENDW,IOWRCH
         STM   14,12,12(13)
         LR    12,15
         USING BCSTRPB,12
         ST    13,OLDSAVE+4
         LA    13,NEWSAVE
         LA    5,FRAME
         XC    FRAME(4),FRAME
         L     15,=A(IOINIT)
         BALR  14,15
* FINDOUTPUT('SYSPRINT') returns primary handle.
         LA    7,NMPRI
         SRL   7,2
         L     15,=A(IOFOUT)
         BALR  6,15
         LTR   7,7
         BZ    BAD
         ST    7,PRIH
         L     15,=A(IOOUT)
         BALR  6,15
         C     7,PRIH
         BNE   BAD
* FINDOUTPUT('BCPALT') opens alternate without selecting.
         LA    7,NMALT
         SRL   7,2
         L     15,=A(IOFOUT)
         BALR  6,15
         LTR   7,7
         BZ    BAD
         ST    7,ALTH
         L     15,=A(IOOUT)
         BALR  6,15
         C     7,PRIH
         BNE   BAD
* SELECTOUTPUT(alt), check selected handle.
         L     7,ALTH
         L     15,=A(IOSOUT)
         BALR  6,15
         L     15,=A(IOOUT)
         BALR  6,15
         C     7,ALTH
         BNE   BAD
         LA    8,ALTMSG
         LA    9,ALTEND-ALTMSG
         BAL   14,WRITE
         L     15,=A(IOWRAP)
         BALR  6,15
* Alternate second partial record; ENDWRITE flushes it and closes.
         LA    8,ALT2MSG
         LA    9,ALT2END-ALT2MSG
         BAL   14,WRITE
         L     15,=A(IOENDW)
         BALR  6,15
         L     15,=A(IOOUT)
         BALR  6,15
         C     7,PRIH
         BNE   BAD
* Primary message (left partial until IOFIN).
         LA    8,PRIMSG
         LA    9,PRIEND-PRIMSG
         BAL   14,WRITE
         L     15,=A(IOFIN)
         BALR  14,15
         L     13,OLDSAVE+4
         LM    14,12,12(13)
         SR    15,15
         BR    14
BAD      L     13,OLDSAVE+4
         LM    14,12,12(13)
         LA    15,8
         BR    14
WRITE    ST    14,WRRET
WLOOP    SR    7,7
         IC    7,0(8)
         L     15,=A(IOWRCH)
         BALR  6,15
         LA    8,1(8)
         BCT   9,WLOOP
         L     14,WRRET
         BR    14
         LTORG
         DS    0F
NMPRI    DC    X'08'
         DC    C'SYSPRINT'
         DS    0F
NMALT    DC    X'06'
         DC    C'BCPALT'
PRIMSG   DC    C'BCPLIO HANDLE PRIMARY'
PRIEND   EQU   *
ALTMSG   DC    C'BCPLIO HANDLE ALT WRAP'
ALTEND   EQU   *
ALT2MSG  DC    C'BCPLIO HANDLE ALT END'
ALT2END  EQU   *
         DS    0F
WRRET    DC    F'0'
PRIH     DC    F'0'
ALTH     DC    F'0'
FRAME    DC    F'0'
OLDSAVE  DS    18F
NEWSAVE  DS    18F
         END   BCSTRPB
