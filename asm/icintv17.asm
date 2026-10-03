         TITLE 'ICINT V17 - RICHARDS INTCODE ASSEMBLER/INTERPRETER'
         PRINT NOGEN
*
* STRUCTURAL SYSTEM/370 TRANSLATION OF
* RICHARDS-BCPLTAPE/MR10/BCPLKIT/ICINT.
*
* V17 INVALID-ADDRESS TRACE DIAGNOSTICS
*
* BASE:
*   ICINT V15. INTCODE EXECUTION AND INTCODE OUTPUT SEMANTICS ARE
*   INTENDED TO BE UNCHANGED.
*
* V17 SCOPE:
*   - RETAIN V16 STREAM AND CHARACTER-TRANSLATION BEHAVIOR.
*   - RECORD THE EIGHT MOST RECENT DECODED INTCODE INSTRUCTIONS.
*   - GUARD OP1 STORES AGAINST ADDRESSES OUTSIDE BCPL PROGRAM/GLOBAL
*     STORAGE; DUMP THE TRACE AND RETURN CODE -2 INSTEAD OF S0C4.
*
* V16 SCOPE:
*   - RETAIN V15 ARBITRARY DDNAME DISCOVERY.
*   - REPLACE FIXED GENERIC INPUT/OUTPUT POOLS WITH GETMAIN OBJECTS.
*   - KEEP INTIN, SYSPRINT, AND INTCODE AS SPECIAL STATIC STREAMS.
*   - RETURN ZERO WHEN A REQUESTED DDNAME IS NOT ALLOCATED OR WHEN A
*     CONDITIONAL GETMAIN REQUEST CANNOT BE SATISFIED.
*   - RELEASE ORDINARY STREAM STORAGE ON ENDREAD/ENDWRITE.
*   - RETAIN V14/V15 INTCODE RECORDIZATION UNCHANGED.
*   - USE 80-BYTE TEXT RECORDS FOR DISCOVERED INPUT/OUTPUT STREAMS.
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
*   - V15 FACTORIAL AND INTCODE OUTPUT MUST REMAIN UNCHANGED.
*   - FINDOUTPUT("OCODE") MUST DISCOVER //OCODE WITHOUT OCODE CODE.
*   - OCODE RECORDS MUST BE DIRECTLY REUSABLE AS CGI //SYSIN INPUT.
*   - ARBITRARY VALID DDNAME STREAMS MUST USE THE SAME DISCOVERY PATH.
*   - GENERIC STREAM COUNT MUST NOT BE LIMITED BY STATIC SLOT COUNT.
*
* OBJECTIVES:
*   - KEEP THE ICINT LOGIC CLOSE TO THE ORIGINAL BCPL.
*   - KEEP MVS RECORD I/O BELOW A BCPL STREAM INTERFACE.
*   - MAKE THE BOOTSTRAP STREAM IMPLEMENTATION USEFUL AS A MODEL FOR
*     THE LATER NATIVE BCPL/MVS RUNTIME.
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
***********************************************************************
* INTCODE MANIFEST CONSTANTS
***********************************************************************
FSHIFT   EQU   13
IBIT     EQU   X'1000'
PBIT     EQU   X'0800'
GBIT     EQU   X'0400'
DBIT     EQU   X'0200'
ABITS    EQU   X'01FF'
WORDSIZE EQU   16
BYTESIZE EQU   8
LIG1     EQU   X'1401'
K2       EQU   X'C002'
X22V     EQU   X'E016'
***********************************************************************
* DYNAMIC BCPL VECTOR SIZES
***********************************************************************
LABVCNT  EQU   501
GLOBCNT  EQU   401
PROGCNT  EQU   20001
LABVLEN  EQU   LABVCNT*4
GLOBLEN  EQU   GLOBCNT*4
PROGLEN  EQU   PROGCNT*4
***********************************************************************
* HOST STREAM DESCRIPTOR
***********************************************************************
SDTYPE   EQU   0
SDDCB    EQU   4
SDBUF    EQU   8
SDPOS    EQU   12
SDLEN    EQU   16
SDFLAGS  EQU   20
SDNAME   EQU   24
SDLENGTH EQU   32
* DYNAMIC STREAMS EXTEND THE V15 32-BYTE DESCRIPTOR WITH A LINK WORD.
* THE DCB STARTS AT OFFSET 40 SO IT REMAINS DOUBLEWORD ALIGNED WHEN THE
* GETMAIN OBJECT ITSELF IS DOUBLEWORD ALIGNED.
SDNEXT   EQU   32
DYNSDLEN EQU   40
DYDCBOFF EQU   40
STINTIN  EQU   1
STGENIN  EQU   2
STSYSPR  EQU   3
STINTCO  EQU   4
STGENOUT EQU   5
DDNAMOFF EQU   40
***********************************************************************
* PROGRAM ENTRY
***********************************************************************
         STM   R14,R12,12(R13)
         LR    R12,R15
         USING ICINT,R12
         LA    R11,4095(R12)
         LA    R11,1(R11)
         USING ICINT+4096,R11
         LA    R10,4095(R11)
         LA    R10,1(R10)
         USING ICINT+8192,R10
         ST    R13,MAINSAVE+4
         LA    R0,MAINSAVE
         ST    R0,8(R13)
         LR    R13,R0
***********************************************************************
* OBTAIN LARGE BCPL VECTORS
***********************************************************************
         GETMAIN R,LV=LABVLEN
         ST    R1,LABBASE
         ST    R1,LABV
         GETMAIN R,LV=GLOBLEN
         ST    R1,GLOBBASE
         LR    R2,R1
         SRL   R2,2
         ST    R2,G
         GETMAIN R,LV=PROGLEN
         ST    R1,PROGBASE
         LR    R2,R1
         SRL   R2,2
         ST    R2,PROGWORD
         ST    R2,P
         BAL   R14,STRMINIT
         XC    GUSED(256),GUSED
         XC    GUSED+256(145),GUSED+256
***********************************************************************
* BCPL STARTUP SEQUENCE
***********************************************************************
         LA    R2,SYSPRNAM
         BAL   R14,FINDOUT
         ST    R0,SYSPRINT
         LR    R2,R0
         BAL   R14,SELOUT
         LA    R2,ENTERMSG
         BAL   R14,WRITES
         LA    R2,INTINNAM
         BAL   R14,FINDIN
         ST    R0,SOURCE
         LR    R2,R0
         BAL   R14,SELIN
         BAL   R14,ASSEMBLE
         LA    R2,SYSINNAM
         BAL   R14,FINDIN
         ST    R0,SOURCE
         LTR   R0,R0
         BZ    NOSYSIN
         LR    R2,R0
         BAL   R14,SELIN
NOSYSIN  LA    R2,SIZEMSG
         L     R3,P
         S     R3,PROGWORD
         BAL   R14,WRITEF
         LA    R2,ATOETAB+4
         ST    R2,ATOE
         LA    R2,ETOATAB+4
         ST    R2,ETOA
         L     R2,P
         ST    R2,STKBASE
         LA    R2,INITCODE
         SRL   R2,2
         ST    R2,C
         XC    CYCCNT,CYCCNT
         XC    TRIDX,TRIDX
         XC    TRBUF(192),TRBUF
         BAL   R14,INTERPRT
         ST    R0,A
         L     R2,SYSPRINT
         BAL   R14,SELOUT
         LA    R2,EXECMSG
         L     R3,CYCCNT
         L     R4,A
         BAL   R14,WRITEF
         L     R2,A
         LTR   R2,R2
         BNM   MAINEND
         BAL   R14,MAPSTORE
MAINEND  BAL   R14,CLOSEALL
         L     R1,PROGBASE
         FREEMAIN R,LV=PROGLEN,A=(R1)
         L     R1,GLOBBASE
         FREEMAIN R,LV=GLOBLEN,A=(R1)
         L     R1,LABBASE
         FREEMAIN R,LV=LABVLEN,A=(R1)
         L     R13,4(R13)
         XC    8(4,R13),8(R13)
         RETURN (14,12),RC=0
MAINSAVE DS    18F
***********************************************************************
* ASSEMBLE
***********************************************************************
ASSEMBLE DS    0H
         ST    R14,ASMRET
         STM   R6,R9,ASMSAVE
         XC    FVAR,FVAR
ACLEAR   SR    R4,R4
ACLRTST  C     R4,=F'500'
         BH    ACLRDONE
         L     R2,LABV
         LR    R3,R4
         SLL   R3,2
         SR    R5,R5
         ST    R5,0(R3,R2)
         LA    R4,1(R4)
         B     ACLRTST
ACLRDONE XC    CP,CP
ANEXT    BAL   R14,RCH
ASW      CLI   CHEOF,1
         BE    ASMRTN
         CLI   CH,C'0'
         BL    ASW1
         CLI   CH,C'9'
         BNH   ADIGIT
ASW1     CLI   CH,C'$'
         BE    ANEXT
         CLI   CH,C' '
         BE    ANEXT
         CLI   CH,X'15'
         BE    ANEXT
         CLI   CH,C'L'
         BE    CASEL
         CLI   CH,C'S'
         BE    CASES
         CLI   CH,C'A'
         BE    CASEA
         CLI   CH,C'J'
         BE    CASEJ
         CLI   CH,C'T'
         BE    CASET
         CLI   CH,C'F'
         BE    CASEF
         CLI   CH,C'K'
         BE    CASEK
         CLI   CH,C'X'
         BE    CASEX
         CLI   CH,C'C'
         BE    CASEC
         CLI   CH,C'D'
         BE    CASED
         CLI   CH,C'G'
         BE    CASEG
         CLI   CH,C'Z'
         BE    CASEZ
         B     ADEFAULT
ADEFAULT LA    R2,BADCHMSG
         SR    R3,R3
         IC    R3,CH
         L     R4,P
         S     R4,PROGWORD
         BAL   R14,WRITEF
         B     ANEXT
ADIGIT   BAL   R14,RDN
         LR    R2,R0
         BAL   R14,SETLAB
         XC    CP,CP
         B     ASW
CASEL    XC    FVAR,FVAR
         B     AINST
CASES    MVC   FVAR,=F'1'
         B     AINST
CASEA    MVC   FVAR,=F'2'
         B     AINST
CASEJ    MVC   FVAR,=F'3'
         B     AINST
CASET    MVC   FVAR,=F'4'
         B     AINST
CASEF    MVC   FVAR,=F'5'
         B     AINST
CASEK    MVC   FVAR,=F'6'
         B     AINST
CASEX    MVC   FVAR,=F'7'
         B     AINST
CASEC    BAL   R14,RCH
         BAL   R14,RDN
         LR    R2,R0
         BAL   R14,STC
         B     ASW
CASED    BAL   R14,RCH
         CLI   CH,C'L'
         BE    CADLAB
         BAL   R14,RDN
         LR    R2,R0
         BAL   R14,STW
         B     ASW
CADLAB   BAL   R14,RCH
         SR    R2,R2
         BAL   R14,STW
         BAL   R14,RDN
         LR    R2,R0
         L     R3,P
         BCTR  R3,0
         SLL   R3,2
         BAL   R14,LABREF
         B     ASW
CASEG    BAL   R14,RCH
         BAL   R14,RDN
         LR    R3,R0
         LA    R5,GUSED
         AR    R5,R3
         MVI   0(R5),1
         L     R2,G
         AR    R2,R3
         SLL   R2,2
         ST    R2,A
         CLI   CH,C'L'
         BE    CAGLAB
         LA    R2,BADCDMSG
         L     R3,P
         S     R3,PROGWORD
         BAL   R14,WRITEF
         B     CAGCONT
CAGLAB   BAL   R14,RCH
CAGCONT  L     R2,A
         SR    R3,R3
         ST    R3,0(R2)
         BAL   R14,RDN
         LR    R2,R0
         L     R3,A
         BAL   R14,LABREF
         B     ASW
CASEZ    SR    R8,R8
AZTEST   C     R8,=F'500'
         BH    AZDONE
         L     R2,LABV
         LR    R3,R8
         SLL   R3,2
         L     R5,0(R4,R3)
         LTR   R5,R5
         BNP   AZNEXT
         LA    R2,UNSETMSG
         LR    R3,R8
         BAL   R14,WRITEF
AZNEXT   LA    R8,1(R8)
         B     AZTEST
AZDONE   B     ACLEAR
AINST    L     R2,FVAR
         SLL   R2,FSHIFT
         ST    R2,W
         BAL   R14,RCH
         CLI   CH,C'I'
         BNE   ACHKP
         L     R2,W
         A     R2,=F'4096'
         ST    R2,W
         BAL   R14,RCH
ACHKP    CLI   CH,C'P'
         BNE   ACHKG
         L     R2,W
         A     R2,=F'2048'
         ST    R2,W
         BAL   R14,RCH
ACHKG    CLI   CH,C'G'
         BNE   ACHKL
         L     R2,W
         A     R2,=F'1024'
         ST    R2,W
         BAL   R14,RCH
ACHKL    CLI   CH,C'L'
         BE    AOPLAB
         BAL   R14,RDN
         ST    R0,A
         L     R3,W
         N     R3,=F'1024'
         LTR   R3,R3
         BZ    AUSEDOK
         L     R3,A
         C     R3,=F'0'
         BL    AUSEDOK
         C     R3,=F'400'
         BH    AUSEDOK
         LA    R5,GUSED
         AR    R5,R3
         MVI   0(R5),1
AUSEDOK  LR    R3,R0
         N     R3,=F'511'
         CR    R3,R0
         BE    AOPSHORT
         L     R2,W
         A     R2,=F'512'
         BAL   R14,STW
         L     R2,A
         BAL   R14,STW
         B     ASW
AOPSHORT L     R2,W
         A     R2,A
         BAL   R14,STW
         B     ASW
AOPLAB   BAL   R14,RCH
         L     R2,W
         A     R2,=F'512'
         BAL   R14,STW
         SR    R2,R2
         BAL   R14,STW
         BAL   R14,RDN
         LR    R2,R0
         L     R3,P
         BCTR  R3,0
         SLL   R3,2
         BAL   R14,LABREF
         B     ASW
ASMRTN   LM    R6,R9,ASMSAVE
         L     R14,ASMRET
         BR    R14
ASMRET   DS    F
ASMSAVE  DS    4F
***********************************************************************
* STW / STC / INPUT HELPERS
***********************************************************************
STW      DS    0H
         L     R3,P
         LR    R4,R3
         SLL   R4,2
         ST    R2,0(R4)
         LA    R3,1(R3)
         ST    R3,P
         XC    CP,CP
         BR    R14
STC      DS    0H
         ST    R14,STCRET
         ST    R7,STCSV7
         LR    R7,R2
         L     R3,CP
         LTR   R3,R3
         BNZ   STCHAVE
         SR    R2,R2
         BAL   R14,STW
         MVC   CP,=F'16'
STCHAVE  L     R3,CP
         S     R3,=F'8'
         ST    R3,CP
         LR    R4,R7
         SLL   R4,0(R3)
         L     R2,P
         BCTR  R2,0
         SLL   R2,2
         L     R5,0(R2)
         AR    R5,R4
         ST    R5,0(R2)
         L     R7,STCSV7
         L     R14,STCRET
         BR    R14
STCRET   DS    F
STCSV7   DS    F
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
         STM   R7,R9,RDNSAVE
         SR    R7,R7
         SR    R8,R8
         CLI   CH,C'-'
         BNE   RDNTST
         LA    R8,1
         BAL   R14,RCH
RDNTST   CLI   CH,C'0'
         BL    RDNDONE
         CLI   CH,C'9'
         BH    RDNDONE
         LR    R3,R7
         SLL   R7,3
         SLL   R3,1
         AR    R7,R3
         SR    R2,R2
         IC    R2,CH
         S     R2,=F'240'
         AR    R7,R2
         BAL   R14,RCH
         B     RDNTST
RDNDONE  LTR   R8,R8
         BZ    RDNPOS
         LCR   R7,R7
RDNPOS   LR    R0,R7
         LM    R7,R9,RDNSAVE
         L     R14,RDNRET
         BR    R14
RDNRET   DS    F
RDNSAVE  DS    3F
SETLAB   DS    0H
         ST    R14,SETRET
         ST    R8,SETSV8
         LR    R8,R2
         L     R3,LABV
         LR    R4,R8
         SLL   R4,2
         L     R5,0(R4,R3)
         LTR   R5,R5
         BNM   SETWHIL
         ST    R5,SETK
         LA    R2,ALSETMSG
         LR    R3,R8
         LCR   R4,R5
         L     R5,P
         S     R5,PROGWORD
         BAL   R14,WRITEF
         L     R5,SETK
SETWHIL  LTR   R5,R5
         BNP   SETDONE
         L     R6,0(R5)
         L     R7,P
         ST    R7,0(R5)
         LR    R5,R6
         B     SETWHIL
SETDONE  L     R3,LABV
         LR    R4,R8
         SLL   R4,2
         L     R5,P
         LCR   R5,R5
         ST    R5,0(R4,R3)
         L     R8,SETSV8
         L     R14,SETRET
         BR    R14
SETRET   DS    F
SETSV8   DS    F
SETK     DS    F
LABREF   DS    0H
         ST    R14,LABRRET
         ST    R8,LABSV8
         LR    R8,R3
         L     R4,LABV
         LR    R5,R2
         SLL   R5,2
         L     R6,0(R5,R4)
         LTR   R6,R6
         BM    LRKNOWN
         ST    R8,0(R5,R4)
         B     LRADD
LRKNOWN  LCR   R6,R6
LRADD    L     R7,0(R8)
         AR    R7,R6
         ST    R7,0(R8)
         L     R8,LABSV8
         L     R14,LABRRET
         BR    R14
LABRRET  DS    F
LABSV8   DS    F
***********************************************************************
* V12 INTCODE REPRESENTATION CONTRACT
***********************************************************************
*
* RICHARDS ICINT IS DEFINED IN BCPL WORD ADDRESSES. V11 STORED P, G,
* C, LABELS, AND OTHER BCPL POINTER VALUES AS NATIVE S/370 BYTE
* ADDRESSES. THAT BREAKS ORDINARY BCPL POINTER ARITHMETIC AFTER A
* POINTER ESCAPES INTO AN UNTYPED VALUE (FOR EXAMPLE WRITEF T:=T+1).
*
* V12 STORES EVERY BCPL MEMORY/CODE POINTER AS:
*
*       BCPL POINTER VALUE = ALIGNED HOST BYTE ADDRESS / 4
*
* THEREFORE:
*       POINTER + 1        -> NEXT BCPL WORD
*       POINTER + N        -> N BCPL WORDS
*       POINTER DIFFERENCE -> WORD DISTANCE
*
* ONLY A HOST MEMORY ACCESS CONVERTS BACK:
*
*       HOST BYTE ADDRESS = BCPL POINTER VALUE << 2
*
* P, G, C AND RESOLVED LABELS ALL USE THIS WORD-ADDRESS FORM.
* A AND B REMAIN UNTYPED BCPL VALUES AND MAY CARRY SUCH POINTERS.
* D IS AN ORDINARY BCPL VALUE; PBIT/GBIT ADD WORD ADDRESSES DIRECTLY.
* IBIT TRANSLATES D TO A HOST BYTE ADDRESS ONLY FOR THE DEREFERENCE.
*
***********************************************************************
***********************************************************************
* INTERPRET
***********************************************************************
INTERPRT DS    0H
         ST    R14,INTRETAD
         STM   R6,R9,INTSAVE
FETCH    L     R2,CYCCNT
         LA    R2,1(R2)
         ST    R2,CYCCNT
         L     R3,C
         LR    R1,R3
         SLL   R1,2
         L     R4,0(R1)
         ST    R4,W
         LA    R3,1(R3)
         ST    R3,C
         LR    R5,R4
         N     R5,=F'512'
         LTR   R5,R5
         BNZ   FLONG
         LR    R5,R4
         N     R5,=F'511'
         ST    R5,D
         B     FDREADY
FLONG    L     R3,C
         LR    R1,R3
         SLL   R1,2
         L     R5,0(R1)
         ST    R5,D
         LA    R3,1(R3)
         ST    R3,C
FDREADY  LR    R5,R4
         N     R5,=F'2048'
         LTR   R5,R5
         BZ    FNOP
         L     R5,D
         A     R5,P
         ST    R5,D
FNOP     LR    R5,R4
         N     R5,=F'1024'
         LTR   R5,R5
         BZ    FNOG
         L     R5,D
         A     R5,G
         ST    R5,D
FNOG     LR    R5,R4
         N     R5,=F'4096'
         LTR   R5,R5
         BZ    FNOI
         L     R5,D
         SLL   R5,2
         L     R5,0(R5)
         ST    R5,D
FNOI     BAL   R14,TRRECORD
         L     R2,W
         SRL   R2,FSHIFT
         C     R2,=F'0'
         BE    OP0
         C     R2,=F'1'
         BE    OP1
         C     R2,=F'2'
         BE    OP2
         C     R2,=F'3'
         BE    OP3
         C     R2,=F'4'
         BE    OP4
         C     R2,=F'5'
         BE    OP5
         C     R2,=F'6'
         BE    OP6
         C     R2,=F'7'
         BE    OP7
         B     INTERROR
INTERROR L     R2,A
         ST    R2,MSA
         L     R2,B
         ST    R2,MSB
         L     R2,C
         ST    R2,MSC
         L     R2,D
         ST    R2,MSD
         L     R2,P
         ST    R2,MSP
         L     R2,W
         ST    R2,MSW
         L     R2,CYCCNT
         ST    R2,MSCYC
         L     R2,SYSPRINT
         BAL   R14,SELOUT
         LA    R2,INTEMSG
         L     R3,C
         S     R3,PROGWORD
         BAL   R14,WRITEF
         L     R0,=F'-1'
         B     INTRTN
OP0      L     R2,A
         ST    R2,B
         L     R2,D
         ST    R2,A
         B     FETCH
OP1      L     R2,D
* V17: OP1 STORES THROUGH A BCPL WORD POINTER. ACCEPT ADDRESSES ONLY
* WITHIN THE TWO BCPL MEMORY AREAS THAT INTCODE MAY ADDRESS DIRECTLY.
         L     R3,PROGWORD
         CR    R2,R3
         BL    OP1CHKG
         A     R3,=F'20000'
         CR    R2,R3
         BNH   OP1STORE
OP1CHKG  L     R3,G
         CR    R2,R3
         BL    OP1BAD
         A     R3,=F'400'
         CR    R2,R3
         BH    OP1BAD
OP1STORE SLL   R2,2
         L     R3,A
         ST    R3,0(R2)
         B     FETCH
OP1BAD   BAL   R14,TRDUMP
         L     R0,=F'-2'
         B     INTRTN
OP2      L     R2,A
         A     R2,D
         ST    R2,A
         B     FETCH
OP3      L     R2,D
         ST    R2,C
         B     FETCH
OP4      L     R2,A
         X     R2,=F'-1'
         ST    R2,A
OP5      L     R2,A
         LTR   R2,R2
         BNZ   OP5DONE
         L     R2,D
         ST    R2,C
OP5DONE  B     FETCH
OP6      L     R2,D
         A     R2,P
         ST    R2,D
         LR    R4,R2
         SLL   R4,2
         L     R3,P
         ST    R3,0(R4)
         L     R3,C
         ST    R3,4(R4)
         ST    R2,P
         L     R3,A
         ST    R3,C
         B     FETCH
OP7      L     R2,D
         C     R2,=F'1'
         BE    X1
         C     R2,=F'2'
         BE    X2
         C     R2,=F'3'
         BE    X3
         C     R2,=F'4'
         BE    X4
         C     R2,=F'5'
         BE    X5
         C     R2,=F'6'
         BE    X6
         C     R2,=F'7'
         BE    X7
         C     R2,=F'8'
         BE    X8
         C     R2,=F'9'
         BE    X9
         C     R2,=F'10'
         BE    X10
         C     R2,=F'11'
         BE    X11
         C     R2,=F'12'
         BE    X12
         C     R2,=F'13'
         BE    X13
         C     R2,=F'14'
         BE    X14
         C     R2,=F'15'
         BE    X15
         C     R2,=F'16'
         BE    X16
         C     R2,=F'17'
         BE    X17
         C     R2,=F'18'
         BE    X18
         C     R2,=F'19'
         BE    X19
         C     R2,=F'20'
         BE    X20
         C     R2,=F'21'
         BE    X21
         C     R2,=F'22'
         BE    X22
         C     R2,=F'23'
         BE    X23
         C     R2,=F'24'
         BE    X24
         C     R2,=F'25'
         BE    X25
         C     R2,=F'26'
         BE    X26
         C     R2,=F'27'
         BE    X27
         C     R2,=F'28'
         BE    X28
         C     R2,=F'29'
         BE    X29
         C     R2,=F'30'
         BE    X30
         C     R2,=F'31'
         BE    X31
         C     R2,=F'32'
         BE    X32
         C     R2,=F'33'
         BE    X33
         C     R2,=F'34'
         BE    X34
         C     R2,=F'35'
         BE    X35
         C     R2,=F'36'
         BE    X36
         C     R2,=F'37'
         BE    X37
         B     INTERROR
X1       L     R2,A
         SLL   R2,2
         L     R2,0(R2)
         ST    R2,A
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
         SLL   R2,2
         L     R3,4(R2)
         ST    R3,C
         L     R3,0(R2)
         ST    R3,P
         B     FETCH
***********************************************************************
* X5 - MULTIPLY - V11 CORRECTION
***********************************************************************
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
X8       L     R2,B
         A     R2,A
         ST    R2,A
         B     FETCH
X9       L     R2,B
         S     R2,A
         ST    R2,A
         B     FETCH
X10      L     R2,B
         C     R2,A
         BE    X10T
         SR    R2,R2
         ST    R2,A
         B     FETCH
X10T     L     R2,=F'-1'
         ST    R2,A
         B     FETCH
X11      L     R2,B
         C     R2,A
         BNE   X11T
         SR    R2,R2
         ST    R2,A
         B     FETCH
X11T     L     R2,=F'-1'
         ST    R2,A
         B     FETCH
X12      L     R2,B
         C     R2,A
         BL    X12T
         SR    R2,R2
         ST    R2,A
         B     FETCH
X12T     L     R2,=F'-1'
         ST    R2,A
         B     FETCH
X13      L     R2,B
         C     R2,A
         BNL   X13T
         SR    R2,R2
         ST    R2,A
         B     FETCH
X13T     L     R2,=F'-1'
         ST    R2,A
         B     FETCH
X14      L     R2,B
         C     R2,A
         BH    X14T
         SR    R2,R2
         ST    R2,A
         B     FETCH
X14T     L     R2,=F'-1'
         ST    R2,A
         B     FETCH
X15      L     R2,B
         C     R2,A
         BNH   X15T
         SR    R2,R2
         ST    R2,A
         B     FETCH
X15T     L     R2,=F'-1'
         ST    R2,A
         B     FETCH
X16      BAL   R14,SHLINT
         ST    R0,A
         B     FETCH
X17      BAL   R14,SHRINT
         ST    R0,A
         B     FETCH
X18      L     R2,B
         N     R2,A
         ST    R2,A
         B     FETCH
X19      L     R2,B
         O     R2,A
         ST    R2,A
         B     FETCH
X20      L     R2,B
         X     R2,A
         ST    R2,A
         B     FETCH
X21      L     R2,B
         X     R2,A
         X     R2,=F'-1'
         ST    R2,A
         B     FETCH
X22      SR    R0,R0
         B     INTRTN
X23      L     R2,C
         LR    R1,R2
         SLL   R1,2
         L     R3,0(R1)
         ST    R3,B
         L     R4,4(R1)
         ST    R4,D
X23LOOP  L     R3,B
         LTR   R3,R3
         BZ    X23DONE
         BCTR  R3,0
         ST    R3,B
         L     R2,C
         LA    R2,2(R2)
         ST    R2,C
         LR    R1,R2
         SLL   R1,2
         L     R3,A
         C     R3,0(R1)
         BNE   X23LOOP
         L     R4,4(R1)
         ST    R4,D
X23DONE  L     R2,D
         ST    R2,C
         B     FETCH
X24      L     R2,A
         BAL   R14,SELIN
         B     FETCH
X25      L     R2,A
         BAL   R14,SELOUT
         B     FETCH
X26      BAL   R14,HOSTRD
         LTR   R0,R0
         BM    X26EOF
         LR    R2,R0
         SLL   R2,2
         L     R3,ETOA
         L     R3,0(R2,R3)
         ST    R3,A
         B     FETCH
X26EOF   ST    R0,A
         B     FETCH
X27      L     R2,A
         SLL   R2,2
         L     R3,ATOE
         L     R2,0(R2,R3)
         BAL   R14,HOSTWR
         B     FETCH
X28      L     R2,A
         BAL   R14,STRING37
         LR    R2,R0
         BAL   R14,FINDIN
         ST    R0,A
         B     FETCH
X29      L     R2,A
         BAL   R14,STRING37
         LR    R2,R0
         BAL   R14,FINDOUT
         ST    R0,A
         B     FETCH
X30      L     R0,A
         B     INTRTN
X31      L     R2,P
         SLL   R2,2
         L     R3,0(R2)
         ST    R3,A
         B     FETCH
X32      L     R2,A
         ST    R2,P
         L     R2,B
         ST    R2,C
         B     FETCH
X33      BAL   R14,ENDREAD
         B     FETCH
X34      BAL   R14,ENDWRITE
         B     FETCH
X35      L     R2,B
         LA    R2,1(R2)
         A     R2,P
         ST    R2,D
         L     R3,P
         LR    R5,R3
         SLL   R5,2
         LR    R1,R2
         SLL   R1,2
         L     R4,0(R5)
         ST    R4,0(R1)
         L     R4,4(R5)
         ST    R4,4(R1)
         ST    R3,8(R1)
         L     R4,B
         ST    R4,12(R1)
         ST    R2,P
         L     R4,A
         ST    R4,C
         B     FETCH
X36      L     R2,A
         L     R3,B
         BAL   R14,ICGETBY
         ST    R0,A
         B     FETCH
X37      L     R2,P
         SLL   R2,2
         L     R4,16(R2)
         L     R2,A
         L     R3,B
         BAL   R14,ICPUTBY
         B     FETCH
INTRTN   LM    R6,R9,INTSAVE
         L     R14,INTRETAD
         BR    R14
INTRETAD DS    F
INTSAVE  DS    4F
***********************************************************************
* STRING / BYTE HELPERS
***********************************************************************
STRING37 DS    0H
         ST    R14,STRRET
         STM   R6,R9,STRSAVE
         LR    R8,R2
         LA    R7,STRTEMP
         XC    STRTEMP(32),STRTEMP
         LR    R2,R8
         SR    R3,R3
         BAL   R14,ICGETBY
         LR    R4,R0
         LR    R2,R7
         SR    R3,R3
         BAL   R14,HOSTPUTB
         LA    R6,1
STRLOOP  LR    R2,R8
         SR    R3,R3
         BAL   R14,ICGETBY
         CR    R6,R0
         BH    STRDONE
         LR    R2,R8
         LR    R3,R6
         BAL   R14,ICGETBY
         LR    R3,R0
         SLL   R3,2
         L     R4,ATOE
         L     R4,0(R3,R4)
         LR    R2,R7
         LR    R3,R6
         BAL   R14,HOSTPUTB
         LA    R6,1(R6)
         B     STRLOOP
STRDONE  LR    R0,R7
         LM    R6,R9,STRSAVE
         L     R14,STRRET
         BR    R14
STRRET   DS    F
STRSAVE  DS    4F
STRTEMP  DS    8F
HOSTPUTB STC   R4,0(R3,R2)
         BR    R14
ICGETBY  LR    R4,R3
         SRL   R4,1
         AR    R4,R2
         SLL   R4,2
         L     R5,0(R4)
         LR    R1,R3
         N     R1,=F'1'
         LTR   R1,R1
         BNZ   IGBLOW
         SRL   R5,8
IGBLOW   N     R5,=F'255'
         LR    R0,R5
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
STRMINIT ST    R14,SMIRET
         XC    CURIN,CURIN
         XC    CUROUT,CUROUT
         XC    DYNLIST,DYNLIST
         XC    INTINSD(SDLENGTH),INTINSD
         MVC   INTINSD+SDTYPE(4),=F'1'
         LA    R2,INTINDCB
         ST    R2,INTINSD+SDDCB
         LA    R2,INTINBUF
         ST    R2,INTINSD+SDBUF
         MVC   INTINSD+SDLEN(4),=F'80'
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
         XC    ICTOKLEN,ICTOKLEN
         XC    ICPEND,ICPEND
         L     R14,SMIRET
         BR    R14
SMIRET   DS    F
***********************************************************************
* FINDINPUT / FINDOUTPUT
***********************************************************************
FINDIN   DS    0H
         ST    R14,FINDIRET
         BAL   R14,MAKENAME
         LTR   R0,R0
         BZ    FINONE
         LA    R3,FINTAB
FILOOK   L     R5,8(R3)
         LTR   R5,R5
         BZ    FIGEN
         CLC   NAMEBUF(8),0(R3)
         BE    FIMATCH
         LA    R3,12(R3)
         B     FILOOK
FIMATCH  ST    R5,FINDIMAT
         LR    R2,R5
         BAL   R14,OPENSTRM
         L     R0,FINDIMAT
         B     FIRETURN
FIGEN    LA    R3,STGENIN
         BAL   R14,DYNFIND
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
         BZ    FOGEN
         CLC   NAMEBUF(8),0(R3)
         BE    FOMATCH
         LA    R3,12(R3)
         B     FOLOOK
FOMATCH  ST    R5,FINDOMAT
         LR    R2,R5
         BAL   R14,OPENSTRM
         L     R0,FINDOMAT
         B     FORETURN
FOGEN    LA    R3,STGENOUT
         BAL   R14,DYNFIND
         B     FORETURN
FONONE   SR    R0,R0
FORETURN L     R14,FINDORET
         BR    R14
FINDORET DS    F
FINDOMAT DS    F
***********************************************************************
* DYNAMIC DDNAME DISCOVERY
***********************************************************************
*
* NAMEBUF HOLDS THE NORMALIZED DDNAME AND R3 HOLDS STGENIN/STGENOUT.
* LIVE ORDINARY STREAM OBJECTS FORM A SINGLY LINKED LIST.  EACH OBJECT
* OWNS ITS DESCRIPTOR, DCB AND 80-BYTE RECORD BUFFER.  A NEW OBJECT IS
* LINKED ONLY AFTER RDJFCB CONFIRMS THAT THE DDNAME IS ALLOCATED.
*
* GETMAIN RC IS DELIBERATELY CONDITIONAL: STORAGE EXHAUSTION RETURNS A
* ZERO FINDINPUT/FINDOUTPUT RESULT RATHER THAN TAKING THE INTERPRETER
* DOWN WITH THE ORDINARY UNCONDITIONAL GETMAIN FAILURE PATH.
*
DYNFIND  DS    0H
         ST    R14,DYFRET
         STM   R6,R9,DYFSAVE
         LR    R8,R3
         L     R6,DYNLIST
DYFSCAN  LTR   R6,R6
         BZ    DYFALLOC
         L     R5,SDTYPE(R6)
         CR    R5,R8
         BNE   DYFNEXT
         CLC   SDNAME(8,R6),NAMEBUF
         BE    DYFFOUND
DYFNEXT  L     R6,SDNEXT(R6)
         B     DYFSCAN
DYFFOUND LR    R2,R6
         BAL   R14,OPENSTRM
         LR    R0,R6
         B     DYFRTN
DYFALLOC C     R8,=F'2'
         BE    DYFALIN
         GETMAIN RC,LV=DYNOLEN
         B     DYFALCK
DYFALIN  GETMAIN RC,LV=DYNILEN
DYFALCK  LTR   R15,R15
         BNZ   DYFNONE
         LR    R6,R1
         C     R8,=F'2'
         BE    DYFINIT
* OUTPUT OBJECT
         XC    0(DYNOLEN,R6),0(R6)
         ST    R8,SDTYPE(R6)
         LA    R5,DYDCBOFF(R6)
         ST    R5,SDDCB(R6)
         LA    R4,DYNOBUFO(R6)
         ST    R4,SDBUF(R6)
         MVC   SDLEN(4,R6),=F'80'
         MVC   SDNAME(8,R6),NAMEBUF
         MVC   0(DYNODCBL,R5),DYNODCBT
         MVC   DDNAMOFF(8,R5),NAMEBUF
         B     DYFVERIF
* INPUT OBJECT
DYFINIT XC   0(DYNILEN,R6),0(R6)
         ST    R8,SDTYPE(R6)
         LA    R5,DYDCBOFF(R6)
         ST    R5,SDDCB(R6)
         LA    R4,DYNIBUFO(R6)
         ST    R4,SDBUF(R6)
         MVC   SDLEN(4,R6),=F'80'
         MVC   SDNAME(8,R6),NAMEBUF
         MVC   0(DYNIDCBL,R5),DYNIDCBT
         MVC   DDNAMOFF(8,R5),NAMEBUF
DYFVERIF LR   R2,R5
         RDJFCB ((2))
         LTR   R15,R15
         BNZ   DYFBADDD
         L     R5,DYNLIST
         ST    R5,SDNEXT(R6)
         ST    R6,DYNLIST
         LR    R2,R6
         BAL   R14,OPENSTRM
         LR    R0,R6
         B     DYFRTN
DYFBADDD LR    R1,R6
         C     R8,=F'2'
         BE    DYFFRIN
         FREEMAIN R,LV=DYNOLEN,A=(R1)
         B     DYFNONE
DYFFRIN  FREEMAIN R,LV=DYNILEN,A=(R1)
DYFNONE  SR    R0,R0
DYFRTN   LM    R6,R9,DYFSAVE
         L     R14,DYFRET
         BR    R14
DYFRET   DS    F
DYFSAVE  DS    4F
***********************************************************************
* DYNAMIC STREAM RELEASE
***********************************************************************
*
* R2 IS THE DYNAMIC DESCRIPTOR/OBJECT BASE.  THE DCB MUST ALREADY HAVE
* BEEN CLOSED.  DYNFREE UNLINKS THE OBJECT THEN RETURNS ALL STORAGE.
*
DYNFREE  DS    0H
         ST    R14,DYURET
         STM   R6,R9,DYUSAVE
         LR    R8,R2
         SR    R7,R7
         L     R6,DYNLIST
DYUSCAN  LTR   R6,R6
         BZ    DYURTN
         CR    R6,R8
         BE    DYUFOUND
         LR    R7,R6
         L     R6,SDNEXT(R6)
         B     DYUSCAN
DYUFOUND L     R5,SDNEXT(R6)
         LTR   R7,R7
         BNZ   DYUMID
         ST    R5,DYNLIST
         B     DYUFREL
DYUMID   ST    R5,SDNEXT(R7)
DYUFREL  L     R5,SDTYPE(R8)
         LR    R1,R8
         C     R5,=F'2'
         BE    DYUIN
         FREEMAIN R,LV=DYNOLEN,A=(R1)
         B     DYURTN
DYUIN    FREEMAIN R,LV=DYNILEN,A=(R1)
DYURTN   LM    R6,R9,DYUSAVE
         L     R14,DYURET
         BR    R14
DYURET   DS    F
DYUSAVE  DS    4F
***********************************************************************
* STREAM NAME NORMALIZATION
***********************************************************************
*
* BCPL FINDINPUT/FINDOUTPUT PASS A COUNTED STRING. MVS DDNAME SPACE IS
* AT MOST EIGHT CHARACTERS, SO NORMALIZE VALID REQUESTS TO AN 8-BYTE,
* SPACE-PADDED KEY.
*
MAKENAME DS    0H
         MVC   NAMEBUF(8),=CL8' '
         SR    R3,R3
         IC    R3,0(R2)
         C     R3,=F'8'
         BH    MNFAIL
         LTR   R3,R3
         BZ    MNFAIL
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
HWRNORM L    R2,HWRCHAR
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
ICWSAVC DS   F
ICWTEMP  DS    X
         DS    0F
* APPEND ONE EBCDIC CHARACTER IN R2 TO THE CURRENT TOKEN.
ICTOKCHR L     R3,ICTOKLEN
         C     R3,=F'80'
         BNL   ICTCRTN
         LA    R5,ICTOKBUF
         STC   R2,0(R3,R5)
         LA    R3,1(R3)
         ST    R3,ICTOKLEN
ICTCRTN  BR    R14
* COMMIT CURRENT TOKEN TO THE 80-COLUMN PHYSICAL RECORD. A SINGLE
* SPACE IS INSERTED BETWEEN TOKENS. IF IT WILL NOT FIT, FLUSH FIRST.
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
* A TRAILING PENDING SLASH WAS NOT FOLLOWED BY NEWLINE: PRESERVE IT.
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
         ST    R2,OSCUR
         L     R5,SDFLAGS(R2)
         N     R5,=F'1'
         LTR   R5,R5
         BNZ   OSRETURN
         L     R5,SDTYPE(R2)
         C     R5,=F'1'
         BE    OSINTIN
         C     R5,=F'2'
         BE    OSGENIN
         C     R5,=F'3'
         BE    OSSYSPR
         C     R5,=F'4'
         BE    OSINTCO
         C     R5,=F'5'
         BE    OSGENOUT
         B     OSRETURN
OSINTIN  OPEN  (INTINDCB,(INPUT))
         B     OSOPENED
OSGENIN  L     R2,OSCUR
         L     R2,SDDCB(R2)
         OPEN  ((2),(INPUT))
         B     OSOPENED
OSSYSPR  OPEN  (SYSPRDCB,(OUTPUT))
         B     OSOPENED
OSINTCO  OPEN  (INTCODCB,(OUTPUT))
         XC    ICTOKLEN,ICTOKLEN
         XC    ICPEND,ICPEND
         B     OSOPENED
OSGENOUT L     R2,OSCUR
         L     R2,SDDCB(R2)
         OPEN  ((2),(OUTPUT))
OSOPENED L     R2,OSCUR
         L     R5,SDFLAGS(R2)
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
OSCUR    DS    F
GETREC   DS    0H
         ST    R14,GRRET
         ST    R2,GRCUR
         L     R5,SDTYPE(R2)
         C     R5,=F'1'
         BE    GRINTIN
         C     R5,=F'2'
         BE    GRGENIN
         B     GREOF
GRINTIN  GET   INTINDCB,INTINBUF
         B     GROK
GRGENIN  L     R2,GRCUR
         L     R3,SDBUF(R2)
         L     R2,SDDCB(R2)
         GET   (2),(3)
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
GENIEOF  L     R2,GRCUR
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
         BE    PRGENOUT
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
         L     R2,PRCUR
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
PRGENOUT L     R3,SDPOS(R2)
         LTR   R3,R3
         BZ    PRRETURN
         L     R5,SDBUF(R2)
PRGOPAD  C     R3,=F'80'
         BNL   PRGOPUT
         LR    R1,R5
         AR    R1,R3
         MVI   0(R1),C' '
         LA    R3,1(R3)
         B     PRGOPAD
PRGOPUT  L     R2,PRCUR
         L     R3,SDBUF(R2)
         L     R2,SDDCB(R2)
         PUT   (2),(3)
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
         BE    CSGENIN
         C     R5,=F'3'
         BE    CSSYSPR
         C     R5,=F'4'
         BE    CSINTCO
         C     R5,=F'5'
         BE    CSGENOUT
         B     CSRETURN
CSINTIN  CLOSE (INTINDCB)
         B     CSCLOSED
CSGENIN  L     R2,CSCUR
         L     R2,SDDCB(R2)
         CLOSE ((2))
         L     R2,CSCUR
         BAL   R14,DYNFREE
         B     CSRETURN
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
CSGENOUT L     R2,CSCUR
         L     R3,SDPOS(R2)
         LTR   R3,R3
         BZ    CSGOCLOS
         BAL   R14,PUTREC
CSGOCLOS L     R2,CSCUR
         L     R2,SDDCB(R2)
         CLOSE ((2))
         L     R2,CSCUR
         BAL   R14,DYNFREE
         B     CSRETURN
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
         LA    R2,SYSPRSD
         BAL   R14,CLOSESTR
         LA    R2,INTCOSD
         BAL   R14,CLOSESTR
CACLOOP  L     R2,DYNLIST
         LTR   R2,R2
         BZ    CADONE
         BAL   R14,CLOSESTR
         B     CACLOOP
CADONE   L     R14,CARET
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
         LA    R2,MSREG1
         L     R3,MSA
         L     R4,MSB
         L     R5,MSC
         BAL   R14,WRITEF
         LA    R2,MSREG2
         L     R3,MSD
         L     R4,MSP
         L     R5,MSW
         BAL   R14,WRITEF
         LA    R2,MSCYCMSG
         L     R3,MSCYC
         BAL   R14,WRITEF
         LA    R2,MSFRMH
         BAL   R14,WRITES
         L     R6,MSP
         SR    R7,R7
MSFLOOP C     R7,=F'16'
         BNL   MSFEND
         L     R8,STKBASE
         CR    R6,R8
         BNH   MSFEND
         L     R8,PROGWORD
         CR    R6,R8
         BL    MSFBAD
         LR    R9,R8
         A     R9,=F'19998'
         CR    R6,R9
         BH    MSFBAD
         ST    R6,MSCURP
         LR    R1,R6
         SLL   R1,2
         L     R8,0(R1)
         ST    R8,MSPREVP
         L     R9,4(R1)
         L     R5,8(R1)
         ST    R5,MSP2
         LA    R2,MSFRAME1
         LR    R3,R7
         LR    R4,R6
         BAL   R14,WRITEF
         LA    R2,MSFRAME2
         L     R3,MSPREVP
         LR    R4,R9
         BAL   R14,WRITEF
         LA    R2,MSFRAME3
         L     R3,MSP2
         BAL   R14,WRITEF
         L     R8,MSPREVP
         L     R9,MSCURP
         CR    R8,R9
         BNL   MSFBAD
         LR    R6,R8
         LA    R7,1(R7)
         B     MSFLOOP
MSFBAD  LA    R2,MSBADFR
         LR    R3,R6
         BAL   R14,WRITEF
MSFEND  LA    R2,MSGLOBH
         BAL   R14,WRITES
         SR    R6,R6
MSGLOOP C     R6,=F'400'
         BH    MSGDONE
         LA    R8,GUSED
         AR    R8,R6
         CLI   0(R8),1
         BNE   MSGNEXT
         L     R8,GLOBBASE
         LR    R9,R6
         SLL   R9,2
         L     R4,0(R9,R8)
         LA    R2,MSGLOB
         LR    R3,R6
         BAL   R14,WRITEF
MSGNEXT LA    R6,1(R6)
         B     MSGLOOP
MSGDONE LA    R2,MSEND
         BAL   R14,WRITES
         LM    R6,R9,MSSAVE
         L     R14,MSRET
         BR    R14
MSRET    DS    F
MSSAVE   DS    4F
MSCURP   DS    F
MSPREVP  DS    F
MSP2     DS    F
***********************************************************************
* V17 RECENT-INSTRUCTION TRACE
***********************************************************************
*
* EACH OF EIGHT 24-BYTE SLOTS HOLDS:
*   C-BEFORE, W, D-AFTER-DECODE, A, B, P
* TRIDX NAMES THE NEXT SLOT TO BE WRITTEN.
* INTERPRETER STATE IS UNCHANGED; R1-R5 ARE VOLATILE HERE.
*
TRRECORD DS    0H
         L     R1,TRIDX
         LR    R2,R1
         SLL   R2,4
         LR    R3,R1
         SLL   R3,3
         AR    R2,R3
         LA    R1,TRBUF
         AR    R1,R2
         L     R2,C
         L     R3,W
         LR    R4,R3
         N     R4,=F'512'
         LTR   R4,R4
         BZ    TRSHORT
         BCTR  R2,0
TRSHORT  BCTR  R2,0
         ST    R2,0(R1)
         ST    R3,4(R1)
         L     R2,D
         ST    R2,8(R1)
         L     R2,A
         ST    R2,12(R1)
         L     R2,B
         ST    R2,16(R1)
         L     R2,P
         ST    R2,20(R1)
         L     R2,TRIDX
         LA    R2,1(R2)
         N     R2,=F'7'
         ST    R2,TRIDX
         BR    R14
*
* OP1BAD ENTERS HERE WITH THE OFFENDING D STILL IN MEMORY. PRINT THE
* CURRENT STATE AND ALL EIGHT RING SLOTS. TRIDX IDENTIFIES THE OLDEST
* SLOT, SO THE LOOP PRINTS THE FULL RING IN CHRONOLOGICAL ORDER.
*
TRDUMP   DS    0H
         ST    R14,TRDRET
         STM   R6,R9,TRDSAVE
         L     R2,SYSPRINT
         BAL   R14,SELOUT
         LA    R2,TRHEAD
         BAL   R14,WRITES
         LA    R2,TRBAD1
         L     R3,A
         L     R4,B
         L     R5,D
         BAL   R14,WRITEF
         LA    R2,TRBAD2
         L     R3,C
         L     R4,P
         L     R5,W
         BAL   R14,WRITEF
         SR    R6,R6
TRDLOOP  C     R6,=F'8'
         BNL   TRDDONE
         L     R7,TRIDX
         AR    R7,R6
         N     R7,=F'7'
         LR    R8,R7
         SLL   R8,4
         LR    R9,R7
         SLL   R9,3
         AR    R8,R9
         LA    R9,TRBUF
         AR    R9,R8
         LA    R2,TRLINE1
         LR    R3,R6
         L     R4,0(R9)
         L     R5,4(R9)
         BAL   R14,WRITEF
         LA    R2,TRLINE2
         L     R3,8(R9)
         L     R4,12(R9)
         L     R5,16(R9)
         BAL   R14,WRITEF
         LA    R2,TRLINE3
         L     R3,20(R9)
         BAL   R14,WRITEF
         LA    R6,1(R6)
         B     TRDLOOP
TRDDONE  LM    R6,R9,TRDSAVE
         L     R14,TRDRET
         BR    R14
TRDRET   DS    F
TRDSAVE  DS    4F
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
DYNLIST  DS    F
STKBASE  DS    F
MSA      DS    F
MSB      DS    F
MSC      DS    F
MSD      DS    F
MSP      DS    F
MSW      DS    F
MSCYC    DS    F
TRIDX    DS    F
TRBUF    DS    48F
GUSED    DS    CL401
         DS    0F
INTINSD  DS    CL32
SYSPRSD  DS    CL32
INTCOSD  DS    CL32
ICTOKLEN DS    F
ICPEND   DS    X
         DS    0F
INTINDCB DCB   DDNAME=INTIN,DSORG=PS,MACRF=GM,EODAD=INTIEOF
SYSPRDCB DCB   DDNAME=SYSPRINT,DSORG=PS,MACRF=PM
INTCODCB DCB   DDNAME=INTCODE,DSORG=PS,MACRF=PM
INTINBUF DS    CL80
SYSPOBUF DS    CL133
INTOBUF  DS    CL80
ICTOKBUF DS    CL80
***********************************************************************
* DYNAMIC DISCOVERED STREAM TEMPLATES
***********************************************************************
*
* ONLY TWO DCB TEMPLATES REMAIN STATIC.  EVERY ORDINARY LIVE STREAM
* GETS A COPY OF THE APPROPRIATE TEMPLATE INSIDE ITS GETMAIN OBJECT.
* GENEXL/GENJFCB ARE SHARED SCRATCH FOR THE SERIAL RDJFCB DISCOVERY
* PATH; ICINT IS SINGLE-THREADED.
*
DYNIDCBT DCB   DDNAME=DYNI,DSORG=PS,MACRF=GM,EODAD=GENIEOF,EXLST=GENEXL
DYNIDCBE EQU   *
DYNIDCBL EQU   DYNIDCBE-DYNIDCBT
DYNIBUFO EQU   DYDCBOFF+DYNIDCBL
DYNILEN  EQU   DYNIBUFO+80
DYNODCBT DCB   DDNAME=DYNO,DSORG=PS,MACRF=PM,EXLST=GENEXL
DYNODCBE EQU   *
DYNODCBL EQU   DYNODCBE-DYNODCBT
DYNOBUFO EQU   DYDCBOFF+DYNODCBL
DYNOLEN  EQU   DYNOBUFO+80
         DS    0F
GENEXL   DC    X'87',AL3(GENJFCB)
GENJFCB  DS    CL176
         DS    0F
INITCODE DC    X'00001401'
         DC    X'0000C002'
         DC    X'0000E016'
ATOETAB  DC    F'-1'
         DC    F'0',F'0',F'0',F'0',F'0',F'0',F'0',F'0'
         DC    F'0',F'5',F'21',F'0',F'12',F'0',F'0',F'0'
         DC    F'0',F'0',F'0',F'0',F'0',F'0',F'0',F'0'
         DC    F'0',F'0',F'0',F'0',F'0',F'0',F'0',F'0'
         DC    F'64',F'90',F'127',F'123',F'91',F'108',F'80',F'125'
         DC    F'77',F'93',F'92',F'78',F'107',F'96',F'75',F'97'
         DC    F'240',F'241',F'242',F'243'
         DC    F'244',F'245',F'246',F'247'
         DC    F'248',F'249',F'122',F'94'
         DC    F'76',F'126',F'110',F'111'
         DC    F'124',F'193',F'194',F'195'
         DC    F'196',F'197',F'198',F'199'
         DC    F'200',F'201',F'209',F'210'
         DC    F'211',F'212',F'213',F'214'
         DC    F'215',F'216',F'217',F'226'
         DC    F'227',F'228',F'229',F'230'
* HERC/TK5 HOST ADAPT: ASCII '\' -> EBCDIC X'E0', NOT MR10 X'62'.
         DC    F'231',F'232',F'233',F'66'
         DC    F'224',F'67',F'101',F'102'
         DC    F'64',F'129',F'130',F'131'
         DC    F'132',F'133',F'134',F'135'
         DC    F'136',F'137',F'145',F'146'
         DC    F'147',F'148',F'149',F'150'
         DC    F'151',F'152',F'153',F'162'
         DC    F'163',F'164',F'165',F'166'
         DC    F'167',F'168',F'169',F'64'
         DC    F'79',F'64',F'95',F'255'
ETOATAB  DC    F'-1'
         DC    F'0',F'0',F'0',F'0',F'0',F'9',F'0',F'0'
         DC    F'0',F'0',F'0',F'11',F'12',F'13',F'0',F'0'
         DC    F'0',F'0',F'0',F'0',F'0',F'10',F'0',F'0'
         DC    F'0',F'0',F'0',F'0',F'0',F'0',F'0',F'0'
         DC    F'0',F'0',F'0',F'0',F'0',F'10',F'0',F'0'
         DC    F'0',F'0',F'0',F'0',F'0',F'0',F'0',F'0'
         DC    F'0',F'0',F'0',F'0',F'0',F'0',F'0',F'0'
         DC    F'0',F'0',F'0',F'0',F'0',F'0',F'0',F'0'
         DC    F'32',F'0',F'91',F'93',F'0',F'0',F'0',F'0'
         DC    F'0',F'0',F'0',F'46',F'60',F'40',F'43',F'124'
         DC    F'38',F'0',F'0',F'0',F'0',F'0',F'0',F'0'
* HERCULES DEFAULT INPUT USES X'5F' FOR '^'; HISTORICAL X'65' BELOW
* REMAINS AS A NON-CONFLICTING ALIAS FOR '^'.
         DC    F'0',F'0',F'33',F'36',F'42',F'41',F'59',F'94'
         DC    F'45',F'47',F'92',F'0',F'0',F'94',F'95',F'0'
* HERCULES DEFAULT INPUT USES X'6A' FOR '|'. HISTORICAL X'4F' ABOVE
* REMAINS AS A NON-CONFLICTING ALIAS.
         DC    F'0',F'0',F'124',F'44',F'37',F'96',F'62',F'63'
         DC    F'0',F'0',F'0',F'0',F'0',F'0',F'0',F'0'
         DC    F'0',F'0',F'58',F'35',F'64',F'39',F'61',F'34'
         DC    F'0',F'97',F'98',F'99',F'100',F'101',F'102',F'103'
         DC    F'104',F'105',F'0',F'0',F'0',F'0',F'0',F'0'
         DC    F'0',F'106',F'107',F'108',F'109',F'110',F'111',F'112'
         DC    F'113',F'114',F'0',F'0',F'0',F'0',F'0',F'0'
* HERCULES DEFAULT INPUT USES X'A1' FOR '~'.
         DC    F'0',F'126',F'115',F'116',F'117',F'118',F'119',F'120'
* HERCULES DEFAULT INPUT USES X'AD' FOR '['.
         DC    F'121',F'122',F'0',F'0',F'0',F'91',F'0',F'0'
         DC    F'0',F'0',F'0',F'0',F'0',F'0',F'0',F'0'
* HERCULES DEFAULT INPUT USES X'BD' FOR ']'.
         DC    F'0',F'0',F'0',F'0',F'0',F'93',F'0',F'0'
* HERCULES DEFAULT INPUT USES X'C0' FOR '{'.
         DC    F'123',F'65',F'66',F'67',F'68',F'69',F'70',F'71'
         DC    F'72',F'73',F'0',F'0',F'0',F'0',F'0',F'0'
* HERCULES DEFAULT INPUT USES X'D0' FOR '}'.
         DC    F'125',F'74',F'75',F'76',F'77',F'78',F'79',F'80'
         DC    F'81',F'82',F'0',F'0',F'0',F'0',F'0',F'0'
* HERCULES DEFAULT INPUT USES X'E0' FOR '\'. HISTORICAL X'62' ABOVE
* REMAINS AS A NON-CONFLICTING ALIAS.
         DC    F'92',F'0',F'83',F'84',F'85',F'86',F'87',F'88'
         DC    F'89',F'90',F'0',F'0',F'0',F'0',F'0',F'0'
         DC    F'48',F'49',F'50',F'51',F'52',F'53',F'54',F'55'
         DC    F'56',F'57',F'0',F'0',F'0',F'0',F'0',F'0'
         DS    0F
FINTAB   DC    CL8'INTIN',A(INTINSD)
         DC    CL8' ',A(0)
FOUTTAB  DC    CL8'SYSPRINT',A(SYSPRSD)
         DC    CL8'INTCODE',A(INTCOSD)
         DC    CL8' ',A(0)
NAMEBUF  DS    CL8
SYSPRNAM DC    AL1(8),C'SYSPRINT'
INTCONAM DC    AL1(7),C'INTCODE'
INTINNAM DC    AL1(5),C'INTIN'
SYSINNAM DC    AL1(5),C'SYSIN'
ENTERMSG DC    AL1(0)
BADCHMSG DC    AL1(21),X'15',C'BAD CH %C AT P = %N',X'15'
BADCDMSG DC    AL1(20),X'15',C'BAD CODE AT P = %N',X'15'
UNSETMSG DC    AL1(10),C'L%N UNSET',X'15'
ALSETMSG DC    AL1(32),C'L%N ALREADY SET TO %N AT P = %N',X'15'
INTEMSG  DC    AL1(25),X'15',C'INTCODE ERROR AT C = %N',X'15'
SIZEMSG  DC    AL1(43),C'INTCODE SYSTEM ENTERED, PROGRAM SIZE = %N'
         DC    X'15',X'15'
EXECMSG  DC    AL1(35),X'15',X'15'
         DC    C'EXECUTION CYCLES = %N, CODE = %N',X'15'
TRHEAD   DC    AL1(30),X'15',C'*** V17 OP1 ADDRESS TRAP ***',X'15'
TRBAD1   DC    AL1(15),C'A=%N B=%N D=%N',X'15'
TRBAD2   DC    AL1(15),C'C=%N P=%N W=%N',X'15'
TRLINE1  DC    AL1(19),C'TRACE %N C=%N W=%N',X'15'
TRLINE2  DC    AL1(17),C'  D=%N A=%N B=%N',X'15'
TRLINE3  DC    AL1(7),C'  P=%N',X'15'
MSHEAD   DC    AL1(24),X'15',C'*** ICINT MAPSTORE ***',X'15'
MSREG1   DC    AL1(15),C'A=%N B=%N C=%N',X'15'
MSREG2   DC    AL1(15),C'D=%N P=%N W=%N',X'15'
MSCYCMSG DC    AL1(10),C'CYCLES=%N',X'15'
MSFRMH   DC    AL1(12),C'CALL FRAMES',X'15'
MSFRAME1 DC    AL1(14),C'FRAME %N P=%N',X'15'
MSFRAME2 DC    AL1(18),C'  OLDP=%N RETC=%N',X'15'
MSFRAME3 DC    AL1(9),C'  P!2=%N',X'15'
MSBADFR  DC    AL1(22),C'FRAME CHAIN BAD AT %N',X'15'
MSGLOBH  DC    AL1(13),C'USED GLOBALS',X'15'
MSGLOB   DC    AL1(10),C'G!%N = %N',X'15'
MSEND    DC    AL1(21),C'*** END MAPSTORE ***',X'15'
         LTORG
         END   ICINT
