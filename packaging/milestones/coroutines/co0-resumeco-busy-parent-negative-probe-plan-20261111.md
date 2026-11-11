# CO.0 — RESUMECO busy-target parent-chain negative probe

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.0 — Historical Research and Behavioral Contract (IN PROGRESS)  
**Date:** 11 November 2026  
**Status:** Isolated experimental BCPL probe and offline checks prepared; **MVS execution NOT YET OBSERVED**.

## Question and design constraint

The evidence-classified [CO.0 behavioral contract](co0-evidence-classified-behavioral-contract-and-open-questions-20261111.md) records **CO0-U03**: reconstructed `RESUMECO(C,A)` clears the current coroutine's parent (`CURRCO!1 := 0`) *before* checking whether target `C!1 != 0`, then returns `-998` when occupied. This is SOURCE-OBSERVED and might violate parent-chain invariants on rejection. A later native contract should not inherit this behavior without an explicit decision and target evidence.

The experiment **does not edit the canonical library** or the prior accepted oracles. The bounded probe is `mr10-kit-compiler/tests/10-coroutines/resumeco-busy-parent-co0-probe.bcpl`. It is not added to the established 12-case Regression Panel or the five accepted development-probe identities.

## Natural busy-target construction

The probe initializes an MR10 root descriptor/arena exactly as the existing development probes, then `CREATECO` builds A and B. ROOT calls A, making ROOT the parent of A. A calls B and passes its own descriptor; B has A as its parent. From B, `RESUMECO(A,123)` attempts to resume **A, which remains active as B's caller and has a nonzero parent ROOT**. Therefore A is a valid live but busy target; no fabricated, invalid or freed descriptor is supplied.

B prints its parent/target occupancy predicates, the returned value, and whether B's parent was preserved or cleared. **Only after these measurements**, B restores `CURRCO!1` from the saved parent and executes `COWAIT(777)`. This artificial repair is solely to unwind the experimental stack safely; it is *not* a modification to, or an endorsement of, the production `RESUMECO` contract. A then yields 888 to ROOT, which attempts to delete both inactive descriptors.

## Source-derived hypothetical output (NOT an accepted oracle)

The following is the **SOURCE-OBSERVED / INFERRED** prediction if the compiled code follows the current library semantics. In MR10, a true predicate and `TRUE` deletion return are conventionally represented as `-1`; actual formatting must be verified on MVS:

```text
CO0 BUSY BEFORE -1
CO0 BUSY TARGET -1
CO0 BUSY RESULT -998
CO0 BUSY PARENT KEPT 0
CO0 BUSY PARENT CLEARED -1
CO0 A GOT 777
CO0 ROOT GOT 888
CO0 DELETE A -1
CO0 DELETE B -1
```

The critical discriminator is **`PARENT KEPT` versus `PARENT CLEARED`**. Preserve complete observed output even if it differs; do not rewrite a golden fixture to agree with unexpected behavior. Unexpected abends, compiler errors or missing final output are failures requiring review, not accepted negative-path semantics.

## Verification workflow and evidence gates

1. Synchronize GitHub `main`, require exact HEAD and `git diff --check` RC=0. Run offline `tools/checks/test_co0_resumeco_busy_parent_probe.py` (2 unit tests) and existing canonical/candidate tests (3 and 6 unit tests). These are **host tests** and do not execute BCPL or JES.
2. Only with operator JES permission, from repository root run:

   ```bash
   tools/mr10/compile-and-run --results \
       mr10-kit-compiler/asm/icintv19.asm \
       mr10-kit-compiler/tests/10-coroutines/resumeco-busy-parent-co0-probe.bcpl \
       +mr10-kit-compiler/library/getvec-freevec.bcpl \
       +mr10-kit-compiler/library/coroutines.bcpl
   ```

   This uses **canonical ICLIB** and canonical coroutine library with separately staged job-temporary source/INTCODE. The generator builds ICINT19 with IFOX00/IEWL and submits to the JES reader; it does **not** overwrite resident MVS source or library members.
3. Retain full `--results` transcript and runner RC, extract the exact payload JOB number, run `tools/mvs/job-summary JOBID`, and preserve any printer report. Assess each JES step RC, interpreted COMP/CG/RUN `CODE` (when available), program records and explicit parent invariant.
4. Only after observation decide whether `RESUMECO` must preserve the current parent on the busy-target failure. A future repair requires a separate owner-reviewed decision and isolated candidate verification; **do not silently patch canonical coroutine semantics**.

**No MVS execution, negative-path acceptance or canonical repair is claimed by preparing this probe.** CO.0 remains IN PROGRESS; CO.1–CO.5 NOT STARTED.
