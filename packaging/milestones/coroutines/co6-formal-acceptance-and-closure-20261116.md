# CO.6 — Common Coroutine Behavioral Contract and Cross-Compiler Verification: formal qualified closure

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.6 — Common Coroutine Behavioral Contract and Cross-Compiler Verification  
**Owner decision:** **ACCEPTED AND CLOSED (qualified)**  
**Decision date:** 16 November 2026  
**Tested source:** GitHub `main` `216b6707c404a91c796ed8f1419a99ef172b184a`  
**Prior acceptance review checkpoint:** GitHub `main` `d742e0d6aad498a1e9f58fc405682f3f12bee56f`  
**Scope of closure:** Documented supported/common-domain behavior; not all historical semantics, unbounded coroutine support, a new release or a native-running compiler.

## Explicit owner acceptance

After the [CO.6 formal qualified acceptance review candidate](co6-qualified-acceptance-review-candidate-20261116.md) was presented, the owner explicitly wrote:

> Yes, let's close CO.6. Commit your work. Give me a handoff prompt for a post-milestone discussion.

This authorizes formal closure of **CO.6 (qualified)** on precisely the previously reviewed terms. It does not authorize production changes, a new official march, an unverified rollback or public distribution. CO.0–CO.5 were previously accepted as CLOSED (qualified), so the overall milestone is now **CLOSED (qualified)**.

## Accepted MVS regression evidence

At the tested Git revision, the source-controlled coordinator ran all eight supported suites in one campaign using `--profile production` and explicit `--allow-device`. It returned **RC=0, PASS**.

| Supported selection | PASS | FAIL | SKIP | BLOCKED |
| --- | ---: | ---: | ---: | ---: |
| `mr10` | 12 | 0 | 0 | 0 |
| `mr10-coroutines-supported` | 5 | 0 | 0 | 0 |
| `bootstrap` | 145 | 0 | 1 (083) | 0 |
| `runtime-extensions` | 13 | 0 | 0 | 0 |
| `bcpltime` | 4 | 0 | 0 | 0 |
| `bcplqsam` | 14 | 0 | 0 | 0 |
| `coroutines` | 13 | 0 | 0 | 0 |
| `coroutine-contract` | 2 | 0 | 0 | 0 |
| **Supported total** | **208** | **0** | **1** | **0** |

The `mr10-coroutines-supported` suite passed all five cases, including separately named valid-frame `fixed-stack-co0-candidate`. The `coroutine-contract` suite independently passed both exact-output interpreted/native application oracles: `co6-pair` (eleven records) and `co6-nested` (eighteen records). The latter exercises two workers, nested continuations, parent-chain transfer and valid delete/reuse within accepted bounds. Application behavior, not shared implementation layout, is the comparison boundary.

**Supported run evidence:**
- `workarea/project-regressions/20261116T151624Z-56400-i4ueoalx/summary.json`
- `mvs-state/reconstruction-evidence/co6-supported-final-20261116T151623Z.log`

## Genuine historical failure explicitly retained

The independently executed, unchanged original five-case `mr10-coroutines` diagnostic returned **RC=1 / FAIL: four PASS, one actual FAIL**. The original `10-coroutines/fixed-stack-producer-consumer` under reconstructed canonical ICINT19 returned `CODE=-1` rather than expected zero. Its manually constructed first-activation frame is incompatible with the verified canonical continuation convention; the separately named valid-frame PASS is **not** a historical compatibility PASS and the original fixture must not become PASS, SKIP, XFAIL or an accepted-successful negative test.

**Historical run evidence:**
- `workarea/project-regressions/20261116T152532Z-76357-_s4f83jy/summary.json`
- `mvs-state/reconstruction-evidence/co6-historical-final-20261116T151623Z.log`

The original 17-entry historical development-probe manifest, BCPL source, expected code, golden output and failure record were preserved. The four historical PASS cases overlap the supported suite; do not add these outcomes to the supported 208 distinct cases.

**Evidence classification:** The operator supplied coordinator results and locations for retained receipts. The original complete JSON and individual raw JES records were not independently opened in this conversation. The source-controlled runner enforces strict completion and output checks; closure claims only the actually reported tested behavior.

## Qualifications and release boundaries

The native implementation continues under the previously owner-accepted **Approach A/S1** constraints: a root and **at most two live registered workers**, fixed independent checked **1024-word** worker stacks, known-live descriptor lifecycle, and permanent coroutine globals **G!289–300**. MR10/ICINT19 and native System/370 coroutine ABIs, saved-frame/descriptor representations and global layouts are **not** identical. The Cambridge compiler still executes as INTCODE under ICINT19 while emitting native System/370 application code; the independent native-running compiler is a separate unfinished deliverable.

Not established: unlimited workers/stacks, stale/freed/ABA-proof descriptor safety, actual GETMAIN resource exhaustion, abnormal cancellation or abend recovery, preemption/reentrancy, byte-identical historical interoperability, or broad historical source/binary compatibility. The earlier CO.5 Bootstrap 117 `LKED` IEWL **SB2D** in JOB 6745 remains a genuine recorded incident despite successful isolated and full later re-execution; its underlying cause was not proven.

The owner-accepted CO.5 Git-backed ten-object clean-room reconstruction, `BOOT_OBJ(BCPLCO)` and `BOOT_OBJ(COROUTIN)` installation and installed-only verification remain prior evidence. No additional clean-room rebuild, object overwrite, automatic rollback, distribution tape publication or public release occurred or was authorized by CO.6 closure.

## Final disposition

- CO.0 — Historical Research and Behavioral Contract: CLOSED (qualified)
- CO.1 — Native ABI and Stack Architecture: CLOSED (qualified)
- CO.2 — Native CHANGECO Implementation: CLOSED (qualified)
- CO.3 — Coroutine Library and Lifecycle: CLOSED (qualified)
- CO.4 — Robustness and Edge-Case Verification: CLOSED (qualified)
- CO.5 — Integration, Regression, and Release: CLOSED (qualified)
- **CO.6 — Common Coroutine Behavioral Contract and Cross-Compiler Verification: CLOSED (qualified), owner accepted 16 November 2026**

**Overall milestone — Implement coroutine support for native compiler: CLOSED (qualified).**

This closure is **documentation-only**: no code, MVS dataset, installed object or distribution release was changed by the sign-off. Post-milestone planning is a separate owner-led discussion, with no new march identifier or implementation authorization inferred. The [post-milestone handoff](co6-post-milestone-discussion-handoff-20261116.md) provides context for that discussion.
