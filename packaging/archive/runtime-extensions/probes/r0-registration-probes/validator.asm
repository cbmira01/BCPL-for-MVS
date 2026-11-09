***********************************************************************
* R.0 TEST ONLY - LINK-RESOLVED BOUNDS AND SELECTED EXPORT PREFLIGHT.
* FOUR INDEPENDENT ASSEMBLIES; NO BCPLMAIN OR ACCEPTED PDS WRITES.
* FIXTURE SELECTS EXPECTED REJECTION; NO GLOBALS ARE PUBLISHED.
***********************************************************************
R0CHK    CSECT
         ENTRY R0CHK
         EXTRN R0RB,R0RE,R0PB,R0PE,R0FUNC
         STM   14,12,12(13)
         LR    12,15
         USING R0CHK,12
         LA    11,SAVREG
         ST    13,4(11)
         ST    11,8(13)
         LR    13,11
         SR    6,6
* FIRST CHECK THE INDEPENDENT LINKED BOUNDS AND ALIGNMENT.
         L     8,=A(R0RB)
         L     9,=A(R0RE)
         LR    0,8
         N     0,=F'3'
         BNZ   BADSPAN
         LR    0,9
         N     0,=F'3'
         BNZ   BADSPAN
         CR    9,8
         BNH   BADSPAN
         LR    7,9
         SR    7,8
         C     7,=F'28'
         BL    BADSPAN
         C     7,=F'256'
         BH    BADSPAN
* CAN READ FIXED HEADER ONLY AFTER INDEPENDENT SPAN CHECK.
         CLC   0(4,8),=CL4'BCRG'
         BNE   BADVERS
         CLC   4(4,8),=F'1'
         BNE   BADVERS
         CLC   8(4,8),=F'28'
         BNE   BADVERS
         CLC   24(4,8),=F'0'
         BNE   BADVERS
* FIXTURE V1 SUPPORTS EXACTLY ONE DESCRIPTOR, ONE REQUIREMENT.
         CLC   16(4,8),=F'1'
         BNE   BADSPAN
         CLC   20(4,8),=F'1'
         BNE   BADSPAN
         C     7,=F'44'
         BNE   BADSPAN
         C     7,12(8)
         BNE   BADSPAN
* VERIFY ENTRY PAIR RELOCATED TO SEPARATE DESCRIPTOR CSECT.
         L     1,28(8)
         L     2,32(8)
         C     1,=A(R0PB)
         BNE   BADSPAN
         C     2,=A(R0PE)
         BNE   BADSPAN
         LR    0,1
         N     0,=F'3'
         BNZ   BADSPAN
         LR    0,2
         N     0,=F'3'
         BNZ   BADSPAN
         CR    2,1
         BNH   BADSPAN
         LR    7,2
         SR    7,1
         C     7,=F'48'
         BL    BADSPAN
         C     7,=F'128'
         BH    BADSPAN
         C     7,12(1)
         BNE   BADSPAN
         CLC   0(4,1),=CL4'BCEX'
         BNE   BADVERS
         CLC   4(4,1),=F'1'
         BNE   BADVERS
         CLC   8(4,1),=F'48'
         BNE   BADVERS
         CLC   44(4,1),=F'0'
         BNE   BADVERS
* A SINGLE PACKAGE MUST SATISFY THE APPLICATION REQUIREMENT.
         CLC   36(8,8),16(1)
         BNE   BADREQ
         CLC   16(8,1),=CL8'PACKA   '
         BNE   BADVERS
         CLC   24(4,1),=F'1'
         BNE   BADVERS
* EXACT DESCRIPTOR SPAN = 48 + 8*EXPORTS + 16*DEPENDENCIES.
         L     4,32(1)
         LTR   4,4
         BNH   BADSPAN
         C     4,=F'2'
         BH    BADSPAN
         L     5,40(1)
         LTR   5,5
         BNZ   BADSPAN
         LR    0,4
         SLL   0,3
         A     0,=F'48'
         CR    0,7
         BNE   BADSPAN
* CHECK A RELOCATED CALLBACK ADDRESS WITHOUT INVOKING IT.
         L     2,=A(R0FUNC)
         C     2,36(1)
         BNE   BADSPAN
         C     2,52(1)
         BNE   BADSPAN
* TEST-LOCAL G!299; NATIVE G!14 IS NEVER A VALID EXPORT.
         L     3,48(1)
         C     3,=F'14'
         BE    BADCORE
         C     3,=F'299'
         BNE   BADSPAN
         C     4,=F'2'
         BNE   RESULT
* TWO EXPORTS OF THE SAME G!299 MUST BE REJECTED.
         C     3,56(1)
         BE    BADDUP
         B     BADSPAN
BADSPAN  LA    6,4
         B     RESULT
BADVERS  LA    6,8
         B     RESULT
BADDUP   LA    6,12
         B     RESULT
BADCORE  LA    6,16
         B     RESULT
BADREQ   LA    6,24
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
         END   R0CHK