* CO.3 private BCPL-callable unregister before FREEVEC.
* G!300 CO3DROP(worker); R7=0 success / -2 refusal. No raw
* descriptor is dereferenced before registered-address admission.
* Refuse unless root is current, worker is idle, parent-free and
* unreferenced by the other registered worker. Reopen vacant slot.
         USING CO3DROP,4
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
