***********************************************************************
* ICINT V16 DYNAMIC STREAM LAYER -- DEVELOPMENT INCLUDE
*
* This file is the implementation fragment for replacing V15's fixed
* GINSD1..3 / GOUTSD1..2 pools with GETMAIN-managed stream objects.
*
* It is intentionally kept separate while the V16 integration is made.
* The code assumes the V15 descriptor offsets and host routines remain
* in force, plus the additions below.  Once integrated and assembled,
* this fragment should disappear into icintv16.asm.
*
* DESIGN:
*   - INTIN, SYSPRINT, and INTCODE remain static/special streams.
*   - Ordinary FINDINPUT/FINDOUTPUT streams are allocated on demand.
*   - No predefined stream-count limit exists.
*   - GETMAIN uses the conditional RC form.  Storage exhaustion returns
*     a zero stream handle instead of causing an ordinary GETMAIN abend.
*   - ENDREAD/ENDWRITE close and FREEMAIN ordinary stream objects.
*   - Active dynamic streams are kept on a singly linked list.
*   - Repeated FIND* of an already-live DDNAME reuses its descriptor.
*
* MVS 3.8 note:
*   GETMAIN RC,LV=... is the conditional register request.  R15=0 means
*   success and R1 contains the obtained address; nonzero R15 means no
*   storage was obtained.  FREEMAIN releases the matching object.
***********************************************************************

***********************************************************************
* DESCRIPTOR EXTENSION
***********************************************************************
*
* V15 descriptor bytes 0..31 are unchanged.  Dynamic descriptors add
* one host-only forward link.  Static descriptors remain 32 bytes.
*
SDNEXT   EQU   32
DYNSDLEN EQU   36

***********************************************************************
* DYNAMIC OBJECT LAYOUT
***********************************************************************
*
* A dynamic object begins with the stream descriptor.  It owns its DCB
* and its 80-byte physical-record buffer.  Therefore closing one object
* can release all per-stream storage with one FREEMAIN.
*
DYDCBOFF EQU   DYNSDLEN

* Input and output DCB templates are copied into each new object.  Their
* embedded EODAD/EXLST addresses continue to point at V15/V16 static
* host-adapter routines/scratch.
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
DYNLIST  DS    F                  HEAD OF LIVE DYNAMIC STREAM OBJECTS

***********************************************************************
* DYNAMIC STREAM INITIALIZATION
***********************************************************************
*
* Called from STRMINIT instead of clearing GINTAB/GOUTTAB.
*
DYNINIT  XC    DYNLIST,DYNLIST
         BR    R14

***********************************************************************
* DYNFIND -- FIND OR CREATE AN ORDINARY STREAM
***********************************************************************
*
* ENTRY:
*   NAMEBUF = normalized 8-byte DDNAME
*   R3      = STGENIN or STGENOUT
*
* EXIT:
*   R0      = stream descriptor address, or zero
*
* The object is linked only after RDJFCB confirms that the requested DD
* exists.  Thus a missing DD or failed GETMAIN leaves no residual object.
*
DYNFIND  DS    0H
         ST    R14,DYFRET
         STM   R6,R9,DYFSAVE
         LR    R8,R3                 REQUESTED STREAM TYPE

* Search live streams first.
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

* Obtain one complete stream object.  RC form avoids an ordinary abend
* when the private-region/storage request cannot be satisfied.
DYFALLOC C     R8,=F'2'              STGENIN
         BE    DYFALIN
         GETMAIN RC,LV=DYNOLEN
         B     DYFALCK
DYFALIN  GETMAIN RC,LV=DYNILEN
DYFALCK  LTR   R15,R15
         BNZ   DYFNONE
         LR    R6,R1                 OBJECT/DESCRIPTOR BASE

* Initialize descriptor and owned DCB/buffer.
         C     R8,=F'2'
         BE    DYFINITIN

* Output object.
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
         B     DYFVERIFY

* Input object.
DYFINITIN XC   0(DYNILEN,R6),0(R6)
         ST    R8,SDTYPE(R6)
         LA    R5,DYDCBOFF(R6)
         ST    R5,SDDCB(R6)
         LA    R4,DYNIBUFO(R6)
         ST    R4,SDBUF(R6)
         MVC   SDLEN(4,R6),=F'80'
         MVC   SDNAME(8,R6),NAMEBUF
         MVC   0(DYNIDCBL,R5),DYNIDCBT
         MVC   DDNAMOFF(8,R5),NAMEBUF

* Verify allocation before making the stream visible.
DYFVERIFY LR   R2,R5
         RDJFCB ((2))
         LTR   R15,R15
         BNZ   DYFBADDD

* Link at head and open.
         L     R5,DYNLIST
         ST    R5,SDNEXT(R6)
         ST    R6,DYNLIST
         LR    R2,R6
         BAL   R14,OPENSTRM
         LR    R0,R6
         B     DYFRTN

* DDNAME not allocated: release the just-created object.
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
* DYNFREE -- UNLINK AND RELEASE AN ORDINARY STREAM OBJECT
***********************************************************************
*
* ENTRY R2 = descriptor/object address.  The DCB must already be closed.
*
DYNFREE  DS    0H
         ST    R14,DYURET
         STM   R6,R9,DYUSAVE
         LR    R8,R2                 OBJECT TO REMOVE
         SR    R7,R7                 PREVIOUS, ZERO MEANS HEAD
         L     R6,DYNLIST

DYUSCAN  LTR   R6,R6
         BZ    DYURTN                 NOT ON LIST: DO NOTHING
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
* DYNCLOSE -- CLOSE/FREE ALL ORDINARY STREAMS
***********************************************************************
*
* Intended for CLOSEALL.  CLOSESTR in integrated V16 will close generic
* DCBs and invoke DYNFREE, so repeatedly closing the head drains the list.
*
DYNCLOSE DS    0H
         ST    R14,DYCRET
DYCLoop  L     R2,DYNLIST
         LTR   R2,R2
         BZ    DYCDONE
         BAL   R14,CLOSESTR
         B     DYCLoop
DYCDONE  L     R14,DYCRET
         BR    R14
DYCRET   DS    F

***********************************************************************
* V16 INTEGRATION POINTS
***********************************************************************
*
* 1. STRMINIT
*      replace CLRPOOL calls for GINTAB/GOUTTAB with BAL R14,DYNINIT.
*
* 2. FINDIN / FINDOUT
*      retain FINTAB/FOUTTAB special-name search; replace GENFIND with
*      DYNFIND, passing STGENIN or STGENOUT in R3.
*
* 3. CLOSESTR
*      after CLOSE of STGENIN/STGENOUT, call DYNFREE instead of merely
*      clearing the descriptor.  Static stream handling remains V15.
*
* 4. CLOSEALL
*      close static streams, then BAL R14,DYNCLOSE.  Remove CLOSEPOL.
*
* 5. Static storage
*      remove GINTAB/GOUTTAB and GINSD*/GOUTSD*/GIDCB*/GODCB*/buffers.
*      Keep GENEXL/GENJFCB because RDJFCB still uses the shared scratch.
*
* 6. FIND semantics
*      a failed GETMAIN or missing DD returns zero, preserving the BCPL
*      FINDINPUT/FINDOUTPUT contract expected by the MR10 compiler.
***********************************************************************
