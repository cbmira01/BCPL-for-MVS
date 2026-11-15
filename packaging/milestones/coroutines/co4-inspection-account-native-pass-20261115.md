# CO.4 — ACCOUNT native PASS; three inspection cases completed

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.4 — Robustness and Edge-Case Verification (**IN PROGRESS**)  
**ACCOUNT tested revision:** `1c97e030e2f12f5786145a8b9f13202d67c0ffe7`  
**Reported:** 15 November 2026  
**Evidence class:** **OWNER-REPORTED NATIVE-MVS-TESTED**, qualified. Underlying raw JES receipts were not independently inspected here.

## ACCOUNT: owner-observed native PASS

The owner performed a guarded fast-forward to the tested revision and invoked:

```sh
python3 -B tools/coroutines/run-co4-inspection-followup.py --run --case account
```

The complete reported result:

```text
CO.4 ACCOUNT PASS
CO.4 followup PASS (1/1 PASS)
CO.4 followup evidence: /home/calvin/Source/Repos/BCPL-for-MVS/workarea/co4-inspection-followup/20261115T143922Z-64hf1aqw
CO.4 ACCOUNT RC=0
```

The runner inherits independent Cambridge compilation of application and BCPL coroutine library, four IFOX assembly steps, IEWL, native GO/JES validation and the strict eight-record `CO4MEM` oracle. This result reports that the runner's complete native gate passed, including the repaired `BOOTSNAP` pre-registration accounting checks and the post-registration `SNAP` equality of machine `CURPTR` and BCPL `CO3CURR`. Exact compiler and native JOB IDs, raw step receipts and the BCPL output have not been furnished or independently inspected.

The prior ACCOUNT results remain separate FAILs:
- Early `CO4MEM FAIL` at `b0ce46fd965d1ca7720594fc5516ad7dd12f3993`, within the original mixed LIMITS PASS/ACCOUNT FAIL batch.
- `FCURR`, `FAIL` at `491f4acaa44a37eb4e63ff7e3bc75693c96211c7`, a test-fixture assertion that compared zero machine `CURPTR` with the initialized BCPL root before the first `CO2INIT`.

The test-only `BOOTSNAP` repair, source-validation changes and focused host checks are documented in [the preceding failure/repair record](co4-inspection-followup-account-fcurr-deny-pass-20261115.md). No accepted native Core Runtime, library source or installed `BOOT_OBJ` object was changed by this repair.

## Inspection suite results across distinct accepted runs

| Candidate | Tested revision | Owner-reported result | Evidence |
| --- | --- | --- | --- |
| `LIMITS` | `b0ce46fd965d1ca7720594fc5516ad7dd12f3993` | **PASS** — 12-record `CO4LIM` oracle | `workarea/co4-inspection-batch/20261115T132404Z-dnfqqr22` |
| `DENY` | `491f4acaa44a37eb4e63ff7e3bc75693c96211c7` | **PASS** — 12-record `CO4DENY` oracle | `workarea/co4-inspection-followup/20261115T140823Z-zg8lgr_p` |
| `ACCOUNT` | `1c97e030e2f12f5786145a8b9f13202d67c0ffe7` | **PASS** — eight-record `CO4MEM` oracle | `workarea/co4-inspection-followup/20261115T143922Z-64hf1aqw` |

**These are three independently reported native PASS results, NOT an uninterrupted PASS of the original three-case runner at a single revision.** The original inspection runner halted on ACCOUNT. Later runs changed the ACCOUNT test fixture and added independent execution so DENY could be verified. Do not substitute the three outcomes for a same-revision suite receipt.

The `DENY` experiment injects zero returns through a temporary BCPL `GETVEC` override and verifies rollback/recovery; it is **not** an actual `GETMAIN` refusal by MVS. `LIMITS` observes the live stack limits and metadata but does not force an overflow.

**CO.4 stays IN PROGRESS pending explicit owner decision. CO.5 remains NOT STARTED.**
