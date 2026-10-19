# Regression 101 — two-open-output-destinations

Status: PENDING TK5. Both SYSPRINT and BCPALT must be OPEN
simultaneously. BCPALT is a separate 132-byte FB SYSOUT DD.
Expected default output: "AC".
Expected alternate output: "B".

Note: pass acceptance requires independent alternate-DD capture,
not merely finding the expected characters in the assembler listing.
