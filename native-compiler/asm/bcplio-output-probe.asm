***********************************************************************
* BCIOPRB - D2.2 DIRECT BCPLIO OUTPUT PROBE (NO BCPLMAIN)
* Native MVS entry: R14 caller return, R13 MVS savearea.
* BCPL simulation: R5 frame, R6 per-call return, R7 character.
* Writes D2 marker and newline, then 133 X bytes; verifies overflow
* reports 12 via native IOSTAT; IOFIN flushes 132-byte record.
* D2.3: every IOWRCH call verifies R0-R3,R5,R7-R9,R11-R12,R15
* and R4 restoration from 0(R5); excludes R6,R10,R13,R14.
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
* D3 repeat-open guard: should not OPEN the DCB a second time.
         L     15,=A(IOINIT)
         BALR  14,15
* Distinct register sentinels through the entire character sequence.
         LA    0,17
         LA    1,34
         LA    2,51
         LA    3,68
         LA    11,85
* IOWRCH uses BCPL R6 return; R7 character.
         LA    8,MSG
         LA    9,MSGEND-MSG
NEXTCH   SR    7,7
         IC    7,0(8)
         BAL   14,CHECKWR
         LA    8,1(8)
         BCT   9,NEXTCH
         LA    7,10
         BAL   14,CHECKWR
* Fill exactly 132 bytes; the 133rd must latch overflow 12.
         LA    9,133
OVLOOP   LA    7,231
         BAL   14,CHECKWR
         BCT   9,OVLOOP
         L     15,=A(IOSTAT)
         BALR  14,15
         ST    15,OVRESULT
* IOFIN flushes/closes output stream via R14.
         L     15,=A(IOFIN)
         BALR  14,15
* D3 repeat-close guard: should not PUT or CLOSE again.
         L     15,=A(IOFIN)
         BALR  14,15
* Select return path while R12 is still our assembler base.
* LM 14,12 also restores R15; set the return code AFTER the LM.
         L     15,OVRESULT
         C     15,=F'12'
         BNE   BADRC
         CLI   BADFLAG,X'00'
         BE    GOODRC
BADRC    L     13,OLDSAVE+4
         LM    14,12,12(13)
         LA    15,8
         BR    14
GOODRC   L     13,OLDSAVE+4
         LM    14,12,12(13)
         SR    15,15
         BR    14
*
* Wrapper snapshots registers immediately before/after each call.
* R6 is a linkage register, R10 BCPLIO's private base. R14 holds
* wrapper return; R13 is the MVS save-area pointer.
CHECKWR  L     15,=A(IOWRCH)
         STM   0,15,REGPRE
         BALR  6,15
         STM   0,15,REGPOST
         CLC   REGPRE(16),REGPOST
         BNE   REGBAD
         CLC   REGPRE+20(4),REGPOST+20
         BNE   REGBAD
         CLC   REGPRE+28(12),REGPOST+28
         BNE   REGBAD
         CLC   REGPRE+44(8),REGPOST+44
         BNE   REGBAD
         CLC   REGPRE+60(4),REGPOST+60
         BNE   REGBAD
         C     4,FRAME
         BNE   REGBAD
         BR    14
REGBAD   MVI   BADFLAG,X'01'
         BR    14
         LTORG
MSG      DC    C'BCPLIO D2 PROBE'
MSGEND   EQU   *
         DS    0F
FRAME    DC    F'0'
OVRESULT DC    F'0'
BADFLAG  DC    X'00'
         DS    0F
REGPRE   DS    16F
REGPOST  DS    16F
OLDSAVE  DS    18F
NEWSAVE  DS    18F
         END   BCIOPRB
