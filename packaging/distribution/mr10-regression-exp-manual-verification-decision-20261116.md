# MR10 12-case regression — `EXP:` output and manual MVS verification

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.4 — MR10 Kit Compiler Distribution and Verification (also gates TA.7)  
**Decision:** **Owner-approved, 16 November 2026**  
**State:** Contract recorded; `EXP:` implementation and MVS verification **not yet performed**

## Approved change to the release acceptance contract

The owner directed that each program in the **standard 12-case `MRREGRES` panel** print its expected results in the same MVS report as its actual results so a person can visually verify the panel. The owner then explicitly adopted the prefix **`EXP:`** for human-readable expected results.

This decision **supersedes the earlier requirement** in [release-payload-scope-decision-20261116.md](release-payload-scope-decision-20261116.md) for an *automatic MVS-resident* semantic PASS/FAIL checker and an automatic non-success job code on semantic mismatch. It does **not** remove MVS-only verification, complete 12-case coverage, or fail-on-discrepancy release acceptance. A human must examine and record an explicit PASS/FAIL for **each** case and refuse release acceptance if any result diverges.

The WSL development runner `tools/mr10/run-regression-panel` remains **automatic** and must continue checking the actual `RP:` lines against the retained `.expected` golden files and the interpreter's `CODE=` completion. `JES RC=0000` alone does not prove a case passed.

## Output contract

- `TEST:` identifies the regression case.
- `EXP:` prints each **literal, fixed, predetermined** expected semantic result for human inspection. Do not recompute expectations using the operation being tested.
- `RP:` prints **actual computed** semantic result records in the preexisting canonical format; do not rename or reformat their accepted values.
- `CODE=` is the interpreted completion reported by `ICINT19`. The standard 12-case panel currently requires interpreted code `0` for every case; verify the stored panel manifest before changing that expectation.

Example, illustrating two expected/actual records (the existing `RP:` lines are unmodified):

```text
TEST: Scalar assignments and vector load/store
EXP: SCALAR 17 42
EXP: VECTOR 5 10 15 20
RP: SCALAR 17 42
RP: VECTOR 5 10 15 20
```

`EXP:` lines must **not** contain the substring `RP:`: the WSL runner's `rp_records()` extracts any line containing `RP:`, compares that list with the golden `.expected` records, and separately checks interpreted `CODE=`. Thus the distinct `EXP:` prefix preserves its existing automated behavior **provided this rule is followed**.

Keep the tracked golden files as the development-side comparison oracle. Verify during TA.4 that all displayed literal `EXP:` records agree with their corresponding independently maintained `.expected` records; do not allow two drifting expectations.

## TA.4 and TA.7 acceptance

1. Update **only** the 12 standard regression BCPL test programs as needed to emit `EXP:` records, preserve existing actual `RP:` behavior and fixtures, and verify the source is valid for MR10.
2. Run the existing WSL automatic regression panel unchanged and obtain **12 PASS, 0 FAIL**, including output and `CODE=` checks. This is a *new required test*, not an already observed result after modification.
3. Run tape-installed `MRREGRES` on recipient MVS using only the independent MR10 payload and ordinary MVS facilities. Capture all 12 test reports, with test identity, expected and actual records, and interpreted completion code.
4. The reviewer checks each `EXP:` against the corresponding `RP:` records, checks the interpreted completion code, records explicit per-case PASS/FAIL, and signs/identifies the overall disposition. Missing, extra, reordered, unexpected, or otherwise mismatched records are FAIL. Review evidence must be retained with release acceptance records.
5. A semantic mismatch blocks acceptance whether or not JES reports nonzero RC. **No additional automatic MVS comparator or automatic semantic-mismatch RC is required** by this decision.

Historical MR10 diagnostic/probe suites remain separate and retain their actual accepted limitations. This decision does not change their results or mask failures.

## Implementation boundary

This is **documentation-only**. It does not alter the current 12 BCPL sources, `MRREGRES` JCL, golden `.expected` files, the WSL runner, or any MVS dataset; TA.4 implementation and verification remain outstanding.

## Superseding owner decision (23 November 2026)

The owner has removed per-case human PASS/FAIL choices and the final human SIGN requirement. The literal EXP: and computed RP: output contract, independently maintained golden expectations, all twelve MVS cases, interpreted CODE=0, and fail-on-discrepancy requirements remain mandatory. A read-only source-controlled verifier must recheck original sealed MVS evidence and record twelve automatic decisions. The prior human-signature portions of this historical decision are superseded, not silently erased. See the tape-artifact-release TA.4 automatic semantic acceptance decision.
