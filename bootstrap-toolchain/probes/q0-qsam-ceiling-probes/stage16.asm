***********************************************************************
* Q.0 TEST ONLY: 16 SIMULTANEOUS PRIVATE 1024-BYTE GETMAIN REGIONS.
* NO DCB/OPEN; NOT 16 SIMULTANEOUS QSAM HANDLES OR BUDGET PROOF.
* CHECK PER-REGION FIRST/LAST SENTINELS; RELEASE EXACTLY ONCE.
***********************************************************************
Q0S16    CSECT
         STM   14,12,12(13)
         LR    12,15
         USING Q0S16,12
         LA    11,SAVREG
         ST    13,4(11)
         ST    11,8(13)
         LR    13,11
         XC    AREAS(64),AREAS
         XC    NALLOC(4),NALLOC
         XC    NFREE(4),NFREE
         SR    5,5
         LA    6,AREAS
ALLOC    GETMAIN RC,LV=1024
         LTR   15,15
         BNZ   FAILED
         ST    1,0(6)
         STC   5,0(1)
         LR    3,5
         X     3,=F'255'
         STC   3,1023(1)
         L     3,NALLOC
         LA    3,1(3)
         ST    3,NALLOC
         LA    5,1(5)
         LA    6,4(6)
         C     5,=F'16'
         BL    ALLOC
* ALL 16 REGIONS MUST REMAIN DISTINCT AND RETAIN SENTINELS.
         SR    5,5
         LA    6,AREAS
VERIFY   L     1,0(6)
         LTR   1,1
         BZ    FAILED
         SR    2,2
         IC    2,0(1)
         CR    2,5
         BNE   FAILED
         SR    2,2
         IC    2,1023(1)
         LR    3,5
         X     3,=F'255'
         CR    2,3
         BNE   FAILED
         LA    5,1(5)
         LA    6,4(6)
         C     5,=F'16'
         BL    VERIFY
* RELEASE EVERYTHING AND SHOW EXACTLY 16 SUCCESSFUL FREES.
         BAL   7,DRAIN
         CLC   NALLOC(4),=F'16'
         BNE   FAILED
         CLC   NFREE(4),=F'16'
         BNE   FAILED
         OPEN  (ODCB,(OUTPUT))
         PUT   ODCB,PASSREC
         CLOSE (ODCB)
         L     13,4(13)
         LM    14,12,12(13)
         SR    15,15
         BR    14
FAILED   BAL   7,DRAIN
         L     13,4(13)
         LM    14,12,12(13)
         LA    15,8
         BR    14
DRAIN    SR    5,5
         LA    6,AREAS
FREELOOP L     1,0(6)
         LTR   1,1
         BZ    FREENEXT
         FREEMAIN R,LV=1024,A=(1)
         SR    3,3
         ST    3,0(6)
         L     3,NFREE
         LA    3,1(3)
         ST    3,NFREE
FREENEXT LA    5,1(5)
         LA    6,4(6)
         C     5,=F'16'
         BL    FREELOOP
         BR    7
         DS    0F
AREAS    DS    16F
NALLOC   DC    F'0'
NFREE    DC    F'0'
PASSREC  DC    CL80'Q0 16 STAGES 1024 GETMAIN FREEMAIN PASS'
SAVREG   DS    18F
ODCB     DCB   DDNAME=QOUT,DSORG=PS,MACRF=PM
         LTORG
         END   Q0S16
