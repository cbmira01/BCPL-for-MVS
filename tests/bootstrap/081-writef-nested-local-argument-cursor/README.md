# 081 — Historical WRITEF's nested-local argument cursor

## Motivation

075 and 076 demonstrate that historical BLIB WRITEF prints data
argument three as 2. Probes 077–080 establish contiguous argument
homes, the twelve-formal signature, and preservation through nested
WRCH/WRITES calls. This probe isolates another feature of the actual
historical body: the loop and lexical scopes surrounding
`LET F, ARG, N = 0, T!0, 0`, and cursor advancement `T:=T+1`.

## Probe

A separately compiled twelve-formal CHECK uses `LET T=@A`,
`FOR P=1 TO 3`, nested blocks and simultaneous local declarations
to fetch and print three arguments, advancing `T` after each one.
There is no SWITCHON or indirect function call yet.

Expected exact output: `11 22 33`.

PASS would shift the next diagnostic to WRITEF's dispatch and
indirect function invocation; FAIL would implicate the
combination of nested local-variable allocation and cursor access.

Persistent BLIB object; no modification of BLIB, CG370 or BCPLMAIN.

## Status

**PASS** — user-executed regression 081 on TK5 (2026-10-08 local), exact `11 22 33`; 1 PASS / 0 FAIL. Nested local ARG cursor semantics succeed; WRITEF 075/076 still fail. Future diagnostics must preserve instrumented CG370 assembly.
