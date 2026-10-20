***********************************************************************
* Q.0 ISOLATED REAL GETMAIN RC REFUSAL (NOT A STORAGE EXHAUSTION LOOP).
* GO REGION=256K; ONE CONDITIONAL 1-MEGABYTE REQUEST.
* A IS AN INDEPENDENT ALLOCATION; B IS NEW SETUP STORAGE.
* IF RETURN RC=4, RELEASE B, PRESERVE A, THEN ALLOCATE D.
* IF THE LARGE REQUEST SUCCEEDS, FREE IT AND RETURN RC=8.
* NO QSAM INPUT, NO PDS WRITES, NO BCPLQSAM IMPLEMENTATION.
***********************************************************************
Q0NOMEM  CSECT
         STM   14,12,12(13)
         LR    12,15
         USING Q0NOMEM,12
         LA    11,SAVREG
         ST    13,4(11)
         LR    13,11
         XC    APTR(4),APTR
         XC    BPTR(4),BPTR
         XC    DPTR(4),DPTR
         XC    LIVE(4),LIVE
         XC    ALLOCS(4),ALLOCS
         XC    FREES(4),FREES
         XC    BIGRC(4),BIGRC
* INDEPENDENT HANDLE'S 80-BYTE STAGE, MUST SURVIVE THE ERROR.
         GETMAIN RC,LV=80
         LTR   15,15
         BNZ   FAILED
         ST    1,APTR
         MVI   0(1),X'5A'
         MVI   79(1),X'A5'
         BAL   7,ACQUIRE
* A DIFFERENT, UNPUBLISHED HANDLE HAS OWNED 96 BYTES.
         GETMAIN RC,LV=96
         LTR   15,15
         BNZ   FAILED
         ST    1,BPTR
         MVI   0(1),X'BC'
         MVI   95(1),X'CB'
         BAL   7,ACQUIRE
* ONE OVERSIZED CONDITIONAL REQUEST: NO RETRIES, NO GROWTH LOOP.
         GETMAIN RC,LV=1048576
         LTR   15,15
         BZ    BIGOK
         ST    15,BIGRC
         C     15,=F'4'
         BNE   FAILED
* THE ACTUAL NONZERO GETMAIN RESULT REACHES THIS ROLLBACK.
ROLLBACK L     1,BPTR
         FREEMAIN R,LV=96,A=(1)
         XC    BPTR(4),BPTR
         BAL   7,RELEASE
         CLC   LIVE(4),=F'1'
         BNE   FAILED
         CLC   BIGRC(4),=F'4'
         BNE   FAILED
         L     1,APTR
         CLI   0(1),X'5A'
         BNE   FAILED
         CLI   79(1),X'A5'
         BNE   FAILED
* PROVE SUBSEQUENT SMALL GETMAIN WORKS AFTER LARGE REFUSAL.
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
         CLC   ALLOCS(4),=F'3'
         BNE   FAILED
         CLC   FREES(4),=F'3'
         BNE   FAILED
         OPEN  (ODCB,(OUTPUT))
         PUT   ODCB,PASSREC
         CLOSE (ODCB)
         L     13,4(13)
         LM    14,12,12(13)
         SR    15,15
         BR    14
* UNEXPECTED SUCCESS MUST RELEASE THE 1MB AREA IMMEDIATELY.
BIGOK    L     2,=F'1048576'
         FREEMAIN R,LV=(2),A=(1)
         B     FAILED
* UNEXPECTED RC / ERROR: CONSERVATIVE POINTER-GUARDED CLEANUP.
FAILED   L     1,DPTR
         LTR   1,1
         BZ    CLEANB
         FREEMAIN R,LV=80,A=(1)
         XC    DPTR(4),DPTR
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
ACQUIRE  L     3,LIVE
         LA    3,1(3)
         ST    3,LIVE
         L     3,ALLOCS
         LA    3,1(3)
         ST    3,ALLOCS
         BR    7
RELEASE  L     3,LIVE
         BCTR  3,0
         ST    3,LIVE
         L     3,FREES
         LA    3,1(3)
         ST    3,FREES
         BR    7
         DS    0F
APTR     DC    F'0'
BPTR     DC    F'0'
DPTR     DC    F'0'
LIVE     DC    F'0'
ALLOCS   DC    F'0'
FREES    DC    F'0'
BIGRC    DC    F'0'
PASSREC  DC    CL80'Q0 REAL GETMAIN RC4 ROLLBACK 3 ALLOC 3 FREE PASS'
SAVREG   DS    18F
ODCB     DCB   DDNAME=QOUT,DSORG=PS,MACRF=PM
         LTORG
         END   Q0NOMEM
