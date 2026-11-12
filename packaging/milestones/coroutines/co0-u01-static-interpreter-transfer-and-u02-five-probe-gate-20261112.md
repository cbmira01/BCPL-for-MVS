# CO.0 — U01 interpreter transfer source trace and U02 execution gate

**Project:** BCPL for MVS 3.8 Reconstruction  
**March:** CO.0 — Historical Research and Behavioral Contract (IN PROGRESS)  
**Checkpoint:** GitHub main at `723c3887b3b732dfa457c169c82e9849b9400b24`  
**Evidence level:** SOURCE-OBSERVED; MVS probe rerun pending

## U01 — What the original interpreter actually does

The historical `richards-bcpltape/mr10/bcplkit/icint`
interpreter's `INTERPRET` routine defines `CASE 32`:

    CASE 32: P, C := A, B;  // USED IN LONGJUMP(P,L)
             GOTO FETCH

The reconstructed `mr10-kit-compiler/asm/icintv19.asm` uses:

    X32      L     R2,A
             ST    R2,P
             L     R2,B
             ST    R2,C
             B     FETCH

This is the same **interpreted** P/C transfer operation, with A
holding the destination P and B the destination C. `X32` does not
allocate a stack, save native CPU registers, or enforce a coroutine
descriptor layout.

Canonical `mr10-kit-compiler/source/iclib.int`, global entry 6,
begins:

    6 LIP2 SG9 LP0 SIG7 LIP3 SG7 LIG7 X1 A1 X1 SG10
      LL498 LIG7 X1 X1 X32
    498 LIG9 JIG10 G6L6

The tokens visibly include saving the value argument to G!9,
reading/updating the current-coroutine global G!7, recording
the outgoing interpreter continuation using G!10, and restoring
the outgoing value at label 498. This description is a source-level
interpretation, **not** a completed token-by-token proof of the
intermediate stack, P/C, G!7/G!9/G!10 and descriptor values.
The compiler's generated `compiler-probe` and `frame-layout-probe`
OCODE/INTCODE must be inspected alongside this path before marking
U01 fully resolved.

The reconstructed coroutine descriptor and first-frame conventions
are summarized in `mr10-kit-compiler/tests/10-coroutines/README.md`:
`C!0` holds saved interpreter frame P, `C!1` is parent, `C!2`
is list link; the synthetic first frame is `P=C+3`, with
`P!0=P`, `P!1=COBOOT`, and `P!2..` holding FN, SIZE, C.
These are reconstructed MR10 conventions, **not native ABI facts**.

## U02 — Five accepted development probes

The test identities remain exactly:

1. `10-coroutines/compiler-probe`
2. `10-coroutines/frame-layout-probe`
3. `10-coroutines/fixed-stack-producer-consumer`
4. `10-coroutines/resumeco-chain`
5. `10-coroutines/create-delete-static-pool`

Use `tools/mr10/run-dev-probes --run` and explicitly select each
identity. The runner checks exact existing program-output oracles;
for the first two probes it also compares generated compiler artifacts
against archived evidence. Run under the promoted canonical
source with no candidate override. Preserve its per-case evidence,
JES summaries, generated OCODE/INTCODE and terminal status.

The fixed-stack case predates the promoted coroutine implementation
and may expose a historical startup-frame incompatibility. A failure
is evidence to analyze, **not** permission to rewrite a golden.

No execution, acceptance, or native System/370 test is claimed by
this research plan. CO.0 remains IN PROGRESS.
