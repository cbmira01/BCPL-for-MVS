***********************************************************************
* Q.3 NATIVE IFOX: INDEPENDENT VERIFIER OF BCPLQSAM V OUTPUT.
* SIX RDW-INCLUSIVE LENGTHS 5,16,36,100,4,5; CHECK ALL DATA BYTES.
* QSAM HANDLES THE PHYSICAL BLOCK; READER CHECKS LOGICAL RDWS.
***********************************************************************
Q3VFY    CSECT
         STM   14,12,12(13)
         LR    12,15
         USING Q3VFY,12
         LA    11,SAVREG
         ST    13,4(11)
         ST    11,8(13)
         LR    13,11
         XC    RECCNT(4),RECCNT
         OPEN  (QDCB,(INPUT))
         OPEN  (ODCB,(OUTPUT))
         MVI   FAILID,C'F'
         CLI   QDCB+36,X'40'
         BNE   FAILED
         MVI   FAILID,C'B'
         CLC   QDCB+62(2),=H'104'
         BNE   FAILED
         MVI   FAILID,C'E'
         CLC   QDCB+82(2),=H'100'
         BNE   FAILED
RLOOP    GET   QDCB,AREA
         MVI   FAILID,C'C'
         L     3,RECCNT
         C     3,=F'6'
         BNL   FAILED
         LR    4,3
         SLL   4,1
         LA    5,LENTAB
         MVI   FAILID,C'L'
         LH    2,AREA
         CH    2,0(4,5)
         BNE   FAILED
         MVI   FAILID,C'R'
         CLC   AREA+2(2),ZERO2
         BNE   FAILED
         SH    2,=H'4'
         LTR   2,2
         BZ    RNEXT
         LA    5,AREA+4
         SR    4,4
RBYTE    MVI   FAILID,C'D'
         LA    6,64
         C     4,=F'0'
         BE    RIDENT
         C     4,=F'1'
         BE    RZERO
         C     4,=F'2'
         BE    RFF
         C     4,=F'11'
         BE    RA5
         C     4,=F'31'
         BE    R7E
         C     4,=F'95'
         BNE   RCOMPARE
         LA    6,195
         B     RCOMPARE
RIDENT   LR    6,3
         B     RCOMPARE
RZERO    SR    6,6
         B     RCOMPARE
RFF      LA    6,255
         B     RCOMPARE
RA5      LA    6,165
         B     RCOMPARE
R7E      LA    6,126
RCOMPARE SR    0,0
         IC    0,0(5)
         CR    0,6
         BNE   FAILED
         LA    5,1(5)
         LA    4,1(4)
         BCT   2,RBYTE
RNEXT    LA    3,1(3)
         ST    3,RECCNT
         B     RLOOP
ATEND    MVI   FAILID,C'Z'
         CLC   RECCNT(4),=F'6'
         BNE   FAILED
         PUT   ODCB,PASSREC
         CLOSE (QDCB)
         CLOSE (ODCB)
         L     13,4(13)
         LM    14,12,12(13)
         SR    15,15
         BR    14
FAILED   L     3,RECCNT
         LA    3,240(3)
         STC   3,FAILNO
         PUT   ODCB,FAILREC
         CLOSE (QDCB)
         CLOSE (ODCB)
         L     13,4(13)
         LM    14,12,12(13)
         LA    15,8
         BR    14
         DS    0F
RECCNT   DC    F'0'
ZERO2    DC    H'0'
LENTAB   DC    H'5',H'16',H'36',H'100',H'4',H'5'
AREA     DS    CL100
PASSREC  DC    CL80'BCPLQSAM Q3 V WRITE 6 RDW BINARY ZERO PASS'
FAILREC  DC    CL34'Q3 V WRITE VERIFY FAILURE CHECK'
FAILID   DC    C'?'
         DC    CL9' RECORD #'
FAILNO   DC    C'?'
         DC    CL35' '
SAVREG   DS    18F
QDCB     DCB   DDNAME=QVDATA,DSORG=PS,MACRF=GM,EODAD=ATEND
ODCB     DCB   DDNAME=QOUT,DSORG=PS,MACRF=PM
         LTORG
         END   Q3VFY
