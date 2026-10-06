# 03 - Single character output

This test introduces the first observable native output action.

It calls the BCPL runtime character-output routine `WRCH` with one
character, then terminates with `FINISH`.

The program is intended to prove these additional contracts:

```text
START
  -> resolve G!14 as WRCH
  -> pass one character argument
  -> native character-output path emits that character
  -> return to START
  -> FINISH
  -> normal MVS return
```

The expected observable result is one `A` character on the selected native
output destination.

The test deliberately avoids formatted output, strings, recursion, dynamic
storage, stream selection, and general library formatting services.

A failure here, after the earlier tests pass, should focus attention on:

- installation of G!14;
- ordinary global runtime-call mechanics;
- one-character argument passing;
- the first native character-output path in BCPLMAIN;
- the initial MVS output destination and its control structures.

This test is intentionally narrower than a future WRITEF test.  WRCH is the
primitive character-output contract to establish first.

## Status

PARTIAL PASS: CHARACTER OUTPUT PROVEN; TERMINATION STILL FAILS.

JES Job 954 on 2026-10-06 assembled and link-edited successfully.  The
generated BCPL program emitted the expected `A` to SYSPRINT, proving the
initial G!14 WRCH path through BCPLMAIN.

The job subsequently ABENDed during or after termination.  Therefore this
test is not yet a full regression pass.  The remaining failure is downstream
of character emission and should be investigated in the FINISH output-flush,
DCB CLOSE, and final MVS return path.

The current implementation intentionally does not yet provide the historical
selected-stream, newline, wrapping, or general I/O semantics.

The regression runner extracts the emitted `A` from the JES report and
displays it under `=== BCPL output ===` in the invoking WSL CLI.


### Job 956

A second native run with a larger CPU allowance again emitted the expected
`A` but terminated with S322.  This confirms that the character-output
path and QSAM PUT complete before the hang.  The common remaining operation
is the explicit QSAM CLOSE in FINISH.

For the next bootstrap probe, FINISH writes the record but does not issue an
explicit CLOSE.  Normal MVS step termination owns DCB cleanup temporarily.
This is a diagnostic/bootstrap accommodation, not the final BCPLMAIN cleanup
contract.
