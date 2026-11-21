***********************************************************************
* TA.2 RC2 - READ-ONLY HISTORICAL CAMBRIDGE SOURCE RECORD FIDELITY.
* QSAM GET ALL FB80 RECORDS; PRINT COUNT, TRAILING BLANKS, FNV1A, SUM.
* INPUT MEMBER NAME IS THE GO STEP PARM. NO PDS UPDATE OCCURS.
***********************************************************************
BCSRCV   CSECT
         STM   14,12,12(13)
         LR    12,15
         USING BCSRCV,12
         LA    11,SAVEAREA
         ST    13,4(11)
         ST    11,8(13)
         LR    13,11
*        PARM IS A TWO-BYTE LENGTH FOLLOWED BY MEMBER NAME.
         LTR   1,1
         BZ    FAILED
         L     2,0(1)
         N     2,=X'00FFFFFF'
         LTR   2,2
         BZ    FAILED
         LH    3,0(2)
         LTR   3,3
         BNP   FAILED
         C     3,=F'8'
         BH    FAILED
         BCTR  3,0
         EX    3,COPYNAME
         B     NAMEOK
COPYNAME MVC   OUTNAME(1),2(2)
NAMEOK   XC    RECCNT(4),RECCNT
         XC    TRAILCNT(4),TRAILCNT
         XC    SUMVAL(4),SUMVAL
         OPEN  (QDCB,(INPUT))
         OPEN  (ODCB,(OUTPUT))
READNEXT GET   QDCB,AREA
         L     3,RECCNT
         A     3,=F'1'
         ST    3,RECCNT
         CLC   AREA(80),BLANKS
         BNE   NOTBLANK
         L     3,TRAILCNT
         A     3,=F'1'
         ST    3,TRAILCNT
         B     HASHREC
NOTBLANK XC    TRAILCNT(4),TRAILCNT
HASHREC  LA    6,AREA
         LA    7,80
HASHBYTE SR    3,3
         IC    3,0(6)
         L     5,FNVHASH
         XR    5,3
         SR    4,4
         M     4,PRIME
         ST    5,FNVHASH
         L     4,SUMVAL
         AR    4,3
         ST    4,SUMVAL
         LA    6,1(6)
         BCT   7,HASHBYTE
         B     READNEXT
ATEOD    L     5,RECCNT
         LA    8,OUTCOUNT
         BAL   9,TOHEX
         L     5,TRAILCNT
         LA    8,OUTTRAIL
         BAL   9,TOHEX
         L     5,FNVHASH
         LA    8,OUTFNV
         BAL   9,TOHEX
         L     5,SUMVAL
         LA    8,OUTSUM
         BAL   9,TOHEX
         PUT   ODCB,OUTREC
         CLOSE (QDCB)
         CLOSE (ODCB)
         L     13,4(13)
         LM    14,12,12(13)
         SR    15,15
         BR    14
FAILED   L     13,4(13)
         LM    14,12,12(13)
         LA    15,8
         BR    14
*        CONVERT UNSIGNED 32-BIT REGISTER 5 INTO 8 EBCDIC HEX DIGITS.
TOHEX    LA    7,8
HEXLOOP  LR    4,5
         SRL   4,28
         LA    3,HEXTAB
         IC    4,0(4,3)
         STC   4,0(8)
         LA    8,1(8)
         SLL   5,4
         BCT   7,HEXLOOP
         BR    9
         DS    0F
RECCNT   DC    F'0'
TRAILCNT DC    F'0'
SUMVAL   DC    F'0'
FNVHASH  DC    X'811C9DC5'
PRIME    DC    F'16777619'
BLANKS   DC    CL80' '
HEXTAB   DC    CL16'0123456789ABCDEF'
AREA     DS    CL80
OUTREC   DC    CL13'BCSRC MEMBER='
OUTNAME  DC    CL8' '
         DC    CL7' COUNT='
OUTCOUNT DC    CL8'00000000'
         DC    CL7' TRAIL='
OUTTRAIL DC    CL8'00000000'
         DC    CL5' FNV='
OUTFNV   DC    CL8'00000000'
         DC    CL5' SUM='
OUTSUM   DC    CL8'00000000'
         DC    CL3' '
SAVEAREA DS    18F
QDCB     DCB   DDNAME=QIN,DSORG=PS,MACRF=GM,EODAD=ATEOD
ODCB     DCB   DDNAME=QOUT,DSORG=PS,MACRF=PM
         LTORG
         END   BCSRCV
