***********************************************************************
* BCIOPRB - D2.2 DIRECT BCPLIO OUTPUT PROBE (NO BCPLMAIN)
* Native MVS entry: R14 caller return, R13 MVS savearea.
* BCPL simulation: R5 frame, R6 per-call return, R7 character.
* Writes D2 marker and newline, then 133 X bytes; verifies overflow
* reports 12 via native IOSTAT; IOFIN flushes 132-byte record.
***********************************************************************
BCIOPRB  CSECT
         ENTRY BCIOPRB
         EXTRN IOINIT,IOWRCH,IOFIN,IOSTAT
         STM   14,12,12(13)
         LR    12,15
         USING BCIOPRB,12
         ST    13,OLDSAVE+4
         LA    13,NEWSAVE
         LA    5,FRAME
         XC    FRAME(4),FRAME
* IOINIT uses native R14 return. Original EXEC PARM pointer in R1.
         L     15,=A(IOINIT)
         BALR  14,15
* IOWRCH uses BCPL R6 return; R7 character.
         LA    8,MSG
         LA    9,MSGEND-MSG
NEXTCH   SR    7,7
         IC    7,0(8)
         L     15,=A(IOWRCH)
         BALR  6,15
         LA    8,1(8)
         BCT   9,NEXTCH
         LA    7,10
         L     15,=A(IOWRCH)
         BALR  6,15
* Fill exactly 132 bytes; the 133rd must latch overflow 12.
         LA    9,133
OVLOOP   LA    7,231
         L     15,=A(IOWRCH)
         BALR  6,15
         BCT   9,OVLOOP
         L     15,=A(IOSTAT)
         BALR  14,15
         ST    15,OVRESULT
* IOFIN flushes/closes output stream via R14.
         L     15,=A(IOFIN)
         BALR  14,15
* Evaluate before restoring R12, the probe's assembler base.
         L     15,OVRESULT
         C     15,=F'12'
         BE    OKRET
         LA    15,8
         B     EXIT
OKRET    SR    15,15
EXIT     L     13,OLDSAVE+4
         LM    14,12,12(13)
         BR    14
         LTORG
MSG      DC    C'BCPLIO D2 PROBE'
MSGEND   EQU   *
         DS    0F
FRAME    DC    F'0'
OVRESULT DC    F'0'
OLDSAVE  DS    18F
NEWSAVE  DS    18F
         END   BCIOPRB
