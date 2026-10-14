***********************************************************************
* BCPLIO - M2.0 D2 FIRST OUTPUT-SERVICE EXTRACTION CANDIDATE
*
* PURPOSE: Independent SYSPRINT/BCPALT QSAM output service.
* This is a candidate isolated from BCPLMAIN dispatch until tested.
* Exports: IOINIT, IOFIN, IOSTAT (R14 native); IOWRCH (BCPL R6).
* EXTRN: none. No private BCPLMAIN storage references.
*
* IOINIT: R1=original MVS EXEC PARM list; open SYSPRINT for output,
*         initialize one 132-byte record and stream state.
* IOFIN:  write any nonempty record, CLOSE SYSPRINT, clear state.
* IOWRCH: R7 EBCDIC byte; 10 ends a QSAM record; returns via R6,
*         restoring R4 from 0(R5); 132-byte buffer capacity.
*         R0-R3, R5-R9, R11-R12, R15 preserved by IOWRCH.
*         R10 is private module base and is clobbered.
* IOSTAT: R15=0 normal, 12 output overflow; native R14 return.
*         Does not clear the sticky result.
* IOINIT/IOFIN preserve R0-R9 and R11-R15, including R14 return;
* R10 clobbered. R13 remains the caller MVS savearea pointer.
*
* Not reentrant: singleton DCB, buffer and register save area.
* Overflow latches IOSTATUS=12; character is not written. STOP(12)
* routing is NOT yet installed. G14 MUST NOT be redirected until then.
* Provisional MVS adaptation, not claimed historical Cambridge code.
***********************************************************************
BCPLIO   CSECT
         ENTRY IOINIT,IOFIN,IOWRCH,IOSTAT,IOSEL
*
IOINIT   BALR  10,0
         USING *,10
         STM   0,9,IOISAVE
         STM   11,15,IOISAVE+44
         CLI   IOACTIVE,X'01'
         BE    IOIDONE
         ST    1,IOPARM
         XC    IOPOS(4),IOPOS
         XC    IO2POS(4),IO2POS
         MVI   IOSELCT,X'01'
         MVI   IO2ACTIVE,X'00'
         XC    IOSTATUS(4),IOSTATUS
         MVI   IOBUF,C' '
         MVC   IOBUF+1(131),IOBUF
         OPEN  (IODCB,(OUTPUT))
         MVI   IOACTIVE,X'01'
IOIDONE  LM    0,9,IOISAVE
         LM    11,15,IOISAVE+44
         BR    14
         DROP  10
*
IOFIN    BALR  10,0
         USING *,10
         STM   0,9,IOFSAVE
         STM   11,15,IOFSAVE+44
         CLI   IOACTIVE,X'01'
         BNE   IOFDONE
         L     1,IOPOS
         LTR   1,1
         BZ    IOFCLOSE
         PUT   IODCB,IOBUF
IOFCLOSE CLOSE (IODCB)
         MVI   IOACTIVE,X'00'
         XC    IOPOS(4),IOPOS
         CLI   IO2ACTIVE,X'01'
         BNE   IOFDONE
         L     1,IO2POS
         LTR   1,1
         BZ    IO2CLOS
         PUT   IO2DCB,IO2BUF
IO2CLOS  CLOSE (IO2DCB)
         MVI   IO2ACTIVE,X'00'
         XC    IO2POS(4),IO2POS
IOFDONE  XC    IOPARM(4),IOPARM
         LM    0,9,IOFSAVE
         LM    11,15,IOFSAVE+44
         BR    14
         DROP  10
*
* BCPL-facing candidate: R7 holds a character code.
* Save caller registers before all output paths, including PUT.
IOWRCH   BALR  10,0
         USING *,10
         STM   0,9,IOSAVE
         STM   11,15,IOSAVE+44
         CLI   IOSELCT,X'02'
         BE    IOW2
         C     7,IOLF
         BE    IOWPUT
         L     14,IOPOS
         C     14,IOMAX
         BNL   IOWFULL
         LA    4,IOBUF
         AR    4,14
         STC   7,0(4)
         LA    14,1(14)
         ST    14,IOPOS
         B     IOWRET
IOWPUT   PUT   IODCB,IOBUF
         XC    IOPOS(4),IOPOS
         MVI   IOBUF,C' '
         MVC   IOBUF+1(131),IOBUF
         B     IOWRET
IOWFULL  MVC   IOSTATUS(4),IOOVCODE
         B     IOWRET
IOW2     C     7,IOLF
         BE    IOW2PUT
         L     14,IO2POS
         C     14,IOMAX
         BNL   IOWFULL
         LA    4,IO2BUF
         AR    4,14
         STC   7,0(4)
         LA    14,1(14)
         ST    14,IO2POS
         B     IOWRET
IOW2PUT  PUT   IO2DCB,IO2BUF
         XC    IO2POS(4),IO2POS
         MVI   IO2BUF,C' '
         MVC   IO2BUF+1(131),IO2BUF
IOWRET   LM    0,9,IOSAVE
         LM    11,15,IOSAVE+44
         L     4,0(5)
         BCR   15,6
         DROP  10
*
* Native diagnostic accessor, not a BCPL global-vector service.
IOSTAT   BALR  10,0
         USING *,10
         L     15,IOSTATUS
         BR    14
         DROP  10
*
*
* Native selected-stream control: R1=1 primary, 2 alternate.
* R15=0 accepted, 8 invalid/inactive, same native ABI as IOINIT.
* Secondary OPEN is lazy; a successful primary selection never OPENs.
IOSEL    BALR  10,0
         USING *,10
         STM   0,9,IOESAVE
         STM   11,14,IOESAVE+44
         LR    15,1
         CLI   IOACTIVE,X'01'
         BNE   IOSEBAD
         C     15,IOONE
         BE    IOSEONE
         C     15,IOTWO
         BNE   IOSEBAD
         CLI   IO2ACTIVE,X'01'
         BE    IOSETWO
         XC    IO2POS(4),IO2POS
         MVI   IO2BUF,C' '
         MVC   IO2BUF+1(131),IO2BUF
         OPEN  (IO2DCB,(OUTPUT))
         MVI   IO2ACTIVE,X'01'
IOSETWO  MVI   IOSELCT,X'02'
         B     IOSEOK
IOSEONE  MVI   IOSELCT,X'01'
IOSEOK   SR    15,15
         B     IOSERET
IOSEBAD  LA    15,8
IOSERET  LM    0,9,IOESAVE
         LM    11,14,IOESAVE+44
         BR    14
         DROP  10
*
         DS    0F
IOPARM   DC    F'0'
IOONE    DC    F'1'
IOTWO    DC    F'2'
IO2POS   DC    F'0'
IO2ACTIVE DC   X'00'
IOSELCT  DC    X'01'
IOPOS    DC    F'0'
IOMAX    DC    F'132'
IOLF     DC    F'10'
IOSTATUS DC    F'0'
IOOVCODE DC    F'12'
IOACTIVE DC    X'00'
         DS    0F
IOSAVE   DS    16F
IOISAVE  DS    16F
IOFSAVE  DS    16F
IOESAVE  DS    16F
IOBUF    DS    CL132
IODCB    DCB   DDNAME=SYSPRINT,DSORG=PS,MACRF=PM
IO2BUF   DS    CL132
IO2DCB   DCB   DDNAME=BCPALT,DSORG=PS,MACRF=PM
         END   BCPLIO
