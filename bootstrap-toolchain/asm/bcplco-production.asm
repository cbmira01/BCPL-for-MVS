***********************************************************************
* BCPLCO - production native coroutine switch and deregistration
* CO2INIT(root,worker,stack,procedure) and CHANGECO(value,target).
* G!298 CO2INIT, G!299 CHANGECO, G!300 CO3DROP.
* Private 24-word descriptor; do not expose its internal layout.
* Root plus two workers; revocation-before-FREEVEC supported.
* Caller owns GETVEC(1087): 4096 safe bytes + 256 clearance.
* Restore 16 GPRs, STKLIM/APLIMIT, G54/G55, and checked /CN frames.
* First entry and natural return use normal generated BCPL linkage.
* No system calls during context transfer. Not reentrant.
***********************************************************************
* BCPL call interface (arguments supplied in R7-R10):
* CO2INIT: R7=root, R8=worker, R9=stack, R10=procedure.
*           All pointers use BCPL word addresses; returns 0/-2.
* CHANGECO: R7=transferred value, R8=known-live target.
*           Returns transferred value or -1 for invalid target.
* CO3DROP: R7=known-live worker; returns 0 or -2.
* Only root plus two registered workers are supported.
* Descriptor layout is PRIVATE; no stale-pointer safety promise.
* Singleton static storage means this code is not reentrant.
BCPLCO   CSECT
         ENTRY CO2INIT,CHANGECO
         ENTRY CO3DROP
         EXTRN STKLIM,APLIMIT
*
* Initialize caller-allocated worker and first saved context.
* The BCPL library allocates and later releases both the stack
* and descriptor. This routine does not call GETVEC or FREEVEC.
* Capture root stack bounds for later context restoration.
CO2INIT  STM   4,10,0(15)
         LR    6,0              SAVE CG370 R0; R6 SAVED IN FRAME
         LR    5,15
         BALR  10,0
         USING *,10
         SLL   7,2              ROOT DESCRIPTOR BYTE ADDRESS
         SLL   8,2              WORKER DESCRIPTOR BYTE ADDRESS
         LR    0,9              KEEP ALLOCATED WORD POINTER
         SLL   9,2              STACK BYTE ADDRESS
* Register a worker only under the same root, with no duplicates.
         L     4,ROOTPTR
         LTR   4,4
         BC    8,CO2FIRST
         C     7,ROOTPTR
         BC    7,CO2INBAD
CO2FIRST C     8,ROOTPTR
         BC    8,CO2INBAD
         C     8,REGW1
         BC    8,CO2INBAD
         C     8,REGW2
         BC    8,CO2INBAD
         L     4,REGW1
         LTR   4,4
         BC    8,CO2REG1
         L     4,REGW2
         LTR   4,4
         BC    8,CO2REG2
         B     CO2INBAD
CO2REG1 ST    8,REGW1
         B     CO2REGOK
CO2REG2 ST    8,REGW2
* Root and live worker addresses occupy a bounded registry.
* SWITCH validates this registry before target dereference.
* The root's saved bounds use its currently active stack.
CO2REGOK ST    7,ROOTPTR
         ST    7,CURPTR
         ST    0,12(8)
         L     0,216(12)         EXISTING ROOT STACKBASE
         ST    0,16(7)
         L     0,220(12)         EXISTING ROOT STACKEND
         ST    0,24(7)
         L     4,=A(STKLIM)
         L     0,0(4)
         ST    0,20(7)          ROOT SAFE LIMIT
         LA    0,1
         ST    0,0(7)           ROOT ACTIVE
         LA    0,2
         ST    0,0(8)           WORKER NEW
         LR    0,7
         SRL   0,2
         ST    0,4(8)           WORKER PARENT WORD POINTER
         LR    0,9
         SRL   0,2
         ST    0,16(8)          WORKER STACKBASE WORD PTR
         L     0,=F'4096'
         AR    0,9
         ST    0,20(8)          WORKER SAFE BYTE LIMIT
         A     0,=F'256'
         SRL   0,2
         ST    0,24(8)          WORKER STACKEND WORD PTR
         L     0,24(5)          ORIGINAL R10 = WORKER PROCEDURE
         ST    0,28(8)
*
* Stack paint compatible with BLIB STACKHWM (4096 safe + 256 guard).
* The caller owns at least 1088 words from GETVEC(1087).
*
         LR    7,9
         L     0,=X'5C40E2E3'
         L     14,=X'C3D2405C'
         L     4,=F'512'
* Paint safe worker stack with alternating BLIB STACKHWM
* markers. The 256-byte clearance stores the guard and
* high-water metadata outside the 1024-word checked region.
CO2PAINT ST    0,0(7)
         ST    14,4(7)
         LA    7,8(7)
         BCT   4,CO2PAINT
         L     4,20(8)
         LA    4,248(4)
         ST    0,0(4)           GUARD AT STACKEND-2
         L     4,20(8)
         AH    4,=H'-8'
         SRL   4,2
         L     7,24(8)
         SLL   7,2              ALLOCATED END BYTE ADDRESS
         AH    7,=H'-4'
         ST    4,0(7)           STACKEND-1 (HWM METADATA)
*
* Synthetic caller base. Normal generated WORKER entry stores its own
* caller P and BALR return at R15; RETIMPL returns to CO2WDONE.
*
* Construct a synthetic caller frame and saved GPR image.
* First activation must enter as normal compiler-generated
* BCPL linkage: valid P, W, R6 and R15 on the new worker.
* A direct branch would not set up the matching RETIMPL path.
         L     0,=A(CO2WDONE)
         ST    0,0(9)
         ST    9,4(9)
         ST    0,8(9)
         LA    4,32(8)
         STM   0,15,0(4)        COPY ROOT GENERATED CODE CONSTANTS
         ST    6,0(4)           FIRST WORKER R0 = CALLER R0
         L     0,28(8)
         ST    0,16(4)          RESTORED R4 = WORKER PROCEDURE
         ST    9,20(4)          RESTORED R5 = SYNTHETIC CALLER
         L     0,=A(CO2WBOOT)
         ST    0,24(4)          RESTORED R6 = FIRST ENTRY
         LA    0,64(9)
         ST    0,60(4)          RESTORED R15 = WORKER WORKSPACE
         LR    0,6              RESTORE CG370 R0 FOR CALLER
         SR    7,7              CO2INIT RESULT = ZERO
         BCR   15,11            RETURN THROUGH BCPL RETIMPL
CO2INBAD LR    0,6
         L     7,=F'-2'        INIT REFUSAL; PRIVATE STATUS
         L     10,24(5)
         BCR   15,11
         LTORG
         DROP  10
*
* This first-entry trampoline enters a real compiler-generated worker
* procedure; return follows the ordinary frame-based return path.
*
* The first-entry trampoline calls the actual BCPL worker.
* Normal generated frame linkage must handle its return.
CO2WBOOT BALR  6,4
* A naturally returned worker becomes TERMINATED before
* transferring its final result back to the root. Do not
* resume a terminal continuation.
CO2WDONE BALR  10,0
         USING *,10
         L     4,CURPTR
         LA    0,3
         ST    0,0(4)           TERMINATED BEFORE ROOT TRANSFER
         L     8,ROOTPTR
         SRL   8,2              ROOT AS BCPL WORD POINTER
         LA    15,32(5)         PRIVATE SPACE ON WORKER STACK
         L     4,=A(CHANGECO)
         BALR  6,4              PASS WORKER RESULT TO ROOT
CO2BAD   B     CO2BAD           TERMINATED WORKER MUST NOT RESUME
         LTORG
         DROP  10
*
* Snapshot incoming registers to our private static buffer, NOT the
* generated caller W frame. /CN supplies only linkage space.
* Only three return-frame words are written to that workspace.
* At BCPL call entry R4=CHANGECO; base on it before clobbering GPRs.
* No MVS service or checked BCPL entry occurs during limit updates.
*
         USING CHANGECO,4
* CHANGECO cooperatively suspends the current coroutine.
* Snapshot all sixteen GPRs in private scratch before altering
* registers: /CN generated workspace holds only return linkage,
* not enough space for a complete saved machine context.
CHANGECO    STM   0,15,CO2SREG     SAVE REGISTERS WITHOUT W OVERFLOW
         DROP  4
         LR    5,15             BCPL CALL WORKSPACE W
         BALR  10,0
         USING *,10
* Membership and state verified before target dereference.
         L     2,CO2SREG+32
         SLL   2,2
         LTR   2,2
         BC    8,CO2TERM
         C     2,ROOTPTR
         BC    8,CO2VALID
         C     2,REGW1
         BC    8,CO2VALID
         C     2,REGW2
         BC    7,CO2TERM
* Known-live registry admission happens before dereference.
* Reject self-switch and terminated state. A registry check
* does NOT validate arbitrary machine addresses or stale uses.
CO2VALID C     2,CURPTR
         BC    8,CO2TERM
         L     0,0(2)
         C     0,=F'3'
         BC    8,CO2TERM
         L     2,CURPTR
* Save the outgoing context into its own descriptor and
* make a three-word RETIMPL-compatible caller frame. On later
* resumption CO2RET returns to the suspended BCPL call.
         MVC   32(64,2),CO2SREG PRESERVE ALL ORIGINAL R0..R15
         ST    5,52(2)          SAVED R5 (P) ON RESUMPTION
* Change the first three snapshot words into a real RETIMPL frame:
* R4 at frame!0, original caller P at frame!1, caller R6 at frame!2.
         L     0,CO2SREG+16     ORIGINAL R4
         ST    0,0(5)
         L     0,CO2SREG+20     ORIGINAL R5
         ST    0,4(5)
         L     0,CO2SREG+24     ORIGINAL R6
         ST    0,8(5)
         L     0,=A(CO2RET)
         ST    0,56(2)          SAVED R6 = RESUME TRAMPOLINE
* Original R8 is at offset 32; original R7 is at offset 28.
         L     2,CO2SREG+32     TARGET IS ORIGINAL R8 WORD PTR
         SLL   2,2              DESCRIPTOR BYTE ADDRESS
         L     0,CO2SREG+28     ORIGINAL R7 VALUE
         ST    0,60(2)          INCOMING SAVED R7
* Switch the active stack's checked-entry limits and bounds.
* STKLIM/APLIMIT use byte addresses; G!54/G!55 use BCPL words.
* Restore all of them before resuming the incoming registers,
* without MVS service calls in between.
         L     0,20(2)          INCOMING SAFE LIMIT (BYTE)
         L     4,=A(STKLIM)
         ST    0,0(4)
         L     4,=A(APLIMIT)
         ST    0,0(4)
         L     0,16(2)          INCOMING STACKBASE (WORD)
         ST    0,216(12)
         L     0,24(2)          INCOMING STACKEND (WORD)
         ST    0,220(12)
         ST    2,CURPTR         SWITCH ACTIVE DESCRIPTOR
         LA    1,32(2)
         LM    0,15,0(1)        RESTORE THE INCOMING CONTEXT
         BCR   15,6             ENTER OR RESUME
* A refused target must leave current context and stack limits
* unchanged. Restore normal return linkage and report R7=-1.
CO2TERM L     0,CO2SREG+16
         ST    0,0(5)
         L     0,CO2SREG+20
         ST    0,4(5)
         L     0,CO2SREG+24
         ST    0,8(5)
         L     7,=F'-1'        PRIVATE INVALID TARGET RESULT
         L     2,CO2SREG+8
         L     0,CO2SREG
         L     10,CO2SREG+40
         BCR   15,11
CO2RET   BCR   15,11           ORDINARY BCPL RETURN TRAMPOLINE
         LTORG
         DROP  10
* CO.3 private BCPL-callable unregister before FREEVEC.
* G!300 CO3DROP(worker); R7=0 success / -2 refusal. No raw
* descriptor is dereferenced before registered-address admission.
* Refuse unless root is current, worker is idle, parent-free and
* unreferenced by the other registered worker. Reopen vacant slot.
         USING CO3DROP,4
* CO3DROP unregisters before the BCPL caller frees storage.
* It is called from root for a live inactive, parent-free worker
* not referenced as another registered worker's parent.
* Check slot membership before inspecting descriptor fields.
CO3DROP  STM   4,10,0(15)
         DROP  4
         LR    6,0
         LR    5,15
         BALR  10,0
         USING *,10
         SLL   7,2
         LTR   7,7
         BC    8,C3DFAIL
         L     4,CURPTR
         C     4,ROOTPTR
         BC    7,C3DFAIL
         C     7,REGW1
         BC    8,C3DREG
         C     7,REGW2
         BC    7,C3DFAIL
C3DREG   C     7,CURPTR
         BC    8,C3DFAIL
         L     4,0(7)
         C     4,=F'2'
         BC    7,C3DFAIL
         L     4,100(7)        C!25 = PARENT WORD PTR
         LTR   4,4
         BC    7,C3DFAIL
         L     4,REGW1
         LTR   4,4
         BC    8,C3DCHK2
         CR    4,7
         BC    8,C3DCHK2
         L     0,100(4)
         SLL   0,2
         CR    0,7
         BC    8,C3DFAIL
C3DCHK2 L     4,REGW2
         LTR   4,4
         BC    8,C3DCLEAR
         CR    4,7
         BC    8,C3DCLEAR
         L     0,100(4)
         SLL   0,2
         CR    0,7
         BC    8,C3DFAIL
* First mark the descriptor REVOKED, then clear its slot.
* Only after success may the library FREEVEC its storage.
* This ordering is not general ABA-safe stale-pointer recovery.
C3DCLEAR LA    4,4
         ST    4,0(7)          REVOKED STATE BEFORE UNREGISTER
         SR    4,4
         C     7,REGW1
         BC    8,C3DCLR1
         ST    4,REGW2
         B     C3DOK
C3DCLR1  ST    4,REGW1
C3DOK    SR    7,7
         B     C3DRET
C3DFAIL L     7,=F'-2'
C3DRET  LR    0,6
         L     10,24(5)
         BCR   15,11
         LTORG
         DROP  10
* Private singleton registry and temporary GPR snapshot.
* Shared scratch is why overlapping transfers are unsupported.
* Keep DS and ROOTPTR together for the candidate merge check.
         DS    0F
ROOTPTR  DC    F'0'
REGW1    DC    F'0'
REGW2    DC    F'0'
CURPTR   DC    F'0'
CO2SREG  DS    16F             PRIVATE R0..R15 ENTRY SCRATCH
         END   BCPLCO
