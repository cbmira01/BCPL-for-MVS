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

PARTIAL PASS: STRING OUTPUT PROVEN; TERMINATION STILL FAILS.

Job 962 on 2026-10-06 assembled and link-edited successfully and emitted:

```text
HELLO
```

This validates the intended Test 04 surface: BCPL string-literal layout,
count-byte access, GETBYTE word-pointer handling, generated FOR-loop control,
repeated GETBYTE calls, repeated WRCH calls, and preservation of the caller
B register across native primitive returns.

The job subsequently ABENDed after the observable string output completed.
That termination failure remains separate runtime work and is not yet
classified here as identical to the Test 03 termination failure.


### Job 960 diagnosis

The first native run failed immediately with S0C1. The generated module
contained the expected count-byte/EBCDIC representation of `"HELLO"`, so
string construction itself was correct.

The dump established that R4 still held the address of the native GETBYTE
primitive after GETBYTE returned. Generated code then executed a branch
relative to R4 and landed inside the global vector, where sentinel data was
executed as instructions.

This proves an additional native primitive calling convention: machine-code
primitives called without a new BCPL workspace must restore the caller's B
register (R4) from word zero of the current workspace, 0(R5), before
returning through R6.
