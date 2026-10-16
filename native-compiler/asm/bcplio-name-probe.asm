***********************************************************************
* IONMPRB - M1 DD NAME NORMALIZATION PROBE.
* Tests BCPLIO private R14-linked IONORM; no BCPLMAIN.
***********************************************************************
IONMPRB  CSECT
         ENTRY IONMPRB
         EXTRN IONORM
         STM   14,12,12(13)
         LR    12,15
         USING IONMPRB,12
         ST    13,OLDSAV+4
         LA    13,NEWSAV
         LA    8,TAB
         LA    9,6
NEXTCASE L     1,0(8)
         LA    2,NAMEBUF
         MVI   NAMEBUF,C'?'
         MVC   NAMEBUF+1(7),NAMEBUF
         L     15,=A(IONORM)
         BALR  14,15
         C     15,8(8)
         BNE   FAILED
         L     3,4(8)
         LTR   3,3
         BZ    SKIPCMP
         CLC   NAMEBUF(8),0(3)
         BNE   FAILED
SKIPCMP  LA    8,12(8)
         BCT   9,NEXTCASE
GOOD     L     13,OLDSAV+4
         LM    14,12,12(13)
         SR    15,15
         BR    14
FAILED   L     13,OLDSAV+4
         LM    14,12,12(13)
         LA    15,8
         BR    14
         LTORG
* Table: counted string, expected name or zero, expected RC.
TAB      DC    A(N1),A(E1),F'0'
         DC    A(N2),A(E2),F'0'
         DC    A(N3),A(E3),F'0'
         DC    A(N4),A(0),F'8'
         DC    A(N5),A(0),F'8'
         DC    A(N6),A(0),F'8'
N1       DC    X'08',C'customer'
E1       DC    CL8'CUSTOMER'
N2       DC    X'06',C'RepOrt'
E2       DC    CL8'REPORT'
N3       DC    X'03',C'DD1'
E3       DC    CL8'DD1'
N4       DC    X'00'
N5       DC    X'09',C'ABCDEFGHI'
N6       DC    X'03',C'1AB'
         DS    0F
NAMEBUF  DS    CL8
OLDSAV   DS    18F
NEWSAV   DS    18F
         END   IONMPRB
