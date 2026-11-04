# 063 - WRITEF alphabetic hexadecimal width

The surviving IBM System/370 BLIB WRITEF implementation
interprets an alphabetic field-width character `A` as decimal 10.
For hexadecimal conversion `%XA` therefore outputs ten hexadecimal
digits. The 32-bit argument is treated as an unsigned bit pattern;
two leading zero digits precede its normal eight-digit representation.

## Source

```bcpl
WRITEF(">%XA<", 42)
```

Expected output:

```text
>000000002A<
```

## Acceptance criteria

- Compile an ordinary Cambridge BCPL format string.
- Generate the call to G!76 (byte offset 304) with argument 42 in R8.
- Decode alphabetic width A as 10 in the hexadecimal path.
- Produce exactly ten uppercase hexadecimal digits, including leading zeroes.
- Exit normally and preserve the earlier decimal and octal width decoders.

Historical evidence: `richards-bcpltape/bcplib/bcpl/blib`,
particularly the EBCDIC-specific width conversion in WRITEF.
The assembler implementation is still a provisional bootstrap runtime.

## Status

**PASS** — native MVS execution on 2026-10-08; output `>000000002A<` (1 PASS, 0 FAIL).
