***********************************************************************
* BC2SPRB - D3 ISOLATED PRIMARY/ALTERNATE QSAM ROUTING PROBE
* No BCPLMAIN; DEVOBJ(BCPLIO) only. R12 is probe base.
***********************************************************************
BC2SPRB  CSECT
         ENTRY BC2SPRB
         EXTRN IOINIT,IOSEL,IOWRCH,IOFIN
         STM   14,12,12(13)
         LR    12,15
         USING BC2SPRB,12
         ST    13,OLDSAVE+4
         LA    13,NEWSAVE
         LA    5,FRAME
         XC    FRAME(4),FRAME
         L     15,=A(IOINIT)
         BALR  14,15
* Primary SYSPRINT full-record marker.
         LA    8,PRIMARY
         LA    9,PRIMARYE-PRIMARY
         BAL   14,WRITE
         LA    7,10
         BAL   14,WRBYTE
* Secondary BCPALT selected lazily and left partially buffered.
         LA    1,2
         L     15,=A(IOSEL)
         BALR  14,15
         LTR   15,15
         BNZ   BAD
         LA    8,ALTMSG
         LA    9,ALTEND-ALTMSG
         BAL   14,WRITE
* Return to primary; this must not disturb buffered alternate.
         LA    1,1
         L     15,=A(IOSEL)
         BALR  14,15
         LTR   15,15
         BNZ   BAD
         LA    8,PRIMARY2
         LA    9,PRIM2END-PRIMARY2
         BAL   14,WRITE
* Flush both nonempty buffers, even with alternate not selected.
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
* WRITE: R8 string address, R9 byte count; preserve R14 as
*        the return to mainline across repeated WRBYTE calls.
WRITE    ST    14,WRRET
WRLOOP   SR    7,7
         IC    7,0(8)
         BAL   14,WRBYTE
         LA    8,1(8)
         BCT   9,WRLOOP
         L     14,WRRET
         BR    14
WRBYTE   L     15,=A(IOWRCH)
         BALR  6,15
         BR    14
         LTORG
PRIMARY  DC    C'BCPLIO PRIMARY 1'
PRIMARYE EQU   *
ALTMSG   DC    C'BCPLIO ALTERNATE'
ALTEND   EQU   *
PRIMARY2 DC    C'BCPLIO PRIMARY 2'
PRIM2END EQU   *
         DS    0F
WRRET    DC    F'0'
FRAME    DC    F'0'
OLDSAVE  DS    18F
NEWSAVE  DS    18F
         END   BC2SPRB
