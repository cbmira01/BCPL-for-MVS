# 080 — Long formal argument vector after nested BLIB calls

## Motivation

075 and 076 fail specifically at WRITEF's third data argument.
077, 078 and 079 prove that ordinary @A access works with three,
four, and twelve formal parameters, respectively. Historical WRITEF
also makes nested calls while walking its format.

## Probe

In a freshly compiled twelve-formal CHECK procedure, establish
`T=@A`, call real historical `WRCH` and `WRITES`, and then
read `T!0`, `T!1`, `T!2` and direct C. The caller passes
`CHECK(0,11,22,33)`.

Expected exact output: `>HI< 11 22 33 33`.

A failure implicates preservation of the local argument-vector
pointer across library calls. A pass shifts attention to actual
WRITEF body compilation and the installed BLIB object.

BLIB and BCPLMAIN remain unmodified, and 075/076 remain failing.

## Status

PENDING TK5 execution.
