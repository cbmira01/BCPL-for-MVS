***********************************************************************
* BCPL FOR MVS 3.8 RECONSTRUCTION - BCPLMAIN
*
* Core Runtime coordinator for generated native BCPL applications.
* Creates global/system vectors, binds core services and imports
* application/Base Library exports before entering START.
*
* REGISTRATION:
* RGINIT validates and registers selected optional packages
* before START; RGFINI runs before stream/memory cleanup.
* Exactly one application BCPLREG table is required at link-edit.
*
* LINKAGE:
* Requires BLIB, BCPLIO, BCPLMEM, BCPLBYTE, BCPLAPT,
* and the generic registrar BCPLRGS (RGINIT/RGFINI).
* Preserves the accepted native System/370 BCPL register ABI.
*
* STATUS:
* Accepted R.1-R.3 behavior was tested with temporary MVS
* objects; no BOOT_OBJ or BOOT_DEVOBJ installation is implied.
* A reconstruction, not authenticated historical machine code.
***********************************************************************

BCPLMAIN CSECT
         ENTRY STKOVFL
         EXTRN BLIB
         EXTRN RGINIT,RGFINI
         EXTRN GETVEC,FREEVEC,MEMDRAIN,MEMBIND
         EXTRN GETBYTE,PUTBYTE
         EXTRN APTOVEC,APLIMIT
         EXTRN IOINIT,IOFIN,IOWRCH,IOBIND,IODIAG,IOREPL,IOPMGET
         EXTRN IOFOUT,IOSOUT,IOOUT,IOWRAP,IOENDW
         EXTRN IOSELIN,IOINP,IOPARMST,IORDCH,IOUNRD,IOFINDIN
         EXTRN IOENDRD
*
* Preserve the compiled-module base before R3 is repurposed as R.K12.
*
         LR    3,15
         LR    9,1
         BALR  10,0
         USING *,10
*
* Establish a private MVS save area before any service call.
* The generated module prefix already saved the caller's R14..R12.
*
         L     1,=A(MSVSAVE)
         ST    13,4(1)
         ST    1,8(13)
         LR    13,1
         USING MSVSAVE,13
         ST    9,PARMLIST
         ST    3,MODBASE
*
* Locate L998 = module base + unsigned positive halfword at module+10.
* CG370 limits a generated section to less than 16K bytes, so LH is
* safe.
*
         LH    0,10(3)
         LR    2,3
         AR    2,0
         ST    2,MODEND
*
* Acquire one MVS allocation for G!0..G!699, 16384 usable stack
* words and a provisional 256-byte stack clearance. Preserve the
* tested safe limit while retaining physical headroom above it.
* GETMAIN EC reports failure through R15.
* through R15.  Store base and length for subsequent FREEMAIN R.
*
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
*
* G56 STACKHWM in historical BLIB scans alternating word markers.
* Paint the safe 16384-word stack before the first BCPL frame.
* The final 256-byte clearance stays outside the working stack.
*
         L     2,DYNWORK
         L     3,=X'5C40E2E3'
         L     4,=X'C3D2405C'
         L     0,=F'8192'
STKPAINT ST    3,0(2)
         ST    4,4(2)
         LA    2,8(2)
         BCT   0,STKPAINT
*
* STACKEND-2 is the guard; STACKEND-1 records the highest
* initialized even-marker word as a BCPL word pointer.
* These two fullwords reside in the reserved clearance.
*
         L     2,DYNEND
         AH    2,=H'-8'
         ST    3,0(2)
         L     1,STKLIM
         AH    1,=H'-8'
         SRL   1,2
         ST    1,4(2)
         LA    11,SYSV
*
* Initialize the dynamic global vector with the historical sentinel.
*
         LA    1,GLOBCNT
         ST    1,0(12)
         LA    2,4(12)
         L     3,=X'C7D3F004'
GINIT    ST    3,0(2)
         A     3,=F'4'
         LA    2,4(2)
         BCT   1,GINIT
* CLEAR PER-GLOBAL OWNER LEDGER BEFORE IMPORTS.
         L     4,=A(R1OWNB)
         XC    0(256,4),0(4)
         XC    256(256,4),256(4)
         XC    512(188,4),512(4)
*
* Find the trailer sentinel by scanning backward in two-word units.
* A pair whose second word is zero is treated as [4*MAXGN,0].
*
         L     8,MODEND
GSCAN    AH    8,=H'-8'
         L     9,4(8)
         LTR   9,9
         BC    7,GSCAN
*
* Reject modules requiring more globals than this static WIP provides.
*
         L     0,0(8)
         C     0,=F'2796'
         BC    2,GTOOBIG
         ST    8,TRAILER
*
* Re-scan from the module end and install each exported global.
*
         L     8,MODEND
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
         LR    4,1
         SRL   4,2
         L     2,=A(R1OWNB)
         AR    2,4
         OI    0(2),X'01'
         BC    15,GINST
*
* G!1 must now contain START rather than the unset sentinel.
*
GIDONE   L     8,=A(BLIB)
* IMPORT BLIB EXPORTED GLOBALS BY EXPLICIT MODULE REGISTRATION.
* THE RELOCATED BLIB ENTRY POINT NAMES THE PREFIX AT OFFSET ZERO.
         LH    0,10(8)
         AR    8,0
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
         LR    4,1
         SRL   4,2
         L     2,=A(R1OWNB)
         AR    2,4
         OI    0(2),X'02'
         B     BLIMP
BLIDONE  L     4,4(12)
         C     4,=X'C7D3F004'
         BC    8,NOSTART
*
* Publish the subset of runtime globals whose representation is
* supported strongly enough for this WIP.
*
* G!6 = provisional BCPL word pointer for the current MVS save area.
*
         LR    1,13
         SRL   1,2
         ST    1,24(12)
         L     8,=A(R1OWNB)
         OI    6(8),X'04'
*
* G!52/G!53 = provisional main-program word-address extent.
*
         L     1,MODBASE
         SRL   1,2
         ST    1,208(12)
         L     8,=A(R1OWNB)
         OI    52(8),X'04'
         L     1,MODEND
         SRL   1,2
         ST    1,212(12)
         L     8,=A(R1OWNB)
         OI    53(8),X'04'
*
* G!54/G!55 = BCPL word pointers for the allocated stack extent.
* G!55 includes the reserved clearance; STKLIM is the safe limit.
*
         L     1,DYNWORK
         SRL   1,2
         ST    1,216(12)
         L     8,=A(R1OWNB)
         OI    54(8),X'04'
         L     1,DYNEND
         SRL   1,2
         ST    1,220(12)
         L     8,=A(R1OWNB)
         OI    55(8),X'04'
*
* G!14 = first narrow native WRCH implementation for Regression 03.
* G!76 = bootstrap WRITEF, extended through Regression 058.
* G!85/G!86 = machine-dependent byte primitives required by BLIB.
* G!87/G!88 = first WIP GETVEC/FREEVEC dynamic-storage services.
* G!150 = provisional DEBUGINT bootstrap diagnostic service.
*
         L     1,=A(IOSELIN)
         ST    1,44(12)
         L     8,=A(R1OWNB)
         OI    11(8),X'04'
         L     1,=A(IOINP)
         ST    1,64(12)
         L     8,=A(R1OWNB)
         OI    16(8),X'04'
         L     1,=A(IOOUT)
         ST    1,68(12)
         L     8,=A(R1OWNB)
         OI    17(8),X'04'
         L     1,=A(IOPARMST)
         ST    1,156(12)
         L     8,=A(R1OWNB)
         OI    39(8),X'04'
         L     1,=A(IOWRAP)
         ST    1,132(12)
         L     8,=A(R1OWNB)
         OI    33(8),X'04'
         L     1,=A(IORDCH)
         ST    1,52(12)
         L     8,=A(R1OWNB)
         OI    13(8),X'04'
         L     1,=A(IOUNRD)
         ST    1,60(12)
         L     8,=A(R1OWNB)
         OI    15(8),X'04'
         L     1,=A(IOFINDIN)
         ST    1,168(12)
         L     8,=A(R1OWNB)
         OI    42(8),X'04'
         L     1,=A(IOFOUT)
         ST    1,164(12)
         L     8,=A(R1OWNB)
         OI    41(8),X'04'
         L     1,=A(IOSOUT)
         ST    1,48(12)
         L     8,=A(R1OWNB)
         OI    12(8),X'04'
         L     1,=A(IOENDW)
         ST    1,188(12)
         L     8,=A(R1OWNB)
         OI    47(8),X'04'
         L     1,=A(IOENDRD)
         ST    1,184(12)
         L     8,=A(R1OWNB)
         OI    46(8),X'04'
         L     1,=A(IOWRCH)
         ST    1,56(12)
         L     8,=A(R1OWNB)
         OI    14(8),X'04'
* Keep BLIB's G!76 WRITEF when its export has been imported.
* Install provisional WRITEST only if G!76 retains the unset sentinel.
         L     1,304(12)
         C     1,=X'C7D3F130'
         BNE   WFHAS76
         LA    1,WRITEST
         ST    1,304(12)
         L     8,=A(R1OWNB)
         OI    76(8),X'04'
WFHAS76  EQU   *
         L     1,=A(GETBYTE)
         ST    1,340(12)
         L     8,=A(R1OWNB)
         OI    85(8),X'04'
         L     1,=A(PUTBYTE)
         ST    1,344(12)
         L     8,=A(R1OWNB)
         OI    86(8),X'04'
         L     1,=A(GETVEC)
         ST    1,348(12)
         L     8,=A(R1OWNB)
         OI    87(8),X'04'
         L     1,=A(FREEVEC)
         ST    1,352(12)
         L     8,=A(R1OWNB)
         OI    88(8),X'04'
         ST    10,MBRT10
         L     1,=A(MSVFREE)
         L     9,=A(MEMBIND)
         BALR  14,9
         L     10,MBRT10
         L     1,=A(DEBUGINT)
         ST    1,600(12)
         L     8,=A(R1OWNB)
         OI    150(8),X'04'
* Install independent BCPLAPT G40 entry and its safe stack limit.
         L     1,=A(APLIMIT)
         L     2,STKLIM
         ST    2,0(1)
         L     1,=A(APTOVEC)
         ST    1,160(12)
         L     8,=A(R1OWNB)
         OI    40(8),X'04'
         LA    1,STOPENT
         ST    1,120(12)
         L     8,=A(R1OWNB)
         OI    30(8),X'04'
*
* Regression 03 output is deliberately narrow: one buffered SYSPRINT
* record.  This borrows the proven QSAM shape used by ICINT V19.
*
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
*
* Establish S, initial P/W, and the absolute-base constants required by
* generated USING 4096,1,2,3 code.
*
* REGISTER OPTIONALS AFTER CORE AND BLIB IMPORTS.
         ST    12,R1GVEC
         LA    1,R1GVEC
         L     15,=A(RGINIT)
         BALR  14,15
         LTR   15,15
         BNZ   R1BAD
         LA    11,SYSV
         L     15,DYNWORK
         LR    5,15
         L     1,=F'4096'
         L     2,=F'8192'
         L     3,=F'12288'
*
* START receives no arguments.  Clear argument registers and linkage.
* R10 has served as our assembler base and must cease being one now.
*
         SR    6,6
         SR    7,7
         SR    8,8
         SR    9,9
         SR    10,10
*
* Job 943 makes this initialization a required runtime invariant.
*
         SR    0,0
         BCR   15,4
*
* START is expected to terminate through S.FIN.  Returning here is
* treated as a WIP runtime failure.
*
* REGISTRATION REJECTION BEFORE APPLICATION START.
* IOFIN USES R10 AS A PRIVATE BASE. PRESERVE OUR BASE IN R9.
R1BAD    LR    9,10
         L     15,=A(IOFIN)
         BALR  14,15
         LR    10,9
         BAL   14,RELMEM
         L     13,4(13)
         LM    14,12,12(13)
         LA    15,12
         BR    14
BADRETN  BAL   14,RELMEM
         L     13,4(13)
         LM    14,12,12(13)
         LA    15,36
         BR    14
*
* Bootstrap failures before START.
*
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
*
* Failure before allocation: no storage to release.
GNOCORE  L     13,4(13)
         LM    14,12,12(13)
         LA    15,24
         BR    14
*
* Put literals used by startup inside the startup base-register region.
*
         LTORG
*
* From here on R10 is not a runtime base.  Executable system-vector
* services use R11, whose value is SYSV in generated BCPL code.
*
         DROP  10
*
***********************************************************************
* SYSTEM VECTOR
*
* Each public offset is a four-byte branch followed by padding to the
* next 20-byte slot.  This layout is a reconstruction proposal matching
* the offsets in CGHDR; the historical instruction sequence is unknown.
***********************************************************************
SYSV     EQU   *
         USING SYSV,11
         BC    15,RETIMPL
         DS    8H
*
* S.COUNT = 20
*
SYSCOUNT BC    15,CNTIMPL
         DS    8H
*
* S.FIN = 40
*
SYSFIN   BC    15,FINIMPL
         DS    8H
*
* S.STKCK = 60
*
SYSSTK   BC    15,STKIMPL
         DS    8H
*
* S.STKCKCOUNT = 80
*
SYSSTKC  BC    15,STKCIMP
         DS    8H
*
* Runtime-local byte limit and controlled-overflow message.
* Historical BCPLMAC distinguishes STKLIM (safe limit) from STKHIGH.
* This WIP reserves 256 extra bytes above the tested 16KB safe
* limit.  The exact historical INUM interpretation remains unknown.
*
STKLIM   DC    F'0'
STKMSG   DC    CL14'STACK OVERFLOW'
         DS    0H
*
***********************************************************************
* PROCEDURE RETURN
*
* Restore linkage from the callee frame, then restore the caller's P
* before reloading R4 from the caller frame.  Test 32 showed why R4
* cannot be restored from 0(current P): that word names the callee.
***********************************************************************
RETIMPL  L     6,8(5)
         L     5,4(5)
         L     4,0(5)
         BCR   15,6
*
***********************************************************************
* CALL-COUNT SERVICE -- STUB
*
* CG370 emits BAL R14,S.COUNT(R11) followed by an inline fullword.
* A minimally non-destructive stub must skip that word on return.
* Actual counter semantics remain to be reconstructed.
***********************************************************************
CNTIMPL  LA    14,4(14)
         BR    14
*
***********************************************************************
* FINISH
*
* Restore the MVS registers saved by the generated module prefix.
* FINISH selects RC=0; STOP(N) selects the requested step code.
* Both share the output and storage reclamation path.
***********************************************************************
FINIMPL  XC    STOPRC(4),STOPRC
         XC    R1REAS(4),R1REAS
         XC    R1CODE(4),R1CODE
         B     FINEXIT
STOPENT  ST    7,STOPRC
         ST    7,R1CODE
         LA    1,1
         ST    1,R1REAS
FINEXIT  LR    9,10
* FINALIZERS RUN BEFORE IOFIN AND MEMDRAIN.
         LA    1,R1REAS
         L     15,=A(RGFINI)
         BALR  14,15
         LTR   15,15
         BZ    R1FINOK
         L     1,R1REAS
         LTR   1,1
         BNZ   R1FINOK
         LA    1,8
         ST    1,STOPRC
R1FINOK  L     15,=A(IOFIN)
         BALR  14,15
         LR    10,9
FINNOO2  EQU   *
* BCPLIO IOFIN closes lazily opened BCPIN and BCPINB.
         BAL   14,RELMEM
         L     15,STOPRC
         L     13,4(13)
         LM    14,14,12(13)
         LM    0,12,20(13)
         BR    14
*
* Drain live GETVEC allocations before freeing global/stack memory.
* Each record holds its own byte length and next record address.
* Detach the head before FREEMAIN; never read a released record.
* Save the BAL return across MVS services that may modify R14.
***********************************************************************
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
***********************************************************************
* STACK CHECK -- FRAME-SIZE CONTRACT
*
* Tests 48-49 established the checked-entry sequence and proved that
* this path must perform the LR 5,15 omitted by CG370.
*
* R14 addresses an inline fullword containing the generated frame size
* in bytes.  CG370 has already saved R4-R6 at 0(R15), so R4 is safe as
* a temporary here and can be restored before returning to generated
* code.
*
* Test 50 added structural validation of the inline value.  Test 52
* adds the first WIP limit check: W plus required frame bytes must not
* exceed STKLIM.  BCPLMAC proves that the historical runtime maintained
* a safe stack limit distinct from the byte beyond allocated stack.
* The missing machine-code STKCK body leaves exact clearance semantics
* unrecovered. The provisional boundary remains 16KB from stack base.
***********************************************************************
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
***********************************************************************
* STACK CHECK + CALL COUNT -- STUB
*
* CG370 places an inline fullword after this BAL form, so skip it.
***********************************************************************
STKCIMP  LA    14,4(14)
         BR    14
*
***********************************************************************
* Independent BCPLAPT supplies G40; bootstrap sets APLIMIT.
*
***********************************************************************
* INPUT STREAM RUNG 094 -- SINGLE NAMED QSAM STREAM BCPIN
*
* FINDINPUT accepts the EBCDIC BCPL string "BCPIN", lazily opens
* its DCB and returns a word-address stream handle. Other DDs fail
* with zero. SELECTINPUT retains that handle. RDCH reads characters
* from an 80-byte fixed QSAM record; end-of-data yields -1.
* This is a bootstrap subset, not multi-stream historical BCPL I/O.
***********************************************************************
* D4 input handlers now reside in BCPLIO.

*
***********************************************************************
* BCPL output services and both QSAM DCBs are owned by BCPLIO.
* G14/G12/G16/G17/G41/G47 point to independent entries.
***********************************************************************
*
* WRITEF -- LITERAL + %N/%C/%S/%I/%X/%O BOOTSTRAP
*
* Regression 053 established literal-string output through G76.
* Regression 054 adds the historical BLIB %N case: decimal output of
* the next argument with no width field.  Regression 055 adds %C and
* %S and proves sequential consumption of R8 then R9. Regression 056
* adds the historical %I width path; Test 060 adds A-F width digits.
*
* BCPL strings use a length byte at byte offset zero followed by data
* Literal bytes use the BCPL output service. '%' followed by 'N'
* emits signed decimal; %C emits one character; %S emits a BCPL
* string; %I consumes one width character and emits signed decimal
* right-justified in that field. %X and %O consume one width
* character and emit exactly that many zero-filled hexadecimal or
* octal digits respectively.
*
* This is bootstrap machinery, not a reconstruction of BLIB's BCPL
* WRITEF body.  R0 and R1-R3 remain permanent generated-code registers.
***********************************************************************
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
*
* Historical BLIB default emits the unknown conversion character
* without the '%' and without advancing the argument cursor.
*
*
* Historical BLIB percent-dollar skips one argument; emits nothing.
*
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
* Emit the current signed integer using the proven CVD/UNPK shape
* used by DEBUGINT, then copy digits through the common byte appender.
*
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
*
* R5 is now the digit count.  Pad on the left to WFWIDTH, counting a
* minus sign as part of the field.  A width of zero is the %N case.
*
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
* Emit exactly WFWIDTH hexadecimal digits from the current argument.
* This mirrors historical WRITEHEX: fixed width, zero filled, high
* nibbles first. Regression 057 establishes width 4.
*
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
* Emit exactly WFWIDTH octal digits from the current argument.
* This mirrors historical WRITEOCT: fixed width, zero filled, high
* 3-bit groups first. Regression 058 establishes width 4.
*
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
* Emit a BCPL string argument in R7.  Preserve the format cursor and
* remaining format length in R14/R8 while the string bytes are copied.
*
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
* Fetch the next saved formatting argument into R7 and advance the
* bootstrap argument cursor.  Test 055 exercises R8 then R9.
*
WFNEXT   L     6,WFARGIX
         SLL   6,2
         LA    4,WFARGS
         AR    4,6
         L     7,0(4)
         L     6,WFARGIX
         LA    6,1(6)
         ST    6,WFARGIX
         BR    10
*
* Reload the argument most recently returned by WFNEXT.  The negative
* sign append in WFNUM temporarily consumes R7.
*
WFLAST   L     6,WFARGIX
         BCTR  6,0
         SLL   6,2
         LA    4,WFARGS
         AR    4,6
         L     7,0(4)
         BR    10
*
* Append R7 low byte through the installed BCPL output service.
* Return through R10, which is scratch for this bootstrap WRITEF.
*
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
*
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
***********************************************************************
* G85/G86 are supplied by separate BCPLBYTE CSECT.
*
***********************************************************************
* GETVEC(N) -> R7 -- WIP DYNAMIC STORAGE
*
* Regression 27 success-path implementation.
*
* BCPL VEC N has indices 0..N, so GETVEC(N) supplies N+1 payload
* fullwords.  Twelve private bytes precede the payload and mirror the
* historical VECAREA fields VECBASE, VECLEN, and VECNEXT.
*
* Regression 30 changes allocation to conditional GETMAIN EC.
* GETVEC returns zero for a negative or overlarge size, or an MVS
* allocation failure.  N<=4194299 keeps the byte count within 24 bits.
*
* GETMAIN EC returns its address through A= and completion in R15.
* Generated BCPL requires R0=0 and R1-R3 to hold permanent constants,
* R5 to remain P, R6 to remain L, and R15 to remain W.  Preserve them
* explicitly across the MVS service as defensive runtime discipline.
* Test 32 ultimately identified a separate RETIMPL error, not GETMAIN
* register corruption.
***********************************************************************
* BCPLMEM external allocator routines.
*
***********************************************************************
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
*
* Append one EBCDIC byte from R10.  R14 is local linkage.
*
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
*
***********************************************************************
***********************************************************************
* WIP DATA
***********************************************************************
         DS    0F
MSVSAVE  DS    18F
* Historical USERSAVE-compatible G6 list-head positions.
* The leading 18 words remain the ordinary MVS save area (R13).
* Unimplemented intervening fields are reserved, not emulated.
         DS    11F
MSVLOAD  DC    F'0'              G6!29, byte-pointer load-list head
         DS    18F
MSVFREE  DC    F'0'              G6!48, byte-pointer free-area head
MBRT10   DC    F'0'
* Original MVS EXEC parameter list (R1), retained at entry.
PARMLIST DC    F'0'
MODBASE  DC    F'0'
MODEND   DC    F'0'
TRAILER  DC    F'0'
*
* GETVEC WIP allocation state.
* VECLIST is a byte pointer to the first three-word control record.
*
* Allocator state moved to BCPLMEM.
*
* R13 save area precedes the data controls.
*
* Contiguous GETMAIN layout: 700 global fullwords, 16384 stack
* fullwords, and 256 bytes of provisional clearance.  Dynamic backing
* addresses are saved in static controls.
* The GETMAIN block is released as a unit during FINISH/error exit.
*
GLOBCNT  EQU   699
GVBYTES  EQU   (GLOBCNT+1)*4
DYNLEN   DC    F'68592'
DYNBASE  DC    F'0'
DYNWORK  DC    F'0'
DYNEND   DC    F'0'
RELRET   DC    F'0'
STOPRC   DC    F'0'
R1GVEC   DC    F'0'
R1OWNP   DC    A(R1OWNB)
R1REAS   DC    F'0'
R1CODE   DC    F'0'
         DS    0F
R1OWNB   DS    CL700
*
* DEBUGINT state remains local; QSAM stream state belongs to BCPLIO.
*
DBGSV    DS    16F
DBGPOS   DC    F'0'
DBGBUF   DS    CL132
DECPACK  DS    D
DECZON   DS    CL15
* Retired obsolete local output DCBs, buffers, and stream handles.

*
* MVS EXEC PARM pseudo-stream: independently selectable via FINDPARM.
* No DCB/GET: PARM bytes are held by MVS for this task step.
         DS    0F
* Input/PARM state, DCBs and EODAD are BCPLIO-owned.

*
* Stack marker initialization and historical clearance remain separate
* work.  No static workspace is reserved in this CSECT.
*
         END   BCPLMAIN
