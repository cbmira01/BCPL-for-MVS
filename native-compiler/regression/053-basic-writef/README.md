# 053 - basic WRITEF

This regression begins the native WRITEF sprint.

G!76 has historically been installed in the WIP runtime only as a no-op so
early control-flow tests could run without native BLIB. Test 053 replaces that
accommodation with the smallest executable WRITEF contract: an ordinary format
string containing no conversions and no newline directive is copied literally
to the existing buffered SYSPRINT record.

## Source shape

The program calls the already-proven no-space string-literal form:

```bcpl
WRITEF("HELLO")
```

and then executes FINISH.

The generated-code assertions require the ordinary global-vector call through
G!76 at byte displacement 304 and BALR linkage.

## WIP runtime rule

For this first step only, WRITEF treats argument 1 as a BCPL string:

- byte 0 is the string length;
- bytes 1..length are copied literally to OUTBUF;
- existing OUTPOS is advanced;
- FINISH performs the existing QSAM PUT.

No formatting conversion is interpreted yet. Newline handling, numeric
conversion, width controls, additional arguments, and selected-stream behavior
are explicitly deferred to later regressions.

This is a bootstrap implementation of the WRITEF surface, not a claim that the
historical BLIB routine had this machine-code body.

## Acceptance criteria

A successful Test 053 must:

- compile a direct WRITEF call through G!76;
- assemble and link with the new literal WRITEF bootstrap;
- emit exactly `HELLO`;
- terminate normally through FINISH.

## Status

PASS — native run on 2026-10-07; emitted `HELLO`.
