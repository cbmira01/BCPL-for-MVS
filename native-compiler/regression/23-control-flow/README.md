# 23 - Control-flow sweep

This regression exercises the classic BCPL conditional, repetitive, loop
control, and switch constructs in one native program.

Covered forms:

```text
IF
UNLESS
TEST ... THEN ... ELSE
WHILE
UNTIL
FOR
REPEAT
REPEATWHILE
REPEATUNTIL
BREAK
LOOP
SWITCHON
CASE
DEFAULT
ENDCASE
```

The source uses one accumulator, X.  Every successful control-flow path
contributes a known amount, and the final value is 42.

Expected output:

```text
42
```

## Expected progression

The intended progression is:

```text
start                         0
IF                            1
UNLESS                        3
TEST/THEN                     7
WHILE, two iterations         9
UNTIL, two iterations        11
FOR 1 TO 3                   17
REPEATWHILE, two iterations  19
REPEATUNTIL, two iterations  21
REPEAT + BREAK               22
FOR + LOOP                   24
SWITCHON CASE 24             42
```

The ELSE and DEFAULT paths deliberately assign 999 so an incorrect branch is
immediately visible in the final result.

## Purpose

Earlier regressions established arithmetic, calls, recursion, pointers, and
workspace/linkage behavior. Test 23 broadens native-code confidence to the
core source-language control-flow repertoire.

## Acceptance criteria

A successful run must:

- compile through the Cambridge compiler and historical CG370;
- assemble and link with no errors;
- terminate normally under MVS;
- emit exactly `42`;
- show generated conditional branches for IF, UNLESS, and TEST;
- show loop-back/exit branches for WHILE and UNTIL;
- show generated FOR-loop control;
- show post-test branches for REPEATWHILE and REPEATUNTIL;
- show BREAK exiting an indefinite REPEAT;
- show LOOP continuing the enclosing FOR without executing the skipped body;
- show SWITCHON dispatch to CASE 24 and an exit via ENDCASE.

Generated-code inspection is part of the proof. Because this test is
deliberately broad, the generated listing should be inspected by construct
rather than merely accepting the final output.

## Scope

This test targets the classic control-flow forms relevant to the current
Cambridge compiler. It does not introduce newer MATCH/EVERY language
extensions or nonlocal GOTO behavior.

## Status

DEFINED. Not yet run.
