# 054 - WRITEF integer formatting

This regression adds the first formatted WRITEF conversion to the native
bootstrap runtime.

The surviving BLIB source defines WRITEF with FORMAT in the first argument and
takes subsequent arguments from the contiguous argument area. Its `%N` case
dispatches directly to `WRITED(ARG,0)`, meaning signed decimal output with no
field-width request.

## Source shape

```bcpl
WRITEF("%N", 42)
```

The expected output is:

```text
42
```

## WIP runtime rule

The bootstrap G!76 implementation now recognizes `%N` in the format string.

For this first native formatting step:

- R7 is the BCPL word pointer to FORMAT;
- R8 supplies the first formatting argument;
- `%N` emits that value as signed decimal;
- literal text continues to use the Test 053 path;
- FINISH flushes the existing buffered SYSPRINT record.

The decimal helper handles zero, positive values, and ordinary negative
32-bit values. The most-negative fullword edge case is not claimed by this
test and remains outside the current bootstrap contract.

Other WRITEF directives, widths, additional arguments beyond this first slot,
and newline semantics remain deferred.

## Acceptance criteria

A successful Test 054 must:

- compile a two-argument WRITEF call;
- show argument 2 arriving through R8;
- call G!76 through byte displacement 304;
- emit exactly `42`;
- terminate normally through FINISH.

## Status

Pending native run.
