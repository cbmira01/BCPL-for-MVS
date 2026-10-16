***********************************************************************
* BCPLIO -- INDEPENDENT BCPL STREAM I/O (M2.0 GATE D, D6)
*
* Owns SYSPRINT/BCPALT output and BCPIN/BCPINB input QSAM DCBs,
* buffers, selected handles, PARM pseudo-stream and I/O cleanup.
* G11-17/G33/G39/G41-42/G46-47 services enter this CSECT.
* Private native entry points: IOINIT, IOFIN, IOBIND, IOSTAT,
* IODIAG, IOREPL and IOPMGET. No BCPLMAIN private-data refs.
*
* BCPL entries use R6 return, R7 argument/result and R5 frame;
* R4 is restored from 0(R5). R10 is a private scratch base.
* Native entry contracts and exceptional results are documented in
* packaging/m2-0-d3-bcplio-linkage-contract.md; that document
* includes early candidate history and must be read with Gate D
* closure evidence in m2-0-gate-d-bcplio-extraction-plan.md.
*
* Not reentrant: QSAM and saved registers use static module state.
* Historical-facing behavior is a tested MVS reconstruction,
* not a claim of recovered original Cambridge machine code.
* Accepted independently in DEVOBJ, including D6 regression 00-123:
* 123 PASS, 0 FAIL, 1 expected source-only SKIP (083).
***********************************************************************
BCPLIO   CSECT
         ENTRY IOINIT,IOFIN,IOWRCH,IOSTAT,IOSEL
         ENTRY IOFOUT,IOSOUT,IOOUT,IOWRAP,IOENDW
         ENTRY IOBIND,IODIAG,IOREPL,IOPMGET
         ENTRY IOSELIN,IOINP,IOPARMST,IORDCH,IOUNRD,IOFINDIN
         ENTRY IOENDRD,IONORM
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
* Second base for DCBs beyond first 4K displacement.
* R11 is already saved, and IOFIN restores it at return.
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
IFDPARM  XC    IOPARM(4),IOPARM
         LM    0,9,IOFSAVE
         LM    11,15,IOFSAVE+44
         BR    14
         DROP  11
         DROP  10
*
* BCPL-facing candidate: R7 holds a character code.
* Save caller registers before all output paths, including PUT.
IOWRCH   LR    4,10
         BALR  10,0
         USING *,10
         ST    4,IOSAVE+40
         STM   0,9,IOSAVE
         STM   11,15,IOSAVE+44
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
* Dynamic stream buffer occupies descriptor-owned region +0..131;
* current fill count at region +236. Handle never dereferenced.
IOWDYN   L     1,IOCURH
         L     15,=A(HLOOK)
         BALR  14,15
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
         LTR   15,15
         BNZ   IOWFULL
         L     1,IOCURH
         L     15,=A(HLOOK)
         BALR  14,15
         L     3,16(15)
         XC    236(4,3),236(3)
         MVI   0(3),C' '
         MVC   1(131,3),0(3)
         B     IOWRET
IOWRET   LM    0,9,IOSAVE
         LM    11,15,IOSAVE+44
         L     4,0(5)
         L     10,IOSAVE+40
         BCR   15,6
         LTORG
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
* M1 STAGING: DD-name normalization; not yet wired to FIND.
* Private R14 call: R1=BCPL counted-string byte address,
* R2=eight-byte caller buffer, R15=0 success/8 invalid.
* Uppercase ASCII-like BCPL names in host EBCDIC, then pad.
* R10 clobbered. All other registers preserved except R15.
* MVS DD first character is alphabetic/@/#/$; remaining
* characters may also be decimal digits. Empty or >8 fails.
*
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
* Lowercase EBCDIC a-i, j-r, s-z => uppercase (OR X'40').
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
* All positions allow A-I, J-R, S-Z and @/#/$.
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
* BCPL output-stream ABI. These five entries use R6 linkage, R7
* argument/result, restore R4 from 0(R5), clobber R10.
* Handles are the word addresses of private IOCTL1/IOCTL2.
*
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
* DQFIND returns a word-address stable handle, or zero.
         LR    7,15
* DQFIND uses independent R11 base and preserves caller R10.
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
IOSDYN   LR    1,7
         L     15,=A(HLOOK)
         BALR  14,15
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
* WRAPOUTPUT: only alternate stream emits an empty record on wrap.
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
* ENDWRITE: only alternate; flush/close and revert selection.
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
* ENDWRITE on selected dynamic handle. If buffered, flush first;
* then close, invalidate handle, free descriptor, select primary.
IOEWDYN  L     1,IOCURH
         L     15,=A(HLOOK)
         BALR  14,15
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
IOEDCLOS L     1,IOWDESC
         L     15,=A(DQCLOSE)
         BALR  14,15
         L     1,IOCURH
         L     15,=A(HCLOSE)
         BALR  14,15
         L     1,IOWDESC
         L     15,=A(DREL)
         BALR  14,15
         B     IOEWDONE
IOEWRET  LM    0,9,IOOSAVE
         LM    11,15,IOOSAVE+44
         L     4,0(5)
         L     10,IOOSAVE+40
         BCR   15,6
         LTORG
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
* D4 private native accessor for original EXEC parameter list.
* IOINIT captured R1 once; R15 returns that pointer (possibly zero).
* R14-linked; preserve all registers except R10 and result R15.
IOPMGET  BALR  10,0
         USING *,10
         L     15,IOPARM
         BR    14
         DROP  10
*
* D4 input services, PARM stream, and QSAM EODAD handlers.
* Each external BCPL entry saves caller R10 before selecting the
* independent BCPLIO base. R3 is local scratch on input paths.
* This static implementation is nonreentrant, consistent with BCPLIO.
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
FNOTFND  SR    7,7
FRET     ST    7,IINRES
         LM    0,15,IINSAVE
         L     7,IINRES
         L     10,IINBASE
         L     4,0(5)
         BCR   15,6
*
* G39 opens a dedicated memory stream over the MVS EXEC PARM field.
* R1 on entry to the load module points to the parameter-list word;
* that word addresses the halfword length and following EBCDIC bytes.
* Capture that original pointer before the BCPL startup reuses R1.
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
* D4: retrieve MVS EXEC PARM owner pointer from BCPLIO.
* R9 carries BCPLMAIN base across the private R14 service.
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
* MVS EXEC PARM length is limited to 100 bytes.
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
IOINP      LR    4,10
         BALR  10,0
         USING *,10
         ST    4,IINBASE
         L     7,INCURR
         L     10,IINBASE
         L     4,0(5)
         BCR   15,6
*
IOSELIN    LR    4,10
         BALR  10,0
         USING *,10
         ST    4,IINBASE
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
         BNE   SELIRET
         ST    7,INCURR
         B     SELIRET
SELPM    ST    7,INCURR
         B     SELIRET
SEL2IN   ST    7,INCURR
SELIRET  L     10,IINBASE
         L     4,0(5)
         BCR   15,6
*
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
* Trim fixed-record padding; blanks inside records remain data.
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
* EXEC PARM stream: bytes, one newline, EOF. A private pushback slot
* prevents UNRDCH on the PARM stream altering either QSAM stream.
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
* Second input DCB has independent record, pushback, and EOF state.
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
* UNRDCH repeats the last RDCH result once for this selected stream.
IOUNRD   LR    4,10
         BALR  10,0
         USING *,10
         ST    4,IINBASE
         ST    3,IINR3
         L     14,INCURR
         LA    3,PMCTRL
         SRL   3,2
         CR    14,3
         BE    UNRDPM
         LA    3,IN2CTRL
         SRL   3,2
         CR    14,3
         BE    UNRD2
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
UNRDRET  L     3,IINR3
         L     10,IINBASE
         L     4,0(5)
         BCR   15,6
*
* ENDREAD closes the selected BCPIN input stream and clears state.
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
ENDRDONE EQU   *
         LM    0,15,IINSAVE
         L     10,IINBASE
         L     4,0(5)
         BCR   15,6
*
* EODAD receives control from QSAM GET during IORDCH.
* Runtime R10 still addresses the IORDCH-local base after GET;
* use that explicit USING rather than IOENDRD's later base.
         DROP  10
         USING IORDCH+4,10
IN2ATEND MVI   IN2EOF,X'01'
         B     RD2END
INATEND  MVI   INEOF,X'01'
         B     RDEND
         DROP  10
*
         DS    0F
IINBASE  DC    F'0'
IINR3    DC    F'0'
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
*
* One-stream bootstrap input controls for native regression 094.
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

*
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
*
* M1 PRIVATE DIAGNOSTIC ONLY. IO2PTR R15=IO2DCB+48 contents.
* Read-only snapshot of QSAM PUT exit pointer; R1/R10 clobbered.
* Never called from BCPL entry points or normal I/O paths.
         ENTRY IO2PTR
IO2PTR   BALR  10,0
         USING *,10
         L     1,=A(IO2DCB)
         L     15,48(1)
         BR    14
         LTORG
         DROP  10
*
* M1 PRIVATE DESCRIPTOR REGISTRY (NOT WIRED TO FIND).
* DALLOC: R2=normalized 8-byte DD name, R3=direction 1/2.
*         R15=allocated descriptor byte address or zero.
* DREL:   R1=descriptor byte address; R15=0 success/8 absent.
* Native R14 linkage, R10 clobbered; static and nonreentrant.
* Descriptor: +0 next, +4 direction, +8 name, +16 owned 268-byte
* QSAM region, +20 DCB, +24 state, +28 reserved.
* The descriptor is NOT a BCPL stream handle. It must never
* escape to the BCPL program: stable handles come separately.
* DALLOC allocates an unopened DCB+buffer region; DREL releases it.
* OPEN/PUT/CLOSE are separate private DQ* calls (output only).
*
         ENTRY DALLOC,DREL
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
* Own 268 bytes: buffer 0..131, DCB 132..227,
* SVC19 list 228..231, SVC20 list 232..235.
         GETMAIN RC,LV=268
         LTR   15,15
         BNZ   DALNOMEM
         LR    8,1
         XC    0(256,8),0(8)
         XC    256(12,8),256(8)
         MVC   132(96,8),DQTEMP
         MVC   172(8,8),8(6)
         MVI   0(8),C' '
         MVC   1(131,8),0(8)
         LA    7,132(8)
         STCM  7,7,229(8)
         STCM  7,7,233(8)
         MVI   228(8),X'8F'
         MVI   232(8),X'80'
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
*
* Private QSAM stream operations: R1=descriptor byte pointer.
* Only callers holding an active descriptor may invoke these;
* output DD is assigned by JCL, FB132. R15 0 success/8 invalid.
* DQPUT: R2 -> complete 132-byte record.
* DQOPEN and DQCLOSE update descriptor +24 open state.
* Uses DQ-owned save area; not reentrant.
         ENTRY DQOPEN,DQPUT,DQCLOSE
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
* The +24 open-state is a fullword.
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
*
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
*
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
*
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
*
* M1 programmer-visible FINDOUTPUT dynamic fallback.
* R1 = BCPL counted string byte address, R15 = stable handle or 0.
* R11 is local base, R14 is call return; nested private helpers
* preserve R11 and R14. Native R10 remains caller-owned here.
* DDVERIFY confirms JCL DD allocation before QSAM OPEN.
* No selection, WRCH or ENDWRITE wiring at this gate.
         ENTRY DQFIND
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
*
* M1 PRIVATE NON-REUSED HANDLE IDENTITIES (NOT WIRED TO FIND).
* HNEW R1=descriptor, R15=BCPL word-address handle or 0.
* HLOOK R1=handle, R15=live descriptor or 0.
* HCLOSE R1=handle, R15=detached descriptor or 0.
* Caller must DREL a nonzero HCLOSE result; HCLOSE itself
* only invalidates the stable handle record. Tombstones are
* retained until IOFIN cleanup is subsequently implemented.
* The public handle names the fullword at record offset +4.
* NEVER dereference the caller-provided handle before search.
*
         ENTRY HNEW,HLOOK,HCLOSE
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
* M1 DD ALLOCATION INQUIRY (PRIVATE, NOT WIRED TO FIND).
* R1 -> normalized EBCDIC CL8 DD name; R15 0 allocated,
* 8 otherwise. Nonreentrant: separate unopened scratch DCB.
* This inquiry does not OPEN the DD, or allocate a stream.
* JFCB exit list + 176-byte area are required by RDJFCB.
* RDJFCB uses the DCB at R2; the offset of the DDNAME
* field is verified against the IFOX DCB macro expansion.
*
         ENTRY DDVERIFY
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
         END   BCPLIO
