# MR10 coroutine development probes — owner-accepted golden outputs

**Recorded:** 11 November 2026 (UTC)  
**Interpreted execution revision:** `777837f7f0333892b8734620055da12d13ef138d`  
**Evidence review revision:** `bcf91cdfd1c5ce991e0bf236bc57c242233dc329`  
**Scope:** Five reconstructed **interpreted MR10** development probes only. No native coroutine support or CO.0 closure.

The owner explicitly approved promotion of these five `10-coroutines/` development probes and committing the resulting golden-output and runner contracts. Before the approval, the operator ran the experimental probes under MVS/ICINT19 and supplied JES summaries, interpreted phase codes extracted from full JES reports, final program outputs, and generated OCODE/INTCODE token comparisons. The original WSL evidence is preserved in:

```text
workarea/mr10-probes/20261111T003215Z-61963-r0h4d1yc/
```

See the [CO.0 evidence review](../../../packaging/milestones/coroutines/co0-mr10-coroutine-jes-summary-review-20261111.md).

| Accepted identity | JES | Steps RC=0000 | Interpreted phases CODE=0 | Golden file |
| --- | ---: | ---: | ---: | --- |
| `10-coroutines/compiler-probe` | 5223 | 12 | 3 | [`compiler-probe.expected`](compiler-probe.expected) |
| `10-coroutines/frame-layout-probe` | 5224 | 12 | 3 | [`frame-layout-probe.expected`](frame-layout-probe.expected) |
| `10-coroutines/fixed-stack-producer-consumer` | 5225 | 10 | 3 | [`fixed-stack-producer-consumer.expected`](fixed-stack-producer-consumer.expected) |
| `10-coroutines/resumeco-chain` | 5226 | 14 | 7 | [`resumeco-chain.expected`](resumeco-chain.expected) |
| `10-coroutines/create-delete-static-pool` | 5227 | 14 | 7 | [`create-delete-static-pool.expected`](create-delete-static-pool.expected) |

**Evidence totals:** Five prior experimental cases OBSERVED; 62/62 JES steps RC=0000; 23/23 interpreted phases CODE=0; all five final program-output traces matched; four of four freshly generated OCODE/INTCODE files token-matched their checked-in evidence.

## Acceptance enforcement

- The manifest validator pins each accepted case's source, modules, expected interpreted completion, exact golden path/content and `ACCEPTED` status; other development probes cannot be silently promoted.
- The runner requires exact final output records and complete ordered JES step/program/RC records before assigning `PASS`. The two compiler probes additionally require fresh OCODE and INTCODE token-matched to archived files.
- The project coordinator's `mr10-probes` suite selects **eleven** accepted cases, the original six plus these five, independently of the separate 12-case MR10 Regression Panel and all native suites.
- Six other development-probe contracts remain `UNVERIFIED`.

**Execution qualification:** The previously reviewed five-job execution used the **experimental pre-promotion runner**. No new JES job was submitted in connection with this Git promotion. The updated eleven-case runner's first all-PASS on-MVS run is a separate verification requirement subject to JES authorization. The historical KM10 native coroutine interface, native System/370 coroutine implementation and CO.0 behavioral-contract research remain open.
