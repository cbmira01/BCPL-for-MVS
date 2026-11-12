# CO.0 — U01 interpreter transfer source trace and U02 execution gate

**Project:** BCPL for MVS 3.8 Reconstruction  
**March:** CO.0 — Historical Research and Behavioral Contract (IN PROGRESS)  
**Checkpoint:** GitHub main at `723c3887b3b732dfa457c169c82e9849b9400b24`  
**Evidence level:** SOURCE-OBSERVED and partial INTERPRETED-MVS-TESTED; one legacy startup incompatibility unresolved

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

## U02 — post-promotion observations, 12 November 2026

**Source revision:** `2d3183879eebf74b1acde424335a464cd265b639`.
The operator ran the same five selected cases twice; each
stopped at the first failing case (fail-fast inside the runner, not
the operator shell). The second run preserved:
`workarea/mr10-probes/20261112T004450Z-5973-nxtpfv9g/`.

- JOB 5316, `compiler-probe`: PASS, all 12 JES steps RC=0000,
  program output and archived OCODE/INTCODE comparisons accepted.
- JOB 5317, `frame-layout-probe`: PASS, all 12 JES steps RC=0000,
  program output and archived OCODE/INTCODE comparisons accepted.
- JOB 5318, `fixed-stack-producer-consumer`: FAIL, final interpreted
  `CODE=-1`, `INTCODE ERROR AT C = 803`, 101 interpreter cycles,
  no producer/consumer records. The independent JES summary reports
  10/10 steps RC=0000 and `JOB RESULT: SUCCESS`. JES RC=0 is not
  a semantic PASS.
- The last two cases were run separately in evidence directory
  `workarea/mr10-probes/20261112T004825Z-6434-cua68fi_/`:
  `resumeco-chain` PASS (14/14 JES steps, accepted golden) and
  `create-delete-static-pool` PASS (14/14 JES steps, accepted golden),
  runner RC=0.

**Overall, four of five original development probes pass under the
promoted source; the legacy fixed-stack source does not.**
The original accepted golden and source remain unchanged. This is
a compatibility qualification, not an unreviewed golden revision.

### Trace-to-source diagnosis

JOB 5318's 64-entry ICINT19 trace shows:
- cycle 98: `X32` transfers P=175844, C=175789;
- cycle 99: `LIG9` restores transfer value 0;
- cycle 100: `JIG10` branches to interpreted C=175839;
- cycle 101: an invalid word is fetched at C-offset 801, producing
  `INTCODE ERROR AT C = 803` and final `CODE=-1`.

The legacy `MAKECO` sets `C!0 := C` and uses C's descriptor words
as the first frame. The promoted bridge expects C!0 to be a saved
CHANGECO call frame containing a valid P!0 and P!1 continuation.
The observed control transfer into invalid code and this source
mismatch together support the startup-frame incompatibility diagnosis.
No blanket claim is made that every arbitrary frame failure is safe.

### Existing isolated compatibility candidate: next MVS gate

Do not duplicate or overwrite the accepted legacy test:
`mr10-kit-compiler/tests/10-coroutines/fixed-stack-co0-candidate.bcpl`
already introduces a separate COBOOT trampoline with `P=C+3`,
`C!0=P`, `P!0=P`, `P!1=COBOOT`, and P!2..P!4 arguments.
It preserves the five producer/consumer exchanges and is
**candidate-only**; its prior JOB 5240 execution used ICLIBC.
A host-side source comparison establishes that canonical `iclib.int`
and candidate `iclib-co0-candidate.int` have identical executable
records (the candidate adds provenance comments only). This is not
a substitute for the next MVS execution.

Run the existing `tools/mr10/compile-and-run --results` with
canonical ICINT19/ICLIB and this distinct candidate BCPL source,
then compare all ten ordered records against the unchanged
`fixed-stack-producer-consumer.expected`, interpreted CODE=0,
runner RC=0, and all JES steps RC=0000. Keep its evidence outside
the five accepted original identities. If it passes, U02 can be
recorded as four unchanged pass plus one qualified legacy failure
with separately verified replacement; it must not be recorded as
five passing original cases.

No permanent MVS dataset updates, manifest changes, or native ABI
decisions are authorized by this plan. CO.0 remains IN PROGRESS.
