# Compiler INTCODE

These files let ICINT run the MR10 BCPL compiler without rebuilding it.

| File | Purpose | Origin |
| --- | --- | --- |
| `syni.int` | Reads BCPL syntax | Historical MR10 kit |
| `trni.int` | Translates BCPL to OCODE | Historical MR10 kit |
| `cgi.int` | Converts OCODE to INTCODE | Historical MR10 kit |
| `blibi.int` | BCPL library functions | Historical MR10 kit |
| `iclib.int` | MVS-specific interpreted runtime support | This project |

The first four files are preserved copies from `richards-bcpltape/mr10/bcplkit/`. Their origin and licenses do not change because copies are kept here.

## Compile path

```text
BCPL source
  -> SYNI / TRNI -> OCODE
  -> CGI -> INTCODE
  -> ICINT with BLIBI / ICLIB -> program output
```

Use `tools/compile-and-run` to compile a BCPL program or `tools/run-intcode` to run an existing INTCODE deck. MVS jobs use the installed `ICINT19`. Native code generation is a separate part of the reconstruction.
