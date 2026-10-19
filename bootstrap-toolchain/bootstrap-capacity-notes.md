# Bootstrap capacity notes

These notes record the empirical INTCODE image sizes relevant to bootstrapping the Cambridge `SYN` and `TRN` phases under `icintv17`.

## icintv17 program-vector capacity

`icintv17.asm` currently defines:

```asm
PROGCNT  EQU   20001
PROGLEN  EQU   PROGCNT*4
```

The program vector is obtained dynamically with `GETMAIN`, so its present capacity is 20,001 BCPL words, or 80,004 host bytes. This is not a fixed static assembler area.

The principal capacity question for the Cambridge bootstrap is therefore straightforward: after Cambridge `SYN` and `TRN` are temporarily source-demoted, compiled by the MR10 frontend, lowered through CGI, and loaded with the bootstrap runtime, does the resulting interpreted image remain below 20,001 words?

## Empirical MR10 baseline

JES2 job 880, produced by a normal `compile-and-run` of `richards-factorial.bcpl`, gives a clean baseline.

The compile step loads:

```text
SYNI + TRNI + BLIBI + ICLIB
```

and `icintv17` reports:

```text
INTCODE SYSTEM ENTERED, PROGRAM SIZE = 9972
```

Therefore:

```text
PROGVEC capacity                 20,001 words
MR10 compiler/runtime image       9,972 words
remaining capacity               10,029 words
headroom                           50.1%
```

This means the existing interpreted compiler/runtime image occupies just under half of the current program vector.

The same job gives two useful secondary measurements.

The code-generation step loads:

```text
CGI + BLIBI + ICLIB = 3388 words
```

The final factorial executable plus runtime loads as:

```text
compiled factorial + BLIBI + ICLIB = 639 words
```

These measurements establish that the 9,972-word compile image, not CGI or the demonstration program, is the useful baseline when judging Cambridge frontend capacity.

## Consequence for Cambridge SYN/TRN

The current compiler/runtime image could grow to almost twice its present total size before reaching the current `PROGVEC` limit:

```text
20001 / 9972 ~= 2.01
```

Because BLIBI and ICLIB are part of both images and are not expected to double merely because the frontend changes, the Cambridge `SYN+TRN` portion has somewhat more than a simple 2x growth allowance relative to the MR10 `SYNI+TRNI` portion.

The practical conclusion is that there is a plausible chance that the source-demoted Cambridge `SYN` and `TRN` will fit in `icintv17` without any increase in `PROGVEC`.

Do not enlarge `PROGVEC` preemptively. First generate the Cambridge INTCODE and let the existing `PROGRAM SIZE = ...` report answer the question empirically.

## If expansion is needed

Expansion appears architecturally simple because the vector is already dynamically allocated. For example:

```asm
PROGCNT  EQU   40001
```

would approximately double the program-vector storage, and the existing `PROGLEN`, `GETMAIN`, and `FREEMAIN` expressions would follow automatically.

Before relying on a larger vector, verify that all INTCODE-assembler stores are bounds-checked against the program-vector extent. Capacity failure should become an explicit diagnostic rather than storage corruption or an S0C4.

A desirable failure form is conceptually:

```text
INTCODE LOAD ERROR: PROGRAM VECTOR EXHAUSTED
required:  <n> words
capacity:  20001 words
```

No evidence currently suggests that the INTCODE address representation itself imposes a 20,001-word limit. In `icintv17`, BCPL code/data pointers are represented as System/370 word addresses and converted to host byte addresses for memory access. The present limit is therefore primarily a storage-allocation policy.

## Acceptance measurement for the Cambridge bootstrap

The decisive test is one line from the first successful load of the source-demoted Cambridge frontend:

```text
INTCODE SYSTEM ENTERED, PROGRAM SIZE = n
```

Interpretation:

```text
n < 20001   -> current icintv17 PROGVEC is sufficient
n >= 20001  -> enlarge PROGVEC and repeat
```

The known baseline to compare against is:

```text
MR10 SYNI + TRNI + BLIBI + ICLIB = 9972 words
```

This measurement should remain part of the bootstrap record so that future changes to Cambridge source adaptation, headers, runtime shims, or ICINT can be compared against a fixed empirical reference.
