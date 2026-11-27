# 200-qsam-combined-rollback-quarantine

Stage refusal and test-injected nonzero status after actual successful rollback CLOSE; primary -11 retained, no handle published, independent handle survives, successful reopen uses next public ID. Quarantined second slot retained with no stage, exactly one close call, finalizer RC=8. This exercises existing provisional precedence, not a new normative API guarantee or genuine MVS CLOSE failure.

Both native profiles use a temporary instrumented QSAM object; neither tests the installed BCPLQSAM object for this fault. No permanent dataset writes or device operations. Fresh compilation on each run, no historical workarea dependency.
