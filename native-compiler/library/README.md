# Native compiler library

This directory is reserved for native BCPL library material.

The intent is to keep library-level BCPL facilities separate from the
machine/runtime substrate in `asm/bcplmain-wip.asm`.

The surviving historical source of truth is:

```text
richards-bcpltape/bcplib/bcpl/blib
```

That source shows that routines such as `WRITES` and `WRITEF` are BCPL
library routines built above lower-level runtime primitives such as `WRCH`,
`GETBYTE`, and `PUTBYTE`.

Do not move historical source into this directory merely for convenience.
Bootstrap or transformed derivatives should remain reproducible and should
not obscure provenance.

Initial policy:

- `BCPLMAIN` owns machine/runtime services and MVS integration.
- This directory will hold native library integration material when that
  work begins.
- Regression tests may temporarily express small historical library
  algorithms inline when the purpose is to validate lower-level contracts.
- Test 04 deliberately does this for the historical `WRITES` loop rather
  than inventing a new machine-code string-output service.
- The first operational use of this directory should be driven by actual
  BLIB integration, not by speculative replacements.

The likely next milestone after primitive string traversal is to arrange for
real historical BLIB code to be compiled and linked with a generated native
BCPL program.
