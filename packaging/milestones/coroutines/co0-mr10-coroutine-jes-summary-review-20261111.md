# CO.0 — MR10 coroutine probe JES summary review

**Milestone:** [Implement coroutine support for native compiler](milestone-implement-coroutine-support-for-native-compiler.md)  
**March:** CO.0 — Historical Research and Behavioral Contract  
**Recorded:** 11 November 2026 (UTC)  
**Status:** **Five OBSERVED; JES summary and second-pass extracted outputs/artifact comparisons reviewed.** Formal acceptance and raw artifact archival remain pending; not a march closure.

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

## Second-pass operator extraction: program records and compiler artifacts (11 November)

The operator ran the read-only Python extraction on the original WSL `workarea/` receipts after updating to Git `3001bb6c89ed986d8a1b7d9f6dce72e6c87a0677`; checkout and host-only manifest check both returned RC=0. The extraction program read each local `*-jes-report.txt`, isolated the final INTCODE run, printed non-metadata program records and compared the four newly generated compiler artifacts with the historical files using whitespace-token equality.

**Result:** `Evidence extraction errors: 0`; **extraction RC=0**. The 23 interpreted phase completion codes reported from the detailed JES files were all zero and agreed with `summary.json`. These results are grounded in the operator's printed extraction results, **not** direct byte-level access to files in the operator's WSL environment.

### Exact extracted final program output

**JES 5223 — `compiler-probe`**

```text
COROUTINE COMPILER PROBE COMPILED
```

**JES 5224 — `frame-layout-probe`**

```text
COROUTINE FRAME PROBE COMPILED
```

**JES 5225 — `fixed-stack-producer-consumer`**

```text
PRODUCER: 1
CONSUMER: 1
PRODUCER: 2
CONSUMER: 2
PRODUCER: 3
CONSUMER: 3
PRODUCER: 4
CONSUMER: 4
PRODUCER: 5
CONSUMER: 5
```

**JES 5226 — `resumeco-chain`**

```text
A START
B START WITH 111
ROOT GOT 222
A RESUMED WITH 333
ROOT GOT 444
B RESUMED WITH 555
ROOT GOT 666
```

**JES 5227 — `create-delete-static-pool`**

```text
CREATED 2
LIST COUNT 3
A RETURNED 11
B RETURNED 21
DELETED A
LIST COUNT 2
DELETED B
LIST COUNT 1
C RETURNED 31
LIST COUNT 2
DELETED C
FINAL LIST COUNT 1
```

All five extracted sequences were independently compared against the **source-derived** candidate traces in `tools/mr10/dev_probe_extras.py` and matched exactly. In addition, the operator's local comparison returned `True` for **four of four** pairs:

- `compiler-probe.ocode` versus `tests/10-coroutines/evidence/compiler-probe.ocode`
- `compiler-probe.intcode` versus `tests/10-coroutines/evidence/compiler-probe.intcode`
- `frame-layout-probe.ocode` versus `tests/10-coroutines/evidence/frame-layout-probe.ocode`
- `frame-layout-probe.intcode` versus `tests/10-coroutines/evidence/frame-layout-probe.intcode`

The two compilation-only probe entries were **not executed** as coroutine switches; their reported output and artifact matches verify generation/structure only. The three actual coroutine exercises verify the specific positive-path behaviors above under reconstructed MR10 ICINT19, not the original missing KM10 native runtime.

### Evidence classification and acceptance boundary

| Aspect | Current evidence classification |
| --- | --- |
| JES job identities, step/program sequences, RCs | Operator-provided JES summary **independently cross-checked** (62/62 zero) |
| Interpreted phases | **Interpreted-MVS-tested**: operator extraction of local full JES reports gives 23/23 zero codes; printed results reviewed |
| Program-visible outputs | **Interpreted-MVS-tested**: five extracted sequences match the source-derived candidate expectations |
| Compiler artifact structure | **Interpreted-MVS-tested**, operator-comparison attested: 4/4 fresh files token-match checked-in evidence |
| Formal new golden baselines / manifest status | **UNVERIFIED**; no separate owner acceptance or manifest promotion |
| Historical KM10 native ABI / full failure-path behavior | **UNVERIFIED**; not covered by these five probes |

This second extraction closes the specific *missing program-output/phase/artifact-comparison transcript* gap from the initial JES-summary-only review. It does **not** mean the original raw reports and artifact bytes have been copied into this Git record, or prove that the source-derived oracles are independently authoritative historical specifications. **Owner review of proposed golden-output acceptance and any manifest promotion is still required.**

No new jobs were submitted for this read-only extraction. No code, manifest, test identities, MVS dataset or historical source was changed as part of the evidence review.

## Acceptance boundary and next evidence

The provided JES summaries independently establish job identities, all named step/program/RC sequences, and successful overall JES dispositions. The supplied `summary.json` supports the runner's provisional `OBSERVED` results. They **do not independently establish** complete program-visible outputs, detailed interpreter `CODE=` records, unexpected diagnostics, or fresh generated OCODE/INTCODE versus archived evidence.

**11 November second-pass update:** The operator supplied the program-visible final records, interpreted CODE arrays extracted from all five full JES reports, and true/false token comparisons against all four compiler artifacts. All matched; see the second-pass section above. Original complete files remain in the operator's WSL `workarea/`, not this repository. Independent historical-oracle authority, broader negative-path testing and explicit owner approval of any accepted golden fixtures/manifest changes remain open.

**Disposition:** Keep all five `UNVERIFIED` in `mr10-kit-compiler/tests/dev-probes-manifest.tsv`. CO.0 remains **IN PROGRESS**; CO.1–CO.5 remain **NOT STARTED**. No native code, existing test contract, JES job, or MVS dataset was modified in this Git evidence record.

## Owner acceptance decision — 11 November 2026

The owner explicitly approved promotion of the five `10-coroutines/` development probes to `ACCEPTED` with a Git commit. The exact final program-visible outputs from JES jobs **5223–5227** are now frozen into separate `.expected` files, with content and paths pinned by the host-only manifest validator. The revised runner requires exact golden output, exact case-specific JES step/program order and RCs, all-zero interpreted phase codes, plus fresh OCODE/INTCODE token matches for the two compilation probes before claiming a new `PASS`.

See the [formal five-case acceptance record](../../../mr10-kit-compiler/tests/10-coroutines/acceptance-20261111.md). This action **does not** mark CO.0 closed or claim new JES execution of the revised eleven-case runner. The six other historical development probes remain `UNVERIFIED`.
