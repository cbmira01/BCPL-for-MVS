* BCPLMEM test object: G87/G88 plus private teardown MEMDRAIN.
* Static singleton allocator; intentionally not reentrant.
BCPLMEM  CSECT
         ENTRY GETVEC,FREEVEC,MEMDRAIN
*
* GETVEC(N): R7=N. R10 is our private addressing base.
GETVEC   BALR  10,0
         USING *,10
         LTR   7,7
         BM    GVFAIL0
         C     7,GVRMAX
         BH    GVFAIL0
         STM   0,3,GVRSAVE
         ST    5,GVRPSAVE
         ST    6,GVRLSAVE
         ST    15,GVRWSAVE
         LR    8,7
         LA    8,1(8)
         SLL   8,2
         LA    8,12(8)
         ST    8,GVRLEN
         GETMAIN EC,LV=(8),A=GVRADDR,SP=0
         LTR   15,15
         BNZ   GVFAIL
         L     14,GVRADDR
         LA    7,12(14)
         SRL   7,2
         ST    7,0(14)
         L     8,GVRLEN
         ST    8,4(14)
         L     8,VECLIST
         ST    8,8(14)
         ST    14,VECLIST
         L     15,GVRWSAVE
         LM    0,3,GVRSAVE
         L     5,GVRPSAVE
         L     6,GVRLSAVE
         L     4,0(5)
         BCR   15,6
GVFAIL   L     15,GVRWSAVE
         LM    0,3,GVRSAVE
         L     5,GVRPSAVE
         L     6,GVRLSAVE
GVFAIL0  SR    7,7
         L     4,0(5)
         BCR   15,6
         DROP  10
*
* FREEVEC(V): R7=BCPL word pointer, unknown pointer is no-op.
FREEVEC  BALR  10,0
         USING *,10
         LTR   7,7
         BZ    FVRETURN
         STM   0,3,FVRSAVE
         ST    5,FVPSAVE
         ST    6,FVLSAVE
         ST    15,FVWSAVE
         LR    9,7
         SR    8,8
         L     14,VECLIST
FVSCAN   LTR   14,14
         BZ    FVNFOUND
         C     9,0(14)
         BE    FVFOUND
         LR    8,14
         L     14,8(14)
         B     FVSCAN
FVFOUND  L     4,8(14)
         LTR   8,8
         BZ    FVHEAD
         ST    4,8(8)
         B     FVUNLNK
FVHEAD   ST    4,VECLIST
FVUNLNK  L     4,4(14)
         LR    1,14
         FREEMAIN R,LV=(4),A=(1)
         L     15,FVWSAVE
         LM    0,3,FVRSAVE
         L     5,FVPSAVE
         L     6,FVLSAVE
FVRETURN L     4,0(5)
         BCR   15,6
FVNFOUND L     15,FVWSAVE
         LM    0,3,FVRSAVE
         L     5,FVPSAVE
         L     6,FVLSAVE
         B     FVRETURN
         DROP  10
*
* MEMDRAIN: private BCPLMAIN exit call, R14 linkage.
* Preserve R0-R3, R15 and all BCPL fixed base registers.
MEMDRAIN BALR  10,0
         USING *,10
         ST    14,MEMRET
         STM   0,3,MEMSAV
         ST    15,MEMWSAV
MEMLOOP  L     1,VECLIST
         LTR   1,1
         BZ    MEMDONE
         L     4,4(1)
         L     9,8(1)
         ST    9,VECLIST
         FREEMAIN R,LV=(4),A=(1)
         B     MEMLOOP
MEMDONE  LM    0,3,MEMSAV
         L     15,MEMWSAV
         L     14,MEMRET
         BR    14
         DROP  10
*
* BCPLMEM owns all allocator storage.
         DS    0F
VECLIST  DC    F'0'
GVRMAX   DC    F'4194299'
GVRLEN   DC    F'0'
GVRADDR  DC    F'0'
GVRSAVE  DS    4F
GVRPSAVE DC    F'0'
GVRLSAVE DC    F'0'
GVRWSAVE DC    F'0'
FVRSAVE  DS    4F
FVPSAVE  DC    F'0'
FVLSAVE  DC    F'0'
FVWSAVE  DC    F'0'
MEMRET   DC    F'0'
MEMSAV   DS    4F
MEMWSAV  DC    F'0'
         END   BCPLMEM
