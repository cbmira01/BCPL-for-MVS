# MR10 development probes — evidence review and candidate expansion

**Project:** BCPL for MVS 3.8 Reconstruction  
**Date:** 4 November 2026  
**Authority:** GitHub `main`, `mr10-kit-compiler/tests/dev-probes-manifest.tsv`  
**Status:** Five additional owner-approved golden baselines established; eleven experimental historical contracts remain UNVERIFIED

## Accepted and observed baselines

The owner-accepted `05-named-dd` golden output derives from JOB 9543
(`DP018361`) and its later independent fresh PASS. That case remains the
**only accepted development-probe contract**.

The broader 4 November run under Git revision
`6c98bcf16171bc7f4589b7af038408f42c8dc725` yielded:

- Original six development probes: 1 PASS (`05-named-dd`), 5 OBSERVED, 0 FAIL.
- Established separate MR10 Regression Panel: 12 PASS, 0 FAIL.
- Local evidence folder:
  `workarea/mr10-probes/20261104T190013Z-28850-2_n4npqv/`.

The following five **now have accepted golden-output contracts**,
based on the saved JES step summaries and interpreted phase evidence from
the combined run. The original six-case run reported five OBSERVED because
these golden baselines were not yet registered; that historical output is
not retroactively relabeled as a runner PASS.

| Case | JES identity | JES verification | Accepted semantic output |
| --- | --- | --- | --- |
| `04-module-test` | JOB 9545 / DP018850 | 12 steps RC=0000, five phases CODE=0 | Ten factorial records |
| `06-dynamic-streams` | JOB 9547 / DP038850 | 10 steps RC=0000, three phases CODE=0 | `DEEPEST GET VALUE = 24680` |
| `07-many-streams` | JOB 9548 / DP048850 | 10 steps RC=0000, three phases CODE=0 | `OPENED 12 STREAMS`, DD1–DD12 outputs, all closed |
| `09-multiple-assignment` | JOB 9549 / DP058850 | 10 steps RC=0000, three phases CODE=0 | Sequential assignment outputs |
| `11-getvec-freevec` | JOB 9550 / DP068850 | 12 steps RC=0000, five phases CODE=0 | Allocations, reuse and coalescing |

Each of the five now has its exact `.expected` output and a
`acceptance-20261104.md` receipt in the historical test directory.
The updated runner still requires a **fresh MVS execution** to establish
that its six-case accepted PASS behavior works live after modification.
Neither the historical acceptance nor offline unit tests constitute that
post-change validation.

## Additional eleven historical candidates

These 11 contracts retain their existing historical identifiers. They are
**experimentally executable** under `tools/mr10/run-dev-probes`, but no
execution or acceptance is claimed by this design document.

| Case | Engine / interpreter | Initial oracle and evidence |
| --- | --- | --- |
| `01-echo-test` | run-intcode / current | Exact nonempty SYSIN echo; runtime BLIBI and ICLIB modules |
| `02-honors-thesis-and-mapstore/honors-thesis` | run-intcode / v12 | Ten factorial values; v12-specific interpreter and existing historical expected file |
| `02-honors-thesis-and-mapstore/mapstore` | run-intcode / v13 | Intentional X38 diagnostic, MAPSTORE and interpreted CODE=-1; negative test, not a normal successful program |
| `03-compile-richards-factorial/compile` | compile-and-run / current | Ten factorial values and generated OCODE/INTCODE |
| `03-compile-richards-factorial/v14-intcode` | run-intcode / v14 | Historical generated INTCODE and factorial output, including record continuation compatibility |
| `08-character-translation` | compile-and-run / current | BCPL backslash operators, RDCH numeric records from PUNCT, generated OCODE/INTCODE |
| `10-coroutines/compiler-probe` | compile-and-run / current | Compiler-only CHANGECO call probe; compare generated OCODE/INTCODE tokens to archived evidence |
| `10-coroutines/frame-layout-probe` | compile-and-run / current | CREATEFRAME call-frame layout; compare generated OCODE/INTCODE to archived evidence |
| `10-coroutines/fixed-stack-producer-consumer` | compile-and-run / current | Producer and consumer exchange values 1–5 in order |
| `10-coroutines/resumeco-chain` | compile-and-run / current | Parent/resume transfer and return values across A, B and root |
| `10-coroutines/create-delete-static-pool` | compile-and-run / current | Coroutine create/delete/reuse and list-count sequence |

### Boundaries and caution

- All 11 additional cases are **UNVERIFIED**; a matching candidate output and clean JES report
  yields `OBSERVED` and never PASS. An unexpected output, missing artifact,
  incomplete job, invalid step RC or wrong interpreted code yields FAIL.
- Current source-based oracles are **hypotheses to test**, not published
  historical truth. In particular, character code translation details and
  old MAPSTORE diagnostics must be revised only against actual MVS evidence.
- The historical v12/v13/v14 assembler selections must not be replaced with
  ICINT19 merely to make a case run.
- `compile-and-run --artifact-dir` directs captured generated artifacts
  under a per-case workarea directory and does not overwrite tracked
  historical evidence or earlier shared workarea outputs.
- The runner saves separate JES report and job-summary text for each
  experimental case and checks the expected interpreted phase count.
- `--run --all-provisional` keeps its existing six-case scope.
  `--run --all-candidates` is an explicit, separate 17-case selection,
  **not** the pre-existing 12-case Regression Panel and **not** the project
  regression coordinator.
- A checkout, host-only check, and a source commit do not authorize new JES
  submissions, permanent MVS dataset modifications, acceptance of another
  case, or publication of a new milestone.

## Next evidence gates

1. Host-only validate the six-case accepted runner and its full negative
   tests; then obtain separate approval for a fresh six-case MVS run.
2. Perform bounded, explicitly authorized MVS experiments on the eleven
   new cases, preferably one engine/interpreter family at a time.
3. Preserve raw output and job identity, review deviations, and avoid
   promoting any experimental candidate solely because its unit test passed.
