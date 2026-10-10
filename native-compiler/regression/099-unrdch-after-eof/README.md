# Regression 099 — unrdch-after-eof

Status: PENDING TK5 acceptance. Deterministic BCPIN QSAM fixture.
Expected output: A/EEE.

This character-stream test exercises the current documented TK5
FB80 trim/newline adapter; it does not assert historical blank-padding
behavior for arbitrary RECFM or variable-length datasets.
