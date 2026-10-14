***********************************************************************
* BCPLIO - M2.0 D2 FIRST OUTPUT-SERVICE EXTRACTION CANDIDATE
*
* PURPOSE: Independent SYSPRINT QSAM output service.
* This is a candidate isolated from BCPLMAIN dispatch until tested.
* Exports: IOINIT, IOFIN (R14 native linkage); IOWRCH (BCPL R6).
* EXTRN: none. No private BCPLMAIN storage references.
*
* IOINIT: R1=original MVS EXEC PARM list; open SYSPRINT for output,
*         initialize one 132-byte record and stream state.
* IOFIN:  write any nonempty record, CLOSE SYSPRINT, clear state.
* IOWRCH: R7 EBCDIC byte; 10 ends a QSAM record; returns via R6,
*         restoring R4 from 0(R5); 132-byte buffer capacity.
*         R0-R3, R5-R9, R11-R12, R15 preserved by IOWRCH.
*         R10 is private module base and is clobbered.
*
* Not reentrant: singleton DCB, buffer and register save area.
* No STOP/overflow routing is installed in this candidate. A full
* buffer is treated as a no-op pending D3 failure-path integration.
* This limitation MUST be resolved before G14 can be redirected.
* Provisional MVS adaptation, not claimed historical Cambridge code.
***********************************************************************
BCPLIO   CSECT
         ENTRY IOINIT,IOFIN,IOWRCH
*
IOINIT   BALR  10,0
         USING *,10
         ST    14,IORET
         ST    1,IOPARM
         XC    IOPOS(4),IOPOS
         MVI   IOBUF,C' '
         MVC   IOBUF+1(131),IOBUF
         OPEN  (IODCB,(OUTPUT))
         MVI   IOACTIVE,X'01'
         L     14,IORET
         BR    14
         DROP  10
*
IOFIN    BALR  10,0
         USING *,10
         ST    14,IORET
         CLI   IOACTIVE,X'01'
         BNE   IOFDONE
         L     1,IOPOS
         LTR   1,1
         BZ    IOFCLOSE
         PUT   IODCB,IOBUF
IOFCLOSE CLOSE (IODCB)
         MVI   IOACTIVE,X'00'
         XC    IOPOS(4),IOPOS
IOFDONE  XC    IOPARM(4),IOPARM
         L     14,IORET
         BR    14
         DROP  10
*
* BCPL-facing candidate: R7 holds a character code.
* Save only registers which might be used by QSAM PUT.
IOWRCH   BALR  10,0
         USING *,10
         C     7,IOLF
         BE    IOWPUT
         L     14,IOPOS
         C     14,IOMAX
         BNL   IOWRET
         LA    4,IOBUF
         AR    4,14
         STC   7,0(4)
         LA    14,1(14)
         ST    14,IOPOS
         B     IOWRET
IOWPUT   STM   0,15,IOSAVE
         PUT   IODCB,IOBUF
         XC    IOPOS(4),IOPOS
         MVI   IOBUF,C' '
         MVC   IOBUF+1(131),IOBUF
         LM    0,15,IOSAVE
IOWRET   L     4,0(5)
         BCR   15,6
         DROP  10
*
         DS    0F
IORET    DC    F'0'
IOPARM   DC    F'0'
IOPOS    DC    F'0'
IOMAX    DC    F'132'
IOLF     DC    F'10'
IOACTIVE DC    X'00'
         DS    0F
IOSAVE   DS    16F
IOBUF    DS    CL132
IODCB    DCB   DDNAME=SYSPRINT,DSORG=PS,MACRF=PM
         END   BCPLIO
