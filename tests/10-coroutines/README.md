# Coroutine reconstruction tests

This directory contains the first reconstruction experiments for BCPL
coroutines under the preserved MR10 compiler and the reconstructed INTCODE
runtime.

The tests are organized around reproducible compiler/runtime observations,
not JES job numbers.  The commands below are the evidence-producing units.

## 1. CHANGECO call-shape probe

Source:

```text
compiler-probe.bcpl
```

Run:

```bash
tools/compile-and-run --results --save-ocode --save-intcode \
    asm/icintv17.asm \
    tests/10-coroutines/compiler-probe.bcpl
```

This leaves:

```text
workarea/compiler-probe.ocode
workarea/compiler-probe.intcode
```

Preserved copies are under `evidence/`.

The generated INTCODE includes:

```text
$ 1 LIP2 SP6 LIP3 SP7 LIG6 K4 X4
```

This establishes the MR10 two-argument call shape used by
`CHANGECO(VALUE, CPTR)`.  The call frame uses `K4`; its arguments are in
`P!2` and `P!3`.  A hand-written CHANGECO entry using

```text
LIP3 LIP2
```

therefore reaches its machine-dependent operation with:

```text
A = VALUE
B = CPTR
```

The test program itself deliberately does not execute CHANGECO.  Its expected
runtime output is:

```text
COROUTINE COMPILER PROBE COMPILED
```

## 2. Synthetic-frame layout probe

Source:

```text
frame-layout-probe.bcpl
```

Run:

```bash
tools/compile-and-run --results --save-ocode --save-intcode \
    asm/icintv17.asm \
    tests/10-coroutines/frame-layout-probe.bcpl
```

This leaves:

```text
workarea/frame-layout-probe.ocode
workarea/frame-layout-probe.intcode
```

Preserved copies are under `evidence/`.

The generated INTCODE begins the CREATEFRAME routine with:

```text
$ 1 LIP4 SP5 ... LIP2 ... LIP3 ...
```

and the CHANGECO call is emitted using `K5`.

From the generated code, the MR10 routine frame used by
`CREATEFRAME(FN, SIZE, C)` is:

```text
P!2 = FN
P!3 = SIZE
P!4 = C
```

This is different from the later Cintcode layout often documented for
`createco`.  The MR10 synthetic coroutine frame must therefore follow the
layout observed here rather than copy later offsets.

The expected runtime output is:

```text
COROUTINE FRAME PROBE COMPILED
```

## 3. Fixed-stack producer/consumer

Source:

```text
fixed-stack-producer-consumer.bcpl
```

Run:

```bash
tools/compile-and-run --results --listing heavy \
    asm/icintv17.asm \
    tests/10-coroutines/fixed-stack-producer-consumer.bcpl
```

Expected program output:

```text
PRODUCER: 1
CONSUMER: 1
PRODUCER: 2
CONSUMER: 2
PRODUCER: 3
CONSUMER: 3
PRODUCER: 4
CONSUMER: 4
PRODUCER: 5
CONSUMER: 5
```

followed by an interpreted completion code of zero.

This test uses statically reserved storage rather than `GETVEC/FREEVEC`, so it
isolates coroutine switching from allocator reconstruction.

The successful run establishes that, under the MR10 compiler and current
runtime:

- separate suspended BCPL stacks can be resumed correctly;
- `CALLCO` / `COWAIT` transfer control correctly;
- values cross the coroutine boundary correctly;
- the producer's local `FOR` state survives repeated suspension;
- the synthetic MR10 coroutine frame is valid; and
- genuine producer/consumer coroutine behavior is possible before full
  `CREATECO` / `DELETECO` reconstruction.

## Runtime implementation status

The current reference implementation of `CHANGECO` lives in hand-written
INTCODE in `intcode/iclib.int`.  It is deliberately a proof of the coroutine
runtime contract and uses already-proven INTCODE mechanisms rather than yet
requiring a new ICINT opcode.

The long-term architecture should preserve the same BCPL-level contract while
allowing the machine-dependent primitive to change by backend:

```text
portable BCPL layer:
    CREATECO
    DELETECO
    CALLCO
    COWAIT
    RESUMECO

machine-dependent layer:
    CHANGECO
```

For the interpreted bootstrap, CHANGECO may be implemented by INTCODE and/or a
dedicated ICINT operation.  For the eventual native System/370 compiler and
runtime, CHANGECO should become a small native routine that saves the current
BCPL resumable frame, installs the target coroutine frame, preserves the
transfer value, and continues at the corresponding return continuation.

The portable coroutine semantics should not depend on whether the backend is
ICINT or native System/370 code.

## Evidence files

The `evidence/` directory contains copies of the generated OCODE and INTCODE
from the two compiler-observation probes:

```text
evidence/compiler-probe.ocode
evidence/compiler-probe.intcode
evidence/frame-layout-probe.ocode
evidence/frame-layout-probe.intcode
```

They are retained because they are primary reconstruction evidence for the
MR10 calling and frame conventions used by the coroutine implementation.
