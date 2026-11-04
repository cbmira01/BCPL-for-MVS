# 064 - WRITEF alphabetic octal width

The surviving IBM System/370 BLIB WRITEF implementation
interprets the alphabetic width character `A` as decimal 10.
For `%OA`, decimal 42 (octal 52) is displayed as exactly ten
zero-filled octal digits.

## Source

```bcpl
WRITEF(">%OA<", 42)
```

Expected output:

```text
>0000000052<
```

## Acceptance criteria

- Compile ordinary Cambridge BCPL and call G!76 at byte offset 304.
- Decode alphabetic octal width A as 10.
- Produce ten octal digits with leading zero padding.
- Terminate normally and preserve existing numeric-format cases.

Historical basis: `richards-bcpltape/bcplib/bcpl/blib`.
The assembler implementation remains a provisional runtime service.

## Status

**PASS** — native MVS execution on 2026-10-08; output `>0000000052<` (1 PASS, 0 FAIL).
