# Observed OCODE surface

This document records the OCODE actually emitted by the working MR10 compiler for the native acceptance corpus. It complements `ocode-contract.md`, which describes the broader static operator inventory.

The rule here is empirical: an operator appears only when it has been observed in saved OCODE from a committed acceptance source.

## Captured cases

| Case | Saved OCODE | Purpose |
| --- | --- | --- |
| A0 | `acceptance/a0-finish.ocode` | startup and FINISH only |
| A1 | `acceptance/a1-arithmetic.ocode` | literals and integer arithmetic |
| A2 | `acceptance/a2-loop.ocode` | locals, comparison, branches, loop |
| A3 | `acceptance/a3-function-call.ocode` | function call and returned value |
| A4 | `acceptance/a4-arguments.ocode` | five arguments |
| A5 | `acceptance/a5-global.ocode` | GLOBAL load/store |

## Cumulative operator surface

### A0 — startup and FINISH

Observed:

```text
STACK
JUMP
ENTRY
SAVE
FINISH
RTRN
ENDPROC
LAB
STORE
GLOBAL
```

The exact OCODE is:

```text
STACK 2 JUMP L2 ENTRY 5 L1 83 84 65 82 84 SAVE 2 FINISH RTRN ENDPROC
0 STACK 2 LAB L2 STORE GLOBAL 1 1 L1
```

This establishes the true minimum native bootstrap surface. No expression evaluation, local/global data access, or arithmetic is required to prove initial generated-code startup and termination.

### A1 — arithmetic

Adds:

```text
LN
PLUS
MULT
MINUS
SG
```

The arithmetic case therefore becomes the second implementation rung rather than the first.

### A2 — locals and loop

Adds:

```text
LP
SP
LE
JT
```

No `JF` is required by this particular source; TRNI chose a loop shape using `JT` and an unconditional `JUMP`.

### A3 — first function call

Adds:

```text
DATALAB
ITEML
FNRN
LL
FNAP
```

This is the first acceptance case that requires the native BCPL call/return ABI rather than only START/FINISH execution.

### A4 — five arguments

Adds no new OCODE mnemonics beyond A3.

Its importance is semantic rather than lexical: the callee executes `SAVE 7` and accesses arguments as `LP 2` through `LP 6`, while the caller pushes five literal arguments before `LL ... FNAP 2`. This makes A4 the test that must demonstrate the historical argument-register/workspace convention correctly handles an argument beyond the first four register arguments.

### A5 — GLOBAL state

Adds:

```text
LG
```

`SG` was already present in A1 because the result mailbox itself is a GLOBAL store.

## Bootstrap subset through A5

The complete observed mnemonic set through A5 is:

```text
DATALAB
ENDPROC
ENTRY
FINISH
FNAP
FNRN
GLOBAL
ITEML
JUMP
LAB
LE
LG
LL
LN
LP
MINUS
MULT
PLUS
RTRN
SAVE
SG
SP
STACK
STORE
JT
```

This is the authoritative initial implementation surface for reconstructed CG370.

Operators that exist in MR10 but do not appear above are not required for A0-A5 and should not delay the first native generated program.

## Per-operator coverage

| OCODE | First observed | Initial native requirement |
| --- | --- | --- |
| `STACK` | A0 | yes |
| `JUMP` | A0 | yes |
| `ENTRY` | A0 | yes |
| `SAVE` | A0 | yes |
| `FINISH` | A0 | yes |
| `RTRN` | A0 | yes |
| `ENDPROC` | A0 | yes |
| `LAB` | A0 | yes |
| `STORE` | A0 | yes |
| `GLOBAL` | A0 | yes |
| `LN` | A1 | after A0 |
| `PLUS` | A1 | after A0 |
| `MULT` | A1 | after A0 |
| `MINUS` | A1 | after A0 |
| `SG` | A1 | after A0 |
| `LP` | A2 | after A1 |
| `SP` | A2 | after A1 |
| `LE` | A2 | after A1 |
| `JT` | A2 | after A1 |
| `DATALAB` | A3 | after A2 |
| `ITEML` | A3 | after A2 |
| `FNRN` | A3 | after A2 |
| `LL` | A3 | after A2 |
| `FNAP` | A3 | after A2 |
| `LG` | A5 | after calls/arguments |

## Important structural observations

### START is represented through GLOBAL initialization

A0 and A1 both end with:

```text
GLOBAL 1 1 L1
```

so native startup must arrange for global slot 1 to resolve to generated START entry `L1` before execution.

### Procedure names are encoded as character numbers in ENTRY

For example START appears as:

```text
ENTRY 5 L1 83 84 65 82 84
```

The five decimal character values spell `START` in ASCII values. These operands are metadata for the generator; they are not five runtime arguments.

Likewise A3 encodes `ADD3` as:

```text
ENTRY 4 L1 65 68 68 51
```

### A3 uses a static cell for the local function address

Before generated procedure bodies A3 emits:

```text
DATALAB L2
ITEML L1
```

and START later executes:

```text
LL L2
FNAP 2
```

CG370 must preserve the distinction between the static data label `L2` and the procedure label `L1`: `L2` denotes storage containing the relocatable address of `L1`.

### A4 confirms five-argument frame semantics must be tested, not inferred from mnemonic count

The OCODE vocabulary is unchanged from A3, but the generated SAVE/local layout changes. Therefore acceptance status must be tracked by semantic cases as well as operator coverage.

## Next implementation target

Implement only the A0 subset first.

The first reconstructed generator should accept the exact committed `a0-finish.ocode`, emit inspectable IFOX assembler, and fail explicitly on every OCODE mnemonic outside the A0 set.

Once A0 assembles, links, and executes correctly, add the A1 arithmetic/global-store operators, then A2 locals/branches, then A3 call/data operators.
