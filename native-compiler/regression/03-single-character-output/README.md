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

IMPLEMENTED, AWAITING NATIVE RUN.

`asm/bcplmain-wip.asm` now installs G!14 as a narrow native WRCH path.
Characters are buffered into one QSAM SYSPRINT record; FINISH writes that
record and closes the DCB.  This intentionally does not yet implement the
historical selected-stream, newline, wrapping, or general I/O semantics.

The regression runner also extracts the emitted `A` from the completed JES
report and displays it under `=== BCPL output ===` in the invoking WSL CLI.
