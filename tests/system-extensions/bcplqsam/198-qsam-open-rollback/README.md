# 198-qsam-open-rollback

One injected stage refusal after genuine OPEN; actual rollback CLOSE, surviving independent handle, successful reopen and zero finalizer counters. Reuses accepted Q5RBFIN trace including its known final WTO fall-through. Expected GO RC=0.

Both native profiles use a temporary instrumented QSAM object; neither tests the installed BCPLQSAM object for this fault. No permanent dataset writes or device operations. Fresh compilation on each run, no historical workarea dependency.
