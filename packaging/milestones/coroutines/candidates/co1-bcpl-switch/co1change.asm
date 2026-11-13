***********************************************************************
* CO1CHG - CO.1 TEST-ONLY BCPL-callable native context transfer
* G!298 CO1INIT(root,worker,stack,procedure), four BCPL arguments
* G!299 CO1SW(value,target), two BCPL arguments
* Root/worker descriptor: 24 words; 8..23 = saved R0..R15.
* CO1SW uses an ordinary BCPL call workspace and resumes through
* the existing System Vector return implementation at R11.
* NOT a released CHANGECO ABI; no validation of invalid pointers.
***********************************************************************
CO1CHG   CSECT
         ENTRY CO1INIT,CO1SW
         EXTRN STKLIM,APLIMIT
*
CO1INIT  STM   4,10,0(15)
         LR    5,15
         BALR  10,0
         USING *,10
         SLL   7,2              ROOT DESCRIPTOR BYTE ADDRESS
         SLL   8,2              WORKER DESCRIPTOR BYTE ADDRESS
         LR    0,9              KEEP ALLOCATED WORD POINTER
         SLL   9,2              STACK BYTE ADDRESS
         ST    7,ROOTPTR
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
         L     0,28(8)
         ST    0,16(4)          RESTORED R4 = WORKER PROCEDURE
         ST    9,20(4)          RESTORED R5 = SYNTHETIC CALLER
         L     0,=A(CO1WBOOT)
         ST    0,24(4)          RESTORED R6 = FIRST ENTRY
         LA    0,64(9)
         ST    0,60(4)          RESTORED R15 = WORKER WORKSPACE
         SR    7,7              CO1INIT RESULT = ZERO
         BCR   15,11            RETURN THROUGH BCPL RETIMPL
         LTORG
         DROP  10
*
* This first-entry trampoline enters a real compiler-generated worker
* procedure; return follows the ordinary frame-based return path.
*
CO1WBOOT BALR  6,4
CO1WDONE BALR  10,0
         USING *,10
         L     8,ROOTPTR
         SRL   8,2              ROOT AS BCPL WORD POINTER
         LA    15,32(5)         PRIVATE SPACE ON WORKER STACK
         L     4,=A(CO1SW)
         BALR  6,4              PASS WORKER RESULT TO ROOT
CO1BAD   B     CO1BAD           TERMINATED WORKER MUST NOT RESUME
         LTORG
         DROP  10
*
* Ordinary BCPL call; 64-byte snapshot is candidate-only workspace.
* No MVS service or checked BCPL entry occurs during limit updates.
*
CO1SW    STM   0,15,0(15)       INCOMING GPRS BEFORE SCRATCH USE
         LR    5,15             PRIVATE SWITCH FRAME / P
         BALR  10,0
         USING *,10
         L     2,CURPTR
         MVC   32(64,2),0(5)    SAVE ALL ORIGINAL R0..R15
         L     0,60(5)          ORIGINAL R15 = SWITCH FRAME
         ST    0,52(2)          SAVED R5 (P) ON RESUMPTION
* Change the first three snapshot words into a real RETIMPL frame:
* R4 at frame!0, original caller P at frame!1, caller R6 at frame!2.
         L     0,16(5)
         ST    0,0(5)
         L     0,20(5)
         ST    0,4(5)
         L     0,24(5)
         ST    0,8(5)
         L     0,=A(CO1RET)
         ST    0,56(2)          SAVED R6 = RESUME TRAMPOLINE
* Original R8 is at offset 32; original R7 is at offset 28.
         L     2,32(5)          TARGET IS ORIGINAL R8 WORD PTR
         SLL   2,2              DESCRIPTOR BYTE ADDRESS
         L     0,28(5)          ORIGINAL R7 VALUE
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
CO1RET BCR   15,11           ORDINARY BCPL RETURN TRAMPOLINE
         LTORG
         DROP  10
         DS    0F
ROOTPTR  DC    F'0'
WORKPTR  DC    F'0'
CURPTR   DC    F'0'
         END   CO1CHG
