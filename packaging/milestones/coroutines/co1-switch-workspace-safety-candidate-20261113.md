# CO.1 — Switch workspace safety correction candidate

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.1 — Native ABI and Stack Architecture (**IN PROGRESS**)  
**Date:** 13 November 2026  
**Status:** Assistant-tested isolated SOURCE CANDIDATE; **target MVS result PENDING**  
**Scope:** No installed MVS object, public ABI, global allocation, or CO.2 promotion

## Investigated defect in the first native PASS

Owner-reported Cambridge compiler JOB **5356** and native JOB **5357**
established a valid positive-path execution (`A1 R1 A2 R2 PASS`,
three IFOX RC=0, IEWL RC=0, GO RC=0) under
`edb8b765b204903b0cbb9688e066319bbb15bb20`.
That acceptance evidence is preserved in the separate
[JOB 5356/5357 report](co1-bcpl-native-candidate-jes-5356-5357-pass-20261113.md).

The owner also supplied the **actual CG370-generated assembly**.
Its checked `/CN` procedure frames and call-site workspaces show:

| Native procedure | Checked frame | CO1SW W offset | Bytes remaining |
| --- | ---: | ---: | ---: |
| WORKER, `L994 EQU 52` | 52 | 24 | 28 |
| START, `L993 EQU 256` | 256 | 224 | 32 |

The passing version of `CO1SW` began with
`STM 0,15,0(15)`, storing 16 registers (64 bytes) at W, then copying
them to the context descriptor. A 64-byte store requires **36 more
bytes than WORKER's frame** and **32 more bytes than START's frame**.
The passing GO test did not detect this overrun. It demonstrates
behavior, not caller-workspace safety.

## Minimal native System/370 correction

To avoid writing beyond the compiler's frame without changing its
call ABI, the candidate `co1change.asm` now:

1. Uses `USING CO1SW,4` before the first executable instruction.
   At a BCPL procedure call, R4 contains the callee entry address,
   as observed in generated calls (`L 4,1196(12)`, then `BALR 6,4`)
   and in the worker-exit trampoline.
2. Saves the complete incoming register image using
   `CO1SW STM 0,15,CO1SREG`, where `CO1SREG DS 16F` is a 64-byte
   **module-private** buffer, not the caller's W.
3. Copies that buffer to the outgoing descriptor's saved R0–R15
   image and synthesizes the three-word RETIMPL frame **only** at
   W+0, W+4 and W+8. It uses R5=W for the suspended context's
   restored R5 and the original R4/R5/R6 from buffer offsets
   16/20/24, preserving existing continuation logic.
4. Reads incoming R7/R8 from the original snapshot offsets 28/32;
   retains the switch's S1 active STKLIM/APLIMIT and G54/G55 updates.
   All incoming saved registers are restored before branch to R6.

The private scratch is sufficient for the current **single-task,
cooperative** candidate; it is not specified as an MVS subtask-safe
or reentrant implementation. It cannot be promoted to the production
coroutine ABI without the remaining CO.1 register, descriptor,
lifecycle and error-handling design gates.

## Reproducibility and checks

The assistant modified and checked the exact `co1change.asm` source
in an independent workspace and matched its Git blob SHA:
`8d2cff1b89619733ea2ac82aedacaf18c74dda45`.

**14/14 focused host tests PASS:** seven previously accepted CO1INIT/R0
guards and seven new switch-workspace guards (original R4 entry base,
complete incoming 16-register snapshot, private 64-byte area, only
three W stores, correct R7/R8 offsets, no W-based 64-byte STM/MVC,
card width and symbol constraints). Both Python tests pass syntax
checks. The existing CO.1 synthetic test expectations are updated
to require the safe buffer. This is **not** native IFOX/IEWL/GO evidence.

The new candidate is assembled from repository source through the
existing `tools/coroutines/run-co1-bcpl-switch.py --run` MVS-facing
runner. It does not modify accepted BOOT_OBJ members; only temporary
MVS assembler/linker/load datasets are used. The success oracle is
unchanged: five RC=0000 steps, followed by the exact ordered
`CO1BCPL A1`, `R1`, `A2`, `R2`, `PASS` records.
A failure must be diagnosed from the newly saved real JES evidence
before further redesign.

CO.0 remains CLOSED (qualified). CO.1 **IN PROGRESS**; CO.2–CO.5
**NOT STARTED**. No closure, public API approval, regression-ID
assignment, clean-room release claim, or installed-object promotion.
