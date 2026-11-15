* CO.4 test-only read-only S1 and BCPLMEM snapshot entry G!301.
* CO4PROB(V) uses word vector V!0..V!8; return R7=0 / -1.
* Snapshot: STKLIM, APLIMIT, G54, G55, CURPTR word ptr,
*           live vector count, peak count, live bytes, peak bytes.
* Call only in quiescent, known-live coroutine/allocator context.
* Save original R1 in R9 and original R0 in R6; RETIMPL frame
* at R15 saves R4..R10. MEMSTAT uses R14 linkage and clobbers R10.
* Keep the probe address base (R10) in R4 across that call.
         USING CO4PROB,4
CO4PROB  STM   4,10,0(15)
         DROP  4
         LR    6,0
         LR    5,15
         LR    9,1
         BALR  10,0
         USING *,10
         LTR   7,7
         BC    8,C4PFAIL
         LR    8,7
         SLL   8,2
         L     4,=A(STKLIM)
         L     0,0(4)
         ST    0,0(8)
         L     4,=A(APLIMIT)
         L     0,0(4)
         ST    0,4(8)
         L     0,216(12)
         ST    0,8(8)
         L     0,220(12)
         ST    0,12(8)
         L     0,CURPTR
         SRL   0,2
         ST    0,16(8)
         LA    1,20(8)
         LR    8,14          SAVE CALLER R14 ACROSS MEMSTAT
         LR    4,10          MEMSTAT CLOBBERS THE IFOX R10 BASE
         L     15,=A(MEMSTAT)
         BALR  14,15
         LR    10,4          RESTORE BASE BEFORE BRANCH/LITERALS
         LR    14,8          RESTORE CALLER R14
         SR    7,7
         B     C4PRET
C4PFAIL L     7,=F'-1'
C4PRET  LR    1,9
         L     8,16(5)
         L     9,20(5)
         LR    0,6
         L     10,24(5)
         LR    15,5
         BCR   15,11
         LTORG
         DROP  10
