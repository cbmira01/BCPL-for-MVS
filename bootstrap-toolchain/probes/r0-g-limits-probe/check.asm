***********************************************************************
* R.0 G NUMERIC ENVELOPE, TEST-ONLY IFOX EXECUTABLE, NO BCPLMAIN.
* ALL SCENARIO RECORDS LINKED FROM INDEPENDENT CSECT R0GDAT.
* VALIDATES COUNTS BEFORE SHIFT/ADDITION; DOES NOT PUBLISH GLOBALS.
***********************************************************************
R0GCHK   CSECT
         ENTRY R0GCHK
         EXTRN R0GDATA
         STM   14,12,12(13)
         LR    12,15
         USING R0GCHK,12
         LA    11,SAVREG
         ST    13,4(11)
         ST    11,8(13)
         LR    13,11
         XC    FLAG(4),FLAG
         OPEN  (ODCB,(OUTPUT))
         L     10,=A(R0GDATA)
         L     5,0(10)
         LA    10,4(10)
R0LOOP   L     6,0(10)
         L     7,4(10)
         L     8,8(10)
         L     9,12(10)
         C     6,=F'1'
         BE    R0REG
         C     6,=F'2'
         BE    R0PKG
         LA    15,1002
         B     R0TEST
R0REG    LTR   7,7
         BM    R0BADR
         LTR   8,8
         BM    R0BADR
         C     7,=F'32'
         BH    R0BADR
         C     8,=F'32'
         BH    R0BADR
         SLL   7,3
         SLL   8,3
         AR    7,8
         A     7,=F'28'
         C     7,=F'540'
         BH    R0BADR
         B     R0GOOD
R0PKG    LTR   7,7
         BNP   R0BADP
         LTR   8,8
         BM    R0BADP
         C     7,=F'8'
         BH    R0BADP
         C     8,=F'16'
         BH    R0BADP
         SLL   7,3
         SLL   8,4
         AR    7,8
         A     7,=F'48'
         C     7,=F'368'
         BH    R0BADP
R0GOOD   SR    15,15
         B     R0TEST
R0BADR   LA    15,1003
         B     R0TEST
R0BADP   LA    15,1006
R0TEST   CR    15,9
         BNE   R0FAIL
         MVC   OUTBUF(80),16(10)
         B     R0PRINT
R0FAIL   LA    0,8
         ST    0,FLAG
         MVC   OUTBUF(80),=CL80'R0 G BOUNDARY CASE FAILED'
R0PRINT  PUT   ODCB,OUTBUF
         LA    10,96(10)
         BCT   5,R0LOOP
         CLOSE (ODCB)
         L     15,FLAG
         L     13,4(13)
         LM    14,14,12(13)
         LM    0,12,20(13)
         BR    14
         DS    0F
FLAG     DC    F'0'
OUTBUF   DS    CL80
SAVREG   DS    18F
ODCB     DCB   DDNAME=QOUT,DSORG=PS,MACRF=PM
         LTORG
         END   R0GCHK
