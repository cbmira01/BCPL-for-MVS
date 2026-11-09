***********************************************************************
* R.0 TEST ONLY: EIGHT-WORD DISPATCHER B.  G!299 IS TEST-LOCAL.
* NATIVE BCPL ABI: R7 OPCODE/RESULT, R8 VECTOR, R9 CAPACITY.
***********************************************************************
R0QBB    CSECT
         USING R0QBB,4
         STM   4,9,0(15)
         LR    5,15
         LTR   7,7
         BNZ   BNON
         LTR   8,8
         BNZ   BPTR
         LTR   9,9
         BNZ   BBAD
         LA    7,8
         BCR   15,11
BPTR     LTR   9,9
         BM    BBAD
         C     9,=F'8'
         BL    BSHORT
         SLL   8,2
         LA    14,1
         ST    14,0(8)
         LA    14,3
         ST    14,4(8)
         LA    14,2
         ST    14,8(8)
         LA    14,8
         ST    14,12(8)
         LA    14,5
         ST    14,16(8)
         LA    14,2
         ST    14,20(8)
         LA    14,77
         ST    14,24(8)
         LA    14,99
         ST    14,28(8)
         LA    7,8
         BCR   15,11
BNON     C     7,=F'1'
         BE    BONE
         C     7,=F'3'
         BE    BTHREE
         L     7,=F'-2'
         BCR   15,11
BONE     LA    7,201
         BCR   15,11
BTHREE   LA    7,203
         BCR   15,11
BSHORT   L     7,=F'-1'
         BCR   15,11
BBAD     L     7,=F'-3'
         BCR   15,11
         LTORG
         END   R0QBB
