# CO.0 — MR10 coroutine probe JES summary review

**Milestone:** [Implement coroutine support for native compiler](milestone-implement-coroutine-support-for-native-compiler.md)  
**March:** CO.0 — Historical Research and Behavioral Contract  
**Recorded:** 11 November 2026 (UTC)  
**Status:** **Five OBSERVED; JES summary review complete; full artifact/output review pending.** Not an accepted test promotion or march closure.

## Evidence provenance

The operator furnished a WSL transcript containing the five-case `tools/mr10/run-dev-probes` generated `summary.json` and all five `*-jes-summary.txt` records. Evidence is held on the operator's WSL machine, not stored in Git:

```text
workarea/mr10-probes/20261111T003215Z-61963-r0h4d1yc/
```

The recorded revision is `777837f7f0333892b8734620055da12d13ef138d`, using `mr10-kit-compiler/asm/icintv19.asm`. The JSON start and finish timestamps are `2026-11-11T00:32:15.701896+00:00` and `2026-11-11T00:33:52.646970+00:00`. The operator reported successful `git pull`, manifest check and case listing (all RC=0), and the expected experimental run RC=3.

## Independent cross-check of supplied JES summaries

| Existing case | JES job / name | JES steps | Runner RC | Interpreted phase codes in JSON | Classification |
| --- | --- | ---: | ---: | --- | --- |
| `10-coroutines/compiler-probe` | 5223 / DP011963 | 12 | 0 | 0, 0, 0 | OBSERVED |
| `10-coroutines/frame-layout-probe` | 5224 / DP021963 | 12 | 0 | 0, 0, 0 | OBSERVED |
| `10-coroutines/fixed-stack-producer-consumer` | 5225 / DP031963 | 10 | 0 | 0, 0, 0 | OBSERVED |
| `10-coroutines/resumeco-chain` | 5226 / DP041963 | 14 | 0 | 0, 0, 0, 0, 0, 0, 0 | OBSERVED |
| `10-coroutines/create-delete-static-pool` | 5227 / DP051963 | 14 | 0 | 0, 0, 0, 0, 0, 0, 0 | OBSERVED |

The supplied `summary.json` was parsed independently and checked against the five separately printed JES summaries:

1. All five `jes_job_id` and `job_name` pairs match their JES summary headers, uniquely.
2. The complete step name, program and return-code sequences in all five summaries match the JSON arrays; **62/62 JES steps have RC=0000**. All five show `JOB RESULT: SUCCESS` and `HIGHEST RC: 0000`.
3. The JSON reports **23/23 interpreted phase codes equal to zero** (3 + 3 + 3 + 7 + 7), plus `interpreted_code=0` and `runner_rc=0` for each case. **The actual CODE= lines have not been independently checked against the original detailed JES reports**, because those reports were not supplied.
4. The aggregate reported counts are `PASS=0, OBSERVED=5, FAIL=0, NOT_RUN=0`, `status=UNVERIFIED`, `verification=UNVERIFIED`. The experimental runner's RC=3 is its documented **UNVERIFIED** classification, not a failed job.
5. The existing runner attested candidate output-oracle agreement in all five cases, and freshly captured OCODE/INTCODE token agreement for the two compiler-only probes. This is **runner-attested**, not an independent byte-by-byte or program-output inspection.

The first two `START` programs do not invoke `CHANGECO` at runtime; they test the compiler output structure, not switching. The other three are reconstructed MR10 positive-path exercises and are not the missing historical KM10 native coroutine implementation.

## Acceptance boundary and next evidence

The provided JES summaries independently establish job identities, all named step/program/RC sequences, and successful overall JES dispositions. The supplied `summary.json` supports the runner's provisional `OBSERVED` results. They **do not independently establish** complete program-visible outputs, detailed interpreter `CODE=` records, unexpected diagnostics, or fresh generated OCODE/INTCODE versus archived evidence.

**Still needed for a full independent review:** all five original `*-jes-report.txt` files (or their program-visible and relevant phase excerpts), and the two compiler probe pairs of fresh OCODE/INTCODE files, alongside checked-in source evidence. Review any failures or differences before proposing new accepted golden fixtures or changing the manifest.

**Disposition:** Keep all five `UNVERIFIED` in `mr10-kit-compiler/tests/dev-probes-manifest.tsv`. CO.0 remains **IN PROGRESS**; CO.1–CO.5 remain **NOT STARTED**. No native code, existing test contract, JES job, or MVS dataset was modified in this Git evidence record.
