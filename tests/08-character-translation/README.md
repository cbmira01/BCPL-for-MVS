# Character translation regression test

This test exercises the boundary between host ASCII source/data, MVS EBCDIC records, ICINT's host stream adapter, and the historical BCPL compiler/runtime character model.

The BCPL source deliberately uses the historical backslash spellings for logical OR (`\/`), logical AND (`/\`), not-equal (`\=`), and unary logical NOT (`\`). These are valid forms recognized by the MR10 SYN lexer and must not be rewritten merely to accommodate a host character-set mismatch.

The program also opens the named input DD `PUNCT` and prints the numeric values returned by `RDCH` for this fixture:

```text
\ / | [ ] { } ^ ~
```

This gives a second check of the EBCDIC-to-BCPL translation path after the source itself has compiled.

Run from the repository root:

```text
tools/compile-and-run \
    --results \
    --save-ocode \
    --save-intcode \
    --job-name CHARXLT \
    --dd PUNCT=tests/08-character-translation/punct.txt \
    asm/icintv16.asm \
    tests/08-character-translation/character-translation.bcpl
```

`--save-ocode` and `--save-intcode` are intentional. A successful compile should recover the intermediate compiler outputs as:

```text
workarea/character-translation.ocode
workarea/character-translation.intcode
```

Those files provide evidence that the backslash-bearing source passed SYN/TRN and CGI, rather than merely reaching the final runtime by some alternate path.

At the time this test was added, the known failure mode was a SYN `ILLEGAL CHARACTER` report at a source backslash. The purpose of the test is to expose and then permanently guard the correct host-character translation fix in ICINT; avoiding the historical BCPL syntax is not an acceptable resolution.
