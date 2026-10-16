***********************************************************************
* DQBPRB - M1 BCPL-facing dynamic output ABI integration.
* R5 frame, R6 return, R7 BCPL value; R10 private BCPLIO base.
* Verify two interleaved outputs, partial close, stale handle,
* primary selection and primary output. Returns RC 0 or 8.
***********************************************************************
DQBPRB   CSECT
         ENTRY DQBPRB
         EXTRN IOINIT,IOFIN,IOFOUT,IOSOUT,IOWRCH,IOENDW,IOOUT
         EXTRN HLOOK
         STM   14,12,12(13)
         LR    12,15
         USING DQBPRB,12
         ST    13,OLDSAVE+4
         LA    13,NEWSAVE
         LA    5,FRAME
         SR    1,1
         L     15,=A(IOINIT)
         BALR  14,15
         LA    1,FRAME
         CR    5,1
         BNE   BADFRAME
* FINDOUTPUT REPORT (BCPL counted string word address)
         LA    7,STR1
         SRL   7,2
         L     15,=A(IOFOUT)
         BALR  6,15
         LA    1,FRAME
         CR    5,1
         BNE   BADFRAME
         LTR   7,7
         BZ    FAIL
         ST    7,HAND1
* FINDOUTPUT REPORT2
         LA    7,STR2
         SRL   7,2
         L     15,=A(IOFOUT)
         BALR  6,15
         LA    1,FRAME
         CR    5,1
         BNE   BADFRAME
         LTR   7,7
         BZ    FAIL
         C     7,HAND1
         BE    FAIL
         ST    7,HAND2
* Select first; emit a complete line.
         L     7,HAND1
         L     15,=A(IOSOUT)
         BALR  6,15
         LA    1,FRAME
         CR    5,1
         BNE   BADFRAME
         LA    8,MSG1
         LA    9,13
         BAL   14,SEND
* Select second; leave partial text (flush on ENDWRITE).
         L     7,HAND2
         L     15,=A(IOSOUT)
         BALR  6,15
         LA    1,FRAME
         CR    5,1
         BNE   BADFRAME
         LA    8,MSG2
         LA    9,16
         BAL   14,SEND
* Select first again, write second complete line.
         L     7,HAND1
         L     15,=A(IOSOUT)
         BALR  6,15
         LA    1,FRAME
         CR    5,1
         BNE   BADFRAME
         LA    8,MSG3
         LA    9,13
         BAL   14,SEND
* ENDWRITE first: closes, tombstones, reverts to primary.
         L     15,=A(IOENDW)
         BALR  6,15
         LA    1,FRAME
         CR    5,1
         BNE   BADFRAME
         L     1,HAND1
         L     15,=A(HLOOK)
         BALR  14,15
         LA    1,FRAME
         CR    5,1
         BNE   BADFRAME
         LTR   15,15
         BNZ   FAIL
* Re-select remaining second handle, then ENDWRITE.
         L     7,HAND2
         L     15,=A(IOSOUT)
         BALR  6,15
         LA    1,FRAME
         CR    5,1
         BNE   BADFRAME
         L     15,=A(IOENDW)
         BALR  6,15
         LA    1,FRAME
         CR    5,1
         BNE   BADFRAME
         L     1,HAND2
         L     15,=A(HLOOK)
         BALR  14,15
         LA    1,FRAME
         CR    5,1
         BNE   BADFRAME
         LTR   15,15
         BNZ   FAIL
* Primary selected after ENDWRITE; output to SYSPRINT.
         L     15,=A(IOOUT)
         BALR  6,15
         LA    1,FRAME
         CR    5,1
         BNE   BADFRAME
         LTR   7,7
         BZ    FAIL
         LA    8,MSG4
         LA    9,12
         BAL   14,SEND
* Flush primary on FIN.
         L     15,=A(IOFIN)
         BALR  14,15
         LA    1,FRAME
         CR    5,1
         BNE   BADFRAME
         SR    8,8
         B     DONE
* SEND R8 byte ptr, R9 byte count; append LF on first / third.
* Test message 2 intentionally omits LF.
SEND     ST    14,SENDRET
SENDLP   SR    7,7
         IC    7,0(8)
         L     15,=A(IOWRCH)
         BALR  6,15
         LA    1,FRAME
         CR    5,1
         BNE   BADFRAME
         LA    8,1(8)
         BCT   9,SENDLP
         L     14,SENDRET
         BR    14
BADFRAME LA    8,12
         B     DONE
FAIL     LA    8,8
DONE     ST    8,RESULT
         L     13,OLDSAVE+4
         L     15,RESULT
         ST    15,16(13)
         LM    14,12,12(13)
         BR    14
         LTORG
         DS    0F
STR1     DC    AL1(6),CL6'REPORT'
         DS    0F
STR2     DC    AL1(7),CL7'REPORT2'
MSG1     DC    C'DQB REPORT A',X'0A'
MSG2     DC    C'DQB REPORT2 PART'
MSG3     DC    C'DQB REPORT B',X'0A'
MSG4     DC    C'DQB PRIMARY',X'0A'
HAND1    DC    F'0'
HAND2    DC    F'0'
RESULT   DC    F'0'
SENDRET  DC    F'0'
FRAME    DC    F'0'
OLDSAVE  DS    18F
NEWSAVE  DS    18F
         END   DQBPRB
