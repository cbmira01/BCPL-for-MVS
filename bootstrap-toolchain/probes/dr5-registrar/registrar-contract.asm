* DR.5 REGISTRAR CONTRACT: PRIVATE TABLES, NO PRODUCTION G SLOTS.
* EACH CHECK ASSERTS EXACT RETURN, REGCOUNT AND PUBLICATION STATE.
RGTEST   CSECT
         ENTRY RGTEST,BCRGBEG,BCRGEND
         EXTRN RGINIT,RGFINI,REGCOUNT
         STM   14,12,12(13)
         LR    12,15
         USING RGTEST,12
         LA    2,SAVE
         ST    13,4(2)
         ST    2,8(13)
         LR    13,2
* 1: TWO DISTINCT DEPENDENCIES; ALL THREE EXPORTS PUBLISHED.
         LA    6,1
         SR    7,7
         BAL   8,CHECK
* FINALIZERS RUN C,B,A ONCE; A SECOND RGFINI MUST DO NOTHING.
         BAL   8,FINAL
* 2: DUPLICATE SECOND DEPENDENCY.
         MVC   DEP2(8),DEP1
         LA    6,2
         LA    7,1014
         BAL   8,CHECK
* 3: DISTINCT BUT MISSING SECOND DEPENDENCY.
         MVC   DEP2(8),=CL8'MISSING'
         LA    6,3
         LA    7,1010
         BAL   8,CHECK
         MVC   DEP2(8),=CL8'TESTB'
* 4: FORWARD DEPENDENCY (C BEFORE A AND B).
         MVC   PAIR(24),FORWARD
         LA    6,4
         LA    7,1012
         BAL   8,CHECK
* 5: LATER INVALID EXTENT BEFORE ANY DEPENDENCY LOOKUP.
* USE A REAL RELOCATED BEGIN AS BOTH ENDS, NOT A BAD POINTER.
         MVC   PAIR+12(4),PAIR+8
         LA    6,5
         LA    7,1004
         BAL   8,CHECK
* 6: STRUCTURAL CATEGORY PRECEDENCE OVER EARLIER BAD MAGIC.
         MVC   DESCC(4),=CL4'BAD!'
         LA    6,6
         LA    7,1004
         BAL   8,CHECK
         MVC   PAIR(24),NORMAL
* 7: FIXED HEADER FAILURE AFTER EXTENTS RESTORED.
         LA    6,7
         LA    7,1005
         BAL   8,CHECK
         MVC   DESCC(4),=CL4'BCEX'
* 8: HEADER CATEGORY PRECEDENCE OVER EARLIER BAD COUNT.
         MVC   DESCA+32(4),=F'9'
         MVC   DESCC(4),=CL4'BAD!'
         LA    6,8
         LA    7,1005
         BAL   8,CHECK
         MVC   DESCC(4),=CL4'BCEX'
* 9: BOUNDED COUNT FAILURE WITH VALID HEADERS.
         LA    6,9
         LA    7,1006
         BAL   8,CHECK
         MVC   DESCA+32(4),=F'1'
* 10: MALFORMED REQUIRED MAJOR ZERO.
         MVC   DEP2+8(4),=F'0'
         LA    6,10
         LA    7,1014
         BAL   8,CHECK
* 11: MALFORMED REQUIRED MAJOR NEGATIVE.
         MVC   DEP2+8(4),=F'-1'
         LA    6,11
         LA    7,1014
         BAL   8,CHECK
         MVC   DEP2+8(4),=F'1'
* 12: MALFORMED MINIMUM MINOR NEGATIVE.
         MVC   DEP2+12(4),=F'-1'
         LA    6,12
         LA    7,1014
         BAL   8,CHECK
* 13: WELL-FORMED INCOMPATIBLE MINOR.
         MVC   DEP2+12(4),=F'1'
         LA    6,13
         LA    7,1011
         BAL   8,CHECK
         MVC   DEP2+12(4),=F'0'
* 14: WELL-FORMED INCOMPATIBLE MAJOR.
         MVC   DEP2+8(4),=F'2'
         LA    6,14
         LA    7,1011
         BAL   8,CHECK
         MVC   DEP2+8(4),=F'1'
* 15: SELF DEPENDENCY.
         MVC   DEP2(8),=CL8'TESTC'
         LA    6,15
         LA    7,1014
         BAL   8,CHECK
* 16: BLANK DEPENDENCY.
         MVC   DEP2(8),=CL8' '
         LA    6,16
         LA    7,1014
         BAL   8,CHECK
         MVC   DEP2(8),=CL8'TESTB'
* 17: REAL EFFECTIVE OWNER COLLISION (LEDGER, NOT G SENTINEL).
         L     3,=A(OWNERS)
         MVI   11(3),X'01'
         LA    6,17
         LA    7,1009
         BAL   8,CHECK
         L     3,=A(OWNERS)
         MVI   11(3),X'00'
* 18: REPEAT VALID CASE AFTER REJECTIONS AND FINALIZE AGAIN.
         LA    6,18
         SR    7,7
         BAL   8,CHECK
         BAL   8,FINAL
         WTO   'DR5 REGISTRAR 18 CASES PASS'
         SR    15,15
         B     RETURN
* CHECK USES PRIVATE G VECTOR AND OWNER LEDGER; RGINIT PRESERVES
* R6 CASE, R7 EXPECTED STATUS AND R8 RETURN LINK.
CHECK    L     3,=A(GAREA)
         MVC   40(12,3),SENTINEL
         LA    1,PARMS
         L     15,=A(RGINIT)
         BALR  14,15
         CR    15,7
         BNE   FAIL
         L     2,=A(REGCOUNT)
         L     3,=A(GAREA)
         LTR   7,7
         BZ    CKGOOD
         CLC   0(4,2),=F'0'
         BNE   FAIL
         CLC   40(12,3),SENTINEL
         BNE   FAIL
         BR    8
CKGOOD   CLC   0(4,2),=F'3'
         BNE   FAIL
         CLC   40(12,3),EXPORTS
         BNE   FAIL
         BR    8
FINAL    MVC   FINLOG(3),=CL3' '
         LA    1,FINPARM
         L     15,=A(RGFINI)
         BALR  14,15
         LTR   15,15
         BNZ   FAIL
         CLC   FINLOG(3),=CL3'CBA'
         BNE   FAIL
         L     2,=A(REGCOUNT)
         CLC   0(4,2),=F'0'
         BNE   FAIL
         LA    1,FINPARM
         L     15,=A(RGFINI)
         BALR  14,15
         LTR   15,15
         BNZ   FAIL
         CLC   FINLOG(3),=CL3'CBA'
         BNE   FAIL
         BR    8
FAIL     WTO   'DR5 REGISTRAR ASSERTION FAILED'
* RC 9..26 IDENTIFIES THE FAILED CASE.
         LR    15,6
         A     15,=F'8'
RETURN   L     13,4(13)
         LM    14,14,12(13)
         LM    0,12,20(13)
         BR    14
         DROP  12
* FINALIZERS HAVE CONVENTIONAL MVS LINKAGE. R15 IS ENTRY BASE.
         DS    0H
FINA     EQU   *
         USING FINA,15
         L     1,=A(FINLOG)
         CLC   0(2,1),=CL2'CB'
         BNE   FINAERR
         MVI   2(1),C'A'
         SR    15,15
         BR    14
FINAERR  LA    15,8
         BR    14
         DROP  15
FINB     EQU   *
         USING FINB,15
         L     1,=A(FINLOG)
         CLI   0(1),C'C'
         BNE   FINBERR
         CLI   1(1),C' '
         BNE   FINBERR
         MVI   1(1),C'B'
         SR    15,15
         BR    14
FINBERR  LA    15,8
         BR    14
         DROP  15
FINC     EQU   *
         USING FINC,15
         L     1,=A(FINLOG)
         CLC   0(3,1),=CL3' '
         BNE   FINCERR
         MVI   0(1),C'C'
         SR    15,15
         BR    14
FINCERR  LA    15,8
         BR    14
         DROP  15
* DISTINCT RELOCATED EXPORT TARGETS, NEVER EXECUTED AS BCPL.
ENTRYA   BR    14
ENTRYB   BR    14
ENTRYC   BR    14
         LTORG
         DS    0F
SAVE     DS    18F
PARMS    DC    A(GAREA),A(OWNERS)
FINPARM  DC    F'0',F'0'
FINLOG   DC    CL3' '
         DS    0F
SENTINEL DC    X'C7D3F028',X'C7D3F02C',X'C7D3F030'
EXPORTS  DC    A(ENTRYA),A(ENTRYB),A(ENTRYC)
NORMAL   DC    A(DESCA),A(ENDA),A(DESCB),A(ENDB)
         DC    A(DESCC),A(ENDC)
FORWARD  DC    A(DESCC),A(ENDC),A(DESCA),A(ENDA)
         DC    A(DESCB),A(ENDB)
BCRGBEG  DS    0F
         DC    CL4'BCRG',F'1',F'28',F'52',F'3',F'0',F'0'
PAIR     DC    A(DESCA),A(ENDA),A(DESCB),A(ENDB)
         DC    A(DESCC),A(ENDC)
BCRGEND  EQU   *
DESCA    DC    CL4'BCEX',F'1',F'48',F'56',CL8'TESTA'
         DC    F'1',F'0',F'1',A(FINA),F'0',F'0'
         DC    F'10',A(ENTRYA)
ENDA     EQU   *
DESCB    DC    CL4'BCEX',F'1',F'48',F'56',CL8'TESTB'
         DC    F'1',F'0',F'1',A(FINB),F'0',F'0'
         DC    F'11',A(ENTRYB)
ENDB     EQU   *
DESCC    DC    CL4'BCEX',F'1',F'48',F'88',CL8'TESTC'
         DC    F'1',F'0',F'1',A(FINC),F'2',F'0'
         DC    F'12',A(ENTRYC)
DEP1     DC    CL8'TESTA',F'1',F'0'
DEP2     DC    CL8'TESTB',F'1',F'0'
ENDC     EQU   *
GAREA    DS    700F
OWNERS   DC    700X'00'
         END   RGTEST
