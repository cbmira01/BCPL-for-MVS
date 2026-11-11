# CO.0 — RESUMECO busy-target isolated repair candidate

**Project:** BCPL for MVS 3.8 Reconstruction  
**March:** CO.0 — Historical Research and Behavioral Contract (IN PROGRESS)  
**Status:** Candidate source and offline checks; MVS verification pending  
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
not restore B's parent after the -998 return. The predicted differences
are PARENT KEPT -1 and PARENT CLEARED 0. These are **unverified** until
their exact output and ordinary unwinding are observed under ICINT19.

This candidate is distinct from the older coroutines-co0-candidate.bcpl
and does not change it, canonical sources, regression identifiers, or
accepted goldens.

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
