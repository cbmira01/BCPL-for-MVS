# CO.2 — Native CHANGECO Implementation: formal qualified closure

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.2 — Native CHANGECO Implementation  
**Owner decision:** **CLOSED (qualified)**  
**Decision date:** 14 November 2026 (Louisville local time)  
**Source reviewed:** GitHub `main` at `382386e86ac54ed150ae20a342f90947a15ac94b`  
**Next march:** CO.3 — Coroutine Library and Lifecycle (**IN PROGRESS**)

## Explicit owner acceptance

The owner directed: **“Close out CO.2 and proceed to CO.3 without delay. Give me a handoff prompt to another conversation.”**

This explicitly accepts the [qualified CO.2 acceptance candidate](co2-qualified-acceptance-candidate-20261114.md), closes **CO.2 — Native CHANGECO Implementation** for its bounded native implementation gate, and authorizes opening **CO.3 — Coroutine Library and Lifecycle**. It does **not** authorize production object installation, final/public ABI registration, publication of a release, or acceptance of later marches.

## Native verification accepted

Both applications compile under the interpreter-hosted Cambridge compiler (generating System/370 code), assemble using IFOX, link with IEWL, and execute **natively** on MVS 3.8J. Both exercise the **same** tracked separate Core Runtime IFOX module, `bootstrap-toolchain/asm/bcplco.asm`.

| Evidence | Compiler JOB | Native JOB | IFOX / IEWL / GO | BCPL oracle | Runner |
| --- | ---: | ---: | --- | --- | --- |
| [First CO.2 candidate](co2-native-changeco-jes-5374-5375-pass-20261114.md) | 5374 | 5375 | 3 / 1 / 1, all RC=0000 | `A1 B1 A2 R1 B2 R2 PASS` | RC=0 |
| [Repeated continuations](co2-native-continuations-jes-5378-5379-pass-20261114.md) | 5378 | 5379 | 3 / 1 / 1, all RC=0000 | `X1 Y1 X2 Y2 X3 R1 Y3 R2 PASS` | RC=0 |

The owner retained generated source, complete job reports and machine-readable receipts in:

- `workarea/co2-native-changeco/20261114T141120Z-w7s__us5`
- `workarea/co2-native-continuations/20261114T161730Z-1a8_w7bf`

**Classification:** OWNER-REPORTED NATIVE-MVS-TESTED. The assistant reviewed repository source and the owner's runner-console results, but did not independently inspect the raw local JES or generated compiler files. The runner requires five exact completed zero-RC JES steps and exact ordered BCPL records. Native execution demonstrated first activation, two independently stacked live workers, direct transfer, nested checked frames and locals, repeated suspension, argument/result continuation, ordinary worker return, terminal re-entry refusal at known-live descriptors, and root G54/G55 restoration.

The first repeated-continuations attempt at `ae51ea4bd3c142bc3aa349d74ee850f2a6fdc4f5` [failed](co2-native-continuations-failed-oracle-20261114.md) with `X1 Y1 X2 Y2 X3 FVALUE`, runner RC=1. The BCPL test fixture's recursion expected 17/22 instead of the mathematically correct 23/32; this was repaired at `5f941bb34cc70649f0325bd73f42eeb67397c5d6` before the second native PASS. The original failure remains preserved as **FAIL**, not retroactively relabeled.

## Scope of qualified acceptance

**Accepted:** an isolated source-backed `BCPLCO` native `CO2INIT`/`CHANGECO` implementation with Approach A valid/live descriptor assumptions and S1 independent checked stacks; temporary candidate linkage; first entry, context preservation at the BCPL behavioral level, value passing, nested continuation and normal return.

**Not accepted as production contracts:** the exact 24-word descriptor, singleton scratch/registry size, test-local G!295–299 slots, candidate error numbers, a public `CHANGECO` header/global ABI, full PSW/condition-code preservation, fully measured `STKLIM`/`APLIMIT`/`STACKHWM` behavior, safe use-after-free/reuse, concurrent access, all error paths, or general historical compatibility. `BOOT_OBJ` remains untouched; the proven object remains a **candidate**, not an installed production object.

Higher-level BCPL coroutine management (`CREATECO`, `DELETECO`, `CALLCO`, `COWAIT`, `RESUMECO`, parent-chain semantics, resource ownership and storage reuse) belongs to **CO.3** with separately approved interfaces. Robustness and release gates belong to CO.4 and CO.5. Historical MR10 G6–G8/G91–G95 collide with the Cambridge environment and are not imported as a native API.

## March disposition and transition

**CO.0 — Historical Research and Behavioral Contract:** CLOSED (qualified).  
**CO.1 — Native ABI and Stack Architecture:** CLOSED (qualified).  
**CO.2 — Native CHANGECO Implementation:** **CLOSED (qualified, owner accepted 14 November 2026)**.  
**CO.3 — Coroutine Library and Lifecycle:** **IN PROGRESS**; see [CO.3 kickoff](co3-coroutine-library-and-lifecycle-kickoff-20261114.md).  
**CO.4 — Robustness and Edge-Case Verification; CO.5 — Integration, Regression, and Release:** NOT STARTED.

This decision produces only a source-tracked milestone closure and CO.3 kickoff. No MVS job, resident dataset change, installation, regression renumbering or release publication is performed by the record.
