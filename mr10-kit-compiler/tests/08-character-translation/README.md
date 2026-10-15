# BCPL character translation

This test checks how source text and input records move between ASCII, EBCDIC, and BCPL character codes.

| Input | What is checked |
| --- | --- |
| BCPL source | Historical backslash forms for OR, AND, not-equal, and NOT |
| `punct.txt` on DD `PUNCT` | Character values returned by RDCH |
| Saved OCODE / INTCODE | Proof that the source passed the compiler stages |

Run with `tools/mr10/compile-and-run --results --save-ocode --save-intcode` and `--dd PUNCT=mr10-kit-compiler/tests/08-character-translation/punct.txt`; supply the BCPL source in the same directory. Do not replace historical BCPL operators to hide a character-conversion bug.
