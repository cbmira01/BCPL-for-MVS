***********************************************************************
* R.0 DECISION A: TEST-ONLY LINKED EXTENT/POLICY VALIDATOR.
* CHECK ALL BOUNDS BEFORE DEREFERENCE. NO GLOBALS ARE PUBLISHED.
* VALUES ARE APPROVED DECISION G IDS, NOT JES RETURN CODES.
***********************************************************************
R0ATST   CSECT
         ENTRY R0ATST
         EXTRN R0RB,R0RE,R0PB,R0PE,R0FUNC,R0FIN
         STM   14,12,12(13)
         LR    12,15
         USING R0ATST,12
         LA    11,SAVREG
         ST    13,4(11)
         ST    11,8(13)
         LR    13,11
         SR    6,6
* INDEPENDENT LINKER RELOCATED REGISTRY BOUNDS.
         L     8,=A(R0RB)
         L     9,=A(R0RE)
         LR    0,8
         N     0,=F'3'
         BNZ   REGEXT
         LR    0,9
         N     0,=F'3'
         BNZ   REGEXT
         CR    9,8
         BNH   REGEXT
         LR    7,9
         SR    7,8
         C     7,=F'28'
         BL    REGEXT
         C     7,=F'540'
         BH    REGEXT
* FIXED HEADER ONLY AFTER INDEPENDENT REGISTRY EXTENT CHECK.
         CLC   0(4,8),=CL4'BCRG'
         BNE   REGHDR
         CLC   4(4,8),=F'1'
         BNE   REGHDR
         CLC   8(4,8),=F'28'
         BNE   REGHDR
         CLC   24(4,8),=F'0'
         BNE   REGHDR
         CLC   16(4,8),=F'1'
         BNE   REGSIZ
         CLC   20(4,8),=F'1'
         BNE   REGSIZ
         C     7,=F'44'
         BNE   REGSIZ
         C     7,12(8)
         BNE   REGSIZ
* COMPARE POINTERS AGAINST INDEPENDENT LINKER SYMBOLS FIRST.
         L     1,28(8)
         L     2,32(8)
         C     1,=A(R0PB)
         BNE   PKGEXT
         C     2,=A(R0PE)
         BNE   PKGEXT
         LR    0,1
         N     0,=F'3'
         BNZ   PKGEXT
         LR    0,2
         N     0,=F'3'
         BNZ   PKGEXT
         CR    2,1
         BNH   PKGEXT
         LR    7,2
         SR    7,1
         C     7,=F'56'
         BL    PKGEXT
         C     7,=F'368'
         BH    PKGEXT
* FIXED PACKAGE HEADER ONLY AFTER INDEPENDENT EXTENT CHECK.
         CLC   0(4,1),=CL4'BCEX'
         BNE   PKGHDR
         CLC   4(4,1),=F'1'
         BNE   PKGHDR
         CLC   8(4,1),=F'48'
         BNE   PKGHDR
         CLC   44(4,1),=F'0'
         BNE   PKGHDR
         CLC   32(4,1),=F'1'
         BNE   PKGSIZ
         CLC   40(4,1),=F'0'
         BNE   PKGSIZ
         C     7,=F'56'
         BNE   PKGSIZ
         C     7,12(1)
         BNE   PKGSIZ
* VERIFY ID AND EXPORTED CALLABLE RELATION WITHOUT CALLING IT.
         CLC   36(8,8),16(1)
         BNE   IDENT
         CLC   16(8,1),=CL8'PACKA   '
         BNE   IDENT
         CLC   24(4,1),=F'1'
         BNE   IDENT
         CLC   48(4,1),=F'299'
         BNE   IDENT
         L     2,=A(R0FUNC)
         C     2,52(1)
         BNE   IDENT
* ONLY ZERO OR SEPARATELY EXPORTED R0FIN IS A TRUSTED HOOK.
         L     2,36(1)
         LTR   2,2
         BZ    RESULT
         C     2,=A(R0FIN)
         BNE   HOOKBAD
         B     RESULT
REGEXT   LA    6,1001
         B     RESULT
REGHDR   LA    6,1002
         B     RESULT
REGSIZ   LA    6,1003
         B     RESULT
PKGEXT   LA    6,1004
         B     RESULT
PKGHDR   LA    6,1005
         B     RESULT
PKGSIZ   LA    6,1006
         B     RESULT
IDENT    LA    6,1008
         B     RESULT
HOOKBAD  LA    6,1013
RESULT   C     6,EXPECT
         BNE   FAILED
         OPEN  (ODCB,(OUTPUT))
         PUT   ODCB,PASSREC
         CLOSE (ODCB)
         L     13,4(13)
         LM    14,12,12(13)
         SR    15,15
         BR    14
FAILED   L     13,4(13)
         LM    14,12,12(13)
         LA    15,8
         BR    14
         DS    0F
EXPECT   DC    F'EXPCODE'
PASSREC  DC    CL80'PASSMARKER'
SAVREG   DS    18F
ODCB     DCB   DDNAME=QOUT,DSORG=PS,MACRF=PM
         LTORG
         END   R0ATST
