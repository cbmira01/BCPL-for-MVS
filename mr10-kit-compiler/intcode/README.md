# INTCODE material

This directory contains the working INTCODE inputs used by the interpreted bootstrap.

## Historical compiler/runtime files

Four files are byte-for-byte copies of the corresponding files in `richards-bcpltape/mr10/bcplkit/`:

| Working file | Historical source | Role |
| --- | --- | --- |
| `syni.int` | `mr10/bcplkit/syni` | syntax analysis / compiler front end |
| `trni.int` | `mr10/bcplkit/trni` | translator producing OCODE |
| `cgi.int` | `mr10/bcplkit/cgi` | historical OCODE-to-INTCODE generator |
| `blibi.int` | `mr10/bcplkit/blibi` | interpreted BCPL library/runtime support |

These are historical third-party files; keeping convenient copies here does not change their provenance or license status.

`iclib.int` is project-side hosted runtime support used with the reconstructed interpreter, including machine-dependent services such as the interpreted coroutine switch.

## Current pipeline

`tools/compile-and-run` uses these files to run:

```text
BCPL source
  -> SYNI + TRNI
  -> OCODE
  -> CGI
  -> INTCODE
  -> ICINT + BLIBI + ICLIB
```

This path is deliberately kept working while native System/370 work proceeds. The native direction now uses a surviving historical S/370 code generator as the starting point; it is not a plan to replace `CGI` with a newly invented backend without historical evidence.

Direct INTCODE programs can be run with `tools/run-intcode`. See `tools/README.md` for examples.

For the original sources and documentation, see `richards-bcpltape/README.md` and `THIRD-PARTY-NOTICES.md`.