*===================================================================
* BCPLMAIN -- NATIVE BCPL PROGRAM STARTUP AND SYSTEM SERVICES
*
* PURPOSE
* Enter a CG370-compiled BCPL program under MVS, prepare its global
* vector and stack, connect the other runtime modules, call START,
* and return a completion code to MVS.
*
* MODULE ROLES
* BCPLMAIN Program startup, system vector, global setup, exit.
* BCPLMEM GETVEC, FREEVEC, allocation cleanup and counts.
* BCPLBYTE GETBYTE and PUTBYTE.
* BCPLAPT APTOVEC temporary stack workspace.
* BCPLIO BCPL stream I/O and QSAM resource cleanup.
* BLIB BCPL-written formatting and library procedures.
*
* CG370 CALL CONVENTIONS
* R0 Remains zero while BCPL code is running.
* R1-R3 Address constants 4096, 8192, 12288.
* R4 Current procedure entry address.
* R5 Current BCPL workspace (P), in byte units.
* R6 Return address for BCPL calls.
* R7-R10 First four arguments; R7 also holds the result.
* R11 System vector (S).
* R12 Global vector (G).
* R15 Next workspace (W) on a BCPL call.
* BCPL pointers are word addresses. Shift left two bits when
* turning one into a System/370 byte address.
*
* COMPILED MODULE FORMAT
* A compiled section begins with a short entry prefix. At byte
* offset 10, a halfword gives the distance to the section end.
* Near that end, pairs of words bind global numbers to addresses.
* The pair with a zero address marks the start of the global list.
* Globals are indexed as four-byte entries at G + (4 * number).
*
* STARTUP AND SHUTDOWN
* Use GETMAIN for one area containing 700 globals, 16384 stack
* words, and 256 bytes of stack clearance. Initialize globals,
* import the main section and BLIB, attach native service entries,
* and call G!1 (START). Finish through the system vector or STOP.
* On exit, close streams and free heap vectors before freeing the
* global/stack block. Return the selected completion code to MVS.
*
* IMPORTANT LIMITS
* This code imports global exports from the starting section and
* BLIB only. Other compiled sections need explicit registration.
* G!150 currently holds the DEBUGINT helper. The Cambridge
* compiler uses G!150 for FORMTREE; that overlap must be resolved.
* The code does not implement a general segment loader.
*
* COMMENTS DESCRIBE THIS IMPLEMENTATION, NOT A FULL IBM RUNTIME.
*===================================================================
*
*------------------------------------------------------------------
* MODULE ENTRY
* Preserve the compiled section base, establish an MVS save area,
* and allocate the global-vector and stack block.
*------------------------------------------------------------------
BCPLMAIN CSECT
         ENTRY STKOVFL
         EXTRN BLIB
         EXTRN GETVEC,FREEVEC,MEMDRAIN,MEMBIND
         EXTRN GETBYTE,PUTBYTE
         EXTRN APTOVEC,APLIMIT
         EXTRN IOINIT,IOFIN,IOWRCH,IOBIND,IODIAG,IOREPL,IOPMGET
         EXTRN IOFOUT,IOSOUT,IOOUT,IOWRAP,IOENDW
         EXTRN IOSELIN,IOINP,IOPARMST,IORDCH,IOUNRD,IOFINDIN
         EXTRN IOENDRD
         LR    3,15
         LR    9,1
         BALR  10,0
         USING *,10
         L     1,=A(MSVSAVE)
         ST    13,4(1)
         ST    1,8(13)
         LR    13,1
         USING MSVSAVE,13
         ST    9,PARMLIST
         ST    3,MODBASE
         LH    0,10(3)
         LR    2,3
         AR    2,0
         ST    2,MODEND
         L     9,DYNLEN
         GETMAIN EC,LV=(9),A=DYNBASE,SP=0
         LTR   15,15
         BNZ   GNOCORE
         L     12,DYNBASE
         LA    1,GVBYTES(12)
         ST    1,DYNWORK
         A     1,=F'65536'
         ST    1,STKLIM
         A     1,=F'256'
         ST    1,DYNEND
         L     2,DYNWORK
         L     3,=X'5C40E2E3'
         L     4,=X'C3D2405C'
         L     0,=F'8192'
*
*------------------------------------------------------------------
* STACK MARKERS
* Fill the usable stack with marker words. STACKHWM can later
* measure how much stack was used.
*------------------------------------------------------------------
STKPAINT ST    3,0(2)
         ST    4,4(2)
         LA    2,8(2)
         BCT   0,STKPAINT
         L     2,DYNEND
         AH    2,=H'-8'
         ST    3,0(2)
         L     1,STKLIM
         AH    1,=H'-8'
         SRL   1,2
         ST    1,4(2)
         LA    11,SYSV
         LA    1,GLOBCNT
         ST    1,0(12)
         LA    2,4(12)
         L     3,=X'C7D3F004'
*
*------------------------------------------------------------------
* INITIAL GLOBAL VALUES
* G!0 holds the highest global number. All other slots start with
* distinct unset values.
*------------------------------------------------------------------
GINIT    ST    3,0(2)
         A     3,=F'4'
         LA    2,4(2)
         BCT   1,GINIT
         L     8,MODEND
*
*------------------------------------------------------------------
* FIND EXPORTED GLOBALS
* Walk backward through the section trailer to find the
* zero-address marker and the required global-vector size.
*------------------------------------------------------------------
GSCAN    AH    8,=H'-8'
         L     9,4(8)
         LTR   9,9
         BC    7,GSCAN
         L     0,0(8)
         C     0,=F'2796'
         BC    2,GTOOBIG
         ST    8,TRAILER
         L     8,MODEND
*
*------------------------------------------------------------------
* INSTALL MAIN-SECTION GLOBALS
* Store the address for each exported global in its numbered
* global-vector slot.
*------------------------------------------------------------------
GINST    AH    8,=H'-8'
         L     9,4(8)
         LTR   9,9
         BC    8,GIDONE
         L     1,0(8)
         C     1,=F'2796'
         BC    2,GTOOBIG
         LR    2,12
         AR    2,1
         ST    9,0(2)
         BC    15,GINST
*
*------------------------------------------------------------------
* IMPORT THE LIBRARY
* The initial program and BLIB use the same compiled-section
* trailer format. BLIB supplies callable library globals.
*------------------------------------------------------------------
GIDONE   L     8,=A(BLIB)
         LH    0,10(8)
         AR    8,0
*
*------------------------------------------------------------------
* REGISTER BLIB EXPORTS
* Read BLIB's exported-global pairs and copy their addresses into
* G.
*------------------------------------------------------------------
BLIMP    AH    8,=H'-8'
         L     9,4(8)
         LTR   9,9
         BZ    BLIDONE
         L     1,0(8)
         C     1,=F'800'
         BH    GTOOBIG
         LR    2,12
         AR    2,1
         ST    9,0(2)
         B     BLIMP
*
*------------------------------------------------------------------
* PUBLISH RUNTIME GLOBALS
* Fill machine-dependent entries for streams, byte access, memory,
* APTOVEC, STOP, and runtime state.
*------------------------------------------------------------------
BLIDONE  L     4,4(12)
         C     4,=X'C7D3F004'
         BC    8,NOSTART
         LR    1,13
         SRL   1,2
         ST    1,24(12)
         L     1,MODBASE
         SRL   1,2
         ST    1,208(12)
         L     1,MODEND
         SRL   1,2
         ST    1,212(12)
         L     1,DYNWORK
         SRL   1,2
         ST    1,216(12)
         L     1,DYNEND
         SRL   1,2
         ST    1,220(12)
         L     1,=A(IOSELIN)
         ST    1,44(12)
         L     1,=A(IOINP)
         ST    1,64(12)
         L     1,=A(IOOUT)
         ST    1,68(12)
         L     1,=A(IOPARMST)
         ST    1,156(12)
         L     1,=A(IOWRAP)
         ST    1,132(12)
         L     1,=A(IORDCH)
         ST    1,52(12)
         L     1,=A(IOUNRD)
         ST    1,60(12)
         L     1,=A(IOFINDIN)
         ST    1,168(12)
         L     1,=A(IOFOUT)
         ST    1,164(12)
         L     1,=A(IOSOUT)
         ST    1,48(12)
         L     1,=A(IOENDW)
         ST    1,188(12)
         L     1,=A(IOENDRD)
         ST    1,184(12)
         L     1,=A(IOWRCH)
         ST    1,56(12)
         L     1,304(12)
         C     1,=X'C7D3F130'
         BNE   WFHAS76
         LA    1,WRITEST
         ST    1,304(12)
WFHAS76  EQU   *
         L     1,=A(GETBYTE)
         ST    1,340(12)
         L     1,=A(PUTBYTE)
         ST    1,344(12)
         L     1,=A(GETVEC)
         ST    1,348(12)
         L     1,=A(FREEVEC)
         ST    1,352(12)
         ST    10,MBRT10
         L     1,=A(MSVFREE)
         L     9,=A(MEMBIND)
         BALR  14,9
         L     10,MBRT10
         L     1,=A(DEBUGINT)
         ST    1,600(12)
         L     1,=A(APLIMIT)
         L     2,STKLIM
         ST    2,0(1)
         L     1,=A(APTOVEC)
         ST    1,160(12)
         LA    1,STOPENT
         ST    1,120(12)
         LR    9,10
         L     1,PARMLIST
         L     15,=A(IOINIT)
         BALR  14,15
         LR    10,9
         LR    9,10
         LA    1,IOSTOP
         L     15,=A(IOBIND)
         BALR  14,15
         LR    10,9
         LA    11,SYSV
         L     15,DYNWORK
         LR    5,15
         L     1,=F'4096'
         L     2,=F'8192'
         L     3,=F'12288'
         SR    6,6
         SR    7,7
         SR    8,8
         SR    9,9
         SR    10,10
         SR    0,0
         BCR   15,4
*
*------------------------------------------------------------------
* STARTUP AND RETURN ERRORS
* Return a nonzero MVS completion code if START returns directly or
* initial setup fails.
*------------------------------------------------------------------
BADRETN  BAL   14,RELMEM
         L     13,4(13)
         LM    14,12,12(13)
         LA    15,36
         BR    14
GTOOBIG  BAL   14,RELMEM
         L     13,4(13)
         LM    14,12,12(13)
         LA    15,16
         BR    14
NOSTART  BAL   14,RELMEM
         L     13,4(13)
         LM    14,12,12(13)
         LA    15,20
         BR    14
GNOCORE  L     13,4(13)
         LM    14,12,12(13)
         LA    15,24
         BR    14
         LTORG
         DROP  10
*
*------------------------------------------------------------------
* SYSTEM VECTOR
* R11 points here. Each 20-byte slot branches to a service: return,
* counting, finish, stack check, or counted stack check.
*------------------------------------------------------------------
SYSV     EQU   *
         USING SYSV,11
         BC    15,RETIMPL
         DS    8H
SYSCOUNT BC    15,CNTIMPL
         DS    8H
SYSFIN   BC    15,FINIMPL
         DS    8H
SYSSTK   BC    15,STKIMPL
         DS    8H
SYSSTKC  BC    15,STKCIMP
         DS    8H
STKLIM   DC    F'0'
STKMSG   DC    CL14'STACK OVERFLOW'
         DS    0H
*
*------------------------------------------------------------------
* RETURN FROM A BCPL PROCEDURE
* Restore the caller's linkage, workspace, and R4 procedure entry
* from the saved BCPL frame.
*------------------------------------------------------------------
RETIMPL  L     6,8(5)
         L     5,4(5)
         L     4,0(5)
         BCR   15,6
*
*------------------------------------------------------------------
* CALL-COUNT SLOT
* Skip the inline counter address and return. This implementation
* does not maintain call counts.
*------------------------------------------------------------------
CNTIMPL  LA    14,4(14)
         BR    14
*
*------------------------------------------------------------------
* NORMAL STOP AND MVS RETURN
* FINISH selects RC 0. STOP uses the requested RC. Flush and close
* I/O, release vectors, release the main block, and restore MVS
* registers.
*------------------------------------------------------------------
FINIMPL  XC    STOPRC(4),STOPRC
         B     FINEXIT
STOPENT  ST    7,STOPRC
FINEXIT  LR    9,10
         L     15,=A(IOFIN)
         BALR  14,15
         LR    10,9
FINNOO2  EQU   *
         BAL   14,RELMEM
         L     15,STOPRC
         L     13,4(13)
         LM    14,14,12(13)
         LM    0,12,20(13)
         BR    14
*
*------------------------------------------------------------------
* RELEASE THE MAIN STORAGE BLOCK
* MEMDRAIN clears remaining vector allocations before FREEMAIN
* returns the global/stack allocation.
*------------------------------------------------------------------
RELMEM   ST    14,RELRET
         L     1,=A(MEMDRAIN)
         BALR  14,1
         SR    1,1
         L     9,=A(MEMBIND)
         BALR  14,9
RELMAIN  L     1,DYNBASE
         LTR   1,1
         BZ    RELDONE
         L     10,DYNLEN
         FREEMAIN R,LV=(10),A=(1)
         XC    DYNBASE(4),DYNBASE
RELDONE  L     14,RELRET
         BR    14
         LTORG
*
*------------------------------------------------------------------
* STACK CHECK
* Update the current workspace and compare the next frame with
* STKLIM. Branch to overflow handling if the frame crosses the safe
* end.
*------------------------------------------------------------------
STKIMPL  LR    5,15
         L     4,0(14)
         LTR   4,4
         BC    12,STKFORM
         TM    3(14),X'03'
         BC    7,STKFORM
         AR    4,15
         C     4,STKLIM
         BH    STKOVFL
         L     4,0(15)
         LA    14,4(14)
         BR    14
STKOVFL  LR    9,10
         LA    1,STKMSG
         LA    2,14
         L     15,=A(IOREPL)
         BALR  14,15
         LR    10,9
         B     FINIMPL
IOSTOP   LA    7,12
         B     STOPENT
STKFORM  L     4,0(15)
         L     13,4(13)
         LM    14,12,12(13)
         LA    15,36
         BR    14
*
*------------------------------------------------------------------
* COUNTED STACK-CHECK SLOT
* Skip the inline counter field, then perform the normal stack
* check.
*------------------------------------------------------------------
STKCIMP  LA    14,4(14)
         BR    14

*
*------------------------------------------------------------------
* SIMPLE FORMATTED OUTPUT FALLBACK
* This local WRITEF-like entry is used only when BLIB has not
* supplied G!76. It writes through BCPL output services.
*------------------------------------------------------------------
WRITEST  STM   2,6,WFREGSV
         ST    8,WFARGS
         ST    9,WFARGS+4
         XC    WFARGIX(4),WFARGIX
         LR    14,7
         SLL   14,2
         SR    8,8
         IC    8,0(14)
         LA    14,1(14)
         SR    9,9
WFLITLP  LTR   8,8
         BZ    WFLITDN
         SR    7,7
         IC    7,0(14)
         CLI   0(14),C'%'
         BNE   WFLITCP
         LA    4,2
         CR    8,4
         BL    WFLITCP
         CLI   1(14),C'N'
         BE    WFNSEL
         CLI   1(14),C'C'
         BE    WFCSEL
         CLI   1(14),C'I'
         BE    WFISEL
         CLI   1(14),C'X'
         BE    WFXSEL
         CLI   1(14),C'O'
         BE    WFOSEL
         CLI   1(14),C'S'
         BE    WFSTSEL
         CLI   1(14),C'$'
         BE    WFSKARG
         B     WFUNK
WFSTSEL  EQU   *
         LA    14,2(14)
         SR    8,4
         BAL   10,WFNEXT
         B     WFSTR
WFSKARG  L     6,WFARGIX
         LA    6,1(6)
         ST    6,WFARGIX
         LA    14,2(14)
         SR    8,4
         B     WFLITLP
WFUNK    SR    7,7
         IC    7,1(14)
         LA    14,2(14)
         SR    8,4
         BAL   10,WFPUTC
         B     WFLITLP
WFNSEL   XC    WFWIDTH(4),WFWIDTH
         LA    14,2(14)
         SR    8,4
         BAL   10,WFNEXT
         B     WFNUM
WFISEL  LA    5,3
         CR    8,5
         BL    WFLITCP
         SR    6,6
         IC    6,2(14)
         CLI   2(14),C'A'
         BL    WFIDEC
         CLI   2(14),C'F'
         BH    WFIDEC
         S     6,WFHEXAO
         B     WFISTOR
WFIDEC   S     6,WFZERO
WFISTOR  ST    6,WFWIDTH
         LA    14,3(14)
         SR    8,5
         BAL   10,WFNEXT
         B     WFNUM
WFXSEL   LA    5,3
         CR    8,5
         BL    WFLITCP
         SR    6,6
         IC    6,2(14)
         CLI   2(14),C'A'
         BL    WFXDEC
         CLI   2(14),C'F'
         BH    WFXDEC
         S     6,WFHEXAO
         B     WFXSTOR
WFXDEC   S     6,WFZERO
WFXSTOR  ST    6,WFWIDTH
         LA    14,3(14)
         SR    8,5
         BAL   10,WFNEXT
         B     WFHEX
WFOSEL   LA    5,3
         CR    8,5
         BL    WFLITCP
         SR    6,6
         IC    6,2(14)
         CLI   2(14),C'A'
         BL    WFODEC
         CLI   2(14),C'F'
         BH    WFODEC
         S     6,WFHEXAO
         B     WFOSTOR
WFODEC   S     6,WFZERO
WFOSTOR  ST    6,WFWIDTH
         LA    14,3(14)
         SR    8,5
         BAL   10,WFNEXT
         B     WFOCT
WFCSEL   LA    14,2(14)
         SR    8,4
         BAL   10,WFNEXT
         BAL   10,WFPUTC
         B     WFLITLP
WFLITCP  LA    14,1(14)
         BCTR  8,0
         BAL   10,WFPUTC
         B     WFLITLP
*
*------------------------------------------------------------------
* SIGNED DECIMAL FORMAT
* Convert a signed integer to printable decimal bytes and apply an
* optional field width.
*------------------------------------------------------------------
WFNUM    ST    8,WFREM
         ST    14,WFFMTP
         XC    WFSIGN(4),WFSIGN
         LTR   7,7
         BNM   WFCVT
         LA    6,1
         ST    6,WFSIGN
WFCVT    CVD   7,WFDECPK
         UNPK  WFDECZN(15),WFDECPK(8)
         OI    WFDECZN+14,X'F0'
         LA    4,WFDECZN
         LA    5,15
WFSKIP   CLI   0(4),C'0'
         BNE   WFPAD
         LA    6,1
         CR    5,6
         BE    WFPAD
         LA    4,1(4)
         BCT   5,WFSKIP
WFPAD    L     2,WFWIDTH
         LTR   2,2
         BZ    WFSIGNO
         SR    2,5
         S     2,WFSIGN
         BNP   WFSIGNO
WFPADLP  LA    7,64
         BAL   10,WFPUTC
         BCT   2,WFPADLP
WFSIGNO  L     6,WFSIGN
         LTR   6,6
         BZ    WFDCOPY
         LA    7,96
         BAL   10,WFPUTC
WFDCOPY  SR    7,7
         IC    7,0(4)
         BAL   10,WFPUTC
         LA    4,1(4)
         BCT   5,WFDCOPY
         L     8,WFREM
         L     14,WFFMTP
         B     WFLITLP
*
*------------------------------------------------------------------
* HEXADECIMAL FORMAT
* Write the requested number of hexadecimal digits, with zero fill.
*------------------------------------------------------------------
WFHEX    ST    8,WFREM
         ST    14,WFFMTP
         ST    7,WFHEXVAL
         L     5,WFWIDTH
         LTR   5,5
         BZ    WFHEXDN
         LR    2,5
         BCTR  2,0
         SLL   2,2
WFHEXLP  L     7,WFHEXVAL
         SRL   7,0(2)
         N     7,WFHEXMSK
         C     7,WFHEXNIN
         BL    WFHEXDIG
         A     7,WFHEXAO
         B     WFHEXOUT
WFHEXDIG A     7,WFHEXZO
WFHEXOUT BAL   10,WFPUTC
         SH    2,WFHXFOUR
         BCT   5,WFHEXLP
WFHEXDN  L     8,WFREM
         L     14,WFFMTP
         B     WFLITLP
*
*------------------------------------------------------------------
* OCTAL FORMAT
* Write a fixed-width octal value using three-bit digits.
*------------------------------------------------------------------
WFOCT    ST    8,WFREM
         ST    14,WFFMTP
         ST    7,WFOCTVAL
         L     5,WFWIDTH
         LTR   5,5
         BZ    WFOCTDN
         LR    2,5
         BCTR  2,0
         LR    6,2
         SLL   2,1
         AR    2,6
WFOCTLP  L     7,WFOCTVAL
         SRL   7,0(2)
         N     7,WFOCTMSK
         A     7,WFHEXZO
         BAL   10,WFPUTC
         SH    2,WFOCTTHR
         BCT   5,WFOCTLP
WFOCTDN  L     8,WFREM
         L     14,WFFMTP
         B     WFLITLP
*
*------------------------------------------------------------------
* BCPL STRING FORMAT
* Read a byte-counted BCPL string and send each byte through the
* selected output service.
*------------------------------------------------------------------
WFSTR    LR    4,7
         SLL   4,2
         SR    5,5
         IC    5,0(4)
         LA    4,1(4)
WFSTRLP  LTR   5,5
         BZ    WFLITLP
         SR    7,7
         IC    7,0(4)
         BAL   10,WFPUTC
         LA    4,1(4)
         BCTR  5,0
         B     WFSTRLP
*
*------------------------------------------------------------------
* FORMAT ARGUMENTS
* Advance through the saved argument registers used by formatted
* output.
*------------------------------------------------------------------
WFNEXT   L     6,WFARGIX
         SLL   6,2
         LA    4,WFARGS
         AR    4,6
         L     7,0(4)
         L     6,WFARGIX
         LA    6,1(6)
         ST    6,WFARGIX
         BR    10
WFLAST   L     6,WFARGIX
         BCTR  6,0
         SLL   6,2
         LA    4,WFARGS
         AR    4,6
         L     7,0(4)
         BR    10
*
*------------------------------------------------------------------
* OUTPUT ONE FORMAT BYTE
* Send the current byte to the installed character-output service.
*------------------------------------------------------------------
WFPUTC   LA    6,132
         CR    9,6
         BNL   WFPUTRT
         LA    6,WFBUF
         AR    6,9
         STC   7,0(6)
         LA    9,1(9)
WFPUTRT  BR    10
WFLITDN  ST    9,WFLEN
         LM    2,6,WFREGSV
         STM   0,15,WFALLSV
         LR    8,10
         LA    1,WFBUF
         L     2,WFLEN
         L     9,=A(IODIAG)
         BALR  14,9
         LR    10,8
         LM    0,15,WFALLSV
         L     4,0(5)
         BCR   15,6
WFALLSV  DS    16F
WFLEN    DC    F'0'
WFBUF    DS    CL132
WFREGSV  DS    5F
WFARGS   DS    2F
WFARGIX  DC    F'0'
WFWIDTH  DC    F'0'
WFSIGN   DC    F'0'
WFZERO   DC    X'000000F0'
WFHEXMSK DC    F'15'
WFHEXNIN DC    F'10'
WFHEXAO  DC    F'183'
WFHEXZO  DC    F'240'
WFHXFOUR DC   H'4'
WFHEXVAL DC    F'0'
WFOCTMSK DC    F'7'
WFOCTTHR DC    H'3'
WFOCTVAL DC    F'0'
WFREM    DC    F'0'
WFFMTP   DC    A(0)
WFDECPK  DS    D
WFDECZN  DS    CL15
*
*------------------------------------------------------------------
* LOCAL DECIMAL DIAGNOSTIC
* Format an integer as decimal text. The current binding at G!150
* conflicts with the Cambridge compiler's FORMTREE global.
*------------------------------------------------------------------
DEBUGINT XC    DBGPOS(4),DBGPOS
         LTR   7,7
         BNM   DBGCVT
         LA    10,C'-'
         BAL   14,DBGAPND
DBGCVT   CVD   7,DECPACK
         UNPK  DECZON(15),DECPACK(8)
         OI    DECZON+14,X'F0'
         LA    8,DECZON
         LA    9,15
DBGSKIP  CLI   0(8),C'0'
         BNE   DBGOUT
         LA    4,1
         CR    9,4
         BE    DBGOUT
         LA    8,1(8)
         BCT   9,DBGSKIP
DBGOUT   SR    10,10
         IC    10,0(8)
         BAL   14,DBGAPND
         LA    8,1(8)
         BCT   9,DBGOUT
         STM   0,15,DBGSV
         LR    8,10
         LA    1,DBGBUF
         L     2,DBGPOS
         L     9,=A(IODIAG)
         BALR  14,9
         LR    10,8
         LM    0,15,DBGSV
         L     4,0(5)
         BCR   15,6
DBGAPND  L     4,DBGPOS
         LA    7,132
         CR    4,7
         BNL   DBGARET
         LA    7,DBGBUF
         AR    7,4
         STC   10,0(7)
         LA    4,1(4)
         ST    4,DBGPOS
DBGARET  BR    14
         DS    0F
*
*------------------------------------------------------------------
* STATIC RUNTIME STATE
* Save areas, loader/free-list headers, input parameters,
* allocation addresses, diagnostics and service work fields.
*------------------------------------------------------------------
MSVSAVE  DS    18F
         DS    11F
MSVLOAD  DC    F'0'              G6!29, byte-pointer load-list head
         DS    18F
MSVFREE  DC    F'0'              G6!48, byte-pointer free-area head
MBRT10   DC    F'0'
PARMLIST DC    F'0'
MODBASE  DC    F'0'
MODEND   DC    F'0'
TRAILER  DC    F'0'
*
*------------------------------------------------------------------
* MAIN ALLOCATION CONSTANTS
* G!0 through G!699 use 2800 bytes. A further 65536 bytes hold the
* usable stack, followed by 256 bytes of clearance.
*------------------------------------------------------------------
GLOBCNT  EQU   699
GVBYTES  EQU   (GLOBCNT+1)*4
DYNLEN   DC    F'68592'
DYNBASE  DC    F'0'
DYNWORK  DC    F'0'
DYNEND   DC    F'0'
RELRET   DC    F'0'
STOPRC   DC    F'0'
DBGSV    DS    16F
DBGPOS   DC    F'0'
DBGBUF   DS    CL132
DECPACK  DS    D
DECZON   DS    CL15

         DS    0F

         END   BCPLMAIN
