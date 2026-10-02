# Word Count

Counts characters, words, and lines from a named MVS input stream called `TEXT`.

Run from the repository root:

```sh
tools/compile-and-run --results \
    --dd TEXT=suite/word-count/input.txt \
    asm/icintv16.asm \
    suite/word-count/word-count.bcpl
```
