# Regression 102 — alternate-output-records

Status: PENDING TK5. Both SYSPRINT and BCPALT must be OPEN
simultaneously. BCPALT is a separate 132-byte FB SYSOUT DD.
Expected default output: "Z".
Expected alternate output: "A\nB".

Note: pass acceptance requires independent alternate-DD capture,
not merely finding the expected characters in the assembler listing.
