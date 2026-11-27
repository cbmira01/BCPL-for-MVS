# 199-qsam-real-getmain-refusal

Bounded 1024-byte conditional GETMAIN pressure, actual stage GETMAIN RC=4, pressure blocks all freed, surviving independent handle and successful reopen. Final counters zero. Expected GO RC=0.

Both native profiles use a temporary instrumented QSAM object; neither tests the installed BCPLQSAM object for this fault. No permanent dataset writes or device operations. Fresh compilation on each run, no historical workarea dependency.
