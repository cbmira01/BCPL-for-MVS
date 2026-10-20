***********************************************************************
* Q.0 TEST ONLY: PRIVATE FB80 RECORD STAGING AND CAPACITY RETRIES.
* SIMULATED APPLICATION READS: -1 WITH REQUIRED=80, 0 WITH 80,
* THEN EOF=1. GET ATTEMPTS COUNTED BEFORE INVOCATION, INCLUDING EODAD.
* NO BCPL DISPATCHER OR PUBLIC HANDLES ARE INVOLVED.
***********************************************************************
Q0PRR    CSECT
         STM   14,12,12(13)
         LR    12,15
         USING Q0PRR,12
         LA    11,SAVREG
         ST    13,4(11)
         ST    11,8(13)
         LR    13,11
         XC    GETCNT(4),GETCNT
         MVI   STATE,X'00'
         OPEN  (QDCB,(INPUT))
         OPEN  (ODCB,(OUTPUT))
* FIRST RECORD: CAPACITY 7, THEN 79, THEN 80.
         MVC   DEST(80),SENTINEL
         LA    2,7
         ST    2,CAPACITY
         BAL   7,READONE
         C     15,=F'-1'
         BNE   FAILED
         C     1,=F'80'
         BNE   FAILED
         CLC   DEST(80),SENTINEL
         BNE   FAILED
         CLC   GETCNT(4),=F'1'
         BNE   FAILED
         CLI   STATE,X'01'
         BNE   FAILED
         LA    2,79
         ST    2,CAPACITY
         BAL   7,READONE
         C     15,=F'-1'
         BNE   FAILED
         C     1,=F'80'
         BNE   FAILED
         CLC   DEST(80),SENTINEL
         BNE   FAILED
         CLC   GETCNT(4),=F'1'
         BNE   FAILED
         LA    2,80
         ST    2,CAPACITY
         BAL   7,READONE
         LTR   15,15
         BNZ   FAILED
         C     1,=F'80'
         BNE   FAILED
         CLI   STATE,X'00'
         BNE   FAILED
         CLC   GETCNT(4),=F'1'
         BNE   FAILED
         CLC   DEST(8),=CL8'Q0PND001'
         BNE   FAILED
         CLI   DEST+8,X'00'
         BNE   FAILED
         CLI   DEST+9,X'FF'
         BNE   FAILED
         CLC   DEST+10(69),SPACES
         BNE   FAILED
         CLI   DEST+79,X'5A'
         BNE   FAILED
* SECOND RECORD: CAPACITY 0, THEN 80. MUST NOT SKIP RECORD TWO.
         MVC   DEST(80),SENTINEL
         SR    2,2
         ST    2,CAPACITY
         BAL   7,READONE
         C     15,=F'-1'
         BNE   FAILED
         C     1,=F'80'
         BNE   FAILED
         CLC   DEST(80),SENTINEL
         BNE   FAILED
         CLC   GETCNT(4),=F'2'
         BNE   FAILED
         LA    2,80
         ST    2,CAPACITY
         BAL   7,READONE
         LTR   15,15
         BNZ   FAILED
         C     1,=F'80'
         BNE   FAILED
         CLC   GETCNT(4),=F'2'
         BNE   FAILED
         CLI   STATE,X'00'
         BNE   FAILED
         CLC   DEST(8),=CL8'Q0PND002'
         BNE   FAILED
         CLI   DEST+8,X'FF'
         BNE   FAILED
         CLI   DEST+9,X'00'
         BNE   FAILED
         CLC   DEST+10(69),SPACES
         BNE   FAILED
         CLI   DEST+79,X'A5'
         BNE   FAILED
* AFTER TWO RECORDS, THIRD GET TRIGGERS EODAD.
         MVC   DEST(80),SENTINEL
         BAL   7,READONE
         C     15,=F'1'
         BNE   FAILED
         LTR   1,1
         BNZ   FAILED
         CLC   GETCNT(4),=F'3'
         BNE   FAILED
         CLI   STATE,X'02'
         BNE   FAILED
         CLC   DEST(80),SENTINEL
         BNE   FAILED
* PERSISTENT EOF: NEXT APPLICATION READ MUST NOT REISSUE GET.
         BAL   7,READONE
         C     15,=F'1'
         BNE   FAILED
         LTR   1,1
         BNZ   FAILED
         CLC   GETCNT(4),=F'3'
         BNE   FAILED
         CLC   DEST(80),SENTINEL
         BNE   FAILED
         PUT   ODCB,PASSREC
         CLOSE (QDCB)
         CLOSE (ODCB)
         L     13,4(13)
         LM    14,12,12(13)
         SR    15,15
         BR    14
* READONE EMULATES PER-HANDLE QSAM READY/PENDING/EOF STATE.
* R2 HOLDS NO PERSISTENT CALLER DATA. CAPACITY IS A PRIVATE WORD.
READONE  ST    7,RETADDR
         CLI   STATE,X'02'
         BE    EOFRET
         CLI   STATE,X'01'
         BE    CHECKCAP
         L     3,GETCNT
         LA    3,1(3)
         ST    3,GETCNT
         GET   QDCB,STAGE
         MVI   STATE,X'01'
CHECKCAP L     3,CAPACITY
         C     3,=F'80'
         BL    TOOSMALL
         MVC   DEST(80),STAGE
         MVI   STATE,X'00'
         SR    15,15
         LA    1,80
         B     RETURN
TOOSMALL L     15,=F'-1'
         LA    1,80
         B     RETURN
ATEND    MVI   STATE,X'02'
EOFRET   LA    15,1
         SR    1,1
RETURN   L     7,RETADDR
         BR    7
FAILED   CLOSE (QDCB)
         CLOSE (ODCB)
         L     13,4(13)
         LM    14,12,12(13)
         LA    15,8
         BR    14
         DS    0F
GETCNT   DC    F'0'
CAPACITY DC    F'0'
RETADDR  DS    F
STATE    DC    X'00'
SPACES   DC    CL69' '
SENTINEL DC    80X'5A'
STAGE    DS    CL80
DEST     DS    CL80
PASSREC  DC    CL80'Q0 FB80 PENDING RETRIES 2 RECORDS PASS'
SAVREG   DS    18F
QDCB     DCB   DDNAME=QDISK,DSORG=PS,MACRF=GM,EODAD=ATEND
ODCB     DCB   DDNAME=QOUT,DSORG=PS,MACRF=PM
         LTORG
         END   Q0PRR
