# CO.0 — Interpreted-to-native coroutine behavioral oracle matrix

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.0 — Historical Research and Behavioral Contract (**IN PROGRESS**)  
**Evidence checkpoint:** GitHub `main` at `1a74c321b20be7f2c92539faadab75690fcdc5aa`  
**Status:** RESEARCH / TEST-MAPPING RECORD. No native coroutine code or tests accepted.

## Purpose and evidence boundary

Consolidate the three owner-accepted **INTERPRETED-MVS-TESTED** CO0-U08
oracles into a reproducible reference for eventual native System/370
verification. The Cambridge Compiler presently runs as INTCODE under
ICINT19 and can emit native System/370 code; the milestone targets the
**native code generated**, not an already self-hosted compiler.

The observed output sequences are authoritative only for their bounded
reconstructed MR10 tests. No native code was executed in these jobs.
A passing ICINT19 run is **not** NATIVE-MVS-TESTED evidence. Do not
interpret MR10's provisional global assignments, descriptor fields,
synthetic first-entry frame or heap initializer as native ABI decisions.

## Verified interpreted reference set

| JOB | Source under `mr10-kit-compiler/tests/10-coroutines/` | Behavior witnessed | Exact output | Interpreter | JES |
| --- | --- | --- | --- | --- | --- |
| **5331** (`BCCO0TWO`) | [two-coroutine local state](../../../mr10-kit-compiler/tests/10-coroutines/co0-two-coroutine-local-state-candidate.bcpl) | Alternating independent state; three direct yields per coroutine; delete | **8/8** | CODE=0; 5,138 cycles; runner RC=0 | **12/12 RC=0000**, SUCCESS |
| **5332** (`BCCO0NES`) | [nested activation](../../../mr10-kit-compiler/tests/10-coroutines/co0-nested-activation-continuation-candidate.bcpl) | Alternating nested LEAF/MIDDLE continuation; one leaf yield each; delete | **14/14** | CODE=0; 9,017 cycles; runner RC=0 | **12/12 RC=0000**, SUCCESS |
| **5333** (`BCCO0NES`) | [nested double yield](../../../mr10-kit-compiler/tests/10-coroutines/co0-nested-double-yield-candidate.bcpl) | Each nested leaf yields twice at distinct sites; persists SAVED/FIRST; delete | **18/18** | CODE=0; 11,593 cycles; runner RC=0 | **12/12 RC=0000**, SUCCESS; summary RC=0 |

**Source revisions executed**, respectively:
`3540202e6da809d2cba55b61ea48f7d3638ef195`,
`cc9e4c36d2593e3d0486e9eced5faa8f59d738cf`, and
`c4164f5957d4870e854f28cc9a22c1cb9b49ff37`.
JOB 5331 and 5332 displayed independently successful `job-summary`
reports without an accompanying shell RC; do not infer one.

Detailed acceptance and exact trace records:
[5331](co0-u08-two-coroutine-oracle-plan-20261112.md),
[5332](co0-u08-nested-activation-continuation-plan-20261112.md),
[5333](co0-u08-nested-double-yield-plan-20261112.md).
The operator-local complete run logs are recorded there; the matrix is
**not** a substitute for those logs or generated OCODE/INTCODE.

## Behavioral assertion mapping

| Observable requirement | Interpreted evidence | Future native verification assertion |
| --- | --- | --- |
| Alternating two live contexts | 5331–5333, INTERPRETED-MVS-TESTED | A/B resume in the specified order and retain separate execution state |
| Argument delivered on each resumption | 5331–5333, INTERPRETED-MVS-TESTED | Correct received values and derived results at the specified calls |
| Local values survive direct suspension | 5331, INTERPRETED-MVS-TESTED | Reproduce exact eight-record 5331 trace |
| Nested active frame survives switch | 5332–5333, INTERPRETED-MVS-TESTED | Reproduce exact 14-/18-record traces with LEAF/MIDDLE/worker returns |
| Two continuation sites in one nested frame | 5333, INTERPRETED-MVS-TESTED | Correct WAIT1, GOT1, second yield and GOT2 ordering and arithmetic |
| Ordinary deletion of inactive workers | 5331–5333, INTERPRETED-MVS-TESTED | Both DELETECO results and lack of intervening corruption |
| Native register/stack restoration | **UNVERIFIED** | Separate native assembly/instrumented probes and ABI evidence required |
| Native per-coroutine stack limits/guards | **UNVERIFIED** | Separate bounded native checked-stack and failure-path cases required |
| Native invalid/stale descriptor behavior | **UNVERIFIED** | Decide validation and ownership semantics before safe native tests |
| Native global/header assignments | **UNVERIFIED** | CO.1 owner-approved registry/ABI mapping required |

The output **order and values**, not ICINT19 interpreter cycles, `PROGRAM
SIZE`, memory addresses, JES job numbers or exact step counts, form the
portable behavioral comparison. A native build necessarily uses a different
compile/link/run pipeline. Native JES success must be checked for its
**actual steps**, not mechanically expected to be 12.

## Native adaptation requirements (not implementation authorization)

1. Retain each BCPL test's worker/leaf/middle arithmetic, switching order,
   observable printed records, and bounded ordinary lifecycle.
2. Replace the MR10-only root descriptor initialization, fixed test heap,
   coroutine library bindings and provisional globals (6–8, 87–95 as
   applicable) with the **approved native** runtime/header/init mechanism
   after the CO.1 design gate. Do not copy descriptor `C!0..C!2` or
   `COBOOT` assumptions into the native ABI.
3. Compile to native System/370 through the Cambridge compiler toolchain,
   assemble/link with IFOX/IEWL as applicable, then execute the resulting
   native load module under MVS 3.8J. Distinguish compiler execution under
   ICINT19 from native application execution.
4. Compare complete ordered program records to their respective accepted
   interpreted references; separately require successful native completion,
   checked JES outcomes, saved artifacts, and reproducibility from GitHub.
5. Store native acceptance separately with source revision, compiler, object
   provenance, JCL, load module identity, full SYSOUT, step RCs, and clear
   **NATIVE-MVS-TESTED** classification. Do not overwrite interpreted
   acceptance records or enroll unverified native tests as accepted.

These are candidate acceptance requirements to be reconciled with CO.1
architecture approval, not a new ABI, stack policy, failure code, or
authorization to run JES/install datasets.

## Remaining CO.0 / CO.1 boundary

The current oracles **do not** settle the missing historical
`KM10.COMAIN`, full interpreter P/C/continuation tracing, busy/invalid
descriptor policy, worker exceptions, recursion/stack overflow, independent
native stack ownership, or native register save/restore behavior. The
broader [evidence and open-question ledger](co0-evidence-classified-behavioral-contract-and-open-questions-20261111.md)
retains those distinct gates.

**Disposition:** The three interpreted oracle references are accepted;
the **mapping is a research aid**, not evidence of native equivalence.
CO.0 remains **IN PROGRESS**; CO.1–CO.5 remain **NOT STARTED**. No native
implementation, regression manifest, installed MVS dataset or acceptance
status is changed.
