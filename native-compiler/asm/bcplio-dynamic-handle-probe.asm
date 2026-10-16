***********************************************************************
* DQHPRB - BCPLIO descriptor-owned QSAM + stable handle smoke test.
* R15 0 success; 8 nonzero error, 12 stale handle found.
***********************************************************************
DQHPRB   CSECT
         ENTRY DQHPRB
         EXTRN DALLOC,DREL,HNEW,HLOOK,HCLOSE
         EXTRN DQOPEN,DQPUT,DQCLOSE
         STM   14,12,12(13)
         LR    12,15
         USING DQHPRB,12
         ST    13,OLDSAVE+4
         LA    13,NEWSAVE
* Descriptor A.
         LA    2,NAME1
         LA    3,2
         L     15,=A(DALLOC)
         BALR  14,15
         LTR   15,15
         BZ    FAIL
         ST    15,DESC1
         LR    1,15
         L     15,=A(HNEW)
         BALR  14,15
         LTR   15,15
         BZ    FAIL
         ST    15,HAND1
* Descriptor B.
         LA    2,NAME2
         LA    3,2
         L     15,=A(DALLOC)
         BALR  14,15
         LTR   15,15
         BZ    FAIL
         ST    15,DESC2
         LR    1,15
         L     15,=A(HNEW)
         BALR  14,15
         LTR   15,15
         BZ    FAIL
         ST    15,HAND2
* Open via handle lookup, verify descriptor matches.
         L     1,HAND1
         L     15,=A(HLOOK)
         BALR  14,15
         C     15,DESC1
         BNE   FAIL
         LR    1,15
         L     15,=A(DQOPEN)
         BALR  14,15
         LTR   15,15
         BNZ   FAIL
         L     1,HAND2
         L     15,=A(HLOOK)
         BALR  14,15
         C     15,DESC2
         BNE   FAIL
         LR    1,15
         L     15,=A(DQOPEN)
         BALR  14,15
         LTR   15,15
         BNZ   FAIL
* Interleave records via descriptor-owned QSAM.
         L     1,DESC1
         LA    2,REC1A
         L     15,=A(DQPUT)
         BALR  14,15
         LTR   15,15
         BNZ   FAIL
         L     1,DESC2
         LA    2,REC2A
         L     15,=A(DQPUT)
         BALR  14,15
         LTR   15,15
         BNZ   FAIL
* Close A, invalidate its handle, release descriptor.
         L     1,DESC1
         L     15,=A(DQCLOSE)
         BALR  14,15
         LTR   15,15
         BNZ   FAIL
         L     1,HAND1
         L     15,=A(HCLOSE)
         BALR  14,15
         C     15,DESC1
         BNE   FAIL
         L     1,HAND1
         L     15,=A(HLOOK)
         BALR  14,15
         LTR   15,15
         BNZ   STALE
         L     1,DESC1
         L     15,=A(DREL)
         BALR  14,15
         LTR   15,15
         BNZ   FAIL
* B remains writable after A is released.
         L     1,DESC2
         LA    2,REC2B
         L     15,=A(DQPUT)
         BALR  14,15
         LTR   15,15
         BNZ   FAIL
         L     1,DESC2
         L     15,=A(DQCLOSE)
         BALR  14,15
         LTR   15,15
         BNZ   FAIL
         L     1,HAND2
         L     15,=A(HCLOSE)
         BALR  14,15
         C     15,DESC2
         BNE   FAIL
         L     1,DESC2
         L     15,=A(DREL)
         BALR  14,15
         LTR   15,15
         BNZ   FAIL
         SR    8,8
         B     FINISH
STALE    LA    8,12
         B     FINISH
FAIL     LA    8,8
FINISH   ST    8,RESULT
         L     13,OLDSAVE+4
         L     15,RESULT
         ST    15,16(13)
         LM    14,12,12(13)
         BR    14
         LTORG
NAME1    DC    CL8'REPORT'
NAME2    DC    CL8'REPORT2'
REC1A    DC    CL132'DQH REPORT ONE'
REC2A    DC    CL132'DQH REPORT2 ONE'
REC2B    DC    CL132'DQH REPORT2 TWO'
DESC1    DC    F'0'
DESC2    DC    F'0'
HAND1    DC    F'0'
HAND2    DC    F'0'
RESULT   DC    F'0'
OLDSAVE  DS    18F
NEWSAVE  DS    18F
         END   DQHPRB
