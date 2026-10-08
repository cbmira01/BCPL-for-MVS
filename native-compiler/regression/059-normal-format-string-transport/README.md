# 059 - normal format-string transport

This regression removes the target-TABLE workaround used by Tests 055-058 and
tests the compiler-input boundary directly.

The source contains an ordinary BCPL format literal:

```bcpl
LET S = "HELLO"
WRITEF("%C%S", 193, S)
```

Expected output:

```text
AHELLO
```

## Motivation

Test 055 initially failed while the final Cambridge source was supplied directly
as in-stream `SYSIN DD DATA`. The compiler diagnosed an unexpected newline
inside `"%C%S"`, even though `%N` had already worked in Test 054.

Rather than preserve target EBCDIC TABLE constants as a permanent workaround,
the host driver now stages the final source through IEBGENER into a temporary
FB80 data set and supplies that data set to the resident compiler as SYSIN.

This matches the record-oriented path already used by the resident compiler's
other MVS inputs and gives the final source a stable, inspectable MVS record
boundary.

## Acceptance criteria

A successful Test 059 must:

- compile the ordinary source literal `"%C%S"` without a lexer error;
- generate the normal three-argument WRITEF call;
- pass target EBCDIC 193 (`A`) as the first formatting argument;
- pass the BCPL pointer to `"HELLO"` as the second formatting argument;
- call G!76 through byte displacement 304;
- emit exactly `AHELLO`;
- terminate normally through FINISH.

If this passes, Tests 055-058 should be converted back from hand-built target
TABLE format strings to ordinary BCPL source literals.

## Status

Pending rerun after resident Cambridge rebuild.

Diagnosis established on 2026-10-08: the MR10 bootstrap lexer does not
recognize Cambridge `*C` or `*E` character escapes. The resident Cambridge
LEX therefore compiled `'*C'` as ordinary `'C'`, causing every literal
containing C to be treated as containing a control character. The bootstrap
demotion now rewrites these escapes to explicit decimal control codes before
building CAMBCOMP.
