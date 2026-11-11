# CO.0 — MR10 coroutine development-probe verification plan

**Milestone:** [Implement coroutine support for native compiler](milestone-implement-coroutine-support-for-native-compiler.md)  
**March:** CO.0 — Historical Research and Behavioral Contract (**IN PROGRESS**)  
**Recorded:** 10 November 2026  
**Evidence status at creation (10 November):** SOURCE/TOOL REVIEW ONLY; JES not yet run. **11 November follow-up:** all five were executed by the operator. [The JES summary review](co0-mr10-coroutine-jes-summary-review-20261111.md) records five OBSERVED and 62 zero-RC steps; full raw output/artifact inspection remains pending.

## Purpose and evidence boundaries

Run **only five** existing reconstructed-MR10 coroutine development probes under current `ICINT19`. These are project-created reconstruction exercises, **not authenticated historical KM10 coroutine code**. The accepted 12-case MR10 panel's `basic-coroutine` is independent and must not be double-counted.

`tools/mr10/run-dev-probes` currently supports all five by repeated `--case`. The five contracts in `mr10-kit-compiler/tests/dev-probes-manifest.tsv` are `UNVERIFIED` with `pending:` oracle labels. `tools/mr10/dev_probe_extras.py` checks candidate program outputs, saved compiler artifacts where specified, and actual JES step/phase returns. Success for these cases is **OBSERVED**; a fully observed group returns **RC=3 / UNVERIFIED**, **not** accepted PASS. RC=1 denotes failure, RC=2 denotes invalid/preflight contract; do not convert them to success.

## Exact five-case selection and candidate oracles

| Manifest identity | Required module binding | Candidate source-derived output / artifact assertions |
| --- | --- | --- |
| `10-coroutines/compiler-probe` | none | `COROUTINE COMPILER PROBE COMPILED`; newly generated OCODE and INTCODE must token-match the preserved `evidence/compiler-probe.*` |
| `10-coroutines/frame-layout-probe` | none | `COROUTINE FRAME PROBE COMPILED`; OCODE and INTCODE token-match `evidence/frame-layout-probe.*` |
| `10-coroutines/fixed-stack-producer-consumer` | none | In order, `PRODUCER: 1`, `CONSUMER: 1`, ... through `PRODUCER: 5`, `CONSUMER: 5` |
| `10-coroutines/resumeco-chain` | `library/getvec-freevec.bcpl`, `library/coroutines.bcpl` | `A START`; `B START WITH 111`; `ROOT GOT 222`; `A RESUMED WITH 333`; `ROOT GOT 444`; `B RESUMED WITH 555`; `ROOT GOT 666` |
| `10-coroutines/create-delete-static-pool` | same two modules | `CREATED 2`, `LIST COUNT 3`, `A RETURNED 11`, `B RETURNED 21`, `DELETED A`, `LIST COUNT 2`, `DELETED B`, `LIST COUNT 1`, `C RETURNED 31`, `LIST COUNT 2`, `DELETED C`, `FINAL LIST COUNT 1` |

All five require expected interpreted `CODE=0`. The runner derives modules, compiler-artifact options and required JES phase counts from the manifests and does **not** accept arbitrary substitutions of source files or interpreter versions. These candidate traces were defined before this run; they are not independent MVS golden output until reviewed with actual evidence.

**Compiler-probe caveat:** the two compiler-only sources do **not** invoke `CHANGECO` in their `START` procedure. A green compiler-only result proves compiler-generated artifacts, **not** the correctness of switching.

## Operator procedure (requires explicit authorization for JES, not just Git checkout)

Run from the repository root in WSL, after verifying the intended Git revision and resident MVS availability. The following command is scoped to exactly the five coroutine contracts; **do not use `--all-candidates`**, which selects all 17 experimental/accepted MR10 development-probe contracts.

```bash
tools/mr10/run-dev-probes --check
tools/mr10/run-dev-probes --list \
    --case 10-coroutines/compiler-probe \
    --case 10-coroutines/frame-layout-probe \
    --case 10-coroutines/fixed-stack-producer-consumer \
    --case 10-coroutines/resumeco-chain \
    --case 10-coroutines/create-delete-static-pool
tools/mr10/run-dev-probes --run \
    --case 10-coroutines/compiler-probe \
    --case 10-coroutines/frame-layout-probe \
    --case 10-coroutines/fixed-stack-producer-consumer \
    --case 10-coroutines/resumeco-chain \
    --case 10-coroutines/create-delete-static-pool
```

This is the command recipe, **not an execution receipt**. The runner preflights all case contracts before submitting and runs in manifest order, **stopping on the first unexpected failure**. It creates a unique directory under `workarea/mr10-probes/`, writes `summary.json` incrementally, preserves each case's `.log` and `.jcl`, and captures `*-jes-summary.txt` and `*-jes-report.txt`. For the two compiler probes, it additionally preserves OCODE and INTCODE under case-specific artifact directories.

## Post-run independent review

1. Confirm the printed evidence directory, `summary.json` `git_head`, current ICINT assembler selection and `selected_cases` match the approved command and revision.
2. For each submitted probe, match `jes_job_id` to the JES report and exact submitted job name; verify all actual IFOX/IEWL/staging/COMP/CG/RUN steps and their RCs. The experimental JES checker requires zero step RCs and the expected number of completed interpreted phases.
3. Compare the complete final **program-visible** trace, including ordering and absence of unexpected records, rather than relying on `CODE=0` or a matching substring.
4. Examine freshly generated OCODE/INTCODE for the compiler/frame-layout probes against the checked-in evidence and source-level frame contract. Report disagreements, even when other cases succeed.
5. Investigate any `FAIL`, especially suspension/resumption, parent-chain changes, shared `G!9/G!10` state and storage reclamation. Preserve partially completed job evidence and do not rerun blindly or mark it accepted.
6. If all five are `OBSERVED`, submit their logs, summaries, extracted JES reports and artifacts for independent review. Only then decide whether to create accepted golden fixtures and change `UNVERIFIED` status in a separate review/commit.

The runner's reported `RC=3` for five `OBSERVED` cases is an **expected evidence classification**, not proof of native coroutine support or permission to mark CO.0 CLOSED. The existing `basic-coroutine` regression panel status is unchanged.

## Limits and next research after results

Neither a fully observed five-probe set nor compiler output settles original `KM10.COMAIN` (missing from the archive), historical native `COBASE` context switching, safe `RESUMECO` failure behavior, invalid-pointer handling in `DELETECO`, or independent native stack-checking. Those remain CO.0/CO.1 research gates. No runtime, historical-tape, source generator, regression manifest, BCPL global registry or installed MVS dataset is changed by this plan.
