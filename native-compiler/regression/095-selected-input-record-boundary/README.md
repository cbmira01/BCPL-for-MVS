# 095 — FB/80 record boundary as BCPL newline

Status: **PENDING TK5**.

A named BCPIN DD supplies two physical records with leading A and B.
After the first record, RDCH should return BCPL newline character 10,
not the remaining EBCDIC blank padding. The test renders the newline
as `|` so existing narrow WRCH can show the result in one SYSPRINT
record. Expected `A|B`; any mismatch prints `?` at its position.

Chosen initial compatibility rule: RDCH trims trailing EBCDIC blanks
from each fixed 80-byte record and returns one logical newline (10)
before advancing to the next physical record. Interior blanks remain.
This is a provisional MVS mapping, **not** a source-proven statement
that historical Cambridge BCPL universally discarded trailing blanks.

This test does not establish EOF, UNRDCH, stream switching, or
general output record framing. Regression 094 must remain passing.
