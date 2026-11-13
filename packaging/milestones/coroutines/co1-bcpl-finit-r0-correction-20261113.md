# CO.1 — Native CO1INIT R0 discrepancy and candidate correction

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.1 — Native ABI and Stack Architecture (IN PROGRESS)  
**Date:** 13 November 2026  
**Evidence:** Owner-reported real MVS GO result and actual Cambridge
S/370 source listing; assistant-tested source correction, not yet
verified by new native MVS execution

## Observed result

The diagnostic candidate at GitHub main
`65791e7ef84af6225104a02a8ac5173a7f5713c9` emitted exactly
`CO1BCPL FINIT` in the owner-run native GO. Its evidence directory is
`workarea/co1-bcpl-switch/20261113T195531Z-63mtn5ew/`.
The runner reached its output comparison, which requires all
ASMA/ASMM/ASMS/LKED/GO steps reported RC=0000. Actual JES job numbers
and the full printer report have not been supplied; these are not
invented here.

The owner subsequently supplied the *real* recovered generated System/370
assembly. At the `CO1INIT` invocation in generated `START`, it shows:

```asm
 L  10,0+L2-L8(4)
 L  9,20(5)
 L  8,16(5)
 LA 15,224(5)
 L  4,1192(12)
 BALR 6,4
 CR 7,0
 BC 8,0+L11-L8(4)
```

Thus `START` compares the initializer's R7 return value **against
the machine value in R0**, not an immediate zero. Its following
`FINIT` branch executes when the comparison is unequal. This is
direct evidence from Cambridge CG370, not a hypothetical ABI.

## Source-level cause

The prior `CO1INIT` source ends:

```asm
         LA    0,64(9)
         ST    0,60(4)
         SR    7,7
         BCR   15,11
```

R7 is explicitly cleared, but R0 still holds the nonzero worker
workspace address from `LA 0,64(9)`. `BCPLMAIN RETIMPL` restores
R6/R5/R4 without restoring R0. On returning to `START`,
`CR 7,0` compares zero against that nonzero address, so `FINIT`
follows. The existing `BCPLMEM GETVEC` code saves/restores R0..R3;
`BCPLMAIN` explicitly clears R0 before entering generated START.
Maintaining R0 across BCPL callable native services is required by
the compiler-generated code examined.

A second source defect would appear at first worker activation:
`CO1INIT` snapshots registers into the never-run worker descriptor
after R0 has been repurposed as a trampoline address. Without repair,
the worker would begin with that nonzero R0 and could misinterpret
generated zero comparisons and initialization.

## Narrow candidate-only correction

Only `co1change.asm` changes:

1. Immediately after `CO1INIT STM 4,10,0(15)`, use `LR 6,0`
   to preserve caller R0 in R6. The ordinary BCPL entry has already
   saved original R6 at `8(R15)` in the new frame. No nested call or
   coroutine switch occurs during initialization.
2. Immediately after the first `STM 0,15,0(4)` worker image,
   `ST 6,0(4)` initializes the worker's saved R0 to caller R0.
3. Immediately before `SR 7,7` and `BCR 15,11`,
   `LR 0,6` restores the caller R0.

No other native register contract, stack extent, descriptor layout,
global number or MVS runtime module changes.

## Assistant-side checks and next MVS gate

The precise revised assembler file was written and checked in the
assistant's independent workspace. Seven focused Python tests passed:
IFOX card widths and symbol lengths; entry R0 capture; original R6
continuation location; no second write to temporary R6; ordering of
worker-image R0 fixup; return R0 restoration followed by R7 zero;
and full register snapshot/resume code remaining present.

The exact locally checked Git blob identities are:

- `co1change.asm`: `b30c6daa25e00c904b41935f299b6d5fc98fac06`
- `tools/checks/test_co1_init_r0.py`:
  `589c979423a1fa4c04fc753293f61d8308c82cef`

Python `py_compile` passed for the added test. These are **host-only**
source checks; real IFOX assembly, IEWL linkage, and native GO of
the corrected source remain pending. Rerun the same candidate-only
`tools/coroutines/run-co1-bcpl-switch.py --run` from the new main
commit and evaluate actual MVS records. The expected full trace stays
`CO1BCPL A1 / R1 / A2 / R2 / PASS`.

No installed `BOOT_OBJ` writes, MR10-kit development, numbered
regression, CO.1 closure or CO.2 opening are implied.
