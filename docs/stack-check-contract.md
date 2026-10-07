# Historical stack-check contract checkpoint

This note records what can and cannot be recovered from the surviving
System/370 BCPL material before native regression Test 52.

## Recovered historical evidence

The surviving BCPLMAC INITSAVE layout records stack allocation state and an
`INUM` option described as the extent of stack clearance.

The user save-area layout records three byte addresses, in this order:

```text
STKBASE  stack base
STKLIM   safe limit for stack
STKHIGH  one byte beyond the area allocated to the stack
```

The distinction between STKLIM and STKHIGH is important: the historical runtime
did not equate the safe execution limit with the end of allocated storage.

BLIB's ABORT routine recognizes system code `X'0D3'` as stack overflow and
prints `STACK OVERFLOW`. It ultimately calls `STOP(100)`.

BLIB also exposes STACKBASE, STACKEND, and STACKHWM to BCPL code and knows the
historical stack fill patterns used for high-water-mark reporting.

CG370 checked procedure entry supplies the required frame size in bytes as the
inline fullword after `BAL 14,60(11)`.

## Missing evidence

The surviving repository does not contain the original machine-code BCPLMAIN
STKCK body. Therefore the exact comparison used by historical STKCK is not
directly recoverable here, including:

- whether equality at STKLIM is accepted;
- how INUM is folded into STKLIM;
- whether any extra linkage or emergency clearance is reserved;
- the exact low-level transition from STKCK failure to ABORT;
- the exact register state supplied to ABORT for code X'0D3'.

Those details must not be presented as historical fact.

## Reconstruction used for Test 52

The current WIP runtime has a static 4096-word WORK area and no reconstructed
INUM clearance policy. It therefore uses WORKEND provisionally as STKLIM and
accepts a checked frame only when:

```text
W + generated-frame-size <= STKLIM
```

This matches the recovered concepts of W, byte-sized generated frame
requirements, and a safe stack limit, but the exact boundary rule remains a WIP
reconstruction.

On overflow, Test 52 emits `STACK OVERFLOW` through the existing bootstrap
SYSPRINT buffer and returns normally to MVS. This is intentionally not claimed
to reproduce historical ABORT/STOP(100); that integration remains future work.
