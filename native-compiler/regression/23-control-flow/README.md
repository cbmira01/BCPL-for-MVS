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

PASS.

Job 1012 on 2026-10-06 assembled, link-edited, and executed successfully:

```text
ASM   RC=0000
LKED  RC=0000
GO    RC=0000
```

The native program emitted:

```text
42
```

Generated-code inspection confirms the control-flow forms individually.

### IF

The generated code compares X with zero and skips the body when the
condition is false:

```asm
C  0,12(5)
BC 7,0+L3-L1(4)
LA 7,1(0)
A  7,12(5)
ST 7,12(5)
L3 EQU *
```

### UNLESS

UNLESS uses the complementary condition, branching over the body when the
condition is true:

```asm
C  0,12(5)
BC 8,0+L4-L1(4)
LA 7,2(0)
A  7,12(5)
ST 7,12(5)
L4 EQU *
```

### TEST / THEN / ELSE

The TEST emits a conditional branch to the ELSE arm plus an unconditional
branch around ELSE after the THEN arm:

```asm
LA 7,3(0)
C  7,12(5)
BC 7,0+L5-L1(4)
...
BC 15,0+L6-L1(4)
L5 EQU *
LA 7,999(0)
ST 7,12(5)
L6 EQU *
```

### WHILE

The WHILE loop uses a branch to the test, then conditionally branches back
to the body while I<2:

```asm
BC 15,0+L8-L1(4)
L7 EQU *
...
L8 EQU *
LA 7,2(0)
C  7,16(5)
BC 2,0+L7-L1(4)
```

### UNTIL

The UNTIL loop has the same top-test structure but uses the complementary
condition, continuing until equality becomes true:

```asm
BC 15,0+L10-L1(4)
L9 EQU *
...
L10 EQU *
LA 7,2(0)
C  7,16(5)
BC 7,0+L9-L1(4)
```

### FOR

The FOR loop initializes J, branches to its test, executes the body, then
increments J and repeats while J<=3:

```asm
LA 7,1(0)
ST 7,20(5)
BC 15,0+L11-L1(4)
L12 EQU *
...
LA 8,1(0)
A  8,20(5)
ST 8,20(5)
L11 EQU *
LA 7,3(0)
C  7,20(5)
BC 10,0+L12-L1(4)
```

### REPEATWHILE

The post-test loop executes the body first and branches back while I<2:

```asm
L13 EQU *
...
CH 7,0+L997-L1(4)
BC 4,0+L13-L1(4)
```

### REPEATUNTIL

The corresponding post-test UNTIL form repeats while the terminating
condition is still false:

```asm
L14 EQU *
...
CH 7,0+L997-L1(4)
BC 7,0+L14-L1(4)
```

### REPEAT with BREAK

The indefinite REPEAT loops through L15.  BREAK branches directly to L17,
the code following the loop:

```asm
L15 EQU *
...
CH 7,0+L997-L1(4)
BC 7,0+L16-L1(4)
BC 15,0+L17-L1(4)
L16 EQU *
...
BC 15,0+L15-L1(4)
L17 EQU *
```

### LOOP

Inside the second FOR loop, the J=2 path branches to L21, which is the
increment/continue point.  The body increment of X at L20 is skipped:

```asm
L19 EQU *
LA 7,2(0)
C  7,20(5)
BC 7,0+L20-L1(4)
BC 15,0+L21-L1(4)
L20 EQU *
...
L21 EQU *
LA 7,1(0)
A  7,20(5)
ST 7,20(5)
```

### SWITCHON / CASE / DEFAULT / ENDCASE

CG370 emits a direct compare-and-branch dispatch for this one-case switch.
X is compared with 24; equality selects the CASE arm, otherwise control
branches to DEFAULT.  Both arms branch to the common ENDCASE exit:

```asm
L22 EQU *
L  7,12(5)
CH 7,2+L997-L1(4)
BC 8,0+L24-L1(4)
BC 15,0+L25-L1(4)

L24 EQU *
LA 7,18(0)
A  7,12(5)
ST 7,12(5)
BC 15,0+L23-L1(4)

L25 EQU *
LA 7,999(0)
ST 7,12(5)
BC 15,0+L23-L1(4)

L23 EQU *
```

The final accumulator value is therefore 42, confirming that the intended
path through every construct was taken.


### Contract established

Test 23 establishes native CG370 code generation and execution for the
classic BCPL control-flow repertoire used by this regression:

- IF;
- UNLESS;
- TEST / THEN / ELSE;
- WHILE;
- UNTIL;
- FOR;
- REPEAT;
- REPEATWHILE;
- REPEATUNTIL;
- BREAK;
- LOOP;
- SWITCHON / CASE / DEFAULT / ENDCASE.

The generated code uses ordinary System/370 compare, conditional branch, and
unconditional branch sequences; no new BCPLMAIN service is required for
these constructs.

This substantially closes basic control-flow coverage before library
integration.
