***********************************************************************
* Q.0 TEST ONLY: EXERCISE REAL FAILURE ROLLBACK BRANCH, NOT OOM.
* A SURVIVES; C THEN B ARE RELEASED; D IS ACQUIRED AFTER ROLLBACK.
* NO QSAM INPUT, NO BCPL HANDLES, NO REAL REGION EXHAUSTION.
***********************************************************************
Q0FAIL   CSECT
         STM   14,12,12(13)
         LR    12,15
         USING Q0FAIL,12
         LA    11,SAVREG
         ST    13,4(11)
         ST    11,8(13)
         LR    13,11
         XC    APTR(4),APTR
         XC    BPTR(4),BPTR
         XC    CPTR(4),CPTR
         XC    DPTR(4),DPTR
         XC    LIVE(4),LIVE
         XC    NALLOC(4),NALLOC
         XC    NFREE(4),NFREE
         XC    HITS(4),HITS
         MVI   ORDER,X'00'
         MVI   INJECT,X'00'
* A IS AN EXISTING HANDLE'S STAGE, OUTSIDE THIS FAILED SETUP.
         GETMAIN RC,LV=80
         LTR   15,15
         BNZ   FAILED
         ST    1,APTR
         MVI   0(1),X'5A'
         MVI   79(1),X'A5'
         BAL   7,ACQUIRE
* B/C ARE OWNED BY THE IN-PROGRESS, UNPUBLISHED HANDLE.
         GETMAIN RC,LV=96
         LTR   15,15
         BNZ   ROLLBACK
         ST    1,BPTR
         MVI   0(1),X'BC'
         MVI   95(1),X'CB'
         BAL   7,ACQUIRE
         GETMAIN RC,LV=64
         LTR   15,15
         BNZ   ROLLBACK
         ST    1,CPTR
         MVI   0(1),X'CD'
         MVI   63(1),X'DC'
         BAL   7,ACQUIRE
         CLC   LIVE(4),=F'3'
         BNE   FAILED
* INJECT A NONZERO STATUS INTO THE ACTUAL ROLLBACK BRANCH.
         MVI   INJECT,X'01'
         LA    15,8
         LTR   15,15
         BNZ   ROLLBACK
         B     FAILED
* SHARED FAILED-SETUP CLEANUP; C THEN B, NEVER A.
ROLLBACK L     3,HITS
         LA    3,1(3)
         ST    3,HITS
         L     1,CPTR
         LTR   1,1
         BZ    ROLLB
         FREEMAIN R,LV=64,A=(1)
         XC    CPTR(4),CPTR
         BAL   7,RELEASE
         MVI   ORDER,X'01'
ROLLB    L     1,BPTR
         LTR   1,1
         BZ    ROLLDONE
         FREEMAIN R,LV=96,A=(1)
         XC    BPTR(4),BPTR
         BAL   7,RELEASE
         CLI   ORDER,X'01'
         BNE   ROLLBORD
         MVI   ORDER,X'02'
         B     ROLLDONE
ROLLBORD MVI   ORDER,X'03'
ROLLDONE CLI   INJECT,X'01'
         BNE   FAILED
* INJECTED PATH MUST HAVE FREED BOTH CHILD ALLOCATIONS.
         CLC   HITS(4),=F'1'
         BNE   FAILED
         CLI   ORDER,X'02'
         BNE   FAILED
         CLC   BPTR(4),=F'0'
         BNE   FAILED
         CLC   CPTR(4),=F'0'
         BNE   FAILED
         CLC   LIVE(4),=F'1'
         BNE   FAILED
         CLC   NALLOC(4),=F'3'
         BNE   FAILED
         CLC   NFREE(4),=F'2'
         BNE   FAILED
         L     1,APTR
         CLI   0(1),X'5A'
         BNE   FAILED
         CLI   79(1),X'A5'
         BNE   FAILED
* NORMAL WORK CAN CONTINUE AFTER THE FAILED SETUP.
         GETMAIN RC,LV=80
         LTR   15,15
         BNZ   FAILED
         ST    1,DPTR
         MVI   0(1),X'33'
         MVI   79(1),X'44'
         BAL   7,ACQUIRE
         L     1,APTR
         CLI   0(1),X'5A'
         BNE   FAILED
         CLI   79(1),X'A5'
         BNE   FAILED
         L     1,DPTR
         CLI   0(1),X'33'
         BNE   FAILED
         CLI   79(1),X'44'
         BNE   FAILED
         FREEMAIN R,LV=80,A=(1)
         XC    DPTR(4),DPTR
         BAL   7,RELEASE
         L     1,APTR
         FREEMAIN R,LV=80,A=(1)
         XC    APTR(4),APTR
         BAL   7,RELEASE
         CLC   LIVE(4),=F'0'
         BNE   FAILED
         CLC   NALLOC(4),=F'4'
         BNE   FAILED
         CLC   NFREE(4),=F'4'
         BNE   FAILED
         OPEN  (ODCB,(OUTPUT))
         PUT   ODCB,PASSREC
         CLOSE (ODCB)
         L     13,4(13)
         LM    14,12,12(13)
         SR    15,15
         BR    14
* UNEXPECTED FAILURE: RELEASE EVERYTHING STILL OWNED; RETURN RC=8.
FAILED   L     1,DPTR
         LTR   1,1
         BZ    FC
         FREEMAIN R,LV=80,A=(1)
         XC    DPTR(4),DPTR
         BAL   7,RELEASE
FC       L     1,CPTR
         LTR   1,1
         BZ    FB
         FREEMAIN R,LV=64,A=(1)
         XC    CPTR(4),CPTR
         BAL   7,RELEASE
FB       L     1,BPTR
         LTR   1,1
         BZ    FA
         FREEMAIN R,LV=96,A=(1)
         XC    BPTR(4),BPTR
         BAL   7,RELEASE
FA       L     1,APTR
         LTR   1,1
         BZ    FRET
         FREEMAIN R,LV=80,A=(1)
         XC    APTR(4),APTR
         BAL   7,RELEASE
FRET     L     13,4(13)
         LM    14,12,12(13)
         LA    15,8
         BR    14
ACQUIRE  L     2,LIVE
         LA    2,1(2)
         ST    2,LIVE
         L     2,NALLOC
         LA    2,1(2)
         ST    2,NALLOC
         BR    7
RELEASE  L     2,LIVE
         BCTR  2,0
         ST    2,LIVE
         L     2,NFREE
         LA    2,1(2)
         ST    2,NFREE
         BR    7
         DS    0F
APTR     DC    F'0'
BPTR     DC    F'0'
CPTR     DC    F'0'
DPTR     DC    F'0'
LIVE     DC    F'0'
NALLOC   DC    F'0'
NFREE    DC    F'0'
HITS     DC    F'0'
ORDER    DC    X'00'
INJECT   DC    X'00'
PASSREC  DC    CL80'Q0 RESOURCE FAILED PATH 4 ALLOC 4 FREE PASS'
SAVREG   DS    18F
ODCB     DCB   DDNAME=QOUT,DSORG=PS,MACRF=PM
         LTORG
         END   Q0FAIL
