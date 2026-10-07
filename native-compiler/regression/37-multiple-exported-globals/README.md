# 37 - Multiple exported globals

This regression exercises BCPLMAIN's generated-module trailer scan with several
user-defined callable globals in the same compiled module.

Expected output:

```text
42
```

## Source shape

The module defines and exports:

- LEFT as G!151;
- RIGHT as G!152;
- ADD as G!153;
- START as G!1.

START calls LEFT and RIGHT through the global vector, then calls ADD with their
returned values and reports the result through DEBUGINT.

## Contract under test

Earlier tests established one user global data slot and one callable exported
global. Test 37 extends the native module ABI to several exported definitions in
one trailer.

BCPLMAIN must:

- locate the trailer sentinel correctly;
- scan all exported-global pairs rather than stopping after one;
- install each generated address at the correct G displacement;
- preserve the START export while also installing several user globals.

Generated BCPL must then successfully load and call LEFT, RIGHT, and ADD through
R12/G.

Expected user-global displacements are:

```text
G!151 -> 604
G!152 -> 608
G!153 -> 612
```

## Acceptance criteria

A successful run must:

- compile through the resident Cambridge compiler and historical CG370;
- assemble, link-edit, and execute normally under MVS;
- emit exactly `42`;
- show trailer entries for globals 151, 152, 153, and START/1;
- show START loading LEFT, RIGHT, and ADD through R12/G at their corresponding
  byte displacements; and
- show all three calls completing through the ordinary native BCPL linkage.

The first successful run was inspected. START loads LEFT, RIGHT, and ADD from
`604(R12)`, `608(R12)`, and `612(R12)` respectively, and calls each through
`BALR 6,4`. The generated trailer contains export pairs for G!151, G!152,
G!153, and G!1/START, preceded by the trailer sentinel pair.

## Scope

This test adds no new language construct or runtime service. It is a focused
native module/trailer/global-vector regression.

## Status

PASS — emitted `42` on 2026-10-07.
