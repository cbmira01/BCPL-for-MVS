***********************************************************************
* BCBYTEST -- INDEPENDENT CALLER FOR BCPLBYTE CROSS-OBJECT PROBE
* GO RC=0: GETBYTE READ, PUTBYTE WRITE, GETBYTE READ SUCCEEDED.
* GO RC=8: BYTE-SERVICE RESULT MISMATCH.
***********************************************************************
BCBYTEST CSECT
         EXTRN GETBYTE,PUTBYTE
         USING BCBYTEST,12
         STM   14,12,12(13)
         LR    12,15
         LA    4,SAVE
         ST    13,4(4)
         ST    4,8(13)
         LR    13,4
         LA    5,FRAME
*
* GETBYTE(DATA,1) SHOULD RETURN EBCDIC 'B' = X'C2'.
         LA    7,DATA
         SRL   7,2
         LA    8,1
         L     15,=A(GETBYTE)
         BALR  6,15
         C     7,=F'194'
         BNE   BAD
*
* PUTBYTE(DATA,1,'Z') WITH EBCDIC 'Z' = X'E9'.
         LA    7,DATA
         SRL   7,2
         LA    8,1
         LA    9,233
         L     15,=A(PUTBYTE)
         BALR  6,15
         CLI   DATA+1,C'Z'
         BNE   BAD
*
* VERIFY GETBYTE SEES THE NEW VALUE.
         LA    7,DATA
         SRL   7,2
         LA    8,1
         L     15,=A(GETBYTE)
         BALR  6,15
         C     7,=F'233'
         BNE   BAD
         SR    15,15
         B     EXIT
BAD      LA    15,8
EXIT     L     13,4(13)
         LM    14,12,12(13)
         BR    14
         LTORG
         DS    0F
DATA     DC    CL4'ABCD'
FRAME    DS    4F
SAVE     DS    18F
         END   BCBYTEST
