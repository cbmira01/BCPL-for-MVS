*
* Native routine for regression 26.
* Called from BCPL through G!151 using the generated BCPL ABI.
*
NATIVEAD CSECT
         STM   4,8,0(15)
         LR    5,15
         AR    8,7
         LR    7,8
         BCR   15,11
         END
