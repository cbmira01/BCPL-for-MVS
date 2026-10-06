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

PASS.

Job 968 on 2026-10-06 assembled, link-edited, and executed successfully:

```text
ASM   RC=0000
LKED  RC=0000
GO    RC=0000
```

The native program emitted:

```text
HELLO
```

The regression runner reported:

```text
=== Regression result ===
TEST:        04-string-output
OBJECTIVE:   PASS
TERMINATION: NORMAL
RESULT:      PASS
```

This validates the intended Test 04 surface: BCPL string-literal layout,
count-byte access, GETBYTE word-pointer handling, generated FOR-loop control,
repeated GETBYTE calls, repeated WRCH calls, preservation of the caller
B register across native primitive returns, and normal return from the
native runtime to MVS.


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


### Job 962 termination classification

`job-summary --verbose 962` reports S322 for the GO step after the expected
`HELLO` output was produced.

This places Test 04 in the same termination-failure class already observed
after Test 03 output.  The string-output objective remains proven; the
remaining defect is normal native termination after FINISH.


### Runner result semantics

The regression runner now treats Test 04's string-output objective as passed
when the JES report contains `HELLO`, even if the GO step subsequently ends
with the known S322 termination defect.

In that case the runner reports:

```text
=== BCPL output ===
HELLO

TEST OBJECTIVE: PASS
TERMINATION: S322 (known runtime defect)
```

This does not classify the overall runtime termination path as correct; it
only keeps Test 04 focused on the contract it was created to validate.


### Job 968 final pass

Job 968 is the first fully successful native string-output run for this
regression.  It completed ASM, LKED, and GO with RC=0000 and emitted the
expected `HELLO` record.

The termination defect seen in Jobs 962, 964, and 966 was traced to MVS
save-area discipline in BCPLMAIN.  The generated module prefix had already
saved the incoming R14..R12 image in the caller's save area, but BCPLMAIN
continued to use that same R13 while issuing MVS services such as OPEN and
PUT.  Those services were therefore free to use or overwrite the caller's
save-area contents before FINISH attempted the final restore.

BCPLMAIN now establishes a private 18-fullword MVS save area before making
MVS service calls.  On final return it restores the caller's R13 first and
then reloads the original R14..R12 image saved by the generated module
prefix.

Job 968 validates that correction for the Test 04 path.

### Contracts established by Test 04

The successful run provides direct evidence for all of the following:

- BCPL string literals use a count byte followed by target character bytes.
- `"HELLO"` is generated as length 5 followed by EBCDIC H, E, L, L, O.
- BCPL string values are word pointers for the machine-dependent byte
  primitives used here.
- G!85 `GETBYTE` correctly converts the BCPL word pointer back to a byte
  address and returns the selected byte.
- Generated FOR-loop control works for this traversal.
- G!14 `WRCH` can be called repeatedly and preserves the execution state
  needed by generated code.
- Native primitives that do not establish a fresh BCPL workspace must
  restore caller B in R4 from 0(R5) before returning through R6.
- The QSAM SYSPRINT output path can OPEN, accept buffered native output, and
  PUT the completed record.
- BCPLMAIN must own a private MVS save area while invoking MVS services.
- FINISH can return normally to MVS once that save-area discipline is
  observed.

### Scope boundaries

This test does not yet prove:

- the historical selected-stream interface;
- newline or record-boundary semantics of WRCH;
- a historical WRITES implementation;
- BLIB linkage;
- dynamic loading or unloading;
- general dataset I/O;
- the full historical BCPLMAIN cleanup and recovery contract.

Test 04 deliberately remains a primitive string-output regression built on
GETBYTE and WRCH.  Library-level WRITES integration belongs to a later test.
