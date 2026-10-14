***********************************************************************
* BCRPPRB - D3 PRIVATE IOREPL PRIMARY REPLACEMENT PROBE
* Independent DEVOBJ(BCPLIO); never installs production objects.
* Expect primary 'STACK OVERFLOW', alternate 'ALT INTACT'.
***********************************************************************
BCRPPRB  CSECT
         ENTRY BCRPPRB
         EXTRN IOINIT,IOFIN,IOSEL,IOREPL,IODIAG,IOSTAT
         EXTRN IOWRCH,IOOUT
         STM   14,12,12(13)
         LR    12,15
         USING BCRPPRB,12
         ST    13,OLDSAVE+4
         LA    13,NEWSAVE
         LA    5,FRAME
         XC    FRAME(4),FRAME
         L     15,=A(IOINIT)
         BALR  14,15
* Buffer alternate text, leaving its record unflushed.
         LA    1,2
         L     15,=A(IOSEL)
         BALR  14,15
         LTR   15,15
         BNZ   BAD
         LA    8,ALTMSG
         LA    9,ALTEND-ALTMSG
         BAL   14,WRITE
* Diagnostic append must go to primary even while alt selected.
         LA    1,OLDMSG
         LA    2,OLDEND-OLDMSG
         L     15,=A(IODIAG)
         BALR  14,15
         LTR   15,15
         BNZ   BAD
* Invalid length 133 must fail without replacing primary.
         LA    1,NEWMSG
         LA    2,133
         L     15,=A(IOREPL)
         BALR  14,15
         C     15,=F'8'
         BNE   BAD
* Valid replacement discards old primary record.
         LA    1,NEWMSG
         LA    2,NEWEND-NEWMSG
         L     15,=A(IOREPL)
         BALR  14,15
         LTR   15,15
         BNZ   BAD
* Successful replacement must not latch output overflow.
         L     15,=A(IOSTAT)
         BALR  14,15
         LTR   15,15
         BNZ   BAD
* Native alternate selection must be unchanged.
         L     15,=A(IOOUT)
         BALR  6,15
         ST    7,ALTH
         LA    1,1
         L     15,=A(IOSEL)
         BALR  14,15
         L     15,=A(IOOUT)
         BALR  6,15
         LTR   7,7
         BZ    BAD
         C     7,ALTH
         BE    BAD
         L     15,=A(IOFIN)
         BALR  14,15
         L     13,OLDSAVE+4
         LM    14,12,12(13)
         SR    15,15
         BR    14
BAD      L     15,=A(IOFIN)
         BALR  14,15
         L     13,OLDSAVE+4
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
OLDMSG   DC    C'OLD PRIMARY MUST NOT APPEAR'
OLDEND   EQU   *
NEWMSG   DC    C'STACK OVERFLOW'
NEWEND   EQU   *
ALTMSG   DC    C'ALT INTACT'
ALTEND   EQU   *
         DS    0F
ALTH     DC    F'0'
WRRET    DC    F'0'
FRAME    DC    F'0'
OLDSAVE  DS    18F
NEWSAVE  DS    18F
         END   BCRPPRB
