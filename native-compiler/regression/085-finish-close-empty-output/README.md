# 085 — FINISH closes an output DCB with no pending record

Status: **PENDING TK5**.

START immediately calls FINISH without WRCH or DEBUGINT. The runtime
opens BCPOUT during startup, but OUTPOS stays zero, so FINISH must
skip PUT, execute the canonical CLOSE (BCPOUT), reclaim allocations
and return normally.

Expected BCPL output: none. This case asserts normal ASM/LKED/GO
completion. It complements 084's pending-record flush-before-CLOSE
behavior. It does not establish general stream CLOSE behavior or
the historical STOP contract.
