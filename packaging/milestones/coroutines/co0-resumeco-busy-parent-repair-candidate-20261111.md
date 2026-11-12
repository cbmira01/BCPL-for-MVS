# CO.0 — RESUMECO busy-target isolated repair candidate

**Project:** BCPL for MVS 3.8 Reconstruction  
**March:** CO.0 — Historical Research and Behavioral Contract (IN PROGRESS)  
**Status:** JOBS 5284–5298 reviewed; canonical source promoted; post-promotion MVS run pending  
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
differed from pre-promotion canonical coroutines.bcpl solely by a reorder
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

## Positive path and complete panel — JOBS 5286–5298

All evidence is **INTERPRETED-MVS-TESTED**, not native System/370
BCPL evidence. The operator verified Git HEAD
`de794d494e7776ef37941794aa7a688400656616` before execution.
Local operator evidence:

- `workarea/co0-busy-parent-repair/20261112T000341Z-positive.log`
- `workarea/co0-busy-parent-repair/20261112T000402Z-regression.log`
- `workarea/co0-busy-parent-repair/jes-5286-5298.log`

**JOB 5286** executed the unchanged `resumeco-chain.bcpl` using the
isolated busy-parent candidate and canonical ICLIB. All seven expected
positive-chain program records matched:

    A START
    B START WITH 111
    ROOT GOT 222
    A RESUMED WITH 333
    ROOT GOT 444
    B RESUMED WITH 555
    ROOT GOT 666

Final interpreted CODE=0, runner RC=0, 14/14 JES steps RC=0000,
and JOB RESULT: SUCCESS.

**JOBS 5287–5298** ran the complete unchanged 12-case MR10 Regression
Panel with the isolated library selected through `--module-override`.
Every existing expected program record matched and all final interpreted
executions returned CODE=0. The panel recorded **12 PASS / 0 FAIL / 12
TOTAL, RC=0**. The per-JOB JES summaries establish **142/142** steps
RC=0000, all JOB RESULT: SUCCESS. JOB 5298 specifically exercised the
candidate, matching `RP: COROUTINE 77 1`.

Combined, JOBS 5284–5298 have **184/184** zero-RC JES steps:
14 each for 5284–5286 and 142 across JOBS 5287–5298.
JOB 5284 is the original *defect counterexample*, not evidence that
its pre-repair state mutation was acceptable.

## Owner-approved canonical source promotion

The owner explicitly approved promoting the isolated `RESUMECO`
correction after reviewing the negative, positive, and regression
evidence. The canonical Git source at
`mr10-kit-compiler/library/coroutines.bcpl` now checks target
occupancy before clearing `CURRCO!1`; all other instructions and
public interfaces are unchanged. The isolated candidate, original
counterexample, regression manifest, and expected outputs remain
unchanged for provenance.

**This is a Git-source promotion only.** It does not modify resident
MVS datasets or certify native System/370 coroutine execution.
A fresh **canonical-default** MR10 regression without
`--module-override` is still required to confirm the promoted default
under MVS before recording post-promotion acceptance.

CO.0 remains IN PROGRESS; CO.1–CO.5 remain NOT STARTED.
