***********************************************************************
* IODRPRB - M1 PRIVATE DESCRIPTOR REGISTRY EXECUTION PROBE.
* DALLOC / DREL ARE NATIVE R14-LINKED BCPLIO ENTRIES.
***********************************************************************
IODRPRB  CSECT
         ENTRY IODRPRB
         EXTRN DALLOC,DREL
         STM   14,12,12(13)
         LR    12,15
         USING IODRPRB,12
         ST    13,OLDSAVE+4
         LA    13,NEWSAVE
* Allocate FIRST input descriptor.
         LA    2,NAME1
         LA    3,1
         L     15,=A(DALLOC)
         BALR  14,15
         LTR   15,15
         BZ    FAILED
         ST    15,PTR1
         C     3,=F'1'
         BNE   FAILED
         CLC   8(8,15),NAME1
         BNE   FAILED
         CLC   4(4,15),=F'1'
         BNE   FAILED
         CLC   0(4,15),=F'0'
         BNE   FAILED
* Allocate SECOND output descriptor; it becomes list head.
         LA    2,NAME2
         LA    3,2
         L     15,=A(DALLOC)
         BALR  14,15
         LTR   15,15
         BZ    FAILED
         ST    15,PTR2
         CLC   8(8,15),NAME2
         BNE   FAILED
         CLC   4(4,15),=F'2'
         BNE   FAILED
         L     6,PTR1
         CR    15,6
         BE    FAILED
         C     6,0(15)
         BNE   FAILED
* Remove FIRST (non-head) while SECOND remains registered.
         LR    1,6
         L     15,=A(DREL)
         BALR  14,15
         LTR   15,15
         BNZ   FAILED
* Repeated release must fail without dereferencing stale pointer.
         L     1,PTR1
         L     15,=A(DREL)
         BALR  14,15
         C     15,=F'8'
         BNE   FAILED
* Remove SECOND (head), then reject repeated release.
         L     1,PTR2
         L     15,=A(DREL)
         BALR  14,15
         LTR   15,15
         BNZ   FAILED
         L     1,PTR2
         L     15,=A(DREL)
         BALR  14,15
         C     15,=F'8'
         BNE   FAILED
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
PTR1     DC    F'0'
PTR2     DC    F'0'
OLDSAVE  DS    18F
NEWSAVE  DS    18F
         END   IODRPRB
