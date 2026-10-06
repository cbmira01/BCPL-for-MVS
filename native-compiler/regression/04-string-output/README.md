# 04 - String output through GETBYTE and WRCH

This test extends primitive character output into BCPL string traversal.

The program deliberately implements the historical shape of `WRITES`
inline:

```bcpl
FOR I = 1 TO GETBYTE(S,0) DO
    WRCH(GETBYTE(S,I))
```

The string literal is `"HELLO"`.

Expected observable output:

```text
HELLO
```

This test is intended to validate:

- generated representation of a BCPL string literal;
- the count byte at string offset zero;
- BCPL word-pointer conversion in `GETBYTE`;
- successive byte access through `GETBYTE`;
- generated FOR-loop control;
- repeated calls through G!14 `WRCH`;
- preservation of runtime state across repeated character output calls;
- visible multi-character output through the native SYSPRINT path.

This test intentionally does not call a native `WRITES` routine.
The surviving historical BLIB implements `WRITES` in BCPL above
`GETBYTE` and `WRCH`; that library integration belongs to a later rung.

## Status

DEFINED.

The lower-level primitives required by this test are already present in the
current BCPLMAIN WIP, but the test has not yet been run.
