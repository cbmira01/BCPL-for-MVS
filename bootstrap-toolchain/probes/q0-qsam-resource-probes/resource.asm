***********************************************************************
* Q.0 TEST ONLY: CONDITIONAL GETMAIN/FREEMAIN AND FAILED OPEN SETUP.
* REAL 80/96-BYTE ALLOCATIONS; INJECT FAILURE BEFORE THIRD REQUEST.
* ROLLBACK MUST KEEP THE EARLIER ALLOCATION INTACT AND TRACK COUNTS.
* NO REAL STORAGE EXHAUSTION, NO QSAM GET/PUT, NO BCPL HANDLES.
***********************************************************************
Q0RES    CSECT
         STM   14,12,12(13)
         LR    12,15
         USING Q0RES,12
         LA    11,SAVREG
         ST    13,4(11)
         ST    11,8(13)
         LR    13,11
         XC    APTR(4),APTR
         XC    BPTR(4),BPTR
         XC    CPTR(4),CPTR
         XC    LIVE(4),LIVE
         XC    NALLOC(4),NALLOC
         XC    NFREE(4),NFREE
* FIRST ALLOCATION STANDS FOR A LIVE, INDEPENDENT HANDLE'S STAGE.
         GETMAIN RC,LV=80
         LTR   15,15
         BNZ   FAILED
         ST    1,APTR
         MVI   0(1),X'5A'
         MVI   79(1),X'A5'
         BAL   7,ACQUIRE
* SECOND ALLOCATION BELONGS TO AN UNPUBLISHED HANDLE UNDER SETUP.
         GETMAIN RC,LV=96
         LTR   15,15
         BNZ   FAILED
         ST    1,BPTR
         MVI   0(1),X'CC'
         MVI   95(1),X'DD'
         BAL   7,ACQUIRE
         CLC   LIVE(4),=F'2'
         BNE   FAILED
* INJECT FAILURE BEFORE NEXT GETMAIN; NOT A REAL MVS SHORTAGE.
         LA    15,8
         LTR   15,15
         BZ    FAILED
* ONLY RELEASE THE UNPUBLISHED HANDLE'S 96-BYTE OWNERSHIP.
         L     1,BPTR
         FREEMAIN R,LV=96,A=(1)
         XC    BPTR(4),BPTR
         BAL   7,RELEASE
* SURVIVING ALLOCATION AND COUNT MUST BE UNCHANGED.
         CLC   LIVE(4),=F'1'
         BNE   FAILED
         L     1,APTR
         CLI   0(1),X'5A'
         BNE   FAILED
         CLI   79(1),X'A5'
         BNE   FAILED
* ALLOCATE/FREE ANOTHER STAGE TO CHECK THE NORMAL RECOVERY PATH.
         GETMAIN RC,LV=80
         LTR   15,15
         BNZ   FAILED
         ST    1,CPTR
         MVI   0(1),X'33'
         MVI   79(1),X'44'
         BAL   7,ACQUIRE
         L     1,APTR
         CLI   0(1),X'5A'
         BNE   FAILED
         CLI   79(1),X'A5'
         BNE   FAILED
         L     1,CPTR
         CLI   0(1),X'33'
         BNE   FAILED
         CLI   79(1),X'44'
         BNE   FAILED
         FREEMAIN R,LV=80,A=(1)
         XC    CPTR(4),CPTR
         BAL   7,RELEASE
         L     1,APTR
         FREEMAIN R,LV=80,A=(1)
         XC    APTR(4),APTR
         BAL   7,RELEASE
         CLC   LIVE(4),=F'0'
         BNE   FAILED
         CLC   NALLOC(4),=F'3'
         BNE   FAILED
         CLC   NFREE(4),=F'3'
         BNE   FAILED
         OPEN  (ODCB,(OUTPUT))
         PUT   ODCB,PASSREC
         CLOSE (ODCB)
         L     13,4(13)
         LM    14,12,12(13)
         SR    15,15
         BR    14
* FAILURE CLEANUP IS OWNERSHIP-GUARDED, IN REVERSE ACQUIRE ORDER.
FAILED   L     1,CPTR
         LTR   1,1
         BZ    CLEANB
         FREEMAIN R,LV=80,A=(1)
         XC    CPTR(4),CPTR
         BAL   7,RELEASE
CLEANB   L     1,BPTR
         LTR   1,1
         BZ    CLEANA
         FREEMAIN R,LV=96,A=(1)
         XC    BPTR(4),BPTR
         BAL   7,RELEASE
CLEANA   L     1,APTR
         LTR   1,1
         BZ    BADRET
         FREEMAIN R,LV=80,A=(1)
         XC    APTR(4),APTR
         BAL   7,RELEASE
BADRET   L     13,4(13)
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
LIVE     DC    F'0'
NALLOC   DC    F'0'
NFREE    DC    F'0'
PASSREC  DC    CL80'Q0 GETMAIN RC ROLLBACK 3 ALLOC 3 FREE PASS'
SAVREG   DS    18F
ODCB     DCB   DDNAME=QOUT,DSORG=PS,MACRF=PM
         LTORG
         END   Q0RES
