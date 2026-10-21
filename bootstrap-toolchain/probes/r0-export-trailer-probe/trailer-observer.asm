***********************************************************************
* R.0 TEST ONLY: READ LINKED APPLICATION AND INSTALLED BLIB TRAILERS.
* R0APP AND BLIB ARE LINK-RESOLVED BUT ARE NEVER EXECUTED.
* REPORT THEIR RELOCATED EXPORT OFFSET/ADDRESS PAIRS VIA QOUT.
* NO BCPLMAIN CALL OR GLOBAL REGISTRATION; READ-ONLY OBSERVATION.
***********************************************************************
R0TRACE  CSECT
         ENTRY R0TRACE
         EXTRN R0APP,BLIB
         STM   14,12,12(13)
         LR    12,15
         USING R0TRACE,12
         LA    11,SAVEAREA
         ST    13,4(11)
         ST    11,8(13)
         LR    13,11
         OPEN  (OUTDCB,(OUTPUT))
         L     8,=A(R0APP)
         MVC   MODNAME(4),=CL4'APP '
         BAL   10,SCAN
         LTR   15,15
         BNZ   FAILURE
         L     8,=A(BLIB)
         MVC   MODNAME(4),=CL4'BLIB'
         BAL   10,SCAN
         LTR   15,15
         BNZ   FAILURE
         MVC   CARD(80),PASSREC
         PUT   OUTDCB,CARD
         CLOSE (OUTDCB)
         L     13,4(13)
         LM    14,12,12(13)
         SR    15,15
         BR    14
FAILURE  CLOSE (OUTDCB)
         L     13,4(13)
         LM    14,12,12(13)
         LA    15,8
         BR    14
*
* SCAN: R8 = TRUSTED LINKED BCPL MODULE ENTRY PREFIX.
* OBSERVATION IS BOUNDED TO THE RECONSTRUCTED CG370 <16K ENVELOPE.
* THIS DOES NOT CLAIM PROTECTION FROM ARBITRARY FORGED POINTERS.
*
SCAN     ST    10,CALLRET
         ST    8,MODBASE
         LH    2,10(8)
         LTR   2,2
         BNP   SCANBAD
         CH    2,=H'16384'
         BNL   SCANBAD
         LR    9,8
         AR    9,2
         ST    9,CURPTR
         XC    PAIRS(4),PAIRS
         MVC   CARD(80),BEGINREC
         MVC   CARD+5(4),MODNAME
         PUT   OUTDCB,CARD
SCANNEXT L     9,CURPTR
         AH    9,=H'-8'
         L     3,MODBASE
         LA    3,16(3)
         CR    9,3
         BL    SCANBAD
         ST    9,CURPTR
         L     4,4(9)
         LTR   4,4
         BZ    SENTINEL
         L     5,0(9)
         C     5,=F'4'
         BL    SCANBAD
         C     5,=F'2796'
         BH    SCANBAD
         LR    6,5
         N     6,=F'3'
         BNZ   SCANBAD
         MVC   CARD(80),PAIRREC
         MVC   CARD+5(4),MODNAME
         LA    3,CARD+14
         BAL   14,HEX8
         L     9,CURPTR
         L     5,4(9)
         LA    3,CARD+28
         BAL   14,HEX8
         PUT   OUTDCB,CARD
         L     7,PAIRS
         LA    7,1(7)
         ST    7,PAIRS
         C     7,=F'256'
         BNL   SCANBAD
         B     SCANNEXT
SENTINEL L     5,0(9)
         C     5,=F'4'
         BL    SCANBAD
         C     5,=F'2796'
         BH    SCANBAD
         LR    6,5
         N     6,=F'3'
         BNZ   SCANBAD
         MVC   CARD(80),LIMITREC
         MVC   CARD+5(4),MODNAME
         LA    3,CARD+16
         BAL   14,HEX8
         PUT   OUTDCB,CARD
         MVC   CARD(80),ENDREC
         MVC   CARD+5(4),MODNAME
         L     5,PAIRS
         LA    3,CARD+20
         BAL   14,HEX8
         PUT   OUTDCB,CARD
         L     10,CALLRET
         SR    15,15
         BR    10
SCANBAD  MVC   CARD(80),BADREC
         MVC   CARD+5(4),MODNAME
         PUT   OUTDCB,CARD
         L     10,CALLRET
         LA    15,8
         BR    10
*
* HEX8: R5 unsigned fullword, R3 target eight-byte EBCDIC field.
* USE AN INDEPENDENT DIGIT TABLE; THE HOST PARSER CONVERTS OFF/4.
*
HEX8     LA    1,HEXDIG
         LA    0,8
HEXLOOP  LR    2,5
         SRL   2,28
         IC    2,0(2,1)
         STC   2,0(3)
         SLL   5,4
         LA    3,1(3)
         BCT   0,HEXLOOP
         BR    14
         DS    0F
CALLRET  DS    F
MODBASE  DS    F
CURPTR   DS    F
PAIRS    DS    F
MODNAME  DS    CL4
CARD     DS    CL80
SAVEAREA DS    18F
HEXDIG   DC    C'0123456789ABCDEF'
BEGINREC DC    CL80'R0TR      BEGIN'
PAIRREC  DC    CL80'R0TR      OFF=00000000 ADDR=00000000'
LIMITREC DC    CL80'R0TR      LIMIT=00000000'
ENDREC   DC    CL80'R0TR      END COUNT=00000000'
BADREC   DC    CL80'R0TR      ERROR INVALID TRAILER'
PASSREC  DC    CL80'R0TR PASS APP AND INSTALLED BLIB'
OUTDCB   DCB   DDNAME=QOUT,DSORG=PS,MACRF=PM
         LTORG
         END   R0TRACE
