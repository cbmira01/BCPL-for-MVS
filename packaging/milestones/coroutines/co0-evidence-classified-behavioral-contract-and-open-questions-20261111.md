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
| CO0-U01 | Full P/C and argument-order trace, including `X32` and synthetic frame | **BEHAVIOR VERIFIED; TRACE DETAIL OPEN:** 18-token bridge and archived compiler calls SOURCE-OBSERVED; canonical JOB 5322 verified bounded nested continuation/value ordering (CODE=0, 14/14 JES RC=0000). Intermediate-cycle state and native ABI unverified. |
| CO0-U02 | Compatibility of five development probes after canonical promotion | **RESOLVED WITH QUALIFICATION (INTERPRETED-MVS-TESTED):** four original cases PASS; original legacy fixed-stack JOB 5318 remains FAIL (CODE=-1); separately identified corrected COBOOT-frame candidate JOB 5321 matches all ten expected records, CODE=0, runner RC=0, 10/10 JES RC=0000. Original golden and manifest unchanged; full original five-case runner still FAILS. |
| CO0-U03 | RESUMECO busy-target behavior and parent-chain preservation | **RESOLVED for valid, live descriptors (INTERPRETED-MVS-TESTED).** Pre-repair counterexample JOB 5284; corrected candidate JOBS 5285–5298; promoted canonical JOBS 5299–5312 (14/14 focused and 142/142 panel JES steps RC=0000, all interpreted CODE=0). Invalid/stale pointers remain CO0-U04. |
| CO0-U04 | Invalid, stale, freed, active and null descriptor semantics | **BOUNDED VALID-DESCRIPTOR CASES VERIFIED (INTERPRETED-MVS-TESTED); BROADER U04 OPEN:** JOB 5325 observed 7/7 lines, CODE=0, runner RC=0, 14/14 JES RC=0000. Null/current deletion, live busy root rejection and post-rejection worker liveness passed. Stale, freed, malformed, arbitrary pointers unverified. |
| CO0-U05 | Natural worker return and repeated activation | **RESOLVED for bounded ordinary-return/re-entry (INTERPRETED-MVS-TESTED):** canonical JOB 5324 returned 110 then 120 on distinct worker invocations, accepted deletion, CODE=0, runner RC=0, 14/14 JES steps RC=0000. Exceptional termination and native teardown unverified. |
| CO0-U06 | Allocation bounds, SIZE validity, stack overruns and cleanup | **BOUNDED REFUSAL, EXACT FIT, REUSE, COALESCING AND MIDDLE UNLINK VERIFIED (INTERPRETED-MVS-TESTED):** JOBS 5326–5329 matched exact oracles, CODE=0, runner RC=0 and 14/14 JES RC=0000 each. A safe negative-SIZE candidate remains MVS-unverified. SIZE=-9..-1, arithmetic overflow, stack guards and exceptional/native cleanup are open. |
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

## 12 November 2026 — U02 acceptance and U01 bridge refinement

The operator's canonical ICINT19 JOB 5321 independently verified the
corrected-frame fixed-stack candidate: 10/10 expected producer/consumer
records, interpreted CODE=0, runner RC=0 and all 10 JES steps RC=0000.
CO0-U02 is therefore **RESOLVED WITH QUALIFICATION**: four unchanged
original probes PASS; the original fixed-stack source still FAILS at
JOB 5318; the separate corrected-frame version PASSes at JOB 5321.
Do not describe this as five original PASSes or silently amend a golden.

CO0-U01 now has a source-derived 18-token canonical ICLIB transfer
trace validated by a host-only symbolic exercise and archived compiler
OCODE/INTCODE call patterns. `X32` installs the incoming frame P and
branches to common label 498, then `JIG10` enters the incoming
continuation; transfer value is restored through G!9. Correlation with
observed intermediate MVS state and nested contexts is still open.
See the [U01/U02 record](co0-u01-static-interpreter-transfer-and-u02-five-probe-gate-20261112.md).

## 12 November 2026 — U01 canonical verification and U05 next gate

JOB **5322**, canonical ICINT19/ICLIB, produced thirteen correct
continuation/value records, **CODE=0**, runner RC=0, and an
independent **14/14 JES RC=0000** summary. The staged worker
resumed after the corresponding root event. Thus U01's tested
continuation behavior is INTERPRETED-MVS-TESTED; complete
intermediate-state tracing and native execution remain open.

U05 has a distinct candidate
`mr10-kit-compiler/tests/10-coroutines/co0-worker-return-reentry-candidate.bcpl`.
Its predicted two worker returns and subsequent deletion are
UNVERIFIED pending MVS. Neither manifest nor accepted golden changed.

## 12 November 2026 — U05 acceptance and bounded U04 gate

**CO0-U05** accepted for ordinary worker return/re-entry:
canonical JOB **5324** completed 14/14 JES steps RC=0000,
interpreted CODE=0, runner RC=0 and five expected records,
including two distinct worker invocations returning 110 and 120
followed by successful deletion. Original JOB 5323 was a
compile-only failure and is not behavioral evidence. See
[U05 detail](co0-u05-worker-return-reentry-probe-plan-20261112.md).
There is no automatic worker destruction claim.

**CO0-U04** remains open. The new standalone
`co0-valid-descriptor-rejections-candidate.bcpl` tests only
explicit guard paths on null deletion and a valid live root
descriptor whose parent marker is nonzero. It avoids freed and
arbitrary memory addresses, checks parent preservation and then
executes a normal create/call/delete as a liveness sanity check.
Predictions remain UNVERIFIED pending actual ICINT19/JES execution.

## 12 November 2026 — U04 bounded acceptance and U06 new gate

JOB **5325** independently verified the source-predicted
seven records for null/current deletion and busy valid-root
CALLCO/RESUMECO rejection, including parent preservation,
then normal worker creation/deletion. Interpreted CODE=0,
runner RC=0 and all 14 JES steps RC=0000. This is
**INTERPRETED-MVS-TESTED only for bounded live/root and null
operations**; general CO0-U04 remains open for stale/invalid
addresses. See [U04 details](co0-u04-valid-descriptor-rejections-plan-20261112.md).

A separate U06 candidate now examines deterministic positive
oversize allocation refusal and ordinary storage recovery in
the source-defined 161-word fixed arena. The prediction
is UNVERIFIED pending MVS. It deliberately excludes stack
overflow, malformed SIZE and native memory reclamation policy.

## 12 November 2026 — U06 acceptance and next exact-fit gate

**JOB 5326 (BCCO0ALL)** passed the complete bounded
positive-oversize refusal and recovery oracle:
five exact records, interpreted CODE=0, runner RC=0,
and independent all **14/14 JES steps RC=0000**.
A separate exact-fit allocation candidate now tests the
source-derived boundary SIZE=149 for a 161-word arena
and SIZE=150 as one word beyond it, followed by normal
deletion and reuse. No new acceptance is claimed for
that candidate until MVS evidence is collected.
CO0-U06 remains open for malformed SIZE, stack overrun,
native cleanup and exceptional termination.

## 12 November 2026 — U06 exact-fit acceptance and coalescing candidate

**JOB 5327** verified the 161-word arena boundary:
SIZE=150 refused (162 required), SIZE=149 succeeded
(161 required), and a post-deletion SIZE=149 reallocation
succeeded. Five expected records, CODE=0, runner RC=0,
independent 14/14 JES RC=0000. Classified
**INTERPRETED-MVS-TESTED**, limited to positive SIZE.

A separate candidate now tests two simultaneously live
coroutines, an oversized third request, partial deletion
without enough contiguous space, and complete deletion
followed by adjacent-free-block coalescing. This new
fragmentation candidate has **no MVS evidence yet**.

## 12 November 2026 — U06 coalescing acceptance and middle-unlink gate

JOB **5328** independently verified nine output records,
interpreted CODE=0, runner RC=0 and **14/14 JES steps
RC=0000**. This accepts the bounded ordinary fragmentation
and coalescing sequence as INTERPRETED-MVS-TESTED.

Next candidate targets the separately source-observed
`DELETECO` **middle-descriptor unlink** path,
surviving coroutine re-entry and normal allocation/deletion.
No dereference of freed B is performed. This candidate
remains UNVERIFIED until actual MVS execution and JES review.

## 12 November 2026 — U06 middle-unlink acceptance and negative-SIZE boundary

JOB **5329** matched all eleven output records, interpreted
CODE=0, runner RC=0 and 14/14 JES steps RC=0000.
Its middle-descriptor unlink and post-delete survivor
liveness are accepted INTERPRETED-MVS-TESTED evidence.

The canonical `CREATECO` forwards `SIZE+9` to
`GETVEC`, which explicitly returns zero for **N<0**.
A separate bounded test proposes SIZE=-10 and SIZE=-20,
then a normal SIZE=100 allocation and deletion.
**Do not run SIZE=-9..-1** without design review: these
values can result in a successful allocation too small
for the unconditional synthetic-frame writes. The
negative-SIZE probe is not yet MVS-tested and does not
prove a comprehensive malformed-SIZE contract.

## 12 November 2026 — U06 guarded negative-SIZE acceptance

JOB **5330** (`BCCO0NEG`) at `40436cbc3f31c8a39426207754d609384b8d7bee` verified four exact records: `NEG TEN CREATE 0`, `NEG TWENTY CREATE 0`, `NORMAL RESULT 51`, `NORMAL DELETE -1`. Canonical ICINT19 completed `CODE=0` (3163 cycles), runner RC=0, and independently checked JES **14/14 steps RC=0000** (`tools/mvs/job-summary 5330`, RC=0). Evidence classification: **INTERPRETED-MVS-TESTED**, only for SIZE=-10/-20 and subsequent ordinary liveness. See [negative-SIZE investigation](co0-u06-negative-size-guard-plan-20261112.md). CO0-U06 remains OPEN for SIZE=-9..-1, arithmetic overflow, stack bounds, exceptional cleanup and native ownership. No general malformed-SIZE guarantee is established. CO.0 remains IN PROGRESS; CO.1 NOT STARTED.
