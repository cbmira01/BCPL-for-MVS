# CO.0 — Candidate-aware MR10 Regression Panel: 12/12 PASS

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.0 — Historical Research and Behavioral Contract (IN PROGRESS)  
**Date:** 11 November 2026  
**Source revision tested:** `a7ba961a26e1e30ecef8745c6948bc1301c08a19` (operator report follows Git `main` correction; full WSL HEAD output for this particular panel was not separately supplied)  
**Evidence class:** **INTERPRETED-MVS-TESTED**, operator-supplied regression runner result, candidate only.

## Invocation

The operator executed the unchanged 12-case `mr10-kit-compiler/tests/00-regression-panel/manifest.tsv` with:

```bash
tools/mr10/run-regression-panel \
    --iclib mr10-kit-compiler/source/iclib-co0-candidate.int \
    --module-override mr10-kit-compiler/library/coroutines.bcpl=mr10-kit-compiler/library/coroutines-co0-candidate.bcpl
```

The runner reported `ICINT: mr10-kit-compiler/asm/icintv19.asm`, `Tests: 12`, the resolved candidate `ICLIB` host path and the exact `coroutines.bcpl` to `coroutines-co0-candidate.bcpl` module replacement. Existing test names, manifest and expected-output files were not changed.

## Per-case outcome

| Category | Existing case | Result |
| --- | --- | --- |
| data-movement | scalar-vector | PASS |
| data-movement | bytes | PASS |
| calculation | integer-arithmetic | PASS |
| control | branches-loops | PASS |
| calls | nested-recursion | PASS |
| modules | separate-module | PASS |
| standard-library | basic-library | PASS |
| standard-library | library-scalars | PASS |
| standard-library | library-strings | PASS |
| standard-library | library-line-io | PASS |
| storage | getvec-reuse | PASS |
| coroutines | basic-coroutine | PASS |

**Runner totals:** `PASS 12`, `FAIL 0`, `TOTAL 12`, **RC=0**.

The earlier single-case pilot `data-movement/scalar-vector` was separately observed at payload **JOB 5259**, with `CODE=0`, matching `RP:` golden output, and runner RC=0. The subsequent 12-case full panel passed as shown above, but its individual payload JOB numbers, step-by-step JES return codes and complete printer reports were **not provided** in the panel output. Do not infer job numbers or assert independent 12-job JES/IFOX/IEWL evidence.

## Relationship to the failed first panel

The prior candidate-aware attempt on JOBS **5247–5258** produced 12 **JCL ERROR** results with no executed steps. Those four `IEF605I` converter errors were caused by `//` comments in candidate `ICLIB` being copied to `DD *` data. The tracked `read_intcode_records()` correction excludes standalone INTCODE comments from the generated deck. The passing JOB 5259 pilot and subsequent 12/12 panel establish that this earlier common JCL-conversion blocker no longer prevents the tested execution path; they do not erase the prior failed evidence.

## Interpretation and remaining gates

Together with candidate JOBS **5238**, **5240**, **5244** and **5246**, the 12/12 panel supports that the repaired, separately named MR10 `ICLIBC` and `COCAND` preserve the observed test oracles, including the continuation-divergence correction and previously accepted parent-chain/create-delete behaviors.

**This is candidate interpreted regression evidence.** It is not native System/370 coroutine execution, evidence of all negative/error cases, proof of storage-address reuse, or approval to replace canonical `mr10-kit-compiler/source/iclib.int` and `mr10-kit-compiler/library/coroutines.bcpl`. The original JOB 5231 divergence remains preserved. Explicit promotion review, canonical-source coordination, post-promotion tests and the outstanding CO.0 behavior/unknown ledger are still distinct gates.

**Disposition:** CO.0 remains **IN PROGRESS**; CO.1–CO.5 remain **NOT STARTED**.
