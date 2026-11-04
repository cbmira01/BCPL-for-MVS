# 089 — Canonical STOP lifecycle regression

Status: **PENDING TK5**.

Leaves a pending character in the BCPL output buffer before canonical STOP(8). Expected output E, normal job-step completion GO RC=0008, and successful ASM/LKED steps. An abnormal end or missing output is failure.

This is a production-runtime test: no test-only STOP adapter is used.
The case does not independently count FREEMAIN calls or prove storage
manager accounting. Negative and out-of-range STOP arguments remain
outside its scope.
