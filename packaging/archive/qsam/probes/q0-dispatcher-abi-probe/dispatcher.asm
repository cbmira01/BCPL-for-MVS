***********************************************************************
* Q.0 TEST-ONLY DISPATCHER: G!200 -> Q0DISP.  NO REAL QSAM I/O.
* R7 OPCODE/RESULT, R8 REQ PTR, R9 RESULT PTR / QUERY CAPACITY.
* R5 WORKSPACE; R11 SYSTEM VECTOR; R12 GLOBAL VECTOR.
* LEAVE ACCEPTED BCPLMAIN, CORE OBJECTS AND BCPLIO UNMODIFIED.
***********************************************************************
Q0DISP   CSECT
         USING Q0DISP,4
         STM   4,9,0(15)
         LR    5,15
         LTR   7,7
         BZ    DQUERY
         C     7,=F'5'
         BE    DINFO
* Unimplemented/invalid opcode: -2 and all other words zero.
         SLL   9,2
         XC    0(32,9),0(9)
         L     7,=F'-2'
         ST    7,0(9)
         BCR   15,11
* INFO surrogate: validate the input vector and fill two fields.
DINFO    SLL   8,2
         SLL   9,2
         XC    0(32,9),0(9)
         L     14,0(8)
         C     14,=F'17'
         BNE   DBAD
         L     14,4(8)
         C     14,=F'25'
         BNE   DBAD
         L     14,8(8)
         LTR   14,14
         BNZ   DBAD
         L     14,12(8)
         LTR   14,14
         BNZ   DBAD
         LA    14,42
         ST    14,4(9)
         L     14,=F'777'
         ST    14,28(9)
         SR    7,7
         BCR   15,11
DBAD     L     7,=F'-3'
         ST    7,0(9)
         BCR   15,11
* QUERY follows the six-word proposal.  Does not alter short buffer.
DQUERY   LTR   8,8
         BNZ   DQPTR
         LTR   9,9
         BNZ   DQBAD
         LA    7,6
         BCR   15,11
DQPTR    C     9,=F'6'
         BL    DQSHORT
         SLL   8,2
         LA    14,1
         ST    14,0(8)
         ST    14,4(8)
         SR    14,14
         ST    14,8(8)
         LA    14,6
         ST    14,12(8)
         LA    14,16
         ST    14,16(8)
         SR    14,14
         ST    14,20(8)
         LA    7,6
         BCR   15,11
DQSHORT  L     7,=F'-1'
         BCR   15,11
DQBAD    L     7,=F'-3'
         BCR   15,11
         LTORG
         END   Q0DISP
