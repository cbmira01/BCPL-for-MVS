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

NOT YET EXPECTED TO PASS.

The current `asm/bcplmain-wip.asm` does not yet implement G!14 WRCH or a
native character-output path.
