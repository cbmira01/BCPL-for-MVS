# Stream Fanout

Opens three named MVS input streams simultaneously, reads each stream, and closes it explicitly.

Run from the repository root:

```sh
tools/compile-and-run --results \
    --dd AIN=suite/stream-fanout/ain.txt \
    --dd BIN=suite/stream-fanout/bin.txt \
    --dd CIN=suite/stream-fanout/cin.txt \
    asm/icintv16.asm \
    suite/stream-fanout/stream-fanout.bcpl
```
