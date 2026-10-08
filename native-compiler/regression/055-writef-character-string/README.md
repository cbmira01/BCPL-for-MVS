# 055 - WRITEF character and string formatting

This regression extends the native WRITEF bootstrap with the two historical
BLIB conversions that map directly to existing character/string output
semantics:

- `%C` -> `WRCH(ARG)`
- `%S` -> `WRITES(ARG)`

The surviving BLIB WRITEF advances its argument pointer after each conversion.
Test 055 therefore exercises two conversions in one call so that sequential
argument consumption is part of the contract.

## Source shape

```bcpl
LET F = TABLE #X046CC36C, #XE2000000
LET S = "HELLO"

WRITEF(F, 193, S)
```

Expected output:

```text
AHELLO
```

The format is constructed as module-resident TABLE data rather than written as an
inline source string. This deliberately bypasses a transport/lexer problem
observed with an inline `%S` format in SYSIN while preserving the exact target
BCPL string bytes: length 4 followed by EBCDIC `%C%S` (`6C C3 6C E2`).

## WIP runtime rule

The bootstrap G!76 implementation now recognizes:

- literal format bytes;
- `%N` signed decimal formatting from Test 054;
- `%C` one-character output;
- `%S` BCPL length-prefixed string output.

For this test, R7 carries FORMAT, R8 carries target EBCDIC 193 (`'A'`), and R9
carries the BCPL word pointer held in local `S`. The runtime saves the formatting
arguments before repurposing R9 as OUTPOS and consumes them through a small
argument cursor.

This remains bootstrap machinery, not a claim that historical BLIB WRITEF was
implemented in machine code.

## Acceptance criteria

A successful Test 055 must:

- compile a three-argument WRITEF call;
- place the target EBCDIC value 193 (`'A'`) in R8;
- construct the third argument as a BCPL word pointer in R9;
- call G!76 through byte displacement 304;
- consume R8 for `%C` and then R9 for `%S`;
- emit exactly `AHELLO`;
- terminate normally through FINISH.

## Status

PASS — native run on 2026-10-08; emitted `AHELLO`.
