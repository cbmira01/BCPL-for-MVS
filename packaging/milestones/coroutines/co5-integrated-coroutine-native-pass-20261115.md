# CO.5 — Integrated native coroutine suite 177–189: PASS

**Project:** BCPL for MVS 3.8 Reconstruction
**Milestone:** Implement coroutine support for native compiler
**March:** CO.5 — Integration, Regression, and Release
**Status:** IN PROGRESS; focused native-suite verification PASS
**Test date:** 15 November 2026
**Tested GitHub main:** `53a4e4feebfec3f41223288416d2f0a3011bb77a`
**Evidence class:** OWNER-REPORTED NATIVE-MVS-TESTED; raw JES reports not independently audited

## Executed MVS command and evidence provenance

The operator fast-forwarded to the exact GitHub revision shown above and
executed `tools/tests/run-project-regressions --run --suite coroutines
--profile production --progress`.

- Coordinator evidence: `workarea/project-regressions/20261115T174552Z-24774-60jc52p8/`
- Summary: `workarea/project-regressions/20261115T174552Z-24774-60jc52p8/summary.json`
- Result: **PASS**; coordinator RC **0**; elapsed **0m 52s**
- Suite counts: **13 PASS, 0 FAIL, 0 SKIP, 0 BLOCKED**; total **13**

### Per-case results from operator transcript

| ID | Native regression case | Result |
| --- | --- | --- |
| 177 | co2-native-changeco | PASS |
| 178 | co2-repeated-continuations | PASS |
| 179 | co3-first-lifecycle | PASS |
| 180 | co3-parent-chain | PASS |
| 181 | co3-delete-reuse | PASS |
| 182 | co4-bounded-stress | PASS |
| 183 | co4-safe-negative | PASS |
| 184 | co4-stack | PASS |
| 185 | co4-churn | PASS |
| 186 | co4-busy | PASS |
| 187 | co4-limits | PASS |
| 188 | co4-deny | PASS |
| 189 | co4-account | PASS |

This was a single coordinated 13-case run on one source revision,
not an aggregation of earlier CO.2–CO.4 candidate successes.
The numbered adapters require exact BCPL output records, checked
Cambridge compilation, individual JES job identities, IFOX/IEWL/GO
step RC=0, and independently compiled BCPL library where applicable.

**Audit boundary:** The assistant received the console summary, not the
local `summary.json`, per-case `result.json`, JES reports or compiler
listings. The asserted underlying job/oracle checks were carried out
by the source-controlled native runners; this record does not claim
independent inspection of the operator's raw MVS evidence.

## Assistant-owned host verification

In an isolated assistant workspace on 15 November 2026, reran:

- Installation/anchor/clean-checkout host tests: **4 PASS**
- Coroutine fixture/adapter/negative-oracle host tests: **5 PASS**
- Python syntax compilation for the native adapter and offline checker: **PASS**
- GitHub 13-case TSV ownership and source revision verification: **PASS**

These checks are host-side; only the operator run supplies target MVS evidence.

## Scope, authority and remaining CO.5 gates

All numbered cases remain source-selected, temporary candidate linkage.
Installed `BOOT_OBJ` remains read-only, and G!289–305 remain private and
test-local. Neither this run nor its record grants a public coroutine ABI,
permanent global allocation, `BOOT_OBJ` overwrite, or release.

Still pending: coordinated MR10 panel and eleven accepted Development Probes,
Bootstrap, Runtime Extensions, BCPLTIME and BCPLQSAM native regression;
preservation of historical SKIP 083; separate JES printer/punch authorization
for BCPLQSAM device cases 175–176; review of raw per-case receipts; an
explicitly authorized clean-room rebuild and IFOX/IEWL reproducibility gate;
release/install/rollback documentation; and distinct owner acceptance.

The CO.4 limitations remain: no real GETMAIN exhaustion, deliberate
stack-overflow recovery, arbitrary stale pointers or ABA-safe identity,
unexpected abend recovery, multitasking or general public interface.
CO.4 remains CLOSED (qualified). **CO.5 remains IN PROGRESS.**
