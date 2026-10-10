# 096 — EOF after final record, stable on repeated RDCH

Status: **PENDING TK5**.

Single physical BCPIN record containing `A`. The selected-input
adapter must produce the character `A`, then a logical newline (10)
at the record boundary, followed by EOF (-1) on two successive
RDCH calls. The rendered markers are `/` for newline and `E` for
each correctly recognized EOF; `?` flags any mismatching value.

Expected output: `A/EE`.

This uses the existing EODAD path (sets INEOF on the first GET beyond
the last physical record) and its short-circuit in RDCH. It tests
the final-record transition, not stream switching, ENDREAD,
missing-DD error handling, or arbitrary record types.
