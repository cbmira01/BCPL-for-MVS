# 088 — Canonical STOP lifecycle regression

Status: **PENDING TK5**.

Leaves two live GETVEC blocks and executes canonical STOP(0). This exercises common STOP cleanup without instrumenting MVS FREEMAIN. Expected output 42; GO RC=0000.

This is a production-runtime test: no test-only STOP adapter is used.
The case does not independently count FREEMAIN calls or prove storage
manager accounting. Negative and out-of-range STOP arguments remain
outside its scope.
