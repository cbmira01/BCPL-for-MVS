***********************************************************************
* IODVPRB - M1 RDJFCB ALLOCATION INQUIRY PROBE.
***********************************************************************
IODVPRB  CSECT
         ENTRY IODVPRB
         EXTRN DDVERIFY
         STM   14,12,12(13)
         LR    12,15
         USING IODVPRB,12
         ST    13,OLDSAVE+4
         LA    13,NEWSAVE
* CUSTOMER is allocated explicitly by the GO JCL step.
         LA    1,NAMEYES
         L     15,=A(DDVERIFY)
         BALR  14,15
         LTR   15,15
         BNZ   FAILED
* A second probe must not inherit the first DDNAME.
         LA    1,NAMENO
         L     15,=A(DDVERIFY)
         BALR  14,15
         C     15,=F'8'
         BNE   FAILED
* The original allocated name still resolves on repetition.
         LA    1,NAMEYES
         L     15,=A(DDVERIFY)
         BALR  14,15
         LTR   15,15
         BNZ   FAILED
GOOD     L     13,OLDSAVE+4
         LM    14,12,12(13)
         SR    15,15
         BR    14
FAILED   L     13,OLDSAVE+4
         LM    14,12,12(13)
         LA    15,8
         BR    14
         LTORG
NAMEYES  DC    CL8'CUSTOMER'
NAMENO   DC    CL8'ZXYZ1234'
OLDSAVE  DS    18F
NEWSAVE  DS    18F
         END   IODVPRB
