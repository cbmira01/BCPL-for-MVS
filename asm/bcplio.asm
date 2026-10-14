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
* routing needs caller-owned nonreturning callback via IOBIND.
* G14 MUST NOT be redirected until BCPLMAIN integration is tested.
* Provisional MVS adaptation, not claimed historical Cambridge code.
***********************************************************************
BCPLIO   CSECT
         ENTRY IOINIT,IOFIN,IOWRCH,IOSTAT,IOSEL
         ENTRY IOFOUT,IOSOUT,IOOUT,IOWRAP,IOENDW
         ENTRY IOBIND,IODIAG,IOREPL
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
         LA    1,IOCTL1
         SRL   1,2
         ST    1,IOCURH
         MVI   IO2ACTV,X'00'
         XC    IOSTATUS(4),IOSTATUS
         XC    IOOVHAND(4),IOOVHAND
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
         CLI   IO2ACTV,X'01'
         BNE   IOFDONE
         L     1,IO2POS
         LTR   1,1
         BZ    IO2CLOS
         PUT   IO2DCB,IO2BUF
IO2CLOS  CLOSE (IO2DCB)
         MVI   IO2ACTV,X'00'
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
         L     14,IOOVHAND
         LTR   14,14
         BZ    IOWRET
* Transfer once, never return. Restore caller R14 with LM, then
* load callback into scratch R10 just before leaving module.
         LM    0,9,IOSAVE
         LM    11,15,IOSAVE+44
         L     4,0(5)
         LA    7,12
         L     14,IOOVHAND
         L     10,IOSAVE+40
         BCR   15,14
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
         CLI   IO2ACTV,X'01'
         BE    IOSETWO
         XC    IO2POS(4),IO2POS
         MVI   IO2BUF,C' '
         MVC   IO2BUF+1(131),IO2BUF
         OPEN  (IO2DCB,(OUTPUT))
         MVI   IO2ACTV,X'01'
IOSETWO  MVI   IOSELCT,X'02'
         LA    1,IOCTL2
         SRL   1,2
         ST    1,IOCURH
         B     IOSEOK
IOSEONE  MVI   IOSELCT,X'01'
         LA    1,IOCTL1
         SRL   1,2
         ST    1,IOCURH
IOSEOK   SR    15,15
         B     IOSERET
IOSEBAD  LA    15,8
IOSERET  LM    0,9,IOESAVE
         LM    11,14,IOESAVE+44
         BR    14
         DROP  10
*
*
* BCPL output-stream ABI. These five entries use R6 linkage, R7
* argument/result, restore R4 from 0(R5), clobber R10.
* Handles are the word addresses of private IOCTL1/IOCTL2.
*
IOFOUT   BALR  10,0
         USING *,10
         STM   0,9,IOOSAVE
         STM   11,15,IOOSAVE+44
         LR    14,7
         SLL   14,2
         CLI   0(14),X'08'
         BNE   IOFALT
         CLC   1(8,14),IONAME1
         BNE   IOFALT
         LA    7,IOCTL1
         SRL   7,2
         B     IOFRET
IOFALT   CLI   0(14),X'06'
         BNE   IOFBAD
         CLC   1(6,14),IONAME2
         BNE   IOFBAD
         CLI   IO2ACTV,X'01'
         BE    IOFOK2
         XC    IO2POS(4),IO2POS
         MVI   IO2BUF,C' '
         MVC   IO2BUF+1(131),IO2BUF
         OPEN  (IO2DCB,(OUTPUT))
         MVI   IO2ACTV,X'01'
IOFOK2   LA    7,IOCTL2
         SRL   7,2
         B     IOFRET
IOFBAD   SR    7,7
IOFRET   ST    7,IORESULT
         LM    0,9,IOOSAVE
         LM    11,15,IOOSAVE+44
         L     7,IORESULT
         L     4,0(5)
         BCR   15,6
         DROP  10
*
IOOUT    BALR  10,0
         USING *,10
         L     7,IOCURH
         L     4,0(5)
         BCR   15,6
         DROP  10
*
IOSOUT   BALR  10,0
         USING *,10
         STM   0,9,IOOSAVE
         STM   11,15,IOOSAVE+44
         LA    14,IOCTL1
         SRL   14,2
         CR    7,14
         BE    IOSPRI
         LA    14,IOCTL2
         SRL   14,2
         CR    7,14
         BNE   IOSRET
         CLI   IO2ACTV,X'01'
         BNE   IOSRET
         MVI   IOSELCT,X'02'
         ST    7,IOCURH
         B     IOSRET
IOSPRI   MVI   IOSELCT,X'01'
         ST    7,IOCURH
IOSRET   LM    0,9,IOOSAVE
         LM    11,15,IOOSAVE+44
         L     4,0(5)
         BCR   15,6
         DROP  10
*
* WRAPOUTPUT: only alternate stream emits an empty record on wrap.
IOWRAP   BALR  10,0
         USING *,10
         STM   0,9,IOOSAVE
         STM   11,15,IOOSAVE+44
         CLI   IOSELCT,X'02'
         BNE   IOWRRET
         CLI   IO2ACTV,X'01'
         BNE   IOWRRET
         PUT   IO2DCB,IO2BUF
         XC    IO2POS(4),IO2POS
         MVI   IO2BUF,C' '
         MVC   IO2BUF+1(131),IO2BUF
IOWRRET  LM    0,9,IOOSAVE
         LM    11,15,IOOSAVE+44
         L     4,0(5)
         BCR   15,6
         DROP  10
*
* ENDWRITE: only alternate; flush/close and revert selection.
IOENDW   BALR  10,0
         USING *,10
         STM   0,9,IOOSAVE
         STM   11,15,IOOSAVE+44
         CLI   IOSELCT,X'02'
         BNE   IOEWRET
         CLI   IO2ACTV,X'01'
         BNE   IOEWDONE
         L     1,IO2POS
         LTR   1,1
         BZ    IOEWCLOS
         PUT   IO2DCB,IO2BUF
IOEWCLOS CLOSE (IO2DCB)
         MVI   IO2ACTV,X'00'
         XC    IO2POS(4),IO2POS
IOEWDONE MVI   IOSELCT,X'01'
         LA    1,IOCTL1
         SRL   1,2
         ST    1,IOCURH
IOEWRET  LM    0,9,IOOSAVE
         LM    11,15,IOOSAVE+44
         L     4,0(5)
         BCR   15,6
         DROP  10
*
*
* Install a caller-owned NONRETURNING overflow exit. R1=entry or 0
* (disable). This is a native R14-linked private setup API.
* Caller must route to STOP(12) and cleanup without returning.
IOBIND   BALR  10,0
         USING *,10
         ST    1,IOOVHAND
         BR    14
         DROP  10
*
*
* Private diagnostic append: R1=EBCDIC byte address, R2=length.
* Appends to PRIMARY buffer regardless of selected output stream.
* No PUT or callback here; R15=0 success, 12 if truncated/full.
* Preserve R0-R9, R11-R14. R10 clobbered, R15 is result.
* Source must not overlap IOBUF, and length must be nonnegative.
IODIAG   BALR  10,0
         USING *,10
         STM   0,9,IODSAVE
         STM   11,14,IODSAVE+44
         LTR   2,2
         BM    IODBAD
         CLI   IOACTIVE,X'01'
         BNE   IODBAD
         L     3,IOPOS
         LA    4,132
         SR    4,3
         CR    2,4
         BNH   IODCOPY
         MVC   IOSTATUS(4),IOOVCODE
         LR    2,4
         LA    15,12
         B     IODWORK
IODCOPY  SR    15,15
IODWORK  LTR   2,2
         BZ    IODRET
* MVC is limited to 256 bytes; primary free space <=132.
         LR    4,1
         LA    5,IOBUF
         AR    5,3
         LR    6,2
         BCTR  6,0
         EX    6,IODMOVE
         AR    3,2
         ST    3,IOPOS
IODRET   ST    15,IODRC
         LM    0,9,IODSAVE
         LM    11,14,IODSAVE+44
         L     15,IODRC
         BR    14
IODBAD   LA    15,8
         B     IODRET
IODMOVE  MVC   0(1,5),0(4)
         DROP  10
*
*
* Private primary record replacement for stack diagnostics.
* R1=source bytes, R2=length (0..132); R15=0 or 8.
* Discards pending primary record, does not PUT or invoke STOP.
* This must not change BCPALT selection or contents.
IOREPL   BALR  10,0
         USING *,10
         STM   0,9,IODSAVE
         STM   11,14,IODSAVE+44
         LTR   2,2
         BM    IORBAD
         C     2,IOMAX
         BH    IORBAD
         CLI   IOACTIVE,X'01'
         BNE   IORBAD
         XC    IOPOS(4),IOPOS
         MVI   IOBUF,C' '
         MVC   IOBUF+1(131),IOBUF
         LTR   2,2
         BZ    IORGOOD
         LA    5,IOBUF
         LR    4,1
         LR    6,2
         BCTR  6,0
         EX    6,IODMOVE
         ST    2,IOPOS
IORGOOD  SR    15,15
         B     IODRET
IORBAD   LA    15,8
         B     IODRET
         DROP  10
*
         DS    0F
IOPARM   DC    F'0'
IODRC    DC    F'0'
IOCTL1   DC    F'1'
IOCTL2   DC    F'2'
IOCURH   DC    F'0'
IORESULT DC    F'0'
IONAME1  DC    CL8'SYSPRINT'
IONAME2  DC    CL6'BCPALT'
IOONE    DC    F'1'
IOTWO    DC    F'2'
IO2POS   DC    F'0'
IO2ACTV DC   X'00'
IOSELCT  DC    X'01'
IOPOS    DC    F'0'
IOMAX    DC    F'132'
IOLF     DC    F'10'
IOSTATUS DC    F'0'
IOOVHAND DC    F'0'
IOOVCODE DC    F'12'
IOACTIVE DC    X'00'
         DS    0F
IOSAVE   DS    16F
IOISAVE  DS    16F
IOFSAVE  DS    16F
IOESAVE  DS    16F
IOOSAVE  DS    16F
IODSAVE  DS    16F
IOBUF    DS    CL132
IODCB    DCB   DDNAME=SYSPRINT,DSORG=PS,MACRF=PM
IO2BUF   DS    CL132
IO2DCB   DCB   DDNAME=BCPALT,DSORG=PS,MACRF=PM
         END   BCPLIO
