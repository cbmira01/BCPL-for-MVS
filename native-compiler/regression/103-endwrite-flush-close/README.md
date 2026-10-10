# Regression 103 — endwrite-flush-close

Status: PENDING TK5. Both SYSPRINT and BCPALT must be OPEN
simultaneously. BCPALT is a separate 132-byte FB SYSOUT DD.
Expected default output: "Z".
Expected alternate output: "Q".

Note: pass acceptance requires independent alternate-DD capture,
not merely finding the expected characters in the assembler listing.
