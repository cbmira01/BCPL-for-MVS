# CO.0 — Evidence-classified coroutine behavior and open-question ledger

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.0 — Historical Research and Behavioral Contract (**IN PROGRESS**)  
**Prepared:** 11 November 2026  
**Source checkpoint:** GitHub `main` at `419aa8a6c28279262e385d88217255a1484b7f04`  
**Status:** REVIEW DRAFT; reconstructed interpreted behavior only. No native ABI, global-slot, stack layout, or error-recovery policy is approved by this record.

## Scope and evidence vocabulary

**DECLARED** means the project states an intended requirement; **SOURCE-OBSERVED** means directly present in tracked source; **INTERPRETED-MVS-TESTED** means the identified MVS/ICINT19 output or JES result was reported and reviewed; **NATIVE-MVS-TESTED** requires native System/370 execution evidence; **INFERRED** means reasoned from source/test observations but not directly exercised; **UNVERIFIED** means there is no sufficient proof.

The reconstructed **MR10 INTCODE coroutine interface** is distinct from the historical **KM10 native** coroutine mechanism. None of the following assigns the MR10 global numbers to the future native compiler or proves the missing historical `KM10.COMAIN` implementation.

## Current reconstructed MR10 contract

| Behavior | Evidence classification | Observed or source-defined behavior and limits |
| --- | --- | --- |
| Call interface | SOURCE-OBSERVED; INTERPRETED-MVS-TESTED for selected calls | `CHANGECO(value, target)`, `CALLCO(C,A)`, `COWAIT(A)`, `RESUMECO(C,A)` use BCPL procedure calls. Existing compiler-only probes verify compiled call/frame artifacts but do **not** execute CHANGECO. |
| Saved execution context | SOURCE-OBSERVED; INTERPRETED-MVS-TESTED for continuation-divergence candidate | Promoted `ICLIB` stores the outgoing **CHANGECO call-frame pointer** in current descriptor `C!0`. On incoming transfer it loads the saved frame and continuation from the target frame before the `X32` trampoline. The original global-10 shared-continuation error was observed in JOB 5231; corrected ordering was observed in candidate JOB 5238. |
| Value transfer | SOURCE-OBSERVED; INTERPRETED-MVS-TESTED for tested positive paths | `ICLIB` moves `CHANGECO`'s value argument through scratch `G!9`. The receiving coroutine resumes with the transfer value as the `CHANGECO` result. Exact observed values are fixed by the tests; arbitrary target and argument validity are not established. |
| First activation | SOURCE-OBSERVED; INTERPRETED-MVS-TESTED for basic/compatibility cases | `CREATECO` allocates `GETVEC(SIZE+9)`, sets `P=C+3`, `C!0=P`, `P!0=P`, `P!1=COBOOT`, `P!2=FN`, `P!3=SIZE`, `P!4=C`. `COBOOT` first calls `COWAIT(C)`, then calls the worker with the next delivered argument. This is an MR10-specific synthetic frame, **not** a native stack ABI. |
| Parent and waiting | SOURCE-OBSERVED; INTERPRETED-MVS-TESTED in selected chains | `CALLCO` rejects a target whose `C!1 != 0` with `-999`; otherwise sets `C!1=CURRCO`. `COWAIT` reads its `CURRCO!1`, clears that parent field, and transfers to the parent. Exact chained outputs are observed in JOB 5244. |
| RESUMECO transfer | SOURCE-OBSERVED; INTERPRETED-MVS-TESTED for busy and positive paths | Canonical `RESUMECO` saves the current parent, **tests `CPTR!1` before clearing `CURRCO!1`**, then installs the saved parent and switches. A valid, busy target returns `-998` and preserves the current parent (JOB 5299). Positive transfer matches all seven chain records (JOB 5300). Invalid/stale pointers remain unverified. |
| Worker natural return | SOURCE-OBSERVED; not independently tested as a termination contract | `COBOOT` executes `C := FN(COWAIT(C)) REPEAT`: a worker function's ordinary return is followed by another wait and possible re-entry, **not automatic permanent termination**. The precise next-call behavior and cleanup are not proven under all cases. |
| Creation failure | SOURCE-OBSERVED; negative path UNVERIFIED | `CREATECO` returns 0 when `GETVEC` returns 0; actual exhaustion thresholds, allocator invariants and malformed `SIZE` inputs are not accepted as coroutine behavior tests. |
| Deletion | SOURCE-OBSERVED; INTERPRETED-MVS-TESTED for selected positive paths | `DELETECO` checks `C=0`, `C=CURRCO` and `C!1 != 0`; it then unlinks a matching descriptor from `COLIST` and calls `FREEVEC(C)`. JOB 5246 observed deletion/list counts and subsequent creation, **not pointer-address reuse**. |
| Invalid or stale descriptors | UNVERIFIED; source indicates unsafe dereference | `CALLCO`, `RESUMECO` and `DELETECO` dereference nonzero descriptors before proving membership or allocation liveness. No promise of safe handling, rollback, a specific return code or recovery from arbitrary addresses is justified. |
| Root coroutine | SOURCE-OBSERVED in probes | The MR10 tests create an explicit root descriptor, initialize `CURRCO`, and in library tests set `COLIST`. This is test-level initialization, not an established native root-registration API. |
| Storage, stack safety and cleanup | SOURCE-OBSERVED for MR10 allocator calls; native UNVERIFIED | MR10 `GETVEC/FREEVEC` and `SIZE+9` are implementation facts. The future native `BCPLMEM` allocator and checked `STKLIM`/stack-high-water contract require a separate CO.1 design. |

## Historical-source boundary

The tape `INDEX` lists `KM10.COMAIN`, `KM10.COMACRO`, `KM10.COBLIB(CORTN)`, `KM10.COBLIB(STANDARD)` and `KM10.J(COLIB)`. `KM10.COMAIN` is **absent** from the preserved archive (UNVERIFIED full implementation). The surviving `km10/comacro` `COBASE` DSECT includes `COFATHER`, `COPSAVE`, `COLBASE`, `COLEND`, `COSTKLIM`, `COENTRY`, `COHOLD` and `COSTART` (SOURCE-OBSERVED). Historical `km10/coblib/cortn` uses stack-related globals `107..109` and private coroutine save-area references; `km10/j/colib` includes that BLIB variant. These findings establish a historical native variant, **not** interchangeability with reconstructed MR10 descriptors or callable names.

The historical MR10 interpreter source `richards-bcpltape/mr10/bcplkit/icint` defines the relevant `X32` P/C-transfer operation; `mr10-kit-compiler/asm/icintv19.asm` is the reconstructed execution substrate. The project repair changes canonical `ICLIB` and `coroutines.bcpl`, **not** the INTCODE instruction set.

## Existing positive oracles and reproducible recipe

**Canonical-default panel:** with Git `main` at `226201834fe205139ef259338bfd8ff508bd8930`, `tools/mr10/run-regression-panel --verbose` (no `--iclib`, no `--module-override`) produced **12/12 PASS, RC=0**, JOBS **5272–5283**, **142/142 JES steps RC=0000**, all 12 final RUN `CODE=0`, and matched unchanged panel goldens. See [canonical panel review](co0-canonical-default-mr10-jes-5272-5283-acceptance-review-20261111.md). Its `coroutines/basic-coroutine` oracle is `RP: COROUTINE 77 1` (JOB 5283).

**Five development probes:** `tools/mr10/run-dev-probes` selects cases from `mr10-kit-compiler/tests/dev-probes-manifest.tsv`. The existing five `10-coroutines/` cases have owner-accepted evidence under JOBS **5223–5227**, including four compiler-artifact token comparisons. Those jobs **preceded the canonical repair**; the original fixed-stack probe uses a different synthetic startup scheme. A repaired **candidate** fixed-stack variant passed JOB **5240**. Do not silently equate the previously accepted unmodified fixed-stack test with the repaired canonical library, or assert that all five have been rerun post-promotion.

**Additional candidate positive paths:** JOB **5238** verified distinct continuation ordering, JOB **5244** the RESUMECO parent chain, JOB **5246** create/delete/recreation; the candidate-aware full panel passed 12/12. Their target was the candidate pair. They support, but do not replace, canonical-default checks.

To reproduce the established canonical panel, use `tools/mr10/run-regression-panel --verbose`, retain a complete report and each `tools/mvs/job-summary JOBID`. For research probes, use the documented `run-dev-probes` commands and preserve distinct source revisions and output oracle identities. No new JES submission is requested by this document.

## Open-question ledger (not concealed assumptions)

| ID | Question / decision needed | Evidence gap and proposed gate |
| --- | --- | --- |
| CO0-U01 | Full P/C and argument-order trace, including `X32` and synthetic frame | Inspect the exact original MR10 opcode semantics, ICINT19 assembly, and existing compiler-probe/frame-layout saved OCODE/INTCODE; source-derived static trace before accepting exact intermediate state. |
| CO0-U02 | Compatibility of five development probes after canonical promotion | **OPEN; qualified 4 PASS / 1 FAIL.** JOBS 5316/5317 and the two separately rerun cases passed their unchanged goldens; JOB 5318 legacy fixed-stack returned interpreted CODE=-1 despite all JES RC=0000. The independent corrected-frame source passed earlier candidate JOB 5240; canonical-ICLIB rerun and separate acceptance pending. |
| CO0-U03 | RESUMECO busy-target behavior and parent-chain preservation | **RESOLVED for valid, live descriptors (INTERPRETED-MVS-TESTED).** Pre-repair counterexample JOB 5284; corrected candidate JOBS 5285–5298; promoted canonical JOBS 5299–5312 (14/14 focused and 142/142 panel JES steps RC=0000, all interpreted CODE=0). Invalid/stale pointers remain CO0-U04. |
| CO0-U04 | Invalid, stale, freed, active and null descriptor semantics | Negative tests and policy for rejectable valid descriptors versus unrecoverable bad addresses; avoid claiming safe arbitrary-pointer inspection. |
| CO0-U05 | Natural worker return and repeated activation | Trace `COBOOT` and test repeated return/re-entry and cleanup or exhaustion; do not infer automatic coroutine destruction. |
| CO0-U06 | Allocation bounds, SIZE validity, stack overruns and cleanup | Define defensible interpreted negative cases first; CO.1 must independently design native stack guards and lifecycle. |
| CO0-U07 | Recover historical `KM10.COMAIN` and complete original callable interface | Missing archive member; continue targeted source/document search, but owner-approved engineering direction does **not** require exhaustive recovery before implementation. |
| CO0-U08 | Equivalent **interpreted/native** behavior oracles | Prepare common BCPL tests for yield/resume/value, parent-chain transfer, first activation, nested locals, return/re-entry and deletion, with documented global/header mapping. Native tests and all native outcomes remain UNVERIFIED. |
| CO0-U09 | Select native ownership, global numbers and descriptor/stack ABI | Reserve for CO.1 owner review against runtime contract, registry, CG370, MVS IFOX/IEWL/GO evidence. Nothing in this document allocates globals or approves the native architecture. |

## Proposed acceptance boundary

This ledger supplies a **reviewable behavior table, source provenance, interpreted reproduction recipe and explicit unknowns**, meeting the *documentation shape* required by the CO.0 gate. It is **not** a declaration that every checkbox in `coroutine-research-and-design-gates.md` has been proved; especially U01/U02/U03/U04/U08 remain open. An owner decision is required for acceptance/closure, and CO.1 remains NOT STARTED.

**No code changes, resident MVS dataset changes, JES submissions, native ABI decisions, canonical golden revisions or march closure are authorized by this review draft.**

## 12 November 2026 update — resolved U03; bounded U01 and U02 gates

The canonical promotion was approved by the owner and committed at
`723c3887b3b732dfa457c169c82e9849b9400b24`. See
[the acceptance evidence](co0-resumeco-busy-parent-repair-candidate-20261111.md)
for JOBS 5284–5312 and exact local reports. **CO0-U03 is resolved
for valid, live descriptors only**. No native test is claimed.

**CO0-U01 partial source trace (SOURCE-OBSERVED):** Original historical
`richards-bcpltape/mr10/bcplkit/icint` has `CASE 32: P, C := A, B`
and the `mr10-kit-compiler/asm/icintv19.asm` `X32` handler loads
interpreter A into P and B into C and branches to FETCH. Both implement
the same atomic interpreter-state transfer. The canonical
`mr10-kit-compiler/source/iclib.int` CHANGECO path starts at label
`6` with `LIP2 SG9 LP0 SIG7 LIP3 SG7 LIG7 X1 A1 X1 SG10`;
its next operations include `LL498 LIG7 X1 X1 X32`, followed at
label 498 by `LIG9 JIG10`. The source shows that argument, current
descriptor, saved frame/continuation and return value are handled
before/after X32. Exact intermediate P/C/scratch-global values still
require a token-by-token trace together with archived compiler
OCODE/INTCODE; these are **not** proved by this static observation.
The source uses interpreter-local globals G!7, G!9 and G!10: no
assignment of these slots is approved for native S/370 BCPL.

**CO0-U02 pending:** The previously accepted five development-probe
goldens predate this canonical RESUMECO correction. The 12-case panel
and isolated positive chain do **not** replace the full five-probe
rerun. Re-execute the existing five accepted probes through
`tools/mr10/run-dev-probes --run` with five explicit `--case`
selectors, preserve compiler OCODE/INTCODE artifacts for
`compiler-probe` and `frame-layout-probe`, and classify any
fixed-stack divergence rather than silently changing a golden.
This work is a distinct interpreted-MVS research gate.

The overall CO.0 status remains IN PROGRESS; CO.1–CO.5 remain
NOT STARTED. This record does not approve a native interface,
descriptor layout, global-slot allocation, or a new milestone.

## 12 November 2026 — U02 compatibility qualification

The first two accepted post-promotion probes (JOBS 5316–5317)
passed output and saved compiler-artifact checks. JOB 5318
(`fixed-stack-producer-consumer`) failed with interpreted CODE=-1
and an ICINT19 invalid-instruction trace at C-offset 803 after
`JIG10`, despite ten zero-RC JES steps. The final two accepted
probes were run independently and passed with 28/28 zero-RC JES steps.
Therefore original probe coverage is **four PASS / one FAIL** at the
promoted canonical revision, not 5/5. The original fixed-stack
source/golden must not be silently replaced. See the updated
[U01/U02 gate note](co0-u01-static-interpreter-transfer-and-u02-five-probe-gate-20261112.md)
for the separate existing COBOOT-style candidate and the pending
canonical-default MVS compatibility gate. No native execution claimed.
