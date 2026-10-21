***********************************************************************
* R.0 TEST ONLY: SIX-WORD DISPATCHER A.  G!298 IS TEST-LOCAL.
* NATIVE BCPL ABI: R7 OPCODE/RESULT, R8 VECTOR, R9 CAPACITY.
***********************************************************************
R0QAA    CSECT
         USING R0QAA,4
         STM   4,9,0(15)
         LR    5,15
         LTR   7,7
         BNZ   ANON
         LTR   8,8
         BNZ   APTR
         LTR   9,9
         BNZ   ABAD
         LA    7,6
         BCR   15,11
APTR     LTR   9,9
         BM    ABAD
         C     9,=F'6'
         BL    ASHORT
         SLL   8,2
         LA    14,1
         ST    14,0(8)
         ST    14,4(8)
         SR    14,14
         ST    14,8(8)
         LA    14,6
         ST    14,12(8)
         LA    14,1
         ST    14,16(8)
         SR    14,14
         ST    14,20(8)
         LA    7,6
         BCR   15,11
ANON     C     7,=F'1'
         BE    AONE
         L     7,=F'-2'
         BCR   15,11
AONE     LA    7,101
         BCR   15,11
ASHORT   L     7,=F'-1'
         BCR   15,11
ABAD     L     7,=F'-3'
         BCR   15,11
         LTORG
         END   R0QAA
