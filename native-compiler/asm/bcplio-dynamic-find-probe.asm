***********************************************************************
* DQFPRB - public FINDOUTPUT private-call gate (R14 linkage).
* Calls DQFIND counted-string and checks HLOOK, DQCLOSE,
* HCLOSE, DREL. Tests unknown DD => 0 and stale handle => 0.
* Not a compiled BCPL WRCH/SELECTOUTPUT regression.
***********************************************************************
DQFPRB   CSECT
         ENTRY DQFPRB
         EXTRN DQFIND,HLOOK,DQCLOSE,HCLOSE,DREL,DQPUT
         STM   14,12,12(13)
         LR    12,15
         USING DQFPRB,12
         ST    13,OLDSAVE+4
         LA    13,NEWSAVE
         LA    1,NAME
         L     15,=A(DQFIND)
         BALR  14,15
         LTR   15,15
         BZ    FAIL
         ST    15,HANDLE
         LR    1,15
         L     15,=A(HLOOK)
         BALR  14,15
         LTR   15,15
         BZ    FAIL
         ST    15,DESC
         LR    1,15
         LA    2,RECORD
         L     15,=A(DQPUT)
         BALR  14,15
         LTR   15,15
         BNZ   FAIL
         L     1,DESC
         L     15,=A(DQCLOSE)
         BALR  14,15
         LTR   15,15
         BNZ   FAIL
         L     1,HANDLE
         L     15,=A(HCLOSE)
         BALR  14,15
         C     15,DESC
         BNE   FAIL
         L     1,DESC
         L     15,=A(DREL)
         BALR  14,15
         LTR   15,15
         BNZ   FAIL
         L     1,HANDLE
         L     15,=A(HLOOK)
         BALR  14,15
         LTR   15,15
         BNZ   FAIL
* Missing JCL DD must be rejected without ABEND.
         LA    1,BOGUS
         L     15,=A(DQFIND)
         BALR  14,15
         LTR   15,15
         BNZ   FAIL
         SR    8,8
         B     DONE
FAIL     LA    8,8
DONE     ST    8,RESULT
         L     13,OLDSAVE+4
         L     15,RESULT
         ST    15,16(13)
         LM    14,12,12(13)
         BR    14
         LTORG
NAME     DC    AL1(6),CL6'REPORT'
BOGUS    DC    AL1(8),CL8'ZZZZZZZZ'
RECORD   DC    CL132'DQFIND OUTPUT SUCCESS'
HANDLE   DC    F'0'
DESC     DC    F'0'
RESULT   DC    F'0'
OLDSAVE  DS    18F
NEWSAVE  DS    18F
         END   DQFPRB
