***********************************************************************
* Q.0 TEST ONLY: POST-OPEN 1024-BYTE V/VB LOGICAL RECORDS.
* VERIFY FORMAT, LENGTH, BLOCKSIZE, RDW-ONLY AND BINARY FIDELITY.
* FULL RECORD COMPARED BYTE FOR BYTE AGAINST KNOWN BLANK PATTERN.
***********************************************************************
Q0CVR    CSECT
         STM   14,12,12(13)
         LR    12,15
         USING Q0CVR,12
         LA    11,SAVREG
         ST    13,4(11)
         ST    11,8(13)
         LR    13,11
         XC    RECCNT(4),RECCNT
         OPEN  (QDCB,(INPUT))
         OPEN  (ODCB,(OUTPUT))
* VALUES CINFMT/CINBLK ARE PROFILE-SPECIFIC FULLWORDS/CONSTANTS.
         CLI   QDCB+36,CINFMT
         BNE   FAILED
         CLC   QDCB+62(2),CINBLK
         BNE   FAILED
         CLC   QDCB+82(2),=H'1024'
         BNE   FAILED
* 1024 STAGING BYTES - 4 RDW BYTES = 1020 BCPL DATA BYTES.
         LH    5,QDCB+82
         SH    5,=H'4'
         CH    5,=H'1020'
         BNE   FAILED
RLOOP    GET   QDCB,AREA
         LH    2,AREA
         L     3,RECCNT
         C     3,=F'15'
         BNL   FAILED
         LR    4,3
         SLL   4,1
         LA    5,LENTAB
         CH    2,0(4,5)
         BNE   FAILED
         CLC   AREA+2(2),ZERO2
         BNE   FAILED
         CH    2,=H'4'
         BE    RFIN
         CH    2,=H'16'
         BE    RSMALL
         CH    2,=H'1024'
         BNE   FAILED
* A 1024-BYTE RECORD: ASSERT EVERY DATA BYTE.
         CLI   AREA+4,X'00'
         BNE   FAILED
         CLC   AREA+5(7),BLANKS
         BNE   FAILED
         SR    4,4
         IC    4,AREA+12
         CR    4,3
         BNE   FAILED
         CLC   AREA+13(242),BLANKS
         BNE   FAILED
         CLI   AREA+255,X'FF'
         BNE   FAILED
         CLC   AREA+256(255),BLANKS
         BNE   FAILED
         CLI   AREA+511,X'00'
         BNE   FAILED
         CLC   AREA+512(255),BLANKS
         BNE   FAILED
         CLI   AREA+767,X'FF'
         BNE   FAILED
         CLC   AREA+768(255),BLANKS
         BNE   FAILED
         CLI   AREA+1023,X'00'
         BNE   FAILED
         B     RFIN
RSMALL   CLC   AREA+4(8),=CL8'Q0VRTST!'
         BNE   FAILED
         SR    4,4
         IC    4,AREA+12
         CR    4,3
         BNE   FAILED
         CLC   AREA+13(3),BLANKS
         BNE   FAILED
RFIN     LA    3,1(3)
         ST    3,RECCNT
         B     RLOOP
ATEND    CLC   RECCNT(4),=F'15'
         BNE   FAILED
         PUT   ODCB,PASSREC
         CLOSE (QDCB)
         CLOSE (ODCB)
         L     13,4(13)
         LM    14,12,12(13)
         SR    15,15
         BR    14
FAILED   CLOSE (QDCB)
         CLOSE (ODCB)
         L     13,4(13)
         LM    14,12,12(13)
         LA    15,8
         BR    14
         DS    0F
RECCNT   DC    F'0'
ZERO2    DC    H'0'
LENTAB   DC    H'4',H'16',H'1024',H'4',H'16',H'1024'
         DC    H'4',H'16',H'1024',H'4',H'16',H'1024'
         DC    H'4',H'16',H'1024'
BLANKS   DC    CL256' '
AREA     DS    CL1024
PASSREC  DC    CL80'CINPASS'
SAVREG   DS    18F
QDCB     DCB   DDNAME=QDISK,DSORG=PS,MACRF=GM,EODAD=ATEND
ODCB     DCB   DDNAME=QOUT,DSORG=PS,MACRF=PM
         LTORG
         END   Q0CVR
