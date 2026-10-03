# OCODE contract for the native compiler

## Purpose

This document defines the OCODE surface that the first native System/370 compiler should support.

The working bootstrap compiler comes from `richards-bcpltape/mr10/bcplkit/`. The surviving IBM/370 backend comes from `richards-bcpltape/bcplib/bcpl/`. Their OCODE vocabularies overlap substantially but are not identical.

The first native compiler should therefore target the **OCODE actually emitted by the working MR10 compiler**, while borrowing target-machine implementation from the later System/370 CG.

The inventory below is an implementation contract, but it is not yet proof that every listed MR10 operator is emitted by our current accepted source programs. Saved OCODE from the native acceptance corpus will turn the static inventory into observed coverage.

---

## Machine model used by OCODE

OCODE describes computation in terms of:

- a conceptual evaluation stack;
- a BCPL workspace/frame addressed by `P`;
- a numbered GLOBAL vector;
- generated labels and static data;
- function/routine application;
- procedure entry/exit;
- word and indirect memory operations.

The native CG is allowed to keep stack values in System/370 registers as the historical generator does, but it must preserve the OCODE stack semantics.

For notation below:

```text
[..., X]          top value is X
[..., X, Y]       Y is top, X is next
push(X)           add one conceptual stack value
pop()             remove one conceptual stack value
P[n]              workspace word n
G[n]              global-vector word n
MEM[a]            BCPL word at address a
L<n>              generated label n
```

Exact stack depths around procedure-control operators are governed by accompanying `STACK`, `SAVE`, `RSTACK`, and call operands; acceptance OCODE will be retained to validate those details.

---

# MR10 operator inventory

## Constants and primary loads

### `TRUE`

```text
[] -> [TRUE]
```

Push BCPL true.

Later S/370 CG: direct match.

### `FALSE`

```text
[] -> [FALSE]
```

Push BCPL false.

Later S/370 CG: direct match.

### `LN n`

```text
[] -> [n]
```

Push literal integer `n`.

Later S/370 CG: direct match.

### `LP n`

```text
[] -> [P[n]]
```

Load value from local/workspace slot `n`.

Native mapping uses displacement `4*n` from R5.

### `LG n`

```text
[] -> [G[n]]
```

Load global-vector slot `n`.

Native mapping uses displacement `4*n` from R12.

### `LL Lx`

```text
[] -> [address(Lx)]
```

Push generated code/data label address.

### `LSTR ...`

```text
[] -> [address(packed-string)]
```

Load address of generated packed BCPL string data. Operand encoding includes the string length/content.

### `LLP n`

```text
[] -> [address(P[n])]
```

Load address of workspace slot.

### `LLG n`

```text
[] -> [address(G[n])]
```

Load address of global-vector slot.

### `LLL Lx`

```text
[] -> [address(Lx)]
```

Load address represented by a generated label; semantically an lvalue/address form distinct from `LL` in the OCODE producer even where target code may converge.

---

## Dereference and stores

### `RV`

```text
[..., A] -> [..., MEM[A]]
```

Replace address on top of stack with the word stored at that address.

### `SP n`

```text
[..., X] -> [...]
P[n] := X
```

Store top value into workspace slot `n` and consume the value.

### `SG n`

```text
[..., X] -> [...]
G[n] := X
```

Store top value into global slot `n` and consume the value.

### `SL Lx`

```text
[..., X] -> [...]
MEM[address(Lx)] := X
```

Store into generated static-label location.

### `STIND`

```text
[..., VALUE, ADDRESS] -> [...]
MEM[ADDRESS] := VALUE
```

The exact top-two ordering above follows the later CG's treatment of `ARG1`/`ARG2` and must be confirmed with one saved MR10 OCODE case before implementation is frozen.

---

## Integer arithmetic

Binary operators consume two values and produce one unless otherwise stated.

### `PLUS`

```text
[..., X, Y] -> [..., X+Y]
```

### `MINUS`

```text
[..., X, Y] -> [..., X-Y]
```

### `MULT`

```text
[..., X, Y] -> [..., X*Y]
```

### `DIV`

```text
[..., X, Y] -> [..., X/Y]
```

Integer division using BCPL/System/370 signed integer semantics. Division-by-zero behavior is a runtime/processor error condition, not normalized by the CG.

### `REM`

```text
[..., X, Y] -> [..., X REM Y]
```

Remainder paired with signed integer division semantics.

### `NEG`

```text
[..., X] -> [..., -X]
```

### `QUERY`

Present in MR10 manifests/parser. Semantics must be recovered from MR10 TRN/CG evidence or observed OCODE before implementation. Do not guess.

---

## Comparisons

Each consumes two operands and produces a BCPL truth value or feeds branch-oriented optimization in the CG.

```text
EQ   X = Y
NE   X ~= Y
LS   X < Y
GR   X > Y
LE   X <= Y
GE   X >= Y
```

Conceptual effect:

```text
[..., X, Y] -> [..., boolean]
```

The later generator may fuse comparison with an immediately following conditional branch; that optimization must not change semantics.

---

## Logical and shift operations

### `NOT`

```text
[..., X] -> [..., NOT X]
```

Bitwise/logical BCPL complement according to historical word semantics.

### `LSHIFT`

```text
[..., X, N] -> [..., X << N]
```

### `RSHIFT`

```text
[..., X, N] -> [..., X >> N]
```

The later S/370 backend uses logical shift instructions for these operators. Signed/right-shift expectations should be validated against interpreted tests if negative operands matter.

### `LOGAND`

```text
[..., X, Y] -> [..., X & Y]
```

### `LOGOR`

```text
[..., X, Y] -> [..., X | Y]
```

### `EQV`

Bitwise equivalence, implemented historically via XOR plus complement.

### `NEQV`

Bitwise non-equivalence/XOR.

### `COND`

Present in MR10 vocabulary. Exact OCODE-level operand/control semantics must be recovered from the MR10 translator or observed output before implementation.

---

## Labels and control flow

### `LAB Lx`

Define label `Lx` at the current code position.

No conceptual stack change, but the CG must reconcile/spill virtual stack state at control-flow joins.

### `JUMP Lx`

Unconditional transfer to label `Lx`.

### `JT Lx`

```text
[..., X] -> [...]
if X ~= FALSE goto Lx
```

Consumes condition.

### `JF Lx`

```text
[..., X] -> [...]
if X = FALSE goto Lx
```

Consumes condition.

### `GOTO`

```text
[..., ADDRESS] -> [...]
branch ADDRESS
```

Computed transfer of control.

### `SWITCHON n ...`

Consumes switch expression and a following table of case constants/labels plus default label according to OCODE encoding.

The later S/370 CG can choose either label-vector or binary-tree implementation.

---

## Procedure/workspace control

### `STACK n`

Set/reconcile conceptual stack/workspace depth to `n` while preserving required values.

This is compiler bookkeeping with real consequences for spill locations.

### `STORE n` / `STORE`

Force live conceptual stack/register values into workspace so control flow or procedure operations see canonical storage.

The MR10 textual syntax/operand use must be taken from captured OCODE; the later generator's `STORE(0,SSP)` calls are internal CG operations, not necessarily identical to the OCODE spelling.

### `ENTRY name,label`

Begin a generated procedure entry. Carries procedure name information and label identity.

Target responsibilities include label/alignment generation and any debugging/name metadata selected by policy.

### `SAVE n`

Establish callee workspace/frame of size/depth `n`.

Under the recovered native ABI this includes:

```text
save incoming BCPL registers into the new workspace as required
R5 := R15
make register arguments visible in their expected local slots
```

### `FNAP k`

Function application.

Conceptually:

```text
function/address + arguments -> returned value
```

The operand `k` identifies the new-workspace boundary/offset used to compute:

```text
new P = old P + 4*k
```

Native call protocol is specified in `native-abi.md`.

### `RTAP k`

Routine application using the same call-frame construction as `FNAP`, but no returned expression value is pushed.

### `FNRN`

Return from function with top expression value as function result.

Native result register: R7.

### `RTRN`

Return from routine without expression result.

### `RSTACK n`

Restore/reconcile stack after a result-producing construct; later generator loads R7 as the resulting value. Exact MR10 producer context should be retained from captured OCODE.

### `RES Lx`

Return/result transfer used by `VALOF`/`RESULTIS` compilation. Stores canonical state, places result in the ABI result register, and branches to label `Lx` in the later generator.

### `RESLAB`

MR10 vocabulary item associated with result-label handling. Exact emitted form must be confirmed before implementation.

### `RETURN`

MR10 vocabulary item. Its distinction from `RTRN` must be established from MR10 source/observed OCODE before implementation.

---

## Program termination

### `FINISH`

Terminate BCPL execution through the runtime support path.

The later native CG branches to a support entry relative to R11 rather than issuing an MVS SVC directly. The reconstructed runtime contract must provide equivalent behavior.

---

## Static data and section finalization

### `DATALAB Lx`

Define static-data label.

### `ITEMN n`

Emit numeric word in static data.

### `ITEML Lx`

Emit relocatable/generated label address in static data.

### `ENDPROC`

Terminate procedure-generation context and associated optional name/debug metadata.

### `GLOBAL n ...`

Ends a generated section and supplies global-number/label definitions.

Semantically, it causes the module's generated entry addresses to be installed into corresponding slots in the BCPL GLOBAL vector when the module is initialized/loaded.

This is the essential BCPL cross-module linkage mechanism.

### `END`

End OCODE input/section stream.

---

## Miscellaneous MR10 vocabulary requiring evidence

### `CHAR`

Present in MR10 manifest. Exact emitted semantics are not yet established from accepted OCODE. Do not infer from name alone.

### `DEBUG`

Debug/metadata operation. The later CG has `DEBUG` support, but the exact MR10 input format and whether current TRNI emits it must be observed.

---

# Compatibility classes

## Class A — direct later-CG matches

These have clear later System/370 implementations and should be adapted first when observed:

```text
TRUE FALSE
RV FNAP RTAP
MULT DIV REM PLUS MINUS NEG
EQ NE LS GR LE GE
NOT LSHIFT RSHIFT LOGAND LOGOR EQV NEQV
LP LG LN LSTR LL LLP LLG LLL
SP SG SL STIND
GOTO JUMP JT JF LAB
STACK
ENTRY SAVE FNRN RTRN RES RSTACK
FINISH SWITCHON GLOBAL
DATALAB ITEML ITEMN ENDPROC END
```

## Class B — MR10-specific/unresolved until observed

```text
QUERY
COND
RETURN
RESLAB
CHAR
DEBUG
```

The rule is: **inspect producer semantics first; do not design from the mnemonic.**

## Class C — later extensions, not initial MR10 requirements

```text
NEEDS SECTION
FIX ABS
SLCTAP SLCTST
STARTBLOCK ENDBLOCK
MOD MODSLCT
GETBYTE PUTBYTE
floating-point family
FLOAT
```

These become relevant only when we intentionally move from MR10 bootstrap compatibility toward the later compiler source.

---

# Input representation decision

The MR10 generator reads textual OCODE. The later S/370 generator reads a compact encoded representation through `READOP`, `READN`, `READL`, and `READGN`.

### Decision

The first reconstructed CG370 may consume **saved textual OCODE from the current MR10 pipeline**.

This keeps the first problem narrowly defined:

```text
OCODE semantics -> System/370 assembler
```

rather than combining it with:

```text
new compact OCODE decoder
```

When self-hosting later compiler components requires the compact representation, add that input layer without changing the target semantics.

---

# Output representation decision

The reconstructed CG370 initially emits **IFOX assembler source**.

That is a reconstruction/debugging decision. The later historical CG's direct object-deck generation remains primary evidence for relocation and eventual compatibility, but it is deferred until the generated instruction stream and ABI are established.

---

# Coverage table to maintain

As acceptance OCODE is captured, append/update a table of this form:

| OCODE | Observed? | First acceptance case | Later S/370 implementation | Native status |
| --- | --- | --- | --- | --- |
| `LN` | pending capture | A1 | `SCAN`, `LOAD(NUMBER,...)` | planned |
| `PLUS` | pending capture | A1 | `CGPLUS` | planned |
| `LP` | pending capture | A2 | `SCAN`, `LOAD(LOC,...)` | planned |
| `FNAP` | pending capture | A3 | `CGAPPLY` | planned |
| `GLOBAL` | pending capture | A5 or earlier | `CGGLOBAL` | planned |

Do not mark an operator “required by MR10” merely because it is present in `CGHDR`; mark it required when captured output demonstrates that current TRNI emits it for supported source.

---

# Unsupported-operation rule

During native-CG development, an unimplemented OCODE operation must fail explicitly and diagnostically.

Report at least:

```text
operator name/number
OCODE input position or record if available
current section/procedure if known
```

Silent approximation is prohibited.

This makes incomplete coverage visible and keeps the native compiler trustworthy while it grows.
