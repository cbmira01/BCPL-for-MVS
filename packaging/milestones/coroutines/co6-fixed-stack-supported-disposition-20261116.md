# CO.6 — Supported MR10 fixed-stack regression and preserved historical diagnostic

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.6 — Common Coroutine Behavioral Contract and Cross-Compiler Verification  
**Decision:** Owner-directed supported/diagnostic separation, 16 November 2026  
**Status:** IMPLEMENTED AND VERIFIED ON MVS; CO.6 owner acceptance pending

## Problem and disposition

The original accepted MR10 fixture
`10-coroutines/fixed-stack-producer-consumer.bcpl`
hand-constructs an invalid saved first-activation frame (`C!0 := C`)
under canonical ICINT19/ICLIB. The standalone interpreted job
has repeatedly produced **CODE=-1** rather than the source-controlled
ten-record golden and the original expected CODE=0. This is a **real
FAIL**, not XFAIL/PASS/SKIP, and the historical source and evidence
cannot be silently rewritten. Earlier CO.0 work demonstrated a
separate valid-frame source with `P=C+3` and
`P!1 := COBOOT`, including a JOB 5321 full ten-record PASS.
A later separate candidate JOB 7693 returned compiler-driver RC0,
but the compact excerpt did not independently establish all
program records.

**Accepted design decision:** keep the exact historical
17-entry `dev-probes-manifest.tsv`, the original
`fixed-stack-producer-consumer.bcpl`, its `.expected` output,
and all true FAIL evidence. Create instead a separate supported
MR10 five-case selection incorporating the existing
`fixed-stack-co0-candidate.bcpl` as a **new and distinct supported
case identity**, with its own identical ten-record output oracle.

## Executable boundaries

| Suite | IDs / scope | Expected classification |
| --- | --- | --- |
| `mr10-coroutines-supported` | compiler-probe, frame-layout-probe, resumeco-chain, create-delete-static-pool, **fixed-stack-co0-candidate** | Five PASS if actual MVS verification succeeds; no historical negative |
| `mr10-coroutines` | The same four original identities plus **fixed-stack-producer-consumer** | Four PASS and **one genuine original FAIL** |
| `mr10-probes` | Eleven original historical accepted identities, including original fixed-stack | Unchanged; never claim whole suite PASS without actually passing original |
| `coroutine-contract` | Two cross-compiler BCPL paired applications, eleven and eighteen exact record oracles | Previously MVS-verified 2 PASS on the recorded revision |
| Regular `mr10` plus native project suites | Established accepted production coverage | Previously 201 PASS and one expected Bootstrap SKIP 083 |

The `mr10-coroutines-supported` manifest resides at
`mr10-kit-compiler/tests/10-coroutines/supported-manifest.tsv`.
The first four cases are run through the **unchanged**
`tools/mr10/run-dev-probes` engine, including independent JES
reports, exact goldens, compiler phases and generated artifact
verification. The fifth is compiled independently through
`tools/mr10/compile-and-run --results` under canonical ICINT19;
its final output must exactly equal the new golden.
The candidate inherits the existing historical test's **JES
structure** (ten zero-RC steps and three zero CODE phases) for
validation; this does not share its case identity or its status.

All source inputs are Git-controlled. The new suite hard-pins
the canonical corrected source, original source and original
golden by their exact verified Git blob hashes. It performs a
non-MVS preflight before running and retains separate evidence
under `workarea/mr10-supported-coroutines/` and
`workarea/mr10-probes/`. The project coordinator's fail-stop
parser checks the five identities, source receipts, job identities,
record oracles, status/RC agreement and expected JES steps/phases
without weakening the original historical diagnostic.

## Acceptance gates

1. Complete the consolidated eight PASS-eligible suite MVS campaign
   with zero FAIL/BLOCKED: the six regular suites (201 PASS,
   one expected SKIP), `coroutine-contract` (two paired PASS)
   and `mr10-coroutines-supported` (five new-or-rerun case PASS),
   subject to actual results rather than forecasts.
2. Run `mr10-coroutines` separately as a diagnostic and preserve
   the original **one FAIL** with CODE=-1; do not label its run PASS.
3. Review all structured receipts, update
   `co6-qualified-acceptance-review-candidate-20261116.md`,
   and obtain the owner's **explicit approval** before closing CO.6.

**Host-only verification at implementation:** 18 synthetic unit
tests PASS; Python syntax passes. This is not MVS verification.
No installed coroutine runtime, IFOX, IEWL, historical source, JCL,
original accepted output, or MVS dataset is changed by the
documentation-only acceptance proposal and new host runner.

## 16 November 2026 — final supported/historical MVS campaign completed

At **tested** GitHub `main` `216b6707c404a91c796ed8f1419a99ef172b184a`, the owner executed the
single eight-suite supported campaign with `--profile production`,
`--allow-device`, and `--progress`: **RC=0,
PROJECT REGRESSION RESULT: PASS; 208 PASS, zero FAIL/BLOCKED,
one expected Bootstrap SKIP 083**. These are six established
suites (201 PASS, one SKIP) plus the verified
`mr10-coroutines-supported` selection (5 PASS) and the
`coroutine-contract` paired selection (2 PASS).
The supported suite's **five real interpreted MVS tests** passed;
this supersedes only the earlier MVS-UNVERIFIED status of the
supported runner, not historical evidence.

A separate original historical `mr10-coroutines` diagnostic
returned **RC=1/FAIL** with **4 PASS, one genuine original
`fixed-stack-producer-consumer` interpreted CODE=-1 FAIL**.
No original fixture, golden, accepted code or manifest was changed.
The four overlapping historical passing identities are not new
unique supported test cases.

Evidence: `workarea/project-regressions/20261116T151624Z-56400-i4ueoalx/summary.json`,
`workarea/project-regressions/20261116T152532Z-76357-_s4f83jy/summary.json`;
operator logs `mvs-state/reconstruction-evidence/co6-supported-final-20261116T151623Z.log`
and `mvs-state/reconstruction-evidence/co6-historical-final-20261116T151623Z.log`.
The submitted terminal excerpts show status/counts, not the
raw JES reports or the whole receipts independently.

The [revised CO.6 formal qualified acceptance review candidate](co6-qualified-acceptance-review-candidate-20261116.md)
documents met gates and retained limits. **CO.6 remains IN PROGRESS
until explicit owner qualified-closure approval.**
No MVS reruns, source/runtime changes or new march are requested.
