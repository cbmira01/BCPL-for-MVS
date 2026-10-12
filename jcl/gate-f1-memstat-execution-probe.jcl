//BCF1RUN  JOB (MVS),'GATE F1 RUN',CLASS=A,MSGCLASS=A,
//             MSGLEVEL=(1,1)
//* TEMP OBJECTS ONLY; NO HERC02 BCPL PDS WRITES.
//ASMMEM   EXEC PGM=IFOX00,REGION=256K,
//             PARM='OBJECT,NODECK,LIST,XREF(FULL),ESD,RLD'
//SYSLIB   DD DSN=SYS1.MACLIB,DISP=SHR
//SYSUT1   DD UNIT=SYSDA,SPACE=(1700,(600,100))
//SYSUT2   DD UNIT=SYSDA,SPACE=(1700,(300,50))
//SYSUT3   DD UNIT=SYSDA,SPACE=(1700,(300,50))
//SYSPRINT DD SYSOUT=*
//SYSPUNCH DD DUMMY
//SYSGO    DD DSN=&&MEMOBJ,UNIT=SYSDA,
//             SPACE=(80,(300,100)),DISP=(NEW,PASS),
//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)
//SYSIN    DD *
* BCPLMEM runtime service: G87/G88 plus private teardown MEMDRAIN.
* Static singleton allocator; intentionally not reentrant.
BCPLMEM  CSECT
         ENTRY GETVEC,FREEVEC,MEMDRAIN,MEMBIND,MEMSTAT
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
* Account only successfully linked allocations.
         L     8,MEMCURN
         LA    8,1(8)
         ST    8,MEMCURN
         C     8,MEMPEAKN
         BNH   GVNCPEAK
         ST    8,MEMPEAKN
GVNCPEAK L     8,MEMCURB
         A     8,GVRLEN
         ST    8,MEMCURB
         C     8,MEMPEAKB
         BNH   GVNBPEAK
         ST    8,MEMPEAKB
GVNBPEAK L     8,VECPUB
         LTR   8,8
         BZ    GVNPUB
         ST    14,0(8)
GVNPUB   L     15,GVRWSAVE
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
         L     8,VECPUB
         LTR   8,8
         BZ    FVUNLNK
         ST    4,0(8)
FVUNLNK  L     4,4(14)
         L     8,MEMCURN
         BCTR  8,0
         ST    8,MEMCURN
         L     8,MEMCURB
         SR    8,4
         ST    8,MEMCURB
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
         L     8,VECPUB
         LTR   8,8
         BZ    MEMFREE
         ST    9,0(8)
MEMFREE  L     8,MEMCURN
         BCTR  8,0
         ST    8,MEMCURN
         L     8,MEMCURB
         SR    8,4
         ST    8,MEMCURB
         FREEMAIN R,LV=(4),A=(1)
         B     MEMLOOP
MEMDONE  LM    0,3,MEMSAV
         L     15,MEMWSAV
         L     14,MEMRET
         BR    14
         DROP  10
*
* MEMBIND: R1=address of writable G6!48 slot, or zero to unbind.
* R14 linkage. Preserve R0-R3, R4-R12, R15 and R1 itself.
MEMBIND  BALR  10,0
         USING *,10
         ST    1,VECPUB
         LTR   1,1
         BZ    MBNRET
         ST    14,MBRET
         L     14,VECLIST
         ST    14,0(1)
         L     14,MBRET
MBNRET   BR    14
         DROP  10
*
* Private snapshot: R1 addresses four fullwords (16 bytes).
* Return R14 intact. R10 is clobbered, as in MEMBIND.
* Call only in quiescent singleton allocator context.
MEMSTAT  BALR  10,0
         USING *,10
         ST    14,MSRET
         L     14,MEMCURN
         ST    14,0(1)
         L     14,MEMPEAKN
         ST    14,4(1)
         L     14,MEMCURB
         ST    14,8(1)
         L     14,MEMPEAKB
         ST    14,12(1)
         L     14,MSRET
         BR    14
         DROP  10
*
* BCPLMEM owns all allocator storage.
         DS    0F
VECLIST  DC    F'0'
MEMCURN  DC    F'0'
MEMPEAKN DC    F'0'
MEMCURB  DC    F'0'
MEMPEAKB DC    F'0'
MSRET    DC    F'0'
VECPUB   DC    F'0'
MBRET    DC    F'0'
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
/*
//ASMDRV   EXEC PGM=IFOX00,REGION=256K,
//             COND=(0,NE,ASMMEM),
//             PARM='OBJECT,NODECK,LIST,XREF(FULL),ESD,RLD'
//SYSLIB   DD DSN=SYS1.MACLIB,DISP=SHR
//SYSUT1   DD UNIT=SYSDA,SPACE=(1700,(600,100))
//SYSUT2   DD UNIT=SYSDA,SPACE=(1700,(300,50))
//SYSUT3   DD UNIT=SYSDA,SPACE=(1700,(300,50))
//SYSPRINT DD SYSOUT=*
//SYSPUNCH DD DUMMY
//SYSGO    DD DSN=&&DRVOBJ,UNIT=SYSDA,
//             SPACE=(80,(300,100)),DISP=(NEW,PASS),
//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)
//SYSIN    DD *
F1PROBE  CSECT
         ENTRY F1PROBE
         EXTRN GETVEC,FREEVEC,MEMSTAT
         STM   14,12,12(13)
         BALR  12,0
         USING *,12
         LA    1,SAVE
         ST    13,4(1)
         ST    1,8(13)
         LR    13,1
         LA    5,FRAME
         LA    9,1
         BAL   14,SNAPSHOT
         CLC   SNAP(16),ZERO
         BNE   FAILURE
* First GETVEC(2): 24 bytes, one allocation.
         LA    7,2
         L     15,=A(GETVEC)
         BALR  6,15
         LTR   7,7
         BZ    FAILURE
         ST    7,V1
         LA    9,2
         BAL   14,SNAPSHOT
         CLC   SNAP(16),ONE
         BNE   FAILURE
* Second GETVEC(4): 32 bytes, total 56.
         LA    7,4
         L     15,=A(GETVEC)
         BALR  6,15
         LTR   7,7
         BZ    FAILURE
         ST    7,V2
         LA    9,3
         BAL   14,SNAPSHOT
         CLC   SNAP(16),TWO
         BNE   FAILURE
* Bad negative size must not affect the snapshot.
         L     7,=F'-1'
         L     15,=A(GETVEC)
         BALR  6,15
         LTR   7,7
         BNZ   FAILURE
         LA    9,4
         BAL   14,SNAPSHOT
         CLC   SNAP(16),TWO
         BNE   FAILURE
* Unknown FREEVEC address is a no-op.
         LA    7,1
         L     15,=A(FREEVEC)
         BALR  6,15
         LA    9,5
         BAL   14,SNAPSHOT
         CLC   SNAP(16),TWO
         BNE   FAILURE
* Free older (non-head) vector: 32 bytes remain.
         L     7,V1
         L     15,=A(FREEVEC)
         BALR  6,15
         LA    9,6
         BAL   14,SNAPSHOT
         CLC   SNAP(16),REMAIN
         BNE   FAILURE
* Free head vector: live totals zero, peaks retained.
         L     7,V2
         L     15,=A(FREEVEC)
         BALR  6,15
         LA    9,7
         BAL   14,SNAPSHOT
         CLC   SNAP(16),DONE
         BNE   FAILURE
         SR    15,15
         B     EXIT
FAILURE  LR    15,9
EXIT     L     13,4(13)
         LM    14,14,12(13)
         LM    0,12,20(13)
         BR    14
* R14 calls snapshot; preserve it across MEMSTAT's R14 call.
SNAPSHOT ST    14,RET
         LA    1,SNAP
         L     15,=A(MEMSTAT)
         BALR  14,15
         L     14,RET
         BR    14
         DS    0F
SAVE     DS    18F
FRAME    DC    F'0'
RET      DC    F'0'
RETCODE  DC    F'0'
V1       DC    F'0'
V2       DC    F'0'
SNAP     DS    4F
ZERO     DC    F'0,0,0,0'
ONE      DC    F'1,1,24,24'
TWO      DC    F'2,2,56,56'
REMAIN   DC    F'1,2,32,56'
DONE     DC    F'0,2,0,56'
         END   F1PROBE
/*
//LKED     EXEC PGM=IEWL,PARM='LIST,XREF,MAP',
//             COND=((0,NE,ASMMEM),(0,NE,ASMDRV))
//SYSLIN   DD DSN=&&DRVOBJ,DISP=(OLD,DELETE)
//         DD DSN=&&MEMOBJ,DISP=(OLD,DELETE)
//         DD *
 ENTRY F1PROBE
 NAME F1PROBE(R)
/*
//SYSLMOD  DD DSN=&&GOSET(F1PROBE),UNIT=SYSDA,
//             SPACE=(1024,(50,20,1)),DISP=(NEW,PASS)
//SYSUT1   DD UNIT=SYSDA,SPACE=(1024,(50,20))
//SYSPRINT DD SYSOUT=*
//GO       EXEC PGM=*.LKED.SYSLMOD,TIME=(,1),
//             COND=((0,NE,ASMMEM),(0,NE,ASMDRV),
//             (0,NE,LKED))
//SYSUDUMP DD SYSOUT=*
//
