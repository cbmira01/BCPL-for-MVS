***********************************************************************
* R.0 TEST ONLY: FINALIZER REVERSE ORDER AND RC POLICY SIMULATION.
* THIS IS NOT BCPLMAIN'S REAL FINISH/STOP FLOW.
***********************************************************************
R0FCHK   CSECT
         ENTRY R0FCHK
         EXTRN R0FA,R0FB
         STM   14,12,12(13)
         LR    12,15
         USING R0FCHK,12
         LA    11,SAVREG
         ST    13,4(11)
         ST    11,8(13)
         LR    13,11
         XC    FLAG(4),FLAG
         OPEN  (ODCB,(OUTPUT))
         LA    10,TESTS
         L     5,0(10)
         LA    10,4(10)
CASELOOP ST    10,CURSC
         ST    5,LEFT
         XC    TRACE(8),TRACE
         XC    ERRFLAG(4),ERRFLAG
         MVC   PBMODE(4),0(10)
         MVC   PBSTOP(4),4(10)
         MVC   PBMASK(4),8(10)
         L     3,PBMODE
         C     3,=F'2'
         BE    NOHOOKS
* CALL DEPENDENT HOOK B FIRST, THEN DEPENDENCY A.
         LA    1,PBMODE
         L     15,=A(R0FB)
         BALR  14,15
         LTR   15,15
         BZ    CALLA
         LA    3,8
         ST    3,ERRFLAG
CALLA    LA    1,PBMODE
         L     15,=A(R0FA)
         BALR  14,15
         LTR   15,15
         BZ    VERIFY
         LA    3,8
         ST    3,ERRFLAG
VERIFY   CLC   TRACE(4),=F'2'
         BNE   FAILED
         CLC   TRACE+4(2),=CL2'BA'
         BNE   FAILED
         B     GETRC
NOHOOKS  CLC   TRACE(4),=F'0'
         BNE   FAILED
GETRC    L     3,PBMODE
         C     3,=F'1'
         BE    STOPRC
         L     15,ERRFLAG
         B     CHECKRC
STOPRC   L     15,PBSTOP
CHECKRC  L     10,CURSC
         C     15,12(10)
         BNE   FAILED
         MVC   OUTBUF(80),16(10)
         B     PRINT
FAILED   LA    3,8
         ST    3,FLAG
         MVC   OUTBUF(80),=CL80'R0 FINALIZER BATCH CASE FAILED'
PRINT    PUT   ODCB,OUTBUF
         L     10,CURSC
         LA    10,96(10)
         L     5,LEFT
         BCT   5,CASELOOP
         CLOSE (ODCB)
         L     15,FLAG
         L     13,4(13)
         LM    14,14,12(13)
         LM    0,12,20(13)
         BR    14
         DS    0F
CURSC    DC    F'0'
LEFT     DC    F'0'
FLAG     DC    F'0'
ERRFLAG  DC    F'0'
PBMODE   DC    F'0'
PBSTOP   DC    F'0'
PBTRACE  DC    A(TRACE)
PBMASK   DC    F'0'
TRACE    DC    F'0'
         DC    CL4'    '
OUTBUF   DS    CL80
SAVREG   DS    18F
ODCB     DCB   DDNAME=QOUT,DSORG=PS,MACRF=PM
         DS    0F
TESTS    DC    F'6'
         DC    F'2',F'0',F'0',F'0'
         DC    CL80'R0 F01 EMPTY FINISH RC0 PASS'
         DC    F'0',F'0',F'0',F'0'
         DC    CL80'R0 F02 REVERSE BA ONCE PASS'
         DC    F'0',F'0',F'1',F'8'
         DC    CL80'R0 F03 FINISH ERROR RC8 PASS'
         DC    F'1',F'4',F'1',F'4'
         DC    CL80'R0 F04 STOP4 PRESERVED PASS'
         DC    F'1',F'8',F'2',F'8'
         DC    CL80'R0 F05 STOP8 PRESERVED PASS'
         DC    F'1',F'0',F'3',F'0'
         DC    CL80'R0 F06 STOP0 PRESERVED PASS'
         LTORG
         END   R0FCHK
