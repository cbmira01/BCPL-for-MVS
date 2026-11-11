# CO.0 — RESUMECO busy-target isolated repair candidate

**Project:** BCPL for MVS 3.8 Reconstruction  
**March:** CO.0 — Historical Research and Behavioral Contract (IN PROGRESS)  
**Status:** Isolated busy-target path INTERPRETED-MVS-TESTED (JOB 5285); positive path and full candidate panel pending  
**Date:** 11 November 2026

## Accepted pre-repair counterexample

Operator-reported JOB 5284 (BCRESUME), dated 12 November in MVS JES,
ran with canonical iclib.int and coroutines.bcpl under ICINT19.
All 14 JES steps had RC=0000 and the final interpreted CODE was 0.
The observed semantic records were:

    CO0 BUSY BEFORE -1
    CO0 BUSY TARGET -1
    CO0 BUSY RESULT -998
    CO0 BUSY PARENT KEPT 0
    CO0 BUSY PARENT CLEARED -1
    CO0 A GOT 777
    CO0 ROOT GOT 888
    CO0 DELETE A -1
    CO0 DELETE B -1

The original probe restored B's parent after measuring the defect, so
successful unwinding does not establish correct rejection behavior.
Classify this evidence as **INTERPRETED-MVS-TESTED**, not native evidence.
The original source and probe remain unchanged as the counterexample.

## Candidate design

The isolated library at
mr10-kit-compiler/library/coroutines-co0-busy-parent-candidate.bcpl
differs from canonical coroutines.bcpl solely by a two-statement reorder
in RESUMECO: the target occupancy test occurs before clearing CURRCO!1.
The successful transfer path preserves the canonical CHANGECO call and
parent propagation. This change does not validate invalid, null, freed,
stale or malformed descriptor pointers.

The independent candidate probe at
mr10-kit-compiler/tests/10-coroutines/resumeco-busy-parent-co0-repair-probe.bcpl
uses the same ROOT -> A -> B busy target scenario as JOB 5284 but does
not restore B's parent after the -998 return. The distinguishing changes are PARENT KEPT -1 and
PARENT CLEARED 0; both were observed in JOB 5285 under ICINT19.

This candidate is distinct from the older coroutines-co0-candidate.bcpl
and does not change it, canonical sources, regression identifiers, or
accepted goldens.


## JOB 5285 — isolated candidate negative-path verification

**Source HEAD:** `d9f317067232ec6e37ebf26e3b08197ff9e63e24`  
**MVS job:** 5285 (BCRESUME)  
**Operator evidence:** `workarea/co0-busy-parent-repair/20261111T235641Z.log`  
**Evidence:** INTERPRETED-MVS-TESTED for the stated busy-target scenario

The owner supplied the compile-and-run transcript after an exact-HEAD
fast-forward pull. The job exercised the separate candidate BCPL library
and the repair probe under ICINT19, with canonical ICLIB. Observed records:

    CO0 BUSY BEFORE -1
    CO0 BUSY TARGET -1
    CO0 BUSY RESULT -998
    CO0 BUSY PARENT KEPT -1
    CO0 BUSY PARENT CLEARED 0
    CO0 A GOT 777
    CO0 ROOT GOT 888
    CO0 DELETE A -1
    CO0 DELETE B -1

Interpreter completion: `EXECUTION CYCLES = 7098, CODE = 0`.
Candidate runner RC=0. All nine program records match the predicted
semantics. In contrast to JOB 5284, the candidate probe contains no
manual `CURRCO!1 := PARENT` restoration. The parent-chain preserved
by the candidate permitted the ordinary A/ROOT unwinding and deletion.

**Limits:** This operator excerpt does not include a `job-summary`
report, so the individual JOB 5285 JES step RCs and final JES status
are not yet independently reviewed. It is not native System/370 BCPL
evidence and does not prove correct positive RESUMECO parent transfer,
all invalid-target behaviors, or the full regression panel.

**Host checks:** On 11 November, three source-level tests of the
committed candidate passed in an isolated assistant workspace.
The fourth, generated-JCL integration test could not execute there
because the complete `compile-and-run-core.py` toolchain and compiler
inputs were unavailable. It must not be counted as PASS.

**Next gate:** Review JOB 5285 JES summary; independently execute
`10-coroutines/resumeco-chain.bcpl` with this repair candidate and
compare its complete output with the existing positive-path fixture.
Then execute all 12 unchanged MR10 Regression Panel cases with the
candidate module override. Preserve per-job RCs, interpreted CODE,
semantic output and runner outcomes; approve canonical promotion only
after explicit owner evidence review.

## Verification and promotion gates

Run host checks:

    python3 -B -m unittest discover -s tools/checks \
        -p 'test_co0_resumeco_busy_parent_repair.py' -v

Only with separately granted JES authorization, run the candidate
probe using canonical ICLIB and the isolated library:

    tools/mr10/compile-and-run --results \
        mr10-kit-compiler/asm/icintv19.asm \
        mr10-kit-compiler/tests/10-coroutines/resumeco-busy-parent-co0-repair-probe.bcpl \
        +mr10-kit-compiler/library/getvec-freevec.bcpl \
        +mr10-kit-compiler/library/coroutines-co0-busy-parent-candidate.bcpl

Review the complete semantic output, parent invariants, unwinding and
deletion, interpreted CODE, JES step RCs, runner RC and full report.
A zero JES RC or CODE alone does not establish correct semantics.

Then verify positive RESUMECO parent-chain behavior using the same
candidate and run the entire existing 12-case MR10 Regression Panel:

    tools/mr10/run-regression-panel --verbose \
        --module-override \
        mr10-kit-compiler/library/coroutines.bcpl=mr10-kit-compiler/library/coroutines-co0-busy-parent-candidate.bcpl

Retain the unchanged manifest and expected output files, capture all
per-job evidence, and seek a separate owner approval before promotion
to canonical coroutines.bcpl. CO.0 remains IN PROGRESS; CO.1–CO.5
remain NOT STARTED.
