***********************************************************************
* CO1ROOT - candidate-only MVS IFOX/IEWL/GO context transfer smoke
* Sequence: A1, B1, A2, B2, PASS (each through real CO1SW).
* No BCPLMAIN, no global registration, no installed object changes.
***********************************************************************
CO1ROOT  CSECT
         EXTRN CO1SW
         STM   14,12,12(13)
         BALR  12,0
         USING *,12
         LA    11,SAVEAREA
         ST    13,4(11)
         ST    11,8(13)
         LR    13,11
         OPEN  (PRINT,(OUTPUT))
*
* Construct two isolated first-entry register images.
* R5 is private frame storage, R6 entry continuation, R12 base,
* R13 MVS save area and R15 a distinct private workspace.
*
         LA    3,AFRAME
         ST    3,ACTX+20
         LA    3,AONE
         ST    3,ACTX+24
         ST    11,ACTX+44
         ST    12,ACTX+48
         ST    13,ACTX+52
         LA    3,AWORK
         ST    3,ACTX+60
         LA    3,BFRAME
         ST    3,BCTX+20
         LA    3,BONE
         ST    3,BCTX+24
         ST    11,BCTX+44
         ST    12,BCTX+48
         ST    13,BCTX+52
         LA    3,BWORK
         ST    3,BCTX+60
*
* Root -> never-run A with result argument 7.
*
         LA    2,RCTX
         LA    1,ACTX
         LA    0,7
         L     4,=A(CO1SW)
         BALR  6,4
ROOTBACK C     7,=F'11'
         BNE   BAD
         PUT   PRINT,MSGOK
         B     DONE
*
* A, first entry -> B; A's stack/frame word survives suspension.
*
AONE     C     7,=F'7'
         BNE   BAD
         LA    3,AFRAME
         CR    5,3
         BNE   BAD
         LA    3,314
         ST    3,0(5)
         PUT   PRINT,MSGA1
         LA    2,ACTX
         LA    1,BCTX
         LA    0,8
         L     4,=A(CO1SW)
         BALR  6,4
ATWO     C     7,=F'9'
         BNE   BAD
         L     3,0(5)
         C     3,=F'314'
         BNE   BAD
         LA    3,AFRAME
         CR    5,3
         BNE   BAD
         PUT   PRINT,MSGA2
         LA    2,ACTX
         LA    1,BCTX
         LA    0,10
         L     4,=A(CO1SW)
         BALR  6,4
         B     BAD              NO THIRD ACTIVATION EXPECTED
*
* B, first entry -> saved A; then B resumes -> root.
*
BONE     C     7,=F'8'
         BNE   BAD
         LA    3,BFRAME
         CR    5,3
         BNE   BAD
         LA    3,2718
         ST    3,0(5)
         PUT   PRINT,MSGB1
         LA    2,BCTX
         LA    1,ACTX
         LA    0,9
         L     4,=A(CO1SW)
         BALR  6,4
BTWO     C     7,=F'10'
         BNE   BAD
         L     3,0(5)
         C     3,=F'2718'
         BNE   BAD
         LA    3,BFRAME
         CR    5,3
         BNE   BAD
         PUT   PRINT,MSGB2
         LA    2,BCTX
         LA    1,RCTX
         LA    0,11
         L     4,=A(CO1SW)
         BALR  6,4
         B     BAD              NO THIRD ACTIVATION EXPECTED
*
BAD      PUT   PRINT,MSGFAIL
         CLOSE (PRINT)
         L     13,4(13)
         LM    14,12,12(13)
         LA    15,12
         BR    14
DONE     CLOSE (PRINT)
         L     13,4(13)
         LM    14,12,12(13)
         SR    15,15
         BR    14
*
         DS    0F
SAVEAREA DS    18F
RCTX     DS    16F
ACTX     DS    16F
BCTX     DS    16F
AFRAME   DS    32F
BFRAME   DS    32F
AWORK    DS    32F
BWORK    DS    32F
MSGA1    DC    CL80'CO1STAGE A1'
MSGB1    DC    CL80'CO1STAGE B1'
MSGA2    DC    CL80'CO1STAGE A2'
MSGB2    DC    CL80'CO1STAGE B2'
MSGOK    DC    CL80'CO1STAGE PASS'
MSGFAIL  DC    CL80'CO1STAGE FAIL'
PRINT    DCB   DDNAME=SYSPRINT,DSORG=PS,MACRF=PM,RECFM=F,LRECL=80
         END   CO1ROOT
