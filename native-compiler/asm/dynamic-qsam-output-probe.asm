***********************************************************************
* DQOPRB - M1 PRIVATE DYNAMIC-DD QSAM OUTPUT SMOKE PROBE.
* Runtime replaces DCB DDNAME; no compiled BCPL or FIND wiring.
* One static prototype DCB (per-DD allocation is next gate).
* R15=0 success, 8 bad post-OPEN PUT pointer.
***********************************************************************
DQOPRB   CSECT
         ENTRY DQOPRB
         STM   14,12,12(13)
         LR    12,15
         USING DQOPRB,12
         ST    13,OLDSAVE+4
         LA    13,NEWSAVE
* Name deliberately differs from assembly-time DCB DDNAME.
         MVC   OUTDCB+40(8),DDNAME
         OPEN  (OUTDCB,(OUTPUT))
* Verify QSAM installed a plausible nonzero PUT routine pointer
* before using the QSAM PUT macro's indirect call.
         LA    1,OUTDCB
         L     15,48(1)
         LTR   15,15
         BZ    BADPTR
         C     15,=X'D01407FE'
         BE    BADPTR
         PUT   OUTDCB,OUTBUF
         CLOSE (OUTDCB)
         SR    8,8
         B     FINISH
BADPTR   LA    8,8
FINISH   ST    8,RESULT
         L     13,OLDSAVE+4
         L     15,RESULT
         ST    15,16(13)
         LM    14,12,12(13)
         BR    14
         LTORG
DDNAME   DC    CL8'REPORT'
RESULT   DS    F
OLDSAVE  DS    18F
NEWSAVE  DS    18F
OUTBUF   DC    CL132'DYNAMIC QSAM DD PROBE PASSED'
OUTDCB   DCB   DDNAME=DUMMY,DSORG=PS,MACRF=PM
         END   DQOPRB
