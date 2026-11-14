***********************************************************************
* CO1CHG - CO.1 TEST-ONLY BCPL-callable native context transfer
* G!298 CO1INIT(root,worker,stack,procedure), four BCPL arguments
* G!299 CO1SW(value,target), two BCPL arguments
* G!295 CO1RES(token) -> registered descriptor or zero
* Root/worker descriptor: 24 words; 8..23 = saved R0..R15.
* CO1SW uses an ordinary BCPL call workspace and resumes through
* the existing System Vector return implementation at R11.
* Candidate-only registered-root/two-worker target membership check.
* Reject NULL, UNREGISTERED, ACTIVE, TERMINATED with R7=-1.
* CO1DROP revokes only a TERMINATED registered worker (R7=0).
* Test-only opaque worker tokens, increased by four each lifetime.
* Test forces same descriptor address reinitialization (ABA model).
* Raw CO1SW and untrusted CO1INIT remain unprotected interfaces.
***********************************************************************
CO1CHG   CSECT
         ENTRY CO1INIT,CO1SW
         ENTRY CO1DROP,CO1RES
         EXTRN STKLIM,APLIMIT
*
CO1INIT  STM   4,10,0(15)
         LR    6,0              SAVE CG370 R0; R6 SAVED IN FRAME
         LR    5,15
         BALR  10,0
         USING *,10
         SLL   7,2              ROOT DESCRIPTOR BYTE ADDRESS
         SLL   8,2              WORKER DESCRIPTOR BYTE ADDRESS
         LR    0,9              KEEP ALLOCATED WORD POINTER
         SLL   9,2              STACK BYTE ADDRESS
* Reject duplicate live address; permit a revoked slot to reopen.
* Identity is the token, never the reused descriptor address alone.
         L     4,ROOTPTR
         LTR   4,4
         BC    8,CO1IFRST      FIRST ROOT SETUP
         C     7,ROOTPTR
         BC    7,CO1INBAD       UNEXPECTED ROOT
CO1IFRST C     8,ROOTPTR
         BC    8,CO1INBAD       ROOT CANNOT BE A WORKER
         C     8,REGW1
         BC    8,CO1INBAD       DUPLICATE LIVE DESCRIPTOR
         C     8,REGW2
         BC    8,CO1INBAD
         L     4,REGW1
         LTR   4,4
         BC    8,CO1RG1
         L     4,REGW2
         LTR   4,4
         BC    8,CO1RG2
         B     CO1INBAD       TWO LIVE WORKER LIMIT
* Token steps of 4 distinguish slot and generation.
* Refuse issuance near signed fullword wrap; no token cycling.
CO1RG1   L     4,TOKW1
         C     4,=F'2147483638'
         BC    2,CO1INBAD       GENERATION EXHAUSTED
         A     4,=F'4'
         ST    4,TOKW1
         ST    8,REGW1
         ST    4,RETTOK
         B     CO1RGOK
CO1RG2   L     4,TOKW2
         C     4,=F'2147483638'
         BC    2,CO1INBAD
         A     4,=F'4'
         ST    4,TOKW2
         ST    8,REGW2
         ST    4,RETTOK
CO1RGOK  ST    7,ROOTPTR
         ST    7,CURPTR
         ST    8,WORKPTR
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
CO1PAINT ST    0,0(7)
         ST    14,4(7)
         LA    7,8(7)
         BCT   4,CO1PAINT
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
* caller P and BALR return at R15; RETIMPL returns to CO1WDONE.
*
         L     0,=A(CO1WDONE)
         ST    0,0(9)
         ST    9,4(9)
         ST    0,8(9)
         LA    4,32(8)
         STM   0,15,0(4)        COPY ROOT GENERATED CODE CONSTANTS
         ST    6,0(4)           FIRST WORKER R0 = CALLER R0
         L     0,28(8)
         ST    0,16(4)          RESTORED R4 = WORKER PROCEDURE
         ST    9,20(4)          RESTORED R5 = SYNTHETIC CALLER
         L     0,=A(CO1WBOOT)
         ST    0,24(4)          RESTORED R6 = FIRST ENTRY
         LA    0,64(9)
         ST    0,60(4)          RESTORED R15 = WORKER WORKSPACE
         LR    0,6              RESTORE CG370 R0 FOR CALLER
         L     7,RETTOK       TEST-ONLY GENERATION TOKEN
         L     10,24(5)         RESTORE ORIGINAL R10
         BCR   15,11            RETURN THROUGH BCPL RETIMPL
* No user descriptor or stack touched on duplicate/full registry.
CO1INBAD LR    0,6
         L     7,=F'-2'        INIT REGISTRY REJECTED
         L     10,24(5)
         BCR   15,11
         LTORG
         DROP  10
*
* This first-entry trampoline enters a real compiler-generated worker
* procedure; return follows the ordinary frame-based return path.
*
CO1WBOOT BALR  6,4
CO1WDONE BALR  10,0
         USING *,10
         L     4,CURPTR         WORKER RETURNED NATURALLY
         LA    0,3
         ST    0,0(4)           STATE=TERMINATED BEFORE RETURN
         L     8,ROOTPTR
         SRL   8,2              ROOT AS BCPL WORD POINTER
         LA    15,32(5)         PRIVATE SPACE ON WORKER STACK
         L     4,=A(CO1SW)
         BALR  6,4              PASS WORKER RESULT TO ROOT
CO1BAD   B     CO1BAD           TERMINATED WORKER MUST NOT RESUME
         LTORG
         DROP  10
*
* Snapshot incoming registers to our private static buffer, NOT the
* generated caller W frame. /CN supplies only linkage space.
* Only three return-frame words are written to that workspace.
* At BCPL call entry R4=CO1SW; base on it before clobbering GPRs.
* No MVS service or checked BCPL entry occurs during limit updates.
*
         USING CO1SW,4
CO1SW    STM   0,15,CO1SREG     SAVE REGISTERS WITHOUT W OVERFLOW
         DROP  4
         LR    5,15             BCPL CALL WORKSPACE W
         BALR  10,0
         USING *,10
* First compare the address with a closed registry, WITHOUT a load
* through the supplied pointer. Do not mutate the active context.
         L     2,CO1SREG+32     ORIGINAL R8 TARGET WORD POINTER
         SLL   2,2
         LTR   2,2
         BC    8,CO1TERM        ZERO IS NEVER VALID
         C     2,ROOTPTR
         BC    8,CO1REGOK
         C     2,REGW1
         BC    8,CO1REGOK
         C     2,REGW2
         BC    7,CO1TERM       UNREGISTERED; NO DEREFERENCE
CO1REGOK C     2,CURPTR
         BC    8,CO1TERM        ACTIVE TARGET IS NOT RESUMABLE
         L     0,0(2)           FIRST TARGET DESCRIPTOR READ
         C     0,=F'3'
         BC    8,CO1TERM        NATURALLY TERMINATED
         L     2,CURPTR
         MVC   32(64,2),CO1SREG PRESERVE ALL ORIGINAL R0..R15
         ST    5,52(2)          SAVED R5 (P) ON RESUMPTION
* Change the first three snapshot words into a real RETIMPL frame:
* R4 at frame!0, original caller P at frame!1, caller R6 at frame!2.
         L     0,CO1SREG+16     ORIGINAL R4
         ST    0,0(5)
         L     0,CO1SREG+20     ORIGINAL R5
         ST    0,4(5)
         L     0,CO1SREG+24     ORIGINAL R6
         ST    0,8(5)
         L     0,=A(CO1RET)
         ST    0,56(2)          SAVED R6 = RESUME TRAMPOLINE
* Original R8 is at offset 32; original R7 is at offset 28.
         L     2,CO1SREG+32     TARGET IS ORIGINAL R8 WORD PTR
         SLL   2,2              DESCRIPTOR BYTE ADDRESS
         L     0,CO1SREG+28     ORIGINAL R7 VALUE
         ST    0,60(2)          INCOMING SAVED R7
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
* Reject without transferring: synthesize BCPL RETIMPL frame at W.
* Preserve original R0 for compiler-generated comparisons.
* R5 points at caller-provided W, and R11 remains RETIMPL.
CO1TERM  L     0,CO1SREG+16     ORIGINAL R4
         ST    0,0(5)
         L     0,CO1SREG+20     ORIGINAL R5
         ST    0,4(5)
         L     0,CO1SREG+24     ORIGINAL R6
         ST    0,8(5)
         L     7,=F'-1'        EXPLICIT TEST-ONLY ERROR VALUE
         L     2,CO1SREG+8
         L     0,CO1SREG
         L     10,CO1SREG+40
         BCR   15,11           ORDINARY BCPL RETURN
CO1RET BCR   15,11           ORDINARY BCPL RETURN TRAMPOLINE
         LTORG
         DROP  10
*
* Test-only CO1DROP(worker). Registry membership is checked before
* inspecting the descriptor. Only terminated, inactive workers can
* be revoked. Caller may FREEVEC only after result zero.
* Revoked slot may be reused with a NEW generation token.
*
         USING CO1DROP,4
CO1DROP  STM   4,10,0(15)       SAVE BCPL CALLER LINKAGE
         DROP  4
         LR    6,0              PRESERVE ORIGINAL R0
         LR    5,15             NEW BCPL RETURN FRAME
         BALR  10,0
         USING *,10
         SLL   7,2              TARGET BCPL WORD -> BYTE PTR
         LTR   7,7
         BC    8,CO1DFAIL       REJECT NULL
         C     7,REGW1
         BC    8,CO1DCHK
         C     7,REGW2
         BC    7,CO1DFAIL       UNKNOWN OR REVOKED
CO1DCHK  C     7,CURPTR
         BC    8,CO1DFAIL       ACTIVE CONTEXT
         L     4,0(7)           FIRST DESCRIPTOR READ
         C     4,=F'3'
         BC    7,CO1DFAIL       NOT TERMINATED
         LA    4,4
         ST    4,0(7)           REVOKED BEFORE UNREGISTRATION
         SR    4,4
         C     7,REGW1
         BC    8,CO1DCLR
         ST    4,REGW2         REMOVE SECOND WORKER
         B     CO1DOK
CO1DCLR ST    4,REGW1         REMOVE FIRST WORKER
CO1DOK  SR    7,7              SUCCESS
         B     CO1DRET
CO1DFAIL L     7,=F'-2'        REJECTED; NO DESCRIPTOR WRITES
CO1DRET LR    0,6              RESTORE ORIGINAL R0
         L     10,24(5)        RESTORE CALLER R10
         BCR   15,11           RETURN VIA BCPL RETIMPL
         LTORG
         DROP  10
*
* CO1RES(token): token-to-live-word-pointer lookup, WITHOUT reading
* descriptor memory. A stale token fails even if address is reused.
* Raw CO1SW is used only after this check in the BCPL CALLH wrapper.
*
         USING CO1RES,4
CO1RES   STM   4,10,0(15)
         DROP  4
         LR    6,0
         LR    5,15
         BALR  10,0
         USING *,10
         C     7,TOKW1
         BC    8,CO1RS1
         C     7,TOKW2
         BC    8,CO1RS2
         SR    7,7              BAD OR STALE TOKEN
         B     CO1RRET
CO1RS1   L     7,REGW1
         B     CO1RNOK
CO1RS2   L     7,REGW2
CO1RNOK  SRL   7,2              BYTE PTR TO BCPL WORD PTR
CO1RRET  LR    0,6
         L     10,24(5)
         BCR   15,11
         LTORG
         DROP  10
         DS    0F
ROOTPTR  DC    F'0'
WORKPTR  DC    F'0'
CURPTR   DC    F'0'
CO1SREG  DS    16F             PRIVATE R0..R15 ENTRY SCRATCH
REGW1    DC    F'0'            LIVE WORKER ONE BYTE ADDRESS
REGW2    DC    F'0'            LIVE WORKER TWO BYTE ADDRESS
TOKW1    DC    F'2'            SLOT ONE TOKEN SEED
TOKW2    DC    F'3'            SLOT TWO TOKEN SEED
RETTOK   DC    F'0'            LAST ISSUED TOKEN
         END   CO1CHG
