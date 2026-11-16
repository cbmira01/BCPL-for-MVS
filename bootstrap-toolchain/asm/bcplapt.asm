***********************************************************************
* BCPL FOR MVS 3.8 RECONSTRUCTION - BCPLAPT
*
* Core Runtime argument-vector and workspace support.
* APTOVEC builds a vector from procedure arguments.
*
* LINKAGE:
* APLIMIT is exported here and initialized by BCPLMAIN.
* Stack/workspace bounds errors transfer to STKOVFL.
***********************************************************************

BCPLAPT  CSECT
         ENTRY APTOVEC,APLIMIT
         EXTRN STKOVFL
* APTOVEC: R7=procedure entry, R8=argument count.
* Build a word-addressed argument vector above the caller frame.
* Invoke the procedure through normal BCPL linkage; the caller
* must have enough checked workspace for its argument words.
APTOVEC  STM   4,6,0(15)
         ST    10,12(15)
         LR    5,15
         BALR  10,0
         USING *,10
         LTR   8,8
         BM    APERROR
         C     8,APMAXN
         BH    APERROR
         LR    14,8
         SLL   14,2
         LA    14,20(14)
         LR    4,15
         AR    4,14
         LR    14,4
         LA    14,16(14)
* Include arguments and call clearance in the safe-limit check.
* APLIMIT is a byte address. The active coroutine determines
* which stack limit belongs here.
         C     14,APLIMIT
         BH    APERROR
         LR    14,7
         LA    7,16(15)
         SRL   7,2
         LR    15,4
         LR    4,14
         L     10,12(5)
         BALR  6,4
         L     6,8(5)
         L     5,4(5)
         L     4,0(5)
         BCR   15,6
* Invalid counts and exhausted workspace take the same
* nonreturning overflow path as a checked BCPL procedure entry.
APERROR  L     4,=A(STKOVFL)
         BR    4
         LTORG
APMAXN   DC    F'16380'
APLIMIT  DC    F'0'
         DROP  10
         END   BCPLAPT
