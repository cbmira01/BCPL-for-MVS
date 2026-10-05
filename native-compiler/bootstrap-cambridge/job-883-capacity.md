# Cambridge SYN bootstrap capacity checkpoint — JOB 883

JOB 883 tested the demoted Cambridge `SYN` compilation unit under `icintv17`
with the MR10 compiler tree workspace set to `L8000`.

Observed result:

```text
INTCODE SYSTEM ENTERED, PROGRAM SIZE = 9972
BCPL 168037
OPTIONS  L8000

SYNTAX ERROR NEAR LINE 447:  PROGRAM TOO LARGE

COMPILATION ABORTED
EXECUTION CYCLES = 2233613, CODE = 8
```

The important distinction is that `L8000` no longer abends ICINT.  The MR10
compiler runs normally and advances Cambridge `SYN` to source line 447 before
its AE-tree workspace fills.  Thus 8,000 words fit inside the current ICINT
memory geometry but are insufficient to compile this unit.

Together with the previous probes:

- default `L5500`: Cambridge `SYN` reaches line 166, then `PROGRAM TOO LARGE`;
- `L12000`: ICINT v17 abends S0C4 because the requested APTOVEC workspace plus
  the 9,972-word loaded compiler image exceeds the 20,001-word PROGVEC;
- `L8000`: no host abend, but Cambridge `SYN` still exhausts the compiler tree
  at line 447.

This is sufficient empirical evidence to stop shrinking the compiler workspace
and enlarge ICINT's PROGVEC deliberately.

The next candidate is ICINT V18 with:

```asm
PROGCNT  EQU   40001
```

This raises PROGVEC from 20,001 to 40,001 BCPL words (80,004 to 160,004 host
bytes with the current four-byte BCPL word representation).  V18 is intended to
be a capacity-only revision of V17.

After generating and promoting V18, restore the Cambridge compiler workspace to
`L12000` and rerun the same `demoted/syn` probe.  The objective remains to reach
nonempty OCODE, not to treat the isolated SYN unit as a complete runnable
program.
