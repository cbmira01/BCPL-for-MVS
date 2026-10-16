***********************************************************************
* IOHPRB - M1 STABLE HANDLE PRIVATE EXECUTION PROBE.
***********************************************************************
IOHPRB   CSECT
         ENTRY IOHPRB
         EXTRN DALLOC,DREL,HNEW,HLOOK,HCLOSE
         STM   14,12,12(13)
         LR    12,15
         USING IOHPRB,12
         ST    13,OLDSAVE+4
         LA    13,NEWSAVE
* Allocate first descriptor and obtain first handle.
         LA    2,NAME1
         LA    3,1
         L     15,=A(DALLOC)
         BALR  14,15
         LTR   15,15
         BZ    FAILED
         ST    15,DESC1
         LR    1,15
         L     15,=A(HNEW)
         BALR  14,15
         LTR   15,15
         BZ    FAILED
         ST    15,HAND1
         LR    1,15
         L     15,=A(HLOOK)
         BALR  14,15
         C     15,DESC1
         BNE   FAILED
* Close handle, then release descriptor.
         L     1,HAND1
         L     15,=A(HCLOSE)
         BALR  14,15
         C     15,DESC1
         BNE   FAILED
         LR    1,15
         L     15,=A(DREL)
         BALR  14,15
         LTR   15,15
         BNZ   FAILED
         L     1,HAND1
         L     15,=A(HLOOK)
         BALR  14,15
         LTR   15,15
         BNZ   FAILED
* Second descriptor might reuse freed GETMAIN address.
         LA    2,NAME2
         LA    3,2
         L     15,=A(DALLOC)
         BALR  14,15
         LTR   15,15
         BZ    FAILED
         ST    15,DESC2
         LR    1,15
         L     15,=A(HNEW)
         BALR  14,15
         LTR   15,15
         BZ    FAILED
         ST    15,HAND2
         C     15,HAND1
         BE    FAILED
         L     1,HAND1
         L     15,=A(HLOOK)
         BALR  14,15
         LTR   15,15
         BNZ   FAILED
         L     1,HAND2
         L     15,=A(HLOOK)
         BALR  14,15
         C     15,DESC2
         BNE   FAILED
         L     1,HAND2
         L     15,=A(HCLOSE)
         BALR  14,15
         C     15,DESC2
         BNE   FAILED
         LR    1,15
         L     15,=A(DREL)
         BALR  14,15
         LTR   15,15
         BNZ   FAILED
* Repeated close cannot access freed descriptor.
         L     1,HAND2
         L     15,=A(HCLOSE)
         BALR  14,15
         LTR   15,15
         BNZ   FAILED
GOOD     L     13,OLDSAVE+4
         LM    14,12,12(13)
         SR    15,15
         BR    14
FAILED   L     13,OLDSAVE+4
         LM    14,12,12(13)
         LA    15,8
         BR    14
         LTORG
NAME1    DC    CL8'CUSTOMER'
NAME2    DC    CL8'REPORT'
HAND1    DC    F'0'
HAND2    DC    F'0'
DESC1    DC    F'0'
DESC2    DC    F'0'
OLDSAVE  DS    18F
NEWSAVE  DS    18F
         END   IOHPRB
