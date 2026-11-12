# CO.0 — U01 interpreter transfer source trace and U02 execution gate

**Project:** BCPL for MVS 3.8 Reconstruction  
**March:** CO.0 — Historical Research and Behavioral Contract (IN PROGRESS)  
**Checkpoint:** GitHub main at `723c3887b3b732dfa457c169c82e9849b9400b24`  
**Evidence level:** SOURCE-OBSERVED and INTERPRETED-MVS-TESTED for bounded MR10 behavior; U02 resolved with qualification

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

## 12 November 2026 — U02 disposition after JOB 5321

**Disposition: RESOLVED WITH QUALIFICATION (INTERPRETED-MVS-TESTED).**
At GitHub `main` HEAD `ee6849ec367574e733a391734aff249060878f21`,
the existing isolated `fixed-stack-co0-candidate.bcpl` was run
through the default canonical `iclib.int` and ICINT19 without a
library override.

- **JOB 5321 (BCFIXEDS)** completed with ten expected alternating
  producer/consumer records, from `PRODUCER: 1` through
  `CONSUMER: 5`, in exact accepted-golden order.
- Final interpreted `EXECUTION CYCLES = 5442, CODE = 0`.
- `tools/mr10/compile-and-run --results` returned RC=0.
- Independent operator `tools/mvs/job-summary 5321` returned RC=0,
  `JOB RESULT: SUCCESS`, highest RC=0000; all **10/10 JES
  steps** (ASM, LKED, STGSYNI, STGTRNI, STGCGI, STGBLIB,
  STGICLIB, COMP, CG, RUN) returned RC=0000.
- Operator evidence:
  `workarea/co0-fixed-stack-compatibility/20261112T005134Z.log`;
  JES JOB 5321 summary was supplied separately.

This acceptance does **not** convert the unmodified legacy test
(JOB 5318, interpreted CODE=-1) into PASS. Four of five original
accepted cases passed under the promoted implementation. The distinct
COBOOT-style fixed-stack candidate passed independently and preserved
the old golden. Original test identities, source, golden and manifest
are unchanged; the five-case runner still fails if all five originals
are selected. The compatibility qualification must be carried into
subsequent suite acceptance and must be explicitly resolved before
claiming an unqualified full-project regression PASS. No native
System/370 coroutine execution is implied.

## U01 — explicit bridge token trace and archived compiler call artifacts

**Classification: SOURCE-OBSERVED and host-only symbolic check;
not a new MVS trace.** Original MR10 `ICINT` defines load (F0)
as `B:=A; A:=D`, store (F1) as `!D:=A`, add (F2) as
`A:=A+D`, jump (F3) as `C:=D`, `X1` as
`A:=!A`, and `X32` as `P,C:=A,B`.
ICINT19 implements the same relevant `X32` transfer.

Let incoming `CHANGECO(value,target)` enter at interpreter frame
`P=p` with `p!2=value`, `p!3=target`,
`G!7=outgoing`, `outgoing!0` writable, and
`target!0=q` referring to a valid saved frame with
`q!0=resumeP`, `q!1=resumeC`.
The canonical bridge at global 6 executes:

| INTCODE token | Relevant effect |
| --- | --- |
| `LIP2 SG9` | Save `value` into scratch `G!9`. |
| `LP0 SIG7` | Save outgoing **CHANGECO call-frame** `p` into `outgoing!0`. |
| `LIP3 SG7` | Select `target` as new `G!7` (current descriptor). |
| `LIG7 X1 A1 X1 SG10` | Read `q=target!0`, then `q!1`; save `resumeC` in scratch `G!10`. |
| `LL498 LIG7 X1 X1 X32` | Load incoming `resumeP=q!0` into interpreter A while B still holds the **common bridge label 498**, then `X32` assigns `P=resumeP`, `C=498`. |
| `498 LIG9 JIG10` | Reload transfer `value` into A, then branch to saved `resumeC=G!10`. |

**Important ordering distinction:** `X32` does **not** branch
directly to `resumeC`. It installs the incoming P and branches
to common label 498. The subsequent `JIG10` jumps to the saved
per-coroutine continuation. G!10 is scratch for this bounded,
non-preemptive sequence, not the descriptor's persistent
continuation slot.

The archived compiler-only `compiler-probe.ocode` has
`LP 2 LP 3 LG 6 FNAP 4` and its INTCODE has
`LIP2 SP6 LIP3 SP7 LIG6 K4 X4`, showing two explicit
arguments supplied in source order, `VALUE` then `CPTR`.
The second compiler call is also present in its INTCODE.
The separate archived `frame-layout-probe` contains
`LG 6 RTAP 5` and `LIG6 K5` for its three-argument
probe; that frame lays out `FN`, `SIZE`, `C`
at P!2, P!3 and P!4 of the synthetic first-activation
frame documented by the probe. The candidate library's
`COBOOT` is the explicit entry continuation.

**Host-side verification:** A constrained symbolic executor
checked all 18 bridge tokens against a two-descriptor,
two-frame example and asserted outgoing saved frame,
incoming current descriptor, value scratch, continuation
scratch, label-498 landing, and final resumed continuation
and value. The model is source-level evidence only;
it is not an ICINT19/JES execution. The existing MVS
evidence for distinct continuation and parent/value
semantics remains JOBS 5238, 5299–5300, 5312 and 5321.

**Remaining U01 gate:** independently inspect full saved
compiler-generated OCODE/INTCODE with their exact labels,
and correlate first-activation entry, outgoing return frame
and per-context nested locals with a bounded MVS execution
trace before declaring U01 completely resolved. The
trace above is sufficient to identify the correct
bridge transfer ordering, not a native coroutine ABI.
