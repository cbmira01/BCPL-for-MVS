*===================================================================
* BCPLIO -- BCPL STREAM I/O AND MVS QSAM SUPPORT
*
* PUBLIC BCPL SERVICES
* G!11/G!12 Select input and output stream.
* G!13/G!14 Read and write one character.
* G!15 Push back the last input character.
* G!16/G!17 Return the selected input/output handle.
* G!33 Control output wrapping.
* G!39 Read MVS EXEC PARM as a stream.
* G!41/G!42 Find an output or input DD stream.
* G!46/G!47 Close an input or output stream.
*
* STREAM MODEL
* Known built-in streams use SYSPRINT, BCPALT, BCPIN, and BCPINB.
* Additional JCL DD names are handled by dynamic descriptors.
* Input is record-oriented underneath the BCPL character stream.
* Output is buffered as FB132 records. Input uses FB80 records.
* Each live dynamic stream owns its DCB, buffer and state.
* Handles are stable while a task runs; closed handles are not
* reused. A missing or invalid stream yields a failure result.
*
* LINKAGE AND OWNERSHIP
* BCPL entries follow the CG370 R4-R12 calling convention.
* R7 holds the first argument or return value. R6 is linkage.
* Private helper entries use their documented R1/R14/R15 rules.
* BCPLMAIN calls IOINIT at startup and IOFIN during shutdown.
* This module uses static work areas and is not reentrant.
* QSAM OPEN, GET, PUT and CLOSE happen within this module.
*===================================================================
*
*------------------------------------------------------------------
* MODULE ENTRY
* Export stream services and private helpers used by BCPLMAIN.
*------------------------------------------------------------------
BCPLIO   CSECT
         ENTRY IOINIT,IOFIN,IOWRCH,IOSTAT,IOSEL
         ENTRY IOFOUT,IOSOUT,IOOUT,IOWRAP,IOENDW
         ENTRY IOBIND,IODIAG,IOREPL,IOPMGET
         ENTRY IOSELIN,IOINP,IOPARMST,IORDCH,IOUNRD,IOFINDIN
         ENTRY IOENDRD,IONORM
*
*------------------------------------------------------------------
* START STREAM STATE
* Save the original MVS EXEC parameter pointer and reset the
* input/output stream descriptors and counters.
*------------------------------------------------------------------
IOINIT   BALR  10,0
         USING *,10
         STM   0,9,IOISAVE
         STM   11,15,IOISAVE+44
         LA    11,3584(10)
         USING IOINIT+3586,11
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
         DROP  11
         DROP  10
*
*------------------------------------------------------------------
* SHUT DOWN STREAMS
* Flush output, close any open built-in QSAM streams, drain dynamic
* descriptors, and clear input state.
*------------------------------------------------------------------
IOFIN    BALR  10,0
         USING *,10
         STM   0,9,IOFSAVE
         STM   11,15,IOFSAVE+44
         LA    11,4095(10)
         LA    11,1(11)
         USING IOFIN+4098,11
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
IOFDONE  CLI   INOPEN,X'01'
         BNE   IFD2
         CLOSE (BCPIN)
         MVI   INOPEN,X'00'
IFD2     CLI   IN2OPEN,X'01'
         BNE   IFDPARM
         CLOSE (BCPIN2)
         MVI   IN2OPEN,X'00'
IFDPARM  LR    9,10
         L     15,=A(IODRAIN)
         BALR  14,15
         LR    10,9
         LA    11,4095(10)
         LA    11,1(11)
         XC    IOPARM(4),IOPARM
         LM    0,9,IOFSAVE
         LM    11,15,IOFSAVE+44
         BR    14
         DROP  11
         DROP  10
*
*------------------------------------------------------------------
* WRITE A CHARACTER -- G!14
* Use R7 as the character. Buffer bytes in the selected output
* stream and PUT complete records with QSAM.
*------------------------------------------------------------------
IOWRCH   LR    4,10
         BALR  10,0
         USING *,10
         ST    4,IOSAVE+40
         STM   0,9,IOSAVE
         STM   11,15,IOSAVE+44
         LA    11,3584(10)
         USING IOWRCH+3588,11
         CLI   IOSELCT,X'03'
         BE    IOWDYN
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
         LA    11,3584(10)
         LM    0,9,IOSAVE
         LM    12,15,IOSAVE+48
         L     4,0(5)
         LA    7,12
         L     14,IOOVHAND
         L     11,IOSAVE+44
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
         B     IOWRET
IOWDYN   LR    9,10
         L     1,IOCURH
         L     15,=A(HLOOK)
         BALR  14,15
         LR    10,9
         LTR   15,15
         BZ    IOWFULL
         LR    2,15
         L     3,16(2)
         L     14,236(3)
         C     7,IOLF
         BE    IOWDPUT
         C     14,IOMAX
         BNL   IOWFULL
         LA    4,0(3,14)
         STC   7,0(4)
         LA    14,1(14)
         ST    14,236(3)
         B     IOWRET
IOWDPUT  LR    1,2
         LR    2,3
         L     15,=A(DQPUT)
         BALR  14,15
         LR    10,9
         LTR   15,15
         BNZ   IOWFULL
         L     1,IOCURH
         L     15,=A(HLOOK)
         BALR  14,15
         LR    10,9
         L     3,16(15)
         XC    236(4,3),236(3)
         MVI   0(3),C' '
         MVC   1(131,3),0(3)
         B     IOWRET
IOWRET   LA    11,3584(10)
         LM    0,9,IOSAVE
         LM    12,15,IOSAVE+48
         L     4,0(5)
         L     11,IOSAVE+44
         L     10,IOSAVE+40
         BCR   15,6
         LTORG
         DROP  11
         DROP  10
         DS    0F
IOSAVE   DS    16F
IOISAVE  DS    16F
IOFSAVE  DS    16F
*
*------------------------------------------------------------------
* OUTPUT STATUS
* Return a saved output status code to the private runtime caller.
*------------------------------------------------------------------
IOSTAT   BALR  10,0
         USING *,10
         L     15,IOSTATUS
         BR    14
         DROP  10
*
*------------------------------------------------------------------
* LOW-LEVEL OUTPUT SELECTION
* Choose the primary or alternate built-in output stream by numeric
* selector.
*------------------------------------------------------------------
IOSEL    BALR  10,0
         USING *,10
         STM   0,9,IOESAVE
         STM   11,14,IOESAVE+44
         LA    11,3584(10)
         USING IOSEL+3586,11
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
         DROP  11
         DROP  10
*
*------------------------------------------------------------------
* NORMALIZE A JCL DD NAME
* Check the name length and legal EBCDIC characters. Convert lower
* case to upper case.
*------------------------------------------------------------------
IONORM   BALR  10,0
         USING *,10
         STM   0,9,IONMSAV
         STM   11,14,IONMSAV+44
         LR    4,1
         LR    5,2
         SR    3,3
         IC    3,0(4)
         LTR   3,3
         BZ    IONMBAD
         CH    3,IONMMAX
         BH    IONMBAD
         MVI   0(5),C' '
         MVC   1(7,5),0(5)
         LA    4,1(4)
         SR    6,6
IONMLOOP SR    7,7
         IC    7,0(4)
         CLI   0(4),X'81'
         BL    IONMUP
         CLI   0(4),X'89'
         BNH   IONMLOW
         CLI   0(4),X'91'
         BL    IONMUP
         CLI   0(4),X'99'
         BNH   IONMLOW
         CLI   0(4),X'A2'
         BL    IONMUP
         CLI   0(4),X'A9'
         BH    IONMUP
IONMLOW  O     7,IONMCASE
IONMUP   STC   7,0(5)
         CLI   0(5),X'C1'
         BL    IONMSPEC
         CLI   0(5),X'C9'
         BNH   IONMOK
         CLI   0(5),X'D1'
         BL    IONMSPEC
         CLI   0(5),X'D9'
         BNH   IONMOK
         CLI   0(5),X'E2'
         BL    IONMSPEC
         CLI   0(5),X'E9'
         BNH   IONMOK
IONMSPEC CLI   0(5),X'7C'
         BE    IONMOK
         CLI   0(5),X'7B'
         BE    IONMOK
         CLI   0(5),X'5B'
         BE    IONMOK
         LTR   6,6
         BZ    IONMBAD
         CLI   0(5),X'F0'
         BL    IONMBAD
         CLI   0(5),X'F9'
         BH    IONMBAD
IONMOK   LA    6,1(6)
         LA    4,1(4)
         LA    5,1(5)
         CR    6,3
         BL    IONMLOOP
         SR    15,15
         B     IONMRET
IONMBAD  LA    15,8
IONMRET  ST    15,IONMRC
         LM    0,9,IONMSAV
         LM    11,14,IONMSAV+44
         L     15,IONMRC
         BR    14
         DROP  10
         DS    0F
IONMCASE DC    X'00000040'
IONMMAX  DC    H'8'
         DS    0F
IONMRC   DC    F'0'
IONMSAV  DS    16F
*
*------------------------------------------------------------------
* FINDOUTPUT -- G!41
* Return a handle for a known output name or a verified dynamic JCL
* DD allocation.
*------------------------------------------------------------------
IOFOUT   LR    4,10
         BALR  10,0
         USING *,10
         ST    4,IOOSAVE+40
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
IOFBAD   LR    1,14
         L     15,=A(DQFIND)
         BALR  14,15
         LR    7,15
IOFRET   ST    7,IORESULT
         LM    0,9,IOOSAVE
         LM    11,15,IOOSAVE+44
         L     7,IORESULT
         L     4,0(5)
         L     10,IOOSAVE+40
         BCR   15,6
         LTORG
         DROP  10
*
*------------------------------------------------------------------
* OUTPUT -- G!17
* Return the current output stream handle.
*------------------------------------------------------------------
IOOUT    LR    4,10
         BALR  10,0
         USING *,10
         ST    4,IOOBASE
         L     7,IOCURH
         L     4,0(5)
         L     10,IOOBASE
         BCR   15,6
         DROP  10
*
*------------------------------------------------------------------
* SELECTOUTPUT -- G!12
* Select a known or dynamic output handle without changing
* unrelated stream state.
*------------------------------------------------------------------
IOSOUT   LR    4,10
         BALR  10,0
         USING *,10
         ST    4,IOOSAVE+40
         STM   0,9,IOOSAVE
         STM   11,15,IOOSAVE+44
         LA    14,IOCTL1
         SRL   14,2
         CR    7,14
         BE    IOSPRI
         LA    14,IOCTL2
         SRL   14,2
         CR    7,14
         BNE   IOSDYN
         CLI   IO2ACTV,X'01'
         BNE   IOSRET
         MVI   IOSELCT,X'02'
         ST    7,IOCURH
         B     IOSRET
IOSDYN   LR    9,10
         LR    1,7
         L     15,=A(HLOOK)
         BALR  14,15
         LR    10,9
         LTR   15,15
         BZ    IOSRET
         C     7,IOCURH
         BE    IOSRET
         ST    7,IOCURH
         MVI   IOSELCT,X'03'
         B     IOSRET
IOSPRI   MVI   IOSELCT,X'01'
         ST    7,IOCURH
IOSRET   LM    0,9,IOOSAVE
         LM    11,15,IOOSAVE+44
         L     4,0(5)
         L     10,IOOSAVE+40
         BCR   15,6
         LTORG
         DROP  10
*
*------------------------------------------------------------------
* WRAPOUTPUT -- G!33
* Get or set the output wrapping behavior for the selected stream.
*------------------------------------------------------------------
IOWRAP   LR    4,10
         BALR  10,0
         USING *,10
         ST    4,IOOSAVE+40
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
         L     10,IOOSAVE+40
         BCR   15,6
         DROP  10
*
*------------------------------------------------------------------
* ENDWRITE -- G!47
* Flush a pending output record, close the stream and release any
* dynamic descriptor.
*------------------------------------------------------------------
IOENDW   LR    4,10
         BALR  10,0
         USING *,10
         ST    4,IOOSAVE+40
         STM   0,9,IOOSAVE
         STM   11,15,IOOSAVE+44
         CLI   IOSELCT,X'03'
         BE    IOEWDYN
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
         B     IOEWRET
IOEWDYN  LR    9,10
         L     1,IOCURH
         L     15,=A(HLOOK)
         BALR  14,15
         LR    10,9
         LTR   15,15
         BZ    IOEWDONE
         ST    15,IOWDESC
         L     2,16(15)
         L     3,236(2)
         LTR   3,3
         BZ    IOEDCLOS
         LR    1,15
         L     15,=A(DQPUT)
         BALR  14,15
         LR    10,9
IOEDCLOS L     1,IOWDESC
         L     15,=A(DQCLOSE)
         BALR  14,15
         LR    10,9
         L     1,IOCURH
         L     15,=A(HCLOSE)
         BALR  14,15
         LR    10,9
         L     1,IOWDESC
         L     15,=A(DREL)
         BALR  14,15
         LR    10,9
         B     IOEWDONE
IOEWRET  LM    0,9,IOOSAVE
         LM    11,15,IOOSAVE+44
         L     4,0(5)
         L     10,IOOSAVE+40
         BCR   15,6
         LTORG
         DROP  10
*
*------------------------------------------------------------------
* PRIVATE OVERFLOW CALLBACK
* Install the runtime's nonreturning output-overflow handler.
*------------------------------------------------------------------
IOBIND   BALR  10,0
         USING *,10
         ST    1,IOOVHAND
         BR    14
         DROP  10
*
*------------------------------------------------------------------
* PRIVATE DIAGNOSTIC APPEND
* Append message bytes to the output buffer, keeping its record
* limits.
*------------------------------------------------------------------
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
*------------------------------------------------------------------
* PRIVATE DIAGNOSTIC REPLACEMENT
* Replace buffered output with a diagnostic record.
*------------------------------------------------------------------
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
         EX    6,IORMOVE
         ST    2,IOPOS
IORGOOD  SR    15,15
         B     IORRET
IORBAD   LA    15,8
         B     IORRET
IORRET   ST    15,IODRC
         LM    0,9,IODSAVE
         LM    11,14,IODSAVE+44
         L     15,IODRC
         BR    14
IORMOVE  MVC   0(1,5),0(4)
         DROP  10
*
*------------------------------------------------------------------
* ORIGINAL MVS PARAMETER POINTER
* Return the pointer captured at IOINIT so the PARM stream can read
* it.
*------------------------------------------------------------------
IOPMGET  BALR  10,0
         USING *,10
         L     15,IOPARM
         BR    14
         DROP  10
*
*------------------------------------------------------------------
* FINDINPUT -- G!42
* Return a stream handle for a built-in input DD or a valid dynamic
* input DD.
*------------------------------------------------------------------
IOFINDIN  LR    4,10
         BALR  10,0
         USING *,10
         ST    4,IINBASE
         STM   0,15,IINSAVE
         LR    14,7
         SLL   14,2
         CLI   0(14),X'06'
         BNE   FTRYIN1
         CLC   1(6,14),IN2NAME
         BNE   FTRYIN1
         CLI   IN2OPEN,X'01'
         BE    FIN2OK
         OPEN  (BCPIN2,(INPUT))
         MVI   IN2OPEN,X'01'
         MVI   IN2EOF,X'00'
         MVI   IN2NL,X'00'
         MVI   IN2PUSH,X'00'
         MVI   IN2SEEN,X'00'
         MVC   IN2POS(4),ININIT
FIN2OK   LA    7,IN2CTRL
         SRL   7,2
         B     FRET
FTRYIN1  EQU   *
         LR    14,7
         SLL   14,2
         CLI   0(14),X'05'
         BNE   FNOTFND
         CLC   1(5,14),INNAME
         BNE   FNOTFND
         CLI   INOPEN,X'01'
         BE    FFOUND
         OPEN  (BCPIN,(INPUT))
         MVI   INOPEN,X'01'
         MVI   INEOF,X'00'
         MVI   INNL,X'00'
         MVI   INPUSH,X'00'
         MVI   INSEEN,X'00'
         MVC   INPOS(4),ININIT
FFOUND   LA    7,INCTRL
         SRL   7,2
         B     FRET
FNOTFND  LR    1,14
         L     15,=A(DIFIND)
         BALR  14,15
         LR    7,15
FRET     ST    7,IINRES
         LM    0,15,IINSAVE
         L     7,IINRES
         L     10,IINBASE
         L     4,0(5)
         BCR   15,6
*
*------------------------------------------------------------------
* FINDPARM -- G!39
* Use the original EXEC PARM bytes as an in-memory input stream, up
* to 100 bytes.
*------------------------------------------------------------------
IOPARMST  LR    4,10
         BALR  10,0
         USING *,10
         ST    4,IINBASE
         STM   0,15,IINSAVE
         CLI   PMINIT,X'01'
         BE    PMREADY
         MVI   PMINIT,X'01'
         XC    PMPOS(4),PMPOS
         XC    PMLEN(4),PMLEN
         XC    PMADDR(4),PMADDR
         L     14,IOPARM
         LTR   14,14
         BZ    PMREADY
         L     14,0(14)
         N     14,PMMASK
         LTR   14,14
         BZ    PMREADY
         LH    3,0(14)
         LTR   3,3
         BNP   PMREADY
         C     3,PMMAX
         BNH   PMSET
         LA    3,100
PMSET    ST    3,PMLEN
         LA    14,2(14)
         ST    14,PMADDR
PMREADY  LM    0,15,IINSAVE
         LA    7,PMCTRL
         SRL   7,2
         L     10,IINBASE
         L     4,0(5)
         BCR   15,6
*
*------------------------------------------------------------------
* INPUT -- G!16
* Return the currently selected input handle.
*------------------------------------------------------------------
IOINP      LR    4,10
         BALR  10,0
         USING *,10
         ST    4,IINBASE
         L     7,INCURR
         L     10,IINBASE
         L     4,0(5)
         BCR   15,6
*
*------------------------------------------------------------------
* SELECTINPUT -- G!11
* Select an input handle. Keep each stream's record cursor and EOF
* state separate.
*------------------------------------------------------------------
IOSELIN    LR    4,10
         BALR  10,0
         USING *,10
         ST    4,IINBASE
         STM   0,15,IINSAVE
         LA    14,PMCTRL
         SRL   14,2
         CR    7,14
         BE    SELPM
         LA    14,IN2CTRL
         SRL   14,2
         CR    7,14
         BE    SEL2IN
         LA    14,INCTRL
         SRL   14,2
         CR    7,14
         BNE   SELDYN
         ST    7,INCURR
         B     SELIRET
SELDYN   LR    9,10
         LR    1,7
         L     15,=A(HLOOK)
         BALR  14,15
         LR    10,9
         LTR   15,15
         BZ    SELIRET
         CLI   7(15),X'01'
         BNE   SELIRET
         CLI   27(15),X'01'
         BNE   SELIRET
         ST    7,INCURR
         B     SELIRET
SELPM    ST    7,INCURR
         B     SELIRET
SEL2IN   ST    7,INCURR
SELIRET  LM    0,15,IINSAVE
         L     10,IINBASE
         L     4,0(5)
         BCR   15,6
*
*------------------------------------------------------------------
* RDCH -- G!13
* Read the next byte. Make record boundaries into newlines and
* return the end-of-stream value at EOF.
*------------------------------------------------------------------
IORDCH    LR    4,10
         BALR  10,0
         USING *,10
         ST    4,IINBASE
         STM   0,15,IINSAVE
         L     14,INCURR
         LTR   14,14
         BZ    RDEND
         LA    3,PMCTRL
         SRL   3,2
         CR    14,3
         BE    RDPM
         LA    3,IN2CTRL
         SRL   3,2
         CR    14,3
         BE    RD2START
         LA    3,INCTRL
         SRL   3,2
         CR    14,3
         BNE   RDYDYN
         CLI   INPUSH,X'01'
         BE    RDPUSH
         CLI   INEOF,X'01'
         BE    RDEND
         L     14,INPOS
         C     14,INRECLEN
         BL    RDGETCH
         CLI   INNL,X'01'
         BE    RDNEWLN
         GET   BCPIN,INBUF
         LA    14,80
         LA    3,INBUF+79
RDTRIM   LTR   14,14
         BZ    RDTRMDN
         CLI   0(3),C' '
         BNE   RDTRMDN
         BCTR  14,0
         BCTR  3,0
         B     RDTRIM
RDTRMDN ST    14,INRECLEN
         XC    INPOS(4),INPOS
         MVI   INNL,X'01'
         LTR   14,14
         BZ    RDNEWLN
         SR    14,14
         B     RDGETCH
RDNEWLN  MVI   INNL,X'00'
         L     14,INRECLEN
         ST    14,INPOS
         LA    7,10
         B     RDRETURN
RDGETCH  LA    3,INBUF
         AR    3,14
         SR    7,7
         IC    7,0(3)
         LA    14,1(14)
         ST    14,INPOS
         B     RDRETURN
RDPUSH   MVI   INPUSH,X'00'
         L     7,INLAST
         B     RDRETURN
RDEND    L     7,INENDVAL
RDRETURN ST    7,IINRES
         ST    7,INLAST
         MVI   INSEEN,X'01'
         LM    0,15,IINSAVE
         L     7,IINRES
         L     10,IINBASE
         L     4,0(5)
         BCR   15,6
*
*------------------------------------------------------------------
* READ FROM EXEC PARM
* Read the in-memory parameter bytes, then one newline, then EOF.
* Keep independent pushback state.
*------------------------------------------------------------------
RDPM     CLI   PMPUSH,X'01'
         BE    RDPMPUSH
         L     14,PMPOS
         C     14,PMLEN
         BL    RDPMCHAR
         CLI   PMNL,X'01'
         BE    RDPMEOF
         MVI   PMNL,X'01'
         LA    7,10
         B     RDPMRET
RDPMCHAR L     3,PMADDR
         AR    3,14
         SR    7,7
         IC    7,0(3)
         LA    14,1(14)
         ST    14,PMPOS
         B     RDPMRET
RDPMPUSH MVI   PMPUSH,X'00'
         L     7,PMLAST
         B     RDPMRET
RDPMEOF  L     7,INENDVAL
RDPMRET  ST    7,IINRES
         ST    7,PMLAST
         MVI   PMSEEN,X'01'
         LM    0,15,IINSAVE
         L     7,IINRES
         L     10,IINBASE
         L     4,0(5)
         BCR   15,6
*
*------------------------------------------------------------------
* SECOND BUILT-IN INPUT STREAM
* BCPINB has a separate DCB, buffer, record cursor, pushback byte
* and EOF flag.
*------------------------------------------------------------------
RD2START CLI   IN2PUSH,X'01'
         BE    RD2PUSH
         CLI   IN2EOF,X'01'
         BE    RD2END
         L     14,IN2POS
         C     14,IN2LEN
         BL    RD2CHAR
         CLI   IN2NL,X'01'
         BE    RD2NL
         GET   BCPIN2,IN2BUF
         LA    14,80
         LA    3,IN2BUF+79
RD2TRIM  LTR   14,14
         BZ    RD2TDONE
         CLI   0(3),C' '
         BNE   RD2TDONE
         BCTR  14,0
         BCTR  3,0
         B     RD2TRIM
RD2TDONE ST    14,IN2LEN
         XC    IN2POS(4),IN2POS
         MVI   IN2NL,X'01'
         LTR   14,14
         BZ    RD2NL
         SR    14,14
         B     RD2CHAR
RD2NL    MVI   IN2NL,X'00'
         L     14,IN2LEN
         ST    14,IN2POS
         LA    7,10
         B     RD2RET
RD2CHAR  LA    3,IN2BUF
         AR    3,14
         SR    7,7
         IC    7,0(3)
         LA    14,1(14)
         ST    14,IN2POS
         B     RD2RET
RD2PUSH  MVI   IN2PUSH,X'00'
         L     7,IN2LAST
         B     RD2RET
RD2END   L     7,INENDVAL
RD2RET   ST    7,IINRES
         ST    7,IN2LAST
         MVI   IN2SEEN,X'01'
         LM    0,15,IINSAVE
         L     7,IINRES
         L     10,IINBASE
         L     4,0(5)
         BCR   15,6
*
*------------------------------------------------------------------
* READ FROM A DYNAMIC INPUT STREAM
* Fetch FB80 records through the stream's own QSAM DCB and
* descriptor.
*------------------------------------------------------------------
RDYDYN   LR    9,10
         LR    1,14
         L     15,=A(HLOOK)
         BALR  14,15
         LR    10,9
         LTR   15,15
         BZ    RDEND
         CLI   7(15),X'01'
         BNE   RDEND
         CLI   27(15),X'01'
         BNE   RDEND
         LR    2,15
         L     3,16(2)
         CLI   245(3),X'01'
         BE    RDYPUSH
         CLI   247(3),X'01'
         BE    RDYEOF
         L     14,236(3)
         C     14,240(3)
         BL    RDYCHAR
         CLI   244(3),X'01'
         BE    RDYNL
         ST    2,INDESC
         L     1,20(2)
         LR    0,3
         GET   (1),(0)
         L     2,INDESC
         L     3,16(2)
         LA    14,80
         LA    2,79(3)
RDYTRIM  LTR   14,14
         BZ    RDYTRDN
         CLI   0(2),C' '
         BNE   RDYTRDN
         BCTR  14,0
         BCTR  2,0
         B     RDYTRIM
RDYTRDN  ST    14,240(3)
         XC    236(4,3),236(3)
         MVI   244(3),X'01'
         LTR   14,14
         BZ    RDYNL
         SR    14,14
         B     RDYCHAR
RDYCHAR  LA    2,0(3,14)
         SR    7,7
         IC    7,0(2)
         LA    14,1(14)
         ST    14,236(3)
         B     RDYRET
RDYNL    MVI   244(3),X'00'
         L     14,240(3)
         ST    14,236(3)
         LA    7,10
         B     RDYRET
RDYPUSH  MVI   245(3),X'00'
         L     7,248(3)
         B     RDYRET
RDYEOF   L     7,INENDVAL
RDYRET   ST    7,248(3)
         MVI   246(3),X'01'
         B     RDRETURN
*
*------------------------------------------------------------------
* DYNAMIC INPUT END-OF-DATA
* Set the descriptor EOF flag when QSAM reaches its EODAD exit.
*------------------------------------------------------------------
INDYEOD  L     2,INDESC
         L     3,16(2)
         MVI   247(3),X'01'
         B     RDYEOF
*
*------------------------------------------------------------------
* UNRDCH -- G!15
* Allow the last character to be returned once more by the selected
* input stream.
*------------------------------------------------------------------
IOUNRD   LR    4,10
         BALR  10,0
         USING *,10
         ST    4,IINBASE
         STM   0,15,IINSAVE
         L     14,INCURR
         LA    3,PMCTRL
         SRL   3,2
         CR    14,3
         BE    UNRDPM
         LA    3,IN2CTRL
         SRL   3,2
         CR    14,3
         BE    UNRD2
         LA    3,INCTRL
         SRL   3,2
         CR    14,3
         BNE   UNRDYN
         CLI   INSEEN,X'01'
         BNE   UNRDRET
         MVI   INPUSH,X'01'
         B     UNRDRET
UNRDPM   CLI   PMSEEN,X'01'
         BNE   UNRDRET
         MVI   PMPUSH,X'01'
         B     UNRDRET
UNRD2    CLI   IN2SEEN,X'01'
         BNE   UNRDRET
         MVI   IN2PUSH,X'01'
         B     UNRDRET
UNRDYN   LR    9,10
         LR    1,14
         L     15,=A(HLOOK)
         BALR  14,15
         LR    10,9
         LTR   15,15
         BZ    UNRDRET
         CLI   7(15),X'01'
         BNE   UNRDRET
         L     3,16(15)
         CLI   246(3),X'01'
         BNE   UNRDRET
         MVI   245(3),X'01'
UNRDRET  LM    0,15,IINSAVE
         L     10,IINBASE
         L     4,0(5)
         BCR   15,6
*
*------------------------------------------------------------------
* ENDREAD -- G!46
* Close and deselect the current input stream. Release a dynamic
* descriptor when needed.
*------------------------------------------------------------------
IOENDRD  LR    4,10
         BALR  10,0
         USING *,10
         ST    4,IINBASE
         STM   0,15,IINSAVE
         L     14,INCURR
         LA    3,PMCTRL
         SRL   3,2
         CR    14,3
         BE    ENDRPM
         LA    3,IN2CTRL
         SRL   3,2
         CR    14,3
         BE    ENDR2
         LA    3,INCTRL
         SRL   3,2
         CR    14,3
         BNE   ENRDYN
         L     14,INCURR
         LTR   14,14
         BZ    ENDRDONE
         CLI   INOPEN,X'01'
         BNE   ENDRCLR
         CLOSE (BCPIN)
         MVI   INOPEN,X'00'
ENDRCLR  XC    INCURR(4),INCURR
         MVI   INEOF,X'00'
         MVI   INNL,X'00'
         MVI   INPUSH,X'00'
         MVI   INSEEN,X'00'
         MVC   INPOS(4),ININIT
         B     ENDRDONE
ENDRPM   XC    INCURR(4),INCURR
         XC    PMPOS(4),PMPOS
         MVI   PMNL,X'00'
         MVI   PMPUSH,X'00'
         MVI   PMSEEN,X'00'
         B     ENDRDONE
ENDR2    CLI   IN2OPEN,X'01'
         BNE   ENDR2CLR
         CLOSE (BCPIN2)
         MVI   IN2OPEN,X'00'
ENDR2CLR XC    INCURR(4),INCURR
         MVI   IN2EOF,X'00'
         MVI   IN2PUSH,X'00'
         MVI   IN2SEEN,X'00'
         B     ENDRDONE
ENRDYN   LR    9,10
         L     1,INCURR
         L     15,=A(HLOOK)
         BALR  14,15
         LR    10,9
         LTR   15,15
         BZ    ENRDCLR
         CLI   7(15),X'01'
         BNE   ENRDCLR
         ST    15,INDESC
         LR    1,15
         L     15,=A(DQCLOSE)
         BALR  14,15
         LR    10,9
         L     1,INCURR
         L     15,=A(HCLOSE)
         BALR  14,15
         LR    10,9
         L     1,INDESC
         L     15,=A(DREL)
         BALR  14,15
         LR    10,9
ENRDCLR  XC    INCURR(4),INCURR
ENDRDONE EQU   *
         LM    0,15,IINSAVE
         L     10,IINBASE
         L     4,0(5)
         BCR   15,6
         DROP  10
         USING IORDCH+4,10
*
*------------------------------------------------------------------
* BUILT-IN INPUT END-OF-DATA
* QSAM EODAD exits set EOF flags for BCPINB and BCPIN.
*------------------------------------------------------------------
IN2ATEND MVI   IN2EOF,X'01'
         B     RD2END
INATEND  MVI   INEOF,X'01'
         B     RDEND
         DROP  10
         DS    0F
*
*------------------------------------------------------------------
* INPUT STREAM STATE
* Keep EXEC PARM, built-in input buffers, current input, pushback
* and EOF controls.
*------------------------------------------------------------------
IINBASE  DC    F'0'
IINR3    DC    F'0'
INDESC   DC    F'0'
PMMASK   DC    X'7FFFFFFF'
PMMAX    DC    F'100'
PMCTRL   DC    F'3'
PMINIT   DC    X'00'
PMNL     DC    X'00'
PMPUSH   DC    X'00'
PMSEEN   DC    X'00'
PMPOS    DC    F'0'
PMLEN    DC    F'0'
PMADDR   DC    F'0'
PMLAST   DC    F'0'
         DS    0F
IN2CTRL  DC    F'2'
IN2NAME  DC    CL6'BCPINB'
IN2OPEN  DC    X'00'
IN2EOF   DC    X'00'
IN2NL    DC    X'00'
IN2PUSH  DC    X'00'
IN2SEEN  DC    X'00'
         DS    0F
IN2POS   DC    F'80'
IN2LEN   DC    F'80'
IN2LAST  DC    F'0'
IN2BUF   DS    CL80
BCPIN2   DCB   DDNAME=BCPINB,DSORG=PS,MACRF=GM,EODAD=IN2ATEND
INCTRL   DC    F'1'
INCURR DC   F'0'
INRECLEN DC    F'80'
INNL     DC    X'00'
INPUSH   DC    X'00'
INSEEN   DC    X'00'
         DS    0F
INLAST   DC    F'0'
INENDVAL DC    F'-1'
INPOS    DC    F'80'
ININIT   DC    F'80'
INNAME   DC    CL5'BCPIN'
INOPEN   DC    X'00'
INEOF    DC    X'00'
         DS    0F
IINRES DC    F'0'
IINSAVE   DS    16F
INBUF    DS    CL80
BCPIN    DCB   DDNAME=BCPIN,DSORG=PS,MACRF=GM,EODAD=INATEND

         DS    0F
IOPARM   DC    F'0'
IOOBASE  DC    F'0'
IODRC    DC    F'0'
IOCTL1   DC    F'1'
IOCTL2   DC    F'2'
IOCURH   DC    F'0'
IORESULT DC    F'0'
IOWDESC  DC    F'0'
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
IOESAVE  DS    16F
IOOSAVE  DS    16F
IODSAVE  DS    16F
IOBUF    DS    CL132
IODCB    DCB   DDNAME=SYSPRINT,DSORG=PS,MACRF=PM
IO2BUF   DS    CL132
IO2DCB   DCB   DDNAME=BCPALT,DSORG=PS,MACRF=PM
         ENTRY IO2PTR
*
*------------------------------------------------------------------
* PRIVATE OUTPUT DCB INSPECTION
* Return an internal pointer to the alternate output DCB's PUT exit
* field.
*------------------------------------------------------------------
IO2PTR   BALR  10,0
         USING *,10
         L     1,=A(IO2DCB)
         L     15,48(1)
         BR    14
         LTORG
         DROP  10
         ENTRY DALLOC,DREL
*
*------------------------------------------------------------------
* DYNAMIC STREAM DESCRIPTORS
* Allocate a private QSAM descriptor, buffer and DD name. Each
* descriptor has its own GETMAIN lifetime.
*------------------------------------------------------------------
DALLOC   BALR  10,0
         USING *,10
         STM   0,9,DSAVE
         STM   11,14,DSAVE+44
         ST    2,DNAMEP
         ST    3,DTYPE
         GETMAIN RC,LV=32
         LTR   15,15
         BNZ   DALFAIL
         LR    6,1
         XC    0(32,6),0(6)
         L     7,DHEAD
         ST    7,0(6)
         L     7,DTYPE
         ST    7,4(6)
         L     7,DNAMEP
         MVC   8(8,6),0(7)
         GETMAIN RC,LV=268
         LTR   15,15
         BNZ   DALNOMEM
         LR    8,1
         XC    0(256,8),0(8)
         XC    256(12,8),256(8)
         CLI   DTYPE+3,X'01'
         BNE   DALOUT
         MVC   132(96,8),DQTIN
         LA    7,80
         ST    7,236(8)
         ST    7,240(8)
         B     DALDCB
DALOUT   MVC   132(96,8),DQTEMP
DALDCB   MVC   172(8,8),8(6)
         MVI   0(8),C' '
         MVC   1(131,8),0(8)
         LA    7,132(8)
         STCM  7,7,229(8)
         STCM  7,7,233(8)
         MVI   228(8),X'8F'
         CLI   DTYPE+3,X'01'
         BNE   DALOMODE
         MVI   228(8),X'80'
DALOMODE MVI   232(8),X'80'
         ST    8,16(6)
         ST    7,20(6)
         ST    6,DHEAD
         ST    6,DRESULT
         B     DALRET
DALNOMEM LR    1,6
         FREEMAIN R,LV=32,A=(1)
DALFAIL  XC    DRESULT(4),DRESULT
DALRET   LM    0,9,DSAVE
         LM    11,14,DSAVE+44
         L     15,DRESULT
         BR    14
         DROP  10
*
*------------------------------------------------------------------
* RELEASE A DYNAMIC DESCRIPTOR
* Unlink a closed descriptor and return its GETMAIN storage.
*------------------------------------------------------------------
DREL     BALR  10,0
         USING *,10
         STM   0,9,DSAVE
         STM   11,14,DSAVE+44
         ST    1,DTARGET
         LA    6,DHEAD
DRELSCAN L     7,0(6)
         LTR   7,7
         BZ    DRELBAD
         C     7,DTARGET
         BE    DRELHIT
         LR    6,7
         B     DRELSCAN
DRELHIT  L     8,24(7)
         LTR   8,8
         BNZ   DRELBAD
         L     8,0(7)
         ST    8,0(6)
         L     1,16(7)
         FREEMAIN R,LV=268,A=(1)
         L     1,DTARGET
         FREEMAIN R,LV=32,A=(1)
         XC    DRESULT(4),DRESULT
         B     DRELRET
DRELBAD  MVC   DRESULT(4),DERR8
DRELRET  LM    0,9,DSAVE
         LM    11,14,DSAVE+44
         L     15,DRESULT
         BR    14
         DROP  10
         DS    0F
DHEAD    DC    F'0'
DNAMEP   DC    F'0'
DTYPE    DC    F'0'
DTARGET  DC    F'0'
DRESULT  DC    F'0'
DERR8    DC    F'8'
DSAVE    DS    16F
         ENTRY DQOPEN,DQPUT,DQCLOSE
*
*------------------------------------------------------------------
* DYNAMIC QSAM OPERATIONS
* Open, write and close a descriptor's QSAM DCB. Helpers return
* status codes.
*------------------------------------------------------------------
DQOPEN   BALR  10,0
         USING *,10
         STM   0,9,DQSAVE
         STM   11,14,DQSAVE+44
         ST    1,DQARG
         LTR   1,1
         BZ    DQBAD
         L     6,16(1)
         LTR   6,6
         BZ    DQBAD
         L     7,24(1)
         LTR   7,7
         BNZ   DQBAD
         LA    1,228(6)
         SVC   19
         L     1,DQARG
         L     7,20(1)
         L     7,48(7)
         LTR   7,7
         BZ    DQBAD
         L     1,DQARG
         LA    7,1
         ST    7,24(1)
         B     DQGOOD
         DROP  10
DQPUT    BALR  10,0
         USING *,10
         STM   0,9,DQSAVE
         STM   11,14,DQSAVE+44
         ST    1,DQARG
         ST    2,DQSRC
         LTR   1,1
         BZ    DQBAD
         L     7,24(1)
         LTR   7,7
         BZ    DQBAD
         L     6,16(1)
         LTR   6,6
         BZ    DQBAD
         L     7,DQSRC
         MVC   0(132,6),0(7)
         L     1,20(1)
         LR    0,6
         L     15,48(1)
         BALR  14,15
         B     DQGOOD
         DROP  10
DQCLOSE  BALR  10,0
         USING *,10
         STM   0,9,DQSAVE
         STM   11,14,DQSAVE+44
         ST    1,DQARG
         LTR   1,1
         BZ    DQBAD
         L     7,24(1)
         LTR   7,7
         BZ    DQBAD
         L     6,16(1)
         LA    1,232(6)
         SVC   20
         L     1,DQARG
         XC    24(4,1),24(1)
         B     DQGOOD
         DROP  10
DQGOOD   BALR  10,0
         USING *,10
         SR    15,15
         B     DQRET
         DROP  10
DQBAD    LA    15,8
DQRET    BALR  10,0
         USING *,10
         ST    15,DQRESULT
         LM    0,9,DQSAVE
         LM    11,14,DQSAVE+44
         L     15,DQRESULT
         BR    14
         DROP  10
         DS    0F
DQARG    DC    F'0'
DQSRC    DC    F'0'
DQRESULT DC    F'0'
DQSAVE   DS    16F
DQTEMP   DCB   DDNAME=DUMMY,DSORG=PS,MACRF=PM
DQTIN    DCB   DDNAME=DUMMY,DSORG=PS,MACRF=GM,EODAD=INDYEOD
         ENTRY DQFIND
*
*------------------------------------------------------------------
* FIND A DYNAMIC OUTPUT DD
* Normalize the caller's name, check the allocation, and reuse an
* existing live handle when possible.
*------------------------------------------------------------------
DQFIND   BALR  11,0
         USING *,11
         STM   0,10,DFFSAV
         STM   12,14,DFFSAV+48
         ST    1,DFFARG
         LA    2,DFFNAME
         L     15,=A(IONORM)
         BALR  14,15
         LTR   15,15
         BNZ   DFFBAD
         LA    1,DFFNAME
         LA    2,2
         L     15,=A(HACTIVE)
         BALR  14,15
         LTR   15,15
         BZ    DFFNEW
         ST    15,DFFRES
         B     DFFRET
DFFNEW   LA    1,DFFNAME
         L     15,=A(DDVERIFY)
         BALR  14,15
         LTR   15,15
         BNZ   DFFBAD
         LA    2,DFFNAME
         LA    3,2
         L     15,=A(DALLOC)
         BALR  14,15
         LTR   15,15
         BZ    DFFBAD
         ST    15,DFFDESC
         LR    1,15
         L     15,=A(DQOPEN)
         BALR  14,15
         LTR   15,15
         BNZ   DFFCLEAN
         L     1,DFFDESC
         L     15,=A(HNEW)
         BALR  14,15
         LTR   15,15
         BZ    DFFCLOSE
         ST    15,DFFRES
         B     DFFRET
DFFCLOSE L     1,DFFDESC
         L     15,=A(DQCLOSE)
         BALR  14,15
DFFCLEAN L     1,DFFDESC
         L     15,=A(DREL)
         BALR  14,15
DFFBAD   XC    DFFRES(4),DFFRES
DFFRET   LM    0,10,DFFSAV
         LM    12,14,DFFSAV+48
         L     15,DFFRES
         BR    14
         LTORG
         DROP  11
         DS    0F
DFFNAME  DC    CL8'        '
DFFARG   DC    F'0'
DFFDESC  DC    F'0'
DFFRES DC   F'0'
DFFSAV   DS    16F
         ENTRY HNEW,HLOOK,HCLOSE
*
*------------------------------------------------------------------
* STABLE STREAM HANDLES
* Create a handle record that is not reused during this execution.
* A closed handle becomes a tombstone.
*------------------------------------------------------------------
HNEW     BALR  10,0
         USING *,10
         STM   0,9,HSAVE
         STM   11,14,HSAVE+44
         ST    1,HDESC
         LTR   1,1
         BZ    HNEWBAD
         GETMAIN RC,LV=16
         LTR   15,15
         BNZ   HNEWBAD
         LR    6,1
         XC    0(16,6),0(6)
         L     7,HHEAD
         ST    7,0(6)
         L     7,HDESC
         ST    7,4(6)
         ST    6,HHEAD
         LA    7,4(6)
         SRL   7,2
         ST    7,HRESULT
         B     HRETURN
HNEWBAD  XC    HRESULT(4),HRESULT
HRETURN  LM    0,9,HSAVE
         LM    11,14,HSAVE+44
         L     15,HRESULT
         BR    14
         DROP  10
*
*------------------------------------------------------------------
* LOOK UP A STREAM HANDLE
* Resolve a valid handle to its live descriptor.
*------------------------------------------------------------------
HLOOK    BALR  10,0
         USING *,10
         STM   0,9,HSAVE
         STM   11,14,HSAVE+44
         ST    1,HTARGET
         L     6,HHEAD
HLNEXT   LTR   6,6
         BZ    HLMISS
         LA    7,4(6)
         SRL   7,2
         C     7,HTARGET
         BE    HLFOUND
         L     6,0(6)
         B     HLNEXT
HLFOUND  L     7,4(6)
         ST    7,HRESULT
         B     HLRET
HLMISS   XC    HRESULT(4),HRESULT
HLRET    LM    0,9,HSAVE
         LM    11,14,HSAVE+44
         L     15,HRESULT
         BR    14
         DROP  10
*
*------------------------------------------------------------------
* CLOSE A HANDLE IDENTITY
* Mark a handle as closed while keeping its identity reserved.
*------------------------------------------------------------------
HCLOSE   BALR  10,0
         USING *,10
         STM   0,9,HSAVE
         STM   11,14,HSAVE+44
         ST    1,HTARGET
         L     6,HHEAD
HCNEXT   LTR   6,6
         BZ    HCMISS
         LA    7,4(6)
         SRL   7,2
         C     7,HTARGET
         BE    HCFOUND
         L     6,0(6)
         B     HCNEXT
HCFOUND  L     7,4(6)
         ST    7,HRESULT
         XC    4(4,6),4(6)
         B     HCRET
HCMISS   XC    HRESULT(4),HRESULT
HCRET    LM    0,9,HSAVE
         LM    11,14,HSAVE+44
         L     15,HRESULT
         BR    14
         DROP  10
         DS    0F
HHEAD    DC    F'0'
HDESC    DC    F'0'
HTARGET  DC    F'0'
HRESULT  DC    F'0'
HSAVE    DS    16F
*
*------------------------------------------------------------------
* MATCH AN ACTIVE DD STREAM
* Find a live stream with the same normalized DD name and
* direction.
*------------------------------------------------------------------
HACTIVE  BALR  10,0
         USING *,10
         STM   0,9,HASAVE
         STM   11,14,HASAVE+44
         LR    7,1
         MVC   HAKEY(8),0(7)
         ST    2,HADIR
         L     1,=A(HHEAD)
         L     6,0(1)
HANEXT   LTR   6,6
         BZ    HAMISS
         L     8,4(6)
         LTR   8,8
         BZ    HASKIP
         L     7,4(8)
         C     7,HADIR
         BNE   HASKIP
         L     7,24(8)
         LTR   7,7
         BZ    HASKIP
         CLC   8(8,8),HAKEY
         BNE   HASKIP
         LA    7,4(6)
         SRL   7,2
         ST    7,HARES
         B     HARET
HASKIP   L     6,0(6)
         B     HANEXT
HAMISS   XC    HARES(4),HARES
HARET    LM    0,9,HASAVE
         LM    11,14,HASAVE+44
         L     15,HARES
         BR    14
         DROP  10
         DS    0F
HAKEY    DC    CL8'        '
HADIR    DC    F'0'
HARES    DC    F'0'
HASAVE   DS    16F
         ENTRY DIFIND
*
*------------------------------------------------------------------
* FIND A DYNAMIC INPUT DD
* Normalize and verify the DD, then obtain or reuse its input
* descriptor and handle.
*------------------------------------------------------------------
DIFIND   BALR  11,0
         USING *,11
         STM   0,10,DIFSAV
         STM   12,14,DIFSAV+48
         LA    2,DIFNAME
         L     15,=A(IONORM)
         BALR  14,15
         LTR   15,15
         BNZ   DIFBAD
         LA    1,DIFNAME
         LA    2,1
         L     15,=A(HACTIVE)
         BALR  14,15
         LTR   15,15
         BZ    DIFNEW
         ST    15,DIFRES
         B     DIFRET
DIFNEW   LA    1,DIFNAME
         L     15,=A(DDVERIFY)
         BALR  14,15
         LTR   15,15
         BNZ   DIFBAD
         LA    2,DIFNAME
         LA    3,1
         L     15,=A(DALLOC)
         BALR  14,15
         LTR   15,15
         BZ    DIFBAD
         ST    15,DIFDESC
         LR    1,15
         L     15,=A(DQOPEN)
         BALR  14,15
         LTR   15,15
         BNZ   DIFCLEAN
         L     1,DIFDESC
         L     15,=A(HNEW)
         BALR  14,15
         LTR   15,15
         BZ    DIFCLOSE
         ST    15,DIFRES
         B     DIFRET
DIFCLOSE L     1,DIFDESC
         L     15,=A(DQCLOSE)
         BALR  14,15
DIFCLEAN L     1,DIFDESC
         L     15,=A(DREL)
         BALR  14,15
DIFBAD   XC    DIFRES(4),DIFRES
DIFRET   LM    0,10,DIFSAV
         LM    12,14,DIFSAV+48
         L     15,DIFRES
         BR    14
         LTORG
         DROP  11
         DS    0F
DIFNAME  DC    CL8'        '
DIFDESC  DC    F'0'
DIFRES   DC    F'0'
DIFSAV   DS    16F
         ENTRY DDVERIFY
*
*------------------------------------------------------------------
* CHECK JCL DD ALLOCATION
* Use RDJFCB to confirm a DD exists before opening its QSAM DCB.
*------------------------------------------------------------------
DDVERIFY BALR  10,0
         USING *,10
         STM   0,9,DVSAVE
         STM   11,14,DVSAVE+44
         LR    7,1
         MVC   DVDCB+40(8),0(7)
         LA    2,DVDCB
         RDJFCB ((2))
         LTR   15,15
         BZ    DVGOOD
         LA    15,8
         B     DVRET
DVGOOD   SR    15,15
DVRET    ST    15,DVRESULT
         LM    0,9,DVSAVE
         LM    11,14,DVSAVE+44
         L     15,DVRESULT
         BR    14
         DROP  10
         DS    0F
DVRESULT DC    F'0'
DVSAVE   DS    16F
DVDCB    DCB   DDNAME=SYSPRINT,DSORG=PS,MACRF=GM,EXLST=DVEXL
         DS    0F
DVEXL    DC    X'87',AL3(DVJFCB)
DVJFCB   DS    CL176
*
*------------------------------------------------------------------
* DRAIN DYNAMIC STREAMS
* Flush buffered output, close QSAM DCBs and release descriptors
* and handle records at shutdown.
*------------------------------------------------------------------
IODRAIN  BALR  11,0
         USING *,11
         STM   0,10,DRSAVE
         STM   12,14,DRSAVE+48
DRAINDS  L     1,=A(DHEAD)
         L     6,0(1)
         LTR   6,6
         BZ    DRAINHS
         ST    6,DRDESC
         L     7,24(6)
         LTR   7,7
         BZ    DRAINFR
         CLI   7(6),X'02'
         BNE   DRAINCL
         L     7,16(6)
         L     7,236(7)
         LTR   7,7
         BZ    DRAINCL
         LR    1,6
         L     2,16(6)
         L     15,=A(DQPUT)
         BALR  14,15
DRAINCL  L     1,DRDESC
         L     15,=A(DQCLOSE)
         BALR  14,15
DRAINFR  L     1,DRDESC
         L     15,=A(DREL)
         BALR  14,15
         B     DRAINDS
DRAINHS  L     1,=A(HHEAD)
         L     6,0(1)
         LTR   6,6
         BZ    DRAINDN
         L     7,0(6)
         ST    7,DRNEXT
         XC    4(4,6),4(6)
         LR    1,6
         FREEMAIN R,LV=16,A=(1)
         L     1,=A(HHEAD)
         L     7,DRNEXT
         ST    7,0(1)
         B     DRAINHS
DRAINDN  LM    0,10,DRSAVE
         LM    12,14,DRSAVE+48
         BR    14
         LTORG
         DROP  11
         DS    0F
DRDESC   DC    F'0'
DRNEXT   DC    F'0'
DRSAVE   DS    16F
         END   BCPLIO
