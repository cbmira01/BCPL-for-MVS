         TITLE 'ICINT V15 - RICHARDS INTCODE ASSEMBLER/INTERPRETER'
         PRINT NOGEN
*
* STRUCTURAL SYSTEM/370 TRANSLATION OF
* RICHARDS-BCPLTAPE/MR10/BCPLKIT/ICINT.
*
* V15 NAMED OCODE OUTPUT STREAM AND TABLE-DRIVEN STREAM LOOKUP
*
* BASE:
*   ICINT V14. INTCODE EXECUTION AND INTCODE OUTPUT SEMANTICS ARE
*   INTENDED TO BE UNCHANGED.
*
* V15 SCOPE:
*   - IMPLEMENT FINDOUTPUT("OCODE") AS A DISTINCT HOST OUTPUT.
*   - RETAIN V14 FINDOUTPUT("INTCODE") RECORDIZATION UNCHANGED.
*   - REPLACE FIXED FINDINPUT/FINDOUTPUT NAME CHAINS WITH TABLE-DRIVEN
*     LOOKUP OF MVS-COMPATIBLE NAMES (UP TO 8 CHARACTERS).
*   - USE ORDINARY RECORD OUTPUT FOR OCODE; HISTORICAL TRN BREAKS ITS
*     OWN PHYSICAL LINES ONLY AT SPACE BOUNDARIES AFTER COLUMN 62.
*   - DO NOT YET IMPLEMENT DYNAMIC DCB ALLOCATION FOR ARBITRARY DDNAME
*     STREAMS. THE TABLE STRUCTURE IS THE BRIDGE TO THAT LATER WORK.
*
* CGI CONTRACT:
*   MR10 CGI WR() INSERTS '/' FOLLOWED BY NEWLINE AT LINEP=71. THAT
*   SEQUENCE IS OUTPUT FORMATTING, NOT AN INTCODE TOKEN OR COMMENT.
*   A LITERAL '/' NOT FOLLOWED BY NEWLINE IS PRESERVED.
*
* V12 REPRESENTATION:
*   BCPL MEMORY/CODE POINTER = ALIGNED HOST BYTE ADDRESS / 4.
*   ORDINARY POINTER +1 THEREFORE ADVANCES ONE BCPL WORD.
*   CONVERT BACK TO A HOST BYTE ADDRESS ONLY AT MEMORY ACCESS.
*
* OPAQUE MVS STREAM HANDLES REMAIN NATIVE HOST VALUES. THEY ARE USED
* ONLY BY THE HOST-SERVICE X-OPERATIONS AND ARE NOT GENERIC BCPL MEMORY
* POINTERS.
*
* ACCEPTANCE TARGETS:
*   - V14 FACTORIAL AND INTCODE-OUTPUT BEHAVIOR MUST REMAIN UNCHANGED.
*   - SYN/TRN FINDOUTPUT("OCODE") MUST SUCCEED WHEN //OCODE EXISTS.
*   - OCODE RECORDS MUST BE DIRECTLY REUSABLE AS CGI //SYSIN INPUT.
*   - CGI-GENERATED INTCODE MUST REMAIN DIRECTLY REUSABLE AS ICINT INPUT.
*
* OBJECTIVES:
*   - KEEP THE ICINT LOGIC CLOSE TO THE ORIGINAL BCPL.
*   - KEEP MVS RECORD I/O BELOW A BCPL STREAM INTERFACE.
*   - ISOLATE HOST RECORDIZATION FROM CGI'S STREAM-ORIENTED OUTPUT.
*
***********************************************************************
* REGISTER CONVENTIONS
***********************************************************************
*
* MVS ENTRY:
*   R1   PARAMETER LIST
*   R13  CALLER SAVE AREA
*   R14  RETURN ADDRESS
*   R15  ENTRY ADDRESS
*
* PERMANENT BASE REGISTERS:
*   R12  ICINT+0
*   R11  ICINT+4096
*   R10  ICINT+8192
*
* INTERNAL CALLS:
*   R0   FUNCTION RESULT / VOLATILE
*   R1   MVS PARAMETER / VOLATILE
*   R2   ARGUMENT 1 / VOLATILE
*   R3   ARGUMENT 2 / VOLATILE
*   R4   ARGUMENT 3 / VOLATILE
*   R5   VOLATILE WORK
*   R6-R9 PRESERVED
*   R10-R12 BASE REGISTERS
*   R13  SAVE AREA
*   R14  RETURN ADDRESS
*   R15  EXTERNAL ENTRY ADDRESS
*
***********************************************************************

ICINT    CSECT
         ENTRY ICINT

R0       EQU   0
R1       EQU   1
R2       EQU   2
R3       EQU   3
R4       EQU   4
R5       EQU   5
R6       EQU   6
R7       EQU   7
R8       EQU   8
R9       EQU   9
R10      EQU   10
R11      EQU   11
R12      EQU   12
R13      EQU   13
R14      EQU   14
R15      EQU   15

         USING ICINT,R12
         B     START
         ORG   ICINT+4096
         USING ICINT+4096,R11
         ORG   ICINT+8192
         USING ICINT+8192,R10
         ORG   ICINT

***********************************************************************
* STREAM DESCRIPTOR LAYOUT
***********************************************************************
SDTYPE   EQU   0
SDDCB    EQU   4
SDBUF    EQU   8
SDPOS    EQU   12
SDLEN    EQU   16
SDFLAGS  EQU   20
SDLENGTH EQU   24

***********************************************************************
* MVS ENTRY / STARTUP
***********************************************************************
START    STM   R14,R12,12(R13)
         LR    R12,R15
         LA    R11,4095(R12)
         LA    R11,1(R11)
         LA    R10,4095(R11)
         LA    R10,1(R10)
         LA    R2,SAVEAREA
         ST    R13,4(R2)
         ST    R2,8(R13)
         LR    R13,R2

         BAL   R14,STRMINIT

         LA    R2,SYSPRNAM
         BAL   R14,FINDOUT
         ST    R0,SYSPRINT
         LR    R2,R0
         BAL   R14,SELOUT

         LA    R2,ENTERMSG
         BAL   R14,WRITES

         BAL   R14,GETSTORE
         LTR   R0,R0
         BNZ   STARTERR

         LA    R2,INTINNAM
         BAL   R14,FINDIN
         LTR   R0,R0
         BZ    STARTERR
         LR    R2,R0
         BAL   R14,SELIN

         BAL   R14,INIT
         BAL   R14,LOADPROG
         LTR   R0,R0
         BNZ   STARTRUN
         BAL   R14,EXECUTE
STARTRUN ST    R0,EXITCODE
         LTR   R0,R0
         BNM   STARTREP
         BAL   R14,MAPSTORE
STARTREP L     R2,SYSPRINT
         BAL   R14,SELOUT
         LA    R2,EXECMSG
         L     R3,CYCCNT
         L     R4,EXITCODE
         BAL   R14,WRITEF
         B     STARTCLO

STARTERR LA    R0,12
         ST    R0,EXITCODE

STARTCLO BAL   R14,CLOSEALL
         BAL   R14,FREESTOR
         L     R15,EXITCODE
         L     R13,4(R13)
         L     R14,12(R13)
         LM    R0,R12,20(R13)
         BR    R14

SAVEAREA DS    18F
EXITCODE DS    F

***********************************************************************
* DYNAMIC STORAGE
***********************************************************************
GETSTORE DS    0H
         ST    R14,GSRET
         GETMAIN RU,LV=LABBYTES
         ST    R1,LABBASE
         ST    R1,LABV
         GETMAIN RU,LV=GLOBBYTS
         ST    R1,GLOBBASE
         ST    R1,G
         GETMAIN RU,LV=PROGBYTS
         ST    R1,PROGBASE
         SR    R0,R0
         L     R14,GSRET
         BR    R14
GSRET    DS    F

FREESTOR DS    0H
         ST    R14,FSRET
         L     R1,PROGBASE
         LTR   R1,R1
         BZ    FSGLOB
         FREEMAIN RU,A=(R1),LV=PROGBYTS
         XC    PROGBASE,PROGBASE
FSGLOB   L     R1,GLOBBASE
         LTR   R1,R1
         BZ    FSLAB
         FREEMAIN RU,A=(R1),LV=GLOBBYTS
         XC    GLOBBASE,GLOBBASE
FSLAB    L     R1,LABBASE
         LTR   R1,R1
         BZ    FSDONE
         FREEMAIN RU,A=(R1),LV=LABBYTES
         XC    LABBASE,LABBASE
FSDONE   L     R14,FSRET
         BR    R14
FSRET    DS    F

***********************************************************************
* INITIALIZATION / LOADER
***********************************************************************
INIT     DS    0H
         L     R2,LABBASE
         LA    R3,LABBYTES
         SR    R4,R4
         MVCL  R2,R4
         L     R2,GLOBBASE
         LA    R3,GLOBBYTS
         SR    R4,R4
         MVCL  R2,R4
         L     R2,PROGBASE
         LA    R3,PROGBYTS
         SR    R4,R4
         MVCL  R2,R4
         XC    GUSED,GUSED
         XC    CH,CH
         XC    CHEOF,CHEOF
         XC    CYCCNT,CYCCNT
         XC    CP,CP
         XC    A,A
         XC    B,B
         XC    C,C
         XC    D,D
         XC    W,W
         XC    FVAR,FVAR
         L     R2,PROGBASE
         SRL   R2,2
         ST    R2,PROGWORD
         ST    R2,P
         LA    R2,INITCODE
         L     R3,PROGBASE
         MVC   0(12,R3),0(R2)
         L     R0,PROGWORD
         A     R0,=F'3'
         ST    R0,CP
         BR    R14

LOADPROG DS    0H
         ST    R14,LPRET
LPLOOP   BAL   R14,RCH
         CLI   CHEOF,1
         BE    LPDONE
         BAL   R14,RDN
         LTR   R0,R0
         BM    LPLOOP
         BAL   R14,LOADITEM
         B     LPLOOP
LPDONE   L     R2,SYSPRINT
         BAL   R14,SELOUT
         LA    R2,SIZEMSG
         L     R3,CP
         L     R4,PROGWORD
         SR    R3,R4
         BAL   R14,WRITEF
         SR    R0,R0
         L     R14,LPRET
         BR    R14
LPRET    DS    F

LOADITEM DS    0H
         ST    R14,LIRET
         LR    R6,R0
         BAL   R14,RDN
         LR    R7,R0
         LR    R0,R6
         C     R0,=F'74'
         BE    LISETLAB
         C     R0,=F'68'
         BE    LIGLOBAL
         C     R0,=F'67'
         BE    LICONST
         C     R0,=F'65'
         BE    LIZERO
         C     R0,=F'66'
         BE    LICHAR
         C     R0,=F'90'
         BE    LIZEND
         C     R0,=F'36'
         BE    LIDOLLAR
         B     LIBAD
LISETLAB LR    R2,R7
         BAL   R14,SETLAB
         B     LIRETURN
LIGLOBAL LR    R2,R7
         BAL   R14,SETGLOBAL
         B     LIRETURN
LICONST  LR    R2,R7
         BAL   R14,PUTWORD
         B     LIRETURN
LIZERO   LR    R2,R7
         BAL   R14,PUTZERO
         B     LIRETURN
LICHAR   LR    R2,R7
         BAL   R14,PUTCHAR
         B     LIRETURN
LIZEND   MVI   CHEOF,1
         B     LIRETURN
LIDOLLAR LR    R2,R7
         BAL   R14,PUTDOLLAR
         B     LIRETURN
LIBAD    LA    R2,BADCHMSG
         LR    R3,R6
         L     R4,CP
         L     R5,PROGWORD
         SR    R4,R5
         L     R5,SYSPRINT
         LR    R8,CUROUT
         LR    R2,R5
         BAL   R14,SELOUT
         LA    R2,BADCHMSG
         LR    R3,R6
         L     R4,CP
         L     R5,PROGWORD
         SR    R4,R5
         BAL   R14,WRITEF
         LR    R2,R8
         BAL   R14,SELOUT
LIRETURN L     R14,LIRET
         BR    R14
LIRET    DS    F

RCH      DS    0H
         ST    R14,RCHRET
RCHREP   BAL   R14,HOSTRD
         LTR   R0,R0
         BM    RCHEOF
         MVI   CHEOF,0
         STC   R0,CH
         CLI   CH,C'/'
         BNE   RCHRTN
RCHCOMM  CLI   CH,X'15'
         BE    RCHREP
         BAL   R14,HOSTRD
         LTR   R0,R0
         BM    RCHEOF
         STC   R0,CH
         B     RCHCOMM
RCHEOF   MVI   CHEOF,1
         MVI   CH,X'00'
RCHRTN   L     R14,RCHRET
         BR    R14
RCHRET   DS    F

RDN      DS    0H
         ST    R14,RDNRET
         SR    R0,R0
         CLI   CH,C'0'
         BL    RDNRET0
         CLI   CH,C'9'
         BH    RDNRET0
RDNDIG   M     R0,=F'10'
         SR    R3,R3
         IC    R3,CH
         S     R3,=F'240'
         AR    R0,R3
         BAL   R14,RCH
         CLI   CH,C'0'
         BL    RDNRET0
         CLI   CH,C'9'
         BNH   RDNDIG
RDNRET0  L     R14,RDNRET
         BR    R14
RDNRET   DS    F

***********************************************************************
* LOADER HELPERS
***********************************************************************
SETLAB   DS    0H
         ST    R14,SLRET
         LR    R6,R2
         BAL   R14,RDN
         LR    R7,R0
         C     R6,=F'500'
         BH    SLBAD
         L     R5,LABBASE
         LR    R4,R6
         SLL   R4,2
         L     R3,0(R4,R5)
         LTR   R3,R3
         BNZ   SLALREADY
         L     R0,CP
         ST    R0,0(R4,R5)
         B     SLRTN
SLALREADY LR   R8,CUROUT
         L     R2,SYSPRINT
         BAL   R14,SELOUT
         LA    R2,ALSETMSG
         LR    R3,R6
         LR    R4,R3
         L     R5,CP
         L     R9,PROGWORD
         SR    R5,R9
         BAL   R14,WRITEF
         LR    R2,R8
         BAL   R14,SELOUT
         B     SLRTN
SLBAD    LA    R0,-1
SLRTN    L     R14,SLRET
         BR    R14
SLRET    DS    F

SETGLOBAL DS   0H
         ST    R14,SGRET
         LR    R6,R2
         BAL   R14,RDN
         LR    R7,R0
         C     R6,=F'400'
         BH    SGBAD
         C     R7,=F'500'
         BH    SGBAD
         L     R5,LABBASE
         LR    R4,R7
         SLL   R4,2
         L     R0,0(R4,R5)
         LTR   R0,R0
         BZ    SGUNSET
         L     R5,GLOBBASE
         LR    R4,R6
         SLL   R4,2
         ST    R0,0(R4,R5)
         LA    R5,GUSED
         AR    R5,R6
         MVI   0(R5),1
         B     SGRTN
SGUNSET  LR    R8,CUROUT
         L     R2,SYSPRINT
         BAL   R14,SELOUT
         LA    R2,UNSETMSG
         LR    R3,R7
         BAL   R14,WRITEF
         LR    R2,R8
         BAL   R14,SELOUT
         B     SGRTN
SGBAD    LA    R0,-1
SGRTN    L     R14,SGRET
         BR    R14
SGRET    DS    F

PUTWORD  DS    0H
         ST    R14,PWRET
         LR    R6,R2
         BAL   R14,RDN
         LR    R2,R6
         BAL   R14,STCODE
         L     R14,PWRET
         BR    R14
PWRET    DS    F

PUTZERO  DS    0H
         ST    R14,PZRET
         LR    R6,R2
PZLOOP   LTR   R6,R6
         BZ    PZRTN
         SR    R2,R2
         BAL   R14,STCODE
         BCT   R6,PZLOOP
PZRTN    L     R14,PZRET
         BR    R14
PZRET    DS    F

PUTCHAR  DS    0H
         ST    R14,PCRET
         LR    R6,R2
         BAL   R14,RDN
         LR    R2,R6
         BAL   R14,STCODE
         L     R14,PCRET
         BR    R14
PCRET    DS    F

PUTDOLLAR DS   0H
         ST    R14,PDRET
         LR    R6,R2
         BAL   R14,RDN
         LR    R2,R6
         BAL   R14,STCODE
         L     R14,PDRET
         BR    R14
PDRET    DS    F

STCODE   DS    0H
         L     R3,CP
         SLL   R3,2
         L     R4,PROGBASE
         L     R5,PROGWORD
         SLL   R5,2
         SR    R3,R5
         AR    R3,R4
         ST    R2,0(R3)
         L     R3,CP
         LA    R3,1(R3)
         ST    R3,CP
         BR    R14

***********************************************************************
* EXECUTION LOOP
***********************************************************************
EXECUTE  DS    0H
         ST    R14,EXRET
         XC    CYCCNT,CYCCNT
         L     R2,PROGWORD
         LA    R2,3(R2)
         ST    R2,C
         L     R2,PROGWORD
         LA    R2,100(R2)
         ST    R2,P
         ST    R2,STKBASE
FETCH    L     R2,CYCCNT
         LA    R2,1(R2)
         ST    R2,CYCCNT
         L     R2,C
         BAL   R14,ICFETCH
         ST    R0,W
         L     R2,C
         LA    R2,1(R2)
         ST    R2,C
         L     R2,W
         SRL   R2,12
         N     R2,=F'15'
         SLL   R2,2
         LA    R3,OPJTAB
         L     R2,0(R2,R3)
         BR    R2

OP0      B     FETCH
OP1      L     R2,W
         N     R2,=F'4095'
         ST    R2,A
         B     FETCH
OP2      L     R2,W
         N     R2,=F'4095'
         L     R3,P
         AR    R3,R2
         LR    R2,R3
         BAL   R14,ICFETCH
         ST    R0,A
         B     FETCH
OP3      L     R2,W
         N     R2,=F'4095'
         L     R3,G
         AR    R3,R2
         LR    R2,R3
         BAL   R14,ICFETCH
         ST    R0,A
         B     FETCH
OP4      L     R2,W
         N     R2,=F'4095'
         L     R3,A
         AR    R3,R2
         LR    R2,R3
         BAL   R14,ICFETCH
         ST    R0,A
         B     FETCH
OP5      L     R2,W
         N     R2,=F'4095'
         L     R3,P
         AR    R3,R2
         LR    R2,R3
         BAL   R14,ICFETCH
         LR    R3,R0
         L     R2,A
         BAL   R14,ICSTORE
         B     FETCH
OP6      L     R2,W
         N     R2,=F'4095'
         ST    R2,D
         L     R2,P
         L     R3,D
         AR    R3,R2
         ST    R2,0(R3)
         L     R4,C
         ST    R4,4(R3)
         ST    R3,P
         L     R2,A
         ST    R2,C
         B     FETCH
OP7      L     R2,W
         N     R2,=F'4095'
         ST    R2,D
         L     R2,P
         L     R3,D
         AR    R3,R2
         ST    R2,0(R3)
         L     R4,C
         ST    R4,4(R3)
         ST    R3,P
         L     R2,A
         ST    R2,C
         B     FETCH
OP8      L     R2,W
         N     R2,=F'4095'
         L     R3,P
         AR    R3,R2
         LR    R2,R3
         L     R3,A
         BAL   R14,ICSTORE
         B     FETCH
OP9      L     R2,W
         N     R2,=F'4095'
         L     R3,G
         AR    R3,R2
         LR    R2,R3
         L     R3,A
         BAL   R14,ICSTORE
         B     FETCH
OPA      L     R2,W
         N     R2,=F'4095'
         L     R3,A
         AR    R3,R2
         ST    R3,A
         B     FETCH
OPB      L     R2,W
         N     R2,=F'4095'
         L     R3,A
         SR    R3,R2
         ST    R3,A
         B     FETCH
OPC      L     R2,W
         N     R2,=F'4095'
         L     R3,A
         SLL   R3,0(R2)
         ST    R3,A
         B     FETCH
OPD      L     R2,W
         N     R2,=F'4095'
         L     R3,A
         SRL   R3,0(R2)
         ST    R3,A
         B     FETCH
OPE      L     R2,W
         N     R2,=F'4095'
         L     R3,A
         LR    R4,R2
         SRL   R4,1
         AR    R3,R4
         LR    R2,R3
         BAL   R14,ICGETBY
         ST    R0,A
         B     FETCH
OPF      L     R2,W
         N     R2,=F'4095'
         ST    R2,D
         L     R2,C
         BAL   R14,ICFETCH
         ST    R0,A
         L     R2,C
         LA    R2,1(R2)
         ST    R2,C
         B     FETCH

***********************************************************************
* X OPERATIONS
***********************************************************************
XOP      L     R2,W
         N     R2,=F'4095'
         C     R2,=F'23'
         BH    XBAD
         SLL   R2,2
         LA    R3,XJTAB
         L     R2,0(R2,R3)
         BR    R2
X0       B     FETCH
X1       L     R2,A
         BAL   R14,ICFETCH
         ST    R0,A
         B     FETCH
X2       L     R2,A
         LCR   R2,R2
         ST    R2,A
         B     FETCH
X3       L     R2,A
         X     R2,=F'-1'
         ST    R2,A
         B     FETCH
X4       L     R2,P
         L     R3,4(R2)
         ST    R3,C
         L     R3,0(R2)
         ST    R3,P
         B     FETCH
X5       L     R3,B
         M     R2,A
         ST    R3,A
         B     FETCH
X6       BAL   R14,DIVINT
         ST    R0,A
         B     FETCH
X7       BAL   R14,REMINT
         ST    R0,A
         B     FETCH
X8       L     R2,A
         AR    R2,B
         ST    R2,A
         B     FETCH
X9       L     R2,B
         SR    R2,A
         ST    R2,A
         B     FETCH
X10      L     R2,B
         C     R2,A
         BNE   X10F
         L     R2,=F'-1'
         ST    R2,A
         B     FETCH
X10F     XC    A,A
         B     FETCH
X11      L     R2,B
         C     R2,A
         BE    X11F
         L     R2,=F'-1'
         ST    R2,A
         B     FETCH
X11F     XC    A,A
         B     FETCH
X12      L     R2,B
         C     R2,A
         BNL   X12F
         L     R2,=F'-1'
         ST    R2,A
         B     FETCH
X12F     XC    A,A
         B     FETCH
X13      L     R2,B
         C     R2,A
         BNH   X13F
         L     R2,=F'-1'
         ST    R2,A
         B     FETCH
X13F     XC    A,A
         B     FETCH
X14      L     R2,B
         C     R2,A
         BH    X14F
         L     R2,=F'-1'
         ST    R2,A
         B     FETCH
X14F     XC    A,A
         B     FETCH
X15      L     R2,B
         C     R2,A
         BL    X15F
         L     R2,=F'-1'
         ST    R2,A
         B     FETCH
X15F     XC    A,A
         B     FETCH
X16      L     R2,B
         OR    R2,A
         ST    R2,A
         B     FETCH
X17      L     R2,B
         NR    R2,A
         ST    R2,A
         B     FETCH
X18      L     R2,B
         XR    R2,A
         ST    R2,A
         B     FETCH
X19      BAL   R14,SHLINT
         ST    R0,A
         B     FETCH
X20      BAL   R14,SHRINT
         ST    R0,A
         B     FETCH
X21      L     R2,A
         N     R2,=F'255'
         ST    R2,A
         B     FETCH
X22      SR    R0,R0
         B     EXRETURN
X23      BAL   R14,SWITCHON
         B     FETCH
XBAD     LA    R0,-1
         B     EXRETURN

EXRETURN L     R14,EXRET
         BR    R14
EXRET    DS    F

***********************************************************************
* SWITCHON
***********************************************************************
SWITCHON DS    0H
         ST    R14,SWRET
         L     R2,C
         BAL   R14,ICFETCH
         LR    R6,R0
         L     R2,C
         LA    R2,1(R2)
         ST    R2,C
         L     R2,C
         BAL   R14,ICFETCH
         LR    R7,R0
         L     R2,C
         LA    R2,1(R2)
         ST    R2,C
         SR    R8,R8
SWLOOP   CR    R8,R6
         BNL   SWDEFAULT
         L     R2,C
         BAL   R14,ICFETCH
         LR    R9,R0
         L     R2,C
         LA    R2,1(R2)
         ST    R2,C
         L     R2,A
         CR    R2,R9
         BE    SWMATCH
         L     R2,C
         LA    R2,1(R2)
         ST    R2,C
         LA    R8,1(R8)
         B     SWLOOP
SWMATCH  L     R2,C
         BAL   R14,ICFETCH
         ST    R0,C
         B     SWDONE
SWDEFAULT ST   R7,C
SWDONE   L     R14,SWRET
         BR    R14
SWRET    DS    F

***********************************************************************
* HOST-SERVICE X OPERATIONS / BCPL LIBRARY PRIMITIVES
***********************************************************************
* NOTE: THE ORIGINAL BCPL ICINT EXPECTS HOST-SERVICE OPERATIONS FOR
* STREAMS, CHARACTER I/O, STORE, AND UTILITY FUNCTIONS. THE RECONSTRUCTED
* INTERPRETER PROVIDES THE SUBSET REQUIRED BY THE MR10 COMPILER/RUNTIME.
*
HOSTX    DS    0H
         ST    R14,HXRET
         LR    R6,R2
         C     R6,=F'1'
         BE    HXFINDIN
         C     R6,=F'2'
         BE    HXFINDOU
         C     R6,=F'3'
         BE    HXSELIN
         C     R6,=F'4'
         BE    HXSELOUT
         C     R6,=F'5'
         BE    HXRDCH
         C     R6,=F'6'
         BE    HXWRCH
         C     R6,=F'7'
         BE    HXENDRD
         C     R6,=F'8'
         BE    HXENDWR
         C     R6,=F'9'
         BE    HXWRITES
         C     R6,=F'10'
         BE    HXWRITEF
         C     R6,=F'11'
         BE    HXSTOP
         C     R6,=F'12'
         BE    HXAPTOV
         C     R6,=F'13'
         BE    HXLEVEL
         C     R6,=F'14'
         BE    HXLONGJP
         C     R6,=F'15'
         BE    HXMAPST
         C     R6,=F'16'
         BE    HXREADN
         C     R6,=F'17'
         BE    HXPACKST
         C     R6,=F'18'
         BE    HXUNPACK
         C     R6,=F'19'
         BE    HXGETBYT
         C     R6,=F'20'
         BE    HXPUTBYT
         LA    R0,-1
         B     HXRETURN

HXFINDIN L     R2,A
         SLL   R2,2
         BAL   R14,FINDIN
         ST    R0,A
         B     HXRETURN
HXFINDOU L     R2,A
         SLL   R2,2
         BAL   R14,FINDOUT
         ST    R0,A
         B     HXRETURN
HXSELIN  L     R2,A
         BAL   R14,SELIN
         B     HXRETURN
HXSELOUT L     R2,A
         BAL   R14,SELOUT
         B     HXRETURN
HXRDCH   BAL   R14,HOSTRD
         ST    R0,A
         B     HXRETURN
HXWRCH   L     R2,A
         BAL   R14,HOSTWR
         B     HXRETURN
HXENDRD  BAL   R14,ENDREAD
         B     HXRETURN
HXENDWR  BAL   R14,ENDWRITE
         B     HXRETURN
HXWRITES L     R2,A
         SLL   R2,2
         BAL   R14,WRITES
         B     HXRETURN
HXWRITEF L     R2,A
         SLL   R2,2
         L     R3,P
         LA    R3,3(R3)
         LR    R4,R3
         LA    R4,1(R4)
         LR    R5,R4
         LA    R5,1(R5)
         SLL   R3,2
         SLL   R4,2
         SLL   R5,2
         L     R3,0(R3)
         L     R4,0(R4)
         L     R5,0(R5)
         BAL   R14,WRITEF
         B     HXRETURN
HXSTOP   L     R0,A
         B     EXRETURN
HXAPTOV  L     R0,A
         B     HXRETURN
HXLEVEL  L     R0,P
         ST    R0,A
         B     HXRETURN
HXLONGJP L     R0,A
         B     HXRETURN
HXMAPST  BAL   R14,MAPSTORE
         B     HXRETURN
HXREADN  BAL   R14,READN
         ST    R0,A
         B     HXRETURN
HXPACKST BAL   R14,PACKSTR
         ST    R0,A
         B     HXRETURN
HXUNPACK BAL   R14,UNPACKST
         B     HXRETURN
HXGETBYT BAL   R14,ICGETBY
         ST    R0,A
         B     HXRETURN
HXPUTBYT BAL   R14,ICPUTBY
         B     HXRETURN
HXRETURN SR    R0,R0
         L     R14,HXRET
         BR    R14
HXRET    DS    F

***********************************************************************
* PACK/UNPACK BYTE HELPERS
***********************************************************************
PACKSTR  DS    0H
         ST    R14,PKRET
         L     R2,A
         SLL   R2,2
         L     R3,P
         LA    R3,3(R3)
         SLL   R3,2
         L     R3,0(R3)
         SLL   R3,2
         SR    R4,R4
         IC    R4,0(R2)
         SR    R5,R5
PKLOOP   CR    R5,R4
         BNL   PKDONE
         SR    R0,R0
         IC    R0,1(R5,R2)
         LR    R6,R5
         SRL   R6,1
         AR    R6,R3
         L     R7,0(R6)
         LR    R8,R5
         N     R8,=F'1'
         LTR   R8,R8
         BNZ   PKODD
         N     R7,=F'255'
         LR    R8,R0
         SLL   R8,8
         OR    R7,R8
         ST    R7,0(R6)
         B     PKNEXT
PKODD    N     R7,=F'65280'
         OR    R7,R0
         ST    R7,0(R6)
PKNEXT   LA    R5,1(R5)
         B     PKLOOP
PKDONE   LR    R0,R4
         A     R0,=F'1'
         SRL   R0,1
         L     R14,PKRET
         BR    R14
PKRET    DS    F

UNPACKST DS    0H
         ST    R14,UPRET
         L     R2,A
         SLL   R2,2
         L     R3,P
         LA    R3,3(R3)
         SLL   R3,2
         L     R3,0(R3)
         SLL   R3,2
         SR    R4,R4
         IC    R4,0(R2)
         SR    R5,R5
UPLOOP   CR    R5,R4
         BNL   UPDONE
         LR    R6,R5
         SRL   R6,1
         AR    R6,R2
         L     R7,0(R6)
         LR    R8,R5
         N     R8,=F'1'
         LTR   R8,R8
         BNZ   UPODD
         SRL   R7,8
UPODD    N     R7,=F'255'
         STC   R7,1(R5,R3)
         LA    R5,1(R5)
         B     UPLOOP
UPDONE   STC   R4,0(R3)
         L     R14,UPRET
         BR    R14
UPRET    DS    F

ICGETBY  LR    R5,R3
         SRL   R5,1
         AR    R5,R2
         SLL   R5,2
         L     R0,0(R5)
         LR    R1,R3
         N     R1,=F'1'
         LTR   R1,R1
         BNZ   IGBODD
         SRL   R0,8
IGBODD   N     R0,=F'255'
         BR    R14

ICPUTBY  LR    R5,R3
         SRL   R5,1
         AR    R5,R2
         SLL   R5,2
         L     R0,0(R5)
         LR    R1,R3
         N     R1,=F'1'
         LTR   R1,R1
         BNZ   IPBODD
         N     R0,=F'255'
         LR    R1,R4
         SLL   R1,8
         OR    R0,R1
         ST    R0,0(R5)
         BR    R14
IPBODD   N     R0,=F'65280'
         OR    R0,R4
         ST    R0,0(R5)
         BR    R14

***********************************************************************
* STREAM LAYER / HOST ADAPTER
***********************************************************************

STRMINIT XC    CURIN,CURIN
         XC    CUROUT,CUROUT
         XC    INTINSD(SDLENGTH),INTINSD
         MVC   INTINSD+SDTYPE(4),=F'1'
         LA    R2,INTINDCB
         ST    R2,INTINSD+SDDCB
         LA    R2,INTINBUF
         ST    R2,INTINSD+SDBUF
         MVC   INTINSD+SDLEN(4),=F'80'
         XC    SYSINSD(SDLENGTH),SYSINSD
         MVC   SYSINSD+SDTYPE(4),=F'2'
         LA    R2,SYSINDCB
         ST    R2,SYSINSD+SDDCB
         LA    R2,SYSINBUF
         ST    R2,SYSINSD+SDBUF
         MVC   SYSINSD+SDLEN(4),=F'80'
         XC    SYSPRSD(SDLENGTH),SYSPRSD
         MVC   SYSPRSD+SDTYPE(4),=F'3'
         LA    R2,SYSPRDCB
         ST    R2,SYSPRSD+SDDCB
         LA    R2,SYSPOBUF+1
         ST    R2,SYSPRSD+SDBUF
         MVC   SYSPRSD+SDLEN(4),=F'132'
         XC    INTCOSD(SDLENGTH),INTCOSD
         MVC   INTCOSD+SDTYPE(4),=F'4'
         LA    R2,INTCODCB
         ST    R2,INTCOSD+SDDCB
         LA    R2,INTOBUF
         ST    R2,INTCOSD+SDBUF
         MVC   INTCOSD+SDLEN(4),=F'80'
         XC    OCODESD(SDLENGTH),OCODESD
         MVC   OCODESD+SDTYPE(4),=F'5'
         LA    R2,OCODDCB
         ST    R2,OCODESD+SDDCB
         LA    R2,OCODBUF
         ST    R2,OCODESD+SDBUF
         MVC   OCODESD+SDLEN(4),=F'80'
         XC    ICTOKLEN,ICTOKLEN
         XC    ICPEND,ICPEND
         BR    R14

FINDIN   DS    0H
         ST    R14,FINDIRET
         BAL   R14,MAKENAME
         LTR   R0,R0
         BZ    FINONE
         LA    R3,FINTAB
FILOOK   L     R5,8(R3)
         LTR   R5,R5
         BZ    FINONE
         CLC   NAMEBUF(8),0(R3)
         BE    FIMATCH
         LA    R3,12(R3)
         B     FILOOK
FIMATCH  ST    R5,FINDIMAT
         LR    R2,R5
         BAL   R14,OPENSTRM
         L     R0,FINDIMAT
         B     FIRETURN
FINONE   SR    R0,R0
FIRETURN L     R14,FINDIRET
         BR    R14
FINDIRET DS    F
FINDIMAT DS    F

FINDOUT  DS    0H
         ST    R14,FINDORET
         BAL   R14,MAKENAME
         LTR   R0,R0
         BZ    FONONE
         LA    R3,FOUTTAB
FOLOOK   L     R5,8(R3)
         LTR   R5,R5
         BZ    FONONE
         CLC   NAMEBUF(8),0(R3)
         BE    FOMATCH
         LA    R3,12(R3)
         B     FOLOOK
FOMATCH  ST    R5,FINDOMAT
         LR    R2,R5
         BAL   R14,OPENSTRM
         L     R0,FINDOMAT
         B     FORETURN
FONONE   SR    R0,R0
FORETURN L     R14,FINDORET
         BR    R14
FINDORET DS    F
FINDOMAT DS    F

***********************************************************************
* STREAM NAME NORMALIZATION
***********************************************************************
*
* BCPL FINDINPUT/FINDOUTPUT PASS A COUNTED STRING. MVS DDNAME SPACE IS
* AT MOST EIGHT CHARACTERS, SO NORMALIZE VALID REQUESTS TO AN 8-BYTE,
* SPACE-PADDED KEY. V15 USES STATIC TABLES; A LATER HOST LAYER CAN USE
* THE SAME KEY TO ALLOCATE A DCB FOR AN ARBITRARY DDNAME.
*
MAKENAME DS    0H
         MVC   NAMEBUF(8),=CL8' '
         SR    R3,R3
         IC    R3,0(R2)
         C     R3,=F'8'
         BH    MNFAIL
         SR    R4,R4
         LA    R5,NAMEBUF
MNCOPY   CR    R4,R3
         BNL   MNDONE
         SR    R0,R0
         IC    R0,1(R4,R2)
         STC   R0,0(R4,R5)
         LA    R4,1(R4)
         B     MNCOPY
MNDONE   LA    R0,1
         BR    R14
MNFAIL   SR    R0,R0
         BR    R14

SELIN    ST    R2,CURIN
         BR    R14
SELOUT   ST    R2,CUROUT
         BR    R14

HOSTRD   DS    0H
         ST    R14,HREADRET
HRDLOOP  L     R2,CURIN
         LTR   R2,R2
         BZ    HRDEOF
         L     R5,SDFLAGS(R2)
         N     R5,=F'2'
         LTR   R5,R5
         BNZ   HRDEOF
         L     R3,SDPOS(R2)
         L     R4,SDLEN(R2)
         CR    R3,R4
         BL    HRDCHAR
         BE    HRDNL
         BAL   R14,GETREC
         LTR   R0,R0
         BNZ   HRDEOF
         B     HRDLOOP
HRDCHAR  L     R5,SDBUF(R2)
         SR    R0,R0
         IC    R0,0(R3,R5)
         LA    R3,1(R3)
         ST    R3,SDPOS(R2)
         B     HRDRTN
HRDNL    LA    R3,1(R3)
         ST    R3,SDPOS(R2)
         LA    R0,21
         B     HRDRTN
HRDEOF   L     R0,=F'-1'
HRDRTN   L     R14,HREADRET
         BR    R14
HREADRET DS    F

HOSTWR   DS    0H
         ST    R14,HWRRET
         ST    R2,HWRCHAR
         L     R4,CUROUT
         LTR   R4,R4
         BZ    HWRDONE
         L     R5,SDTYPE(R4)
         C     R5,=F'4'
         BNE   HWRNORM
         L     R2,HWRCHAR
         BAL   R14,ICOUTWR
         B     HWRDONE
HWRNORM  L     R2,HWRCHAR
         CH    R2,=H'21'
         BE    HWRFLUSH
         L     R3,SDPOS(R4)
         L     R5,SDLEN(R4)
         CR    R3,R5
         BL    HWRSTORE
         LR    R2,R4
         BAL   R14,PUTREC
         L     R3,SDPOS(R4)
         L     R2,HWRCHAR
HWRSTORE L     R5,SDBUF(R4)
         STC   R2,0(R3,R5)
         LA    R3,1(R3)
         ST    R3,SDPOS(R4)
         B     HWRDONE
HWRFLUSH LR    R2,R4
         BAL   R14,PUTREC
HWRDONE  L     R14,HWRRET
         BR    R14
HWRRET   DS    F
HWRCHAR  DS    F

***********************************************************************
* INTCODE OUTPUT ADAPTER
***********************************************************************
*
* CGI'S WR() USES '/' + NEWLINE AS A SOFT CONTINUATION WHEN ITS
* LOGICAL LINE REACHES COLUMN 71. ICOUTWR SUPPRESSES ONLY THAT TWO-
* CHARACTER SEQUENCE. CHARACTERS ARE ACCUMULATED INTO A TOKEN BUFFER;
* PHYSICAL 80-BYTE RECORDS ARE FORMED ONLY BETWEEN TOKENS.
*
ICOUTWR  DS    0H
         ST    R14,ICWRET
         STM   R6,R9,ICWSAVE
         ST    R2,ICWSAVC
         CLI   ICPEND,1
         BNE   ICWNOPND
         MVI   ICPEND,0
         CH    R2,=H'21'
         BE    ICWRTN
* PENDING SLASH WAS LITERAL: APPEND IT BEFORE CURRENT CHARACTER.
         LA    R2,97
         BAL   R14,ICTOKCHR
         L     R2,ICWSAVC
ICWNOPND STC   R2,ICWTEMP
         CLI   ICWTEMP,C'/'
         BNE   ICWNOTSL
         MVI   ICPEND,1
         B     ICWRTN
ICWNOTSL CH    R2,=H'21'
         BNE   ICWNOTNL
         BAL   R14,ICCOMMIT
         LA    R2,INTCOSD
         BAL   R14,PUTREC
         B     ICWRTN
ICWNOTNL CLI   ICWTEMP,C' '
         BNE   ICWAPPND
         BAL   R14,ICCOMMIT
         B     ICWRTN
ICWAPPND L     R2,ICWSAVC
         BAL   R14,ICTOKCHR
ICWRTN   LM    R6,R9,ICWSAVE
         L     R14,ICWRET
         BR    R14
ICWRET   DS    F
ICWSAVE  DS    4F
ICWSAVC  DS    F
ICWTEMP  DS    X
         DS    0F

ICTOKCHR L     R3,ICTOKLEN
         C     R3,=F'80'
         BNL   ICTCRTN
         LA    R5,ICTOKBUF
         STC   R2,0(R3,R5)
         LA    R3,1(R3)
         ST    R3,ICTOKLEN
ICTCRTN  BR    R14

ICCOMMIT DS    0H
         ST    R14,ICCRET
         STM   R6,R9,ICCSAVE
         L     R6,ICTOKLEN
         LTR   R6,R6
         BZ    ICCRTN
         LA    R2,INTCOSD
         L     R7,SDPOS(R2)
         LR    R8,R6
         LTR   R7,R7
         BZ    ICCNEED
         LA    R8,1(R8)
ICCNEED  AR    R8,R7
         C     R8,=F'80'
         BNH   ICCCOPY
         BAL   R14,PUTREC
         SR    R7,R7
ICCCOPY  LTR   R7,R7
         BZ    ICCNOSPC
         LA    R5,INTOBUF
         LR    R1,R5
         AR    R1,R7
         MVI   0(R1),C' '
         LA    R7,1(R7)
ICCNOSPC SR    R8,R8
         LA    R4,ICTOKBUF
         LA    R5,INTOBUF
ICCLOOP  CR    R8,R6
         BNL   ICCDONE
         SR    R3,R3
         IC    R3,0(R8,R4)
         STC   R3,0(R7,R5)
         LA    R8,1(R8)
         LA    R7,1(R7)
         B     ICCLOOP
ICCDONE  LA    R2,INTCOSD
         ST    R7,SDPOS(R2)
         XC    ICTOKLEN,ICTOKLEN
ICCRTN   LM    R6,R9,ICCSAVE
         L     R14,ICCRET
         BR    R14
ICCRET   DS    F
ICCSAVE  DS    4F

ENDREAD  DS    0H
         ST    R14,ERRET
         L     R2,CURIN
         LTR   R2,R2
         BZ    ERDONE
         BAL   R14,CLOSESTR
ERDONE   XC    CURIN,CURIN
         L     R14,ERRET
         BR    R14
ERRET    DS    F

ENDWRITE DS    0H
         ST    R14,EWRET
         L     R2,CUROUT
         LTR   R2,R2
         BZ    EWDONE
         L     R5,SDTYPE(R2)
         C     R5,=F'4'
         BNE   EWNORMAL
         CLI   ICPEND,1
         BNE   EWICCOM
         MVI   ICPEND,0
         LA    R2,97
         BAL   R14,ICTOKCHR
EWICCOM  BAL   R14,ICCOMMIT
         LA    R2,INTCOSD
         L     R3,SDPOS(R2)
         LTR   R3,R3
         BZ    EWCLOSE
         BAL   R14,PUTREC
         B     EWCLOSE
EWNORMAL L     R3,SDPOS(R2)
         LTR   R3,R3
         BZ    EWCLOSE
         BAL   R14,PUTREC
EWCLOSE  L     R2,CUROUT
         BAL   R14,CLOSESTR
EWDONE   XC    CUROUT,CUROUT
         L     R14,EWRET
         BR    R14
EWRET    DS    F

WRITES   DS    0H
         ST    R14,WSRET
         STM   R6,R9,WSSAVE
         LR    R7,R2
         SR    R6,R6
         IC    R6,0(R7)
         SR    R8,R8
WSLOOP   CR    R8,R6
         BNL   WSDONE
         SR    R2,R2
         IC    R2,1(R8,R7)
         BAL   R14,HOSTWR
         LA    R8,1(R8)
         B     WSLOOP
WSDONE   LM    R6,R9,WSSAVE
         L     R14,WSRET
         BR    R14
WSRET    DS    F
WSSAVE   DS    4F

WRITEF   DS    0H
         ST    R14,WFRET
         STM   R6,R9,WFSAVE
         ST    R3,WFARG1
         ST    R4,WFARG2
         ST    R5,WFARG3
         LR    R6,R2
         SR    R7,R7
         IC    R7,0(R6)
         SR    R8,R8
         SR    R9,R9
WFLOOP   CR    R8,R7
         BNL   WFDONE
         SR    R2,R2
         IC    R2,1(R8,R6)
         LA    R8,1(R8)
         STC   R2,WFCHAR
         CLI   WFCHAR,C'%'
         BE    WFPCT
         BAL   R14,HOSTWR
         B     WFLOOP
WFPCT    CR    R8,R7
         BNL   WFPCTLIT
         SR    R2,R2
         IC    R2,1(R8,R6)
         LA    R8,1(R8)
         STC   R2,WFCHAR
         CLI   WFCHAR,C'N'
         BE    WFNUMCV
         CLI   WFCHAR,C'C'
         BE    WFCHRCV
WFPCTUNK LA    R2,108
         BAL   R14,HOSTWR
         SR    R2,R2
         IC    R2,WFCHAR
         BAL   R14,HOSTWR
         B     WFLOOP
WFPCTLIT LA    R2,108
         BAL   R14,HOSTWR
         B     WFLOOP
WFNUMCV  BAL   R14,WFGETARG
         LR    R2,R0
         BAL   R14,WFNUMBER
         B     WFLOOP
WFCHRCV  BAL   R14,WFGETARG
         LR    R2,R0
         BAL   R14,HOSTWR
         B     WFLOOP
WFDONE   LM    R6,R9,WFSAVE
         L     R14,WFRET
         BR    R14
WFRET    DS    F
WFSAVE   DS    4F
WFARG1   DS    F
WFARG2   DS    F
WFARG3   DS    F
WFCHAR   DS    X
         DS    0F

WFGETARG C     R9,=F'0'
         BE    WFGA1
         C     R9,=F'1'
         BE    WFGA2
         C     R9,=F'2'
         BE    WFGA3
         SR    R0,R0
         B     WFGARTN
WFGA1    L     R0,WFARG1
         B     WFGARTN
WFGA2    L     R0,WFARG2
         B     WFGARTN
WFGA3    L     R0,WFARG3
WFGARTN  LA    R9,1(R9)
         BR    R14

WFNUMBER ST    R14,WFNRET
         XC    WFNNEG,WFNNEG
         LTR   R2,R2
         BZ    WFNZERO
         BM    WFNISNEG
         LCR   R2,R2
         B     WFNSET
WFNISNEG MVI   WFNNEG,1
WFNSET   ST    R2,WFNVAL
         LA    R5,WFNBUF+12
         ST    R5,WFNEND
WFNDIG   BCTR  R5,0
         L     R3,WFNVAL
         LR    R2,R3
         SRA   R2,31
         D     R2,=F'10'
         ST    R3,WFNVAL
         LCR   R4,R2
         A     R4,=F'240'
         STC   R4,0(R5)
         LTR   R3,R3
         BNZ   WFNDIG
         CLI   WFNNEG,1
         BNE   WFNOUT
         BCTR  R5,0
         MVI   0(R5),C'-'
         B     WFNOUT
WFNZERO  LA    R5,WFNBUF+11
         MVI   0(R5),C'0'
         LA    R1,WFNBUF+12
         ST    R1,WFNEND
WFNOUT   ST    R5,WFNPOS
WFNPUT   L     R5,WFNPOS
         C     R5,WFNEND
         BNL   WFNRTN
         SR    R2,R2
         IC    R2,0(R5)
         BAL   R14,HOSTWR
         L     R5,WFNPOS
         LA    R5,1(R5)
         ST    R5,WFNPOS
         B     WFNPUT
WFNRTN   L     R14,WFNRET
         BR    R14
         DS    0F
WFNRET   DS    F
WFNVAL   DS    F
WFNPOS   DS    F
WFNEND   DS    F
WFNNEG   DS    X
         DS    0F
WFNBUF   DS    CL12

OPENSTRM DS    0H
         ST    R14,OSRET
         L     R5,SDFLAGS(R2)
         N     R5,=F'1'
         LTR   R5,R5
         BNZ   OSRETURN
         L     R5,SDTYPE(R2)
         C     R5,=F'1'
         BE    OSINTIN
         C     R5,=F'2'
         BE    OSSYSIN
         C     R5,=F'3'
         BE    OSSYSPR
         C     R5,=F'4'
         BE    OSINTCO
         C     R5,=F'5'
         BE    OSOCODE
         B     OSRETURN
OSINTIN  OPEN  (INTINDCB,(INPUT))
         B     OSOPENED
OSSYSIN  OPEN  (SYSINDCB,(INPUT))
         B     OSOPENED
OSSYSPR  OPEN  (SYSPRDCB,(OUTPUT))
         B     OSOPENED
OSINTCO  OPEN  (INTCODCB,(OUTPUT))
         XC    ICTOKLEN,ICTOKLEN
         XC    ICPEND,ICPEND
         B     OSOPENED
OSOCODE  OPEN  (OCODDCB,(OUTPUT))
OSOPENED L     R5,SDFLAGS(R2)
         O     R5,=F'1'
         N     R5,=F'-3'
         ST    R5,SDFLAGS(R2)
         L     R5,SDTYPE(R2)
         C     R5,=F'3'
         BE    OSOUTPUT
         C     R5,=F'4'
         BE    OSOUTPUT
         C     R5,=F'5'
         BE    OSOUTPUT
         L     R5,SDLEN(R2)
         LA    R5,1(R5)
         ST    R5,SDPOS(R2)
         B     OSRETURN
OSOUTPUT XC    SDPOS(4,R2),SDPOS(R2)
OSRETURN L     R14,OSRET
         BR    R14
OSRET    DS    F

GETREC   DS    0H
         ST    R14,GRRET
         ST    R2,GRCUR
         L     R5,SDTYPE(R2)
         C     R5,=F'1'
         BE    GRINTIN
         C     R5,=F'2'
         BE    GRSYSIN
         B     GREOF
GRINTIN  GET   INTINDCB,INTINBUF
         B     GROK
GRSYSIN  GET   SYSINDCB,SYSINBUF
GROK     L     R2,GRCUR
         XC    SDPOS(4,R2),SDPOS(R2)
         MVC   SDLEN(4,R2),=F'80'
         SR    R0,R0
         L     R14,GRRET
         BR    R14
GREOF    LA    R0,1
         L     R14,GRRET
         BR    R14
GRRET    DS    F
GRCUR    DS    F
INTIEOF  L     R2,GRCUR
         L     R5,SDFLAGS(R2)
         O     R5,=F'2'
         ST    R5,SDFLAGS(R2)
         B     GREOF
SYSIEOF  L     R2,GRCUR
         L     R5,SDFLAGS(R2)
         O     R5,=F'2'
         ST    R5,SDFLAGS(R2)
         B     GREOF

PUTREC   DS    0H
         ST    R14,PRRET
         ST    R2,PRCUR
         L     R5,SDTYPE(R2)
         C     R5,=F'4'
         BE    PRINTCO
         C     R5,=F'5'
         BE    PROCODE
         C     R5,=F'3'
         BNE   PRRETURN
         L     R3,SDPOS(R2)
         C     R3,=F'132'
         BNL   PRPUT
         L     R5,SDBUF(R2)
PRPAD    C     R3,=F'132'
         BNL   PRPUT
         LR    R1,R5
         AR    R1,R3
         MVI   0(R1),C' '
         LA    R3,1(R3)
         B     PRPAD
PRPUT    MVI   SYSPOBUF,C' '
         PUT   SYSPRDCB,SYSPOBUF
         XC    SDPOS(4,R2),SDPOS(R2)
         B     PRRETURN
PRINTCO  L     R3,SDPOS(R2)
         LTR   R3,R3
         BZ    PRRETURN
         LA    R5,INTOBUF
PRICPAD  C     R3,=F'80'
         BNL   PRICPUT
         LR    R1,R5
         AR    R1,R3
         MVI   0(R1),C' '
         LA    R3,1(R3)
         B     PRICPAD
PRICPUT  PUT   INTCODCB,INTOBUF
         L     R2,PRCUR
         XC    SDPOS(4,R2),SDPOS(R2)
         B     PRRETURN
PROCODE  L     R3,SDPOS(R2)
         LTR   R3,R3
         BZ    PRRETURN
         LA    R5,OCODBUF
PROCPAD  C     R3,=F'80'
         BNL   PROCPUT
         LR    R1,R5
         AR    R1,R3
         MVI   0(R1),C' '
         LA    R3,1(R3)
         B     PROCPAD
PROCPUT  PUT   OCODDCB,OCODBUF
         L     R2,PRCUR
         XC    SDPOS(4,R2),SDPOS(R2)
PRRETURN L     R14,PRRET
         BR    R14
PRRET    DS    F
PRCUR    DS    F

CLOSESTR DS    0H
         ST    R14,CSRET
         ST    R2,CSCUR
         L     R5,SDFLAGS(R2)
         N     R5,=F'1'
         LTR   R5,R5
         BZ    CSRETURN
         L     R5,SDTYPE(R2)
         C     R5,=F'1'
         BE    CSINTIN
         C     R5,=F'2'
         BE    CSSYSIN
         C     R5,=F'3'
         BE    CSSYSPR
         C     R5,=F'4'
         BE    CSINTCO
         C     R5,=F'5'
         BE    CSOCODE
         B     CSRETURN
CSINTIN  CLOSE (INTINDCB)
         B     CSCLOSED
CSSYSIN  CLOSE (SYSINDCB)
         B     CSCLOSED
CSSYSPR  CLOSE (SYSPRDCB)
         B     CSCLOSED
CSINTCO  CLI   ICPEND,1
         BNE   CSICCOM
         MVI   ICPEND,0
         LA    R2,97
         BAL   R14,ICTOKCHR
CSICCOM  BAL   R14,ICCOMMIT
         LA    R2,INTCOSD
         L     R3,SDPOS(R2)
         LTR   R3,R3
         BZ    CSICCLOS
         BAL   R14,PUTREC
CSICCLOS CLOSE (INTCODCB)
         B     CSCLOSED
CSOCODE  L     R3,SDPOS(R2)
         LTR   R3,R3
         BZ    CSOCCLOS
         BAL   R14,PUTREC
CSOCCLOS CLOSE (OCODDCB)
CSCLOSED L     R2,CSCUR
         XC    SDFLAGS(4,R2),SDFLAGS(R2)
CSRETURN L     R14,CSRET
         BR    R14
CSRET    DS    F
CSCUR    DS    F

CLOSEALL DS    0H
         ST    R14,CARET
         LA    R2,INTINSD
         BAL   R14,CLOSESTR
         LA    R2,SYSINSD
         BAL   R14,CLOSESTR
         LA    R2,SYSPRSD
         BAL   R14,CLOSESTR
         LA    R2,INTCOSD
         BAL   R14,CLOSESTR
         LA    R2,OCODESD
         BAL   R14,CLOSESTR
         L     R14,CARET
         BR    R14
CARET    DS    F

***********************************************************************
* MAPSTORE - V13 RECONSTRUCTED POSTMORTEM DIAGNOSTIC
***********************************************************************
MAPSTORE DS    0H
         ST    R14,MSRET
         STM   R6,R9,MSSAVE
         L     R2,SYSPRINT
         BAL   R14,SELOUT
         LA    R2,MSHEAD
         BAL   R14,WRITES
         L     R14,MSRET
         LM    R6,R9,MSSAVE
         BR    R14
MSRET    DS    F
MSSAVE   DS    4F

***********************************************************************
* INTEGER HELPERS
***********************************************************************
DIVINT   L     R3,B
         LR    R2,R3
         SRA   R2,31
         D     R2,A
         LR    R0,R3
         BR    R14
REMINT   L     R3,B
         LR    R2,R3
         SRA   R2,31
         D     R2,A
         LR    R0,R2
         BR    R14
SHLINT   L     R0,B
         L     R1,A
         SLL   R0,0(R1)
         BR    R14
SHRINT   L     R0,B
         L     R1,A
         SRL   R0,0(R1)
         BR    R14

***********************************************************************
* GLOBALS / STREAMS / DCB / TABLES
***********************************************************************
         DS    0F
SYSPRINT DS    F
SOURCE   DS    F
ETOA     DS    F
ATOE     DS    F
LABBASE  DS    F
GLOBBASE DS    F
PROGBASE DS    F
PROGWORD DS    F
LABV     DS    F
G        DS    F
P        DS    F
CH       DS    X
CHEOF    DS    X
         DS    0F
CYCCNT   DS    F
CP       DS    F
A        DS    F
B        DS    F
C        DS    F
D        DS    F
W        DS    F
FVAR     DS    F
CURIN    DS    F
CUROUT   DS    F
STKBASE  DS    F
GUSED    DS    CL401
         DS    0F
INTINSD  DS    CL24
SYSINSD  DS    CL24
SYSPRSD  DS    CL24
INTCOSD  DS    CL24
OCODESD  DS    CL24
ICTOKLEN DS    F
ICPEND   DS    X
         DS    0F

INTINDCB DCB   DDNAME=INTIN,DSORG=PS,MACRF=GM,EODAD=INTIEOF
SYSINDCB DCB   DDNAME=SYSIN,DSORG=PS,MACRF=GM,EODAD=SYSIEOF
SYSPRDCB DCB   DDNAME=SYSPRINT,DSORG=PS,MACRF=PM
INTCODCB DCB   DDNAME=INTCODE,DSORG=PS,MACRF=PM
OCODDCB  DCB   DDNAME=OCODE,DSORG=PS,MACRF=PM
INTINBUF DS    CL80
SYSINBUF DS    CL80
SYSPOBUF DS    CL133
INTOBUF  DS    CL80
OCODBUF  DS    CL80
ICTOKBUF DS    CL80

         DS    0F
FINTAB   DC    CL8'INTIN',A(INTINSD)
         DC    CL8'SYSIN',A(SYSINSD)
         DC    CL8' ',A(0)
FOUTTAB  DC    CL8'SYSPRINT',A(SYSPRSD)
         DC    CL8'INTCODE',A(INTCOSD)
         DC    CL8'OCODE',A(OCODESD)
         DC    CL8' ',A(0)
NAMEBUF  DS    CL8

SYSPRNAM DC    AL1(8),C'SYSPRINT'
INTCONAM DC    AL1(7),C'INTCODE'
OCODENAM DC    AL1(5),C'OCODE'
INTINNAM DC    AL1(5),C'INTIN'
SYSINNAM DC    AL1(5),C'SYSIN'
ENTERMSG DC    AL1(23),C'INTCODE SYSTEM ENTERED',X'15'
BADCHMSG DC    AL1(21),X'15',C'BAD CH %C AT P = %N',X'15'
BADCDMSG DC    AL1(20),X'15',C'BAD CODE AT P = %N',X'15'
UNSETMSG DC    AL1(10),C'L%N UNSET',X'15'
ALSETMSG DC    AL1(32),C'L%N ALREADY SET TO %N AT P = %N',X'15'
INTEMSG  DC    AL1(25),X'15',C'INTCODE ERROR AT C = %N',X'15'
SIZEMSG  DC    AL1(19),X'15',C'PROGRAM SIZE = %N',X'15'
EXECMSG  DC    AL1(35),X'15',X'15'
         DC    C'EXECUTION CYCLES = %N, CODE = %N',X'15'
MSHEAD   DC    AL1(24),X'15',C'*** ICINT MAPSTORE ***',X'15'
         LTORG
         END   ICINT
