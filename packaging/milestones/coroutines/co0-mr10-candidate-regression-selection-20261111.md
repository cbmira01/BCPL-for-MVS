# CO.0 — MR10 candidate-aware regression selection (host tooling)

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.0 — Historical Research and Behavioral Contract (IN PROGRESS)  
**Date:** 11 November 2026  
**Status:** Source change prepared; independent host unit execution and MVS candidate regression pending.

## Purpose

Select the isolated CO.0 `ICLIBC` / `COCAND` implementation for the existing 12-case MR10 Regression Panel, without replacing canonical `ICLIB` or `COROUTIN`, editing the regression manifest, or changing accepted goldens.

- `tools/mr10/compile-and-run --iclib PATH` selects an alternate ASCII INTCODE `ICLIB` file for staging into the generated job's `&&ICLIB`. All compilation, code-generation and RUN steps therefore consume the same selected runtime.
- `tools/mr10/run-regression-panel --iclib PATH` forwards that image to every selected test.
- `--module-override FROM=TO` substitutes an **exact** manifest `+MODULE` path when constructing the invocation. It checks the replacement file exists, that FROM occurs in the selected tests, and rejects invalid or duplicate overrides. Unrelated modules and test identities remain unchanged.
- Without either override, existing canonical behavior remains the default. Neither flag modifies source files or MVS datasets merely by being parsed; **running** the panel still creates and submits JES jobs.

## Proposed CO.0 candidate execution (requires separate JES authorization)

```bash
tools/mr10/run-regression-panel \
  --iclib mr10-kit-compiler/source/iclib-co0-candidate.int \
  --module-override mr10-kit-compiler/library/coroutines.bcpl=mr10-kit-compiler/library/coroutines-co0-candidate.bcpl \
  --verbose
```

Do not run the above until authorized. The candidate input paths are tracked Git files. The panel still consumes its original `mr10-kit-compiler/tests/00-regression-panel/manifest.tsv`, including its 12 test cases and unchanged expected output files.

## Host-only verification before JES

```bash
python3 -B -m unittest discover \
  -s tools/checks -p 'test_mr10_candidate_selection.py' -v

python3 -B -m py_compile \
  tools/mr10/compile-and-run-core.py \
  tools/mr10/run-regression-panel \
  tools/checks/test_mr10_candidate_selection.py
```

The host tests check exact-path mapping, rejection of missing/mismatched overrides, unchanged defaults, forwarding of both overrides, and generated JCL inclusion of the selected ICLIB image. They **mock the job launcher** and never submit to the JES reader. Actual 12-case candidate MVS behavior, source revision and resident synchronization remain independent verification requirements.

**Disposition:** CO.0 IN PROGRESS; CO.1–CO.5 NOT STARTED. No promotion of reconstructed MR10 runtime or native System/370 coroutine implementation is implied.
