# CO.0 — JOB 5231 CHANGECO continuation-divergence evidence review

**Milestone:** Implement coroutine support for native compiler  
**March:** CO.0 — Historical Research and Behavioral Contract (**IN PROGRESS**)  
**Source revision tested:** 6cfb8f86c2277b3e38c6c784891f2b79c7d9eb22  
**Date:** 11 November 2026  
**Classification:** Operator-reported INTERPRETED-MVS-TESTED observations; SOURCE-OBSERVED mechanism; INFERRED cause; UNVERIFIED instruction-level diagnosis. This experiment is **not ACCEPTED**.

## 1. Operator-supplied MVS execution evidence

The operator confirmed the stated Git revision, then staged new members MR10_TESTS(T10CDIV) and MR10_JCL(CO0TRACE) with dspal put jobs 5228 and 5229 (both RC=0). JES launcher 5230 submitted payload **JOB 5231**, CO0TRACE, 11 NOV 26 14.53.20–14.53.22.

The supplied job summary shows **14/14 JES steps RC=0000**: SSYNI, STRNI, SCGI, SBLIBI, SICLIB, COMPMAIN, SVOCMAIN, CGMAIN, SVINMAIN, COMPGET, CGGET, COMPCOR, CGCOR, RUN. Highest RC=0000; CPU 1.09 sec; SRB 0.14 sec; 185 cards; 940 SYSOUT records.

The operator also pasted a filtered printer report. Seven interpreted phases completed with **CODE=0**: COMPMAIN (500295 cycles), CGMAIN (264940), COMPGET (458262), CGGET (161267), COMPCOR (468966), CGCOR (148394), RUN (9830). Phase associations follow the committed JCL order; codes/cycle counts are from the filtered report, **not** an independently retrieved complete JES report.

## 2. Exact program records, in observed order

~~~text
NORMAL ENTER 10
ROOT A1 101
TRACE A1 G9=101 G10=175829
NORMALLEAF RESUMED 17
NORMAL CALC 118
ROOT A2 103
STAGED ENTER 20
STAGEDWAIT RETURNED 201
ROOT B1 201
TRACE B1 G9=201 G10=175059
STAGEDLEAF RESUMED 27
STAGED CALC 228
ROOT B2 203
~~~

**INTERPRETED-MVS-TESTED (operator-reported):** The ordinary path gives the predicted values. The staged path ultimately yields 201 and later computes 228, but **STAGEDWAIT RETURNED 201 appears before ROOT B1 201**. In a correct suspension, STAGEDWAIT must not execute post-CHANGECO work until B resumes. Its own post-call print, if reached upon resume with 27, would be **STAGEDWAIT RETURNED 27**, after ROOT B1 201 and before STAGEDLEAF RESUMED 27. That latter ordering is a specification expectation, **not observed execution**.

A zero JES return code and interpreted CODE=0 therefore do **not** prove correct suspend/resume semantics. The printed G!9/G!10 values are observed scratch-global contents; they alone do not identify saved frame/continuation addresses.

## 3. SOURCE-OBSERVED switching mechanism and INFERRED failure

[Reconstructed ICLIB](../../../mr10-kit-compiler/source/iclib.int) implements global-6 CHANGECO:

~~~text
6   LIP2 SG9 LIP1 SG10 LIP0 SIG7
    LIP3 SG7 LL498 LIG7 X1 X32
498 LIG9 JIG10 G6L6
~~~

The code saves outgoing call value P!2 in shared G!9 and outgoing return continuation P!1 in shared G!10. It stores outgoing caller P!0 in the current descriptor C!0, chooses incoming descriptor and restores **only its P** with X32; the trampoline installs A=G!9 and executes at **C=G!10 from the outgoing switch**. [Original ICINT](../../../richards-bcpltape/mr10/bcplkit/icint) and [reconstructed ICINT19](../../../mr10-kit-compiler/asm/icintv19.asm) define X32 as P,C := A,B. X4 returns through the current P!0/P!1 frame linkage.

**INFERRED from source and execution order:** On yielding from STAGEDWAIT, its nontrivial post-CHANGECO instructions can run with the incoming ROOT frame, causing STAGEDWAIT's print *during* the yield. Later, a return-style CALLCO continuation can resume STAGED's saved frame without replaying its own post-CHANGECO path. This explains the observations, but the actual **SVINMAIN generated instruction sequence and decoded P/C transitions were not supplied**. Do not claim this as an exact dynamic opcode trace.

This is a limitation of the **project-reconstructed interpreted MR10 ICLIB**. It is not evidence of an identical defect in missing historical KM10.COMAIN or future native System/370 code. The five previously accepted interpreted coroutine tests remain accepted for their *specific* successful output contracts, not arbitrary-continuation correctness.

## 4. Corrected candidate behavioral contract — requires design approval

1. At every suspension, preserve the outgoing coroutine's **own frame plus its own pending continuation**, together with whatever additional machine state the applicable ABI actually requires.
2. On transfer, restore the **incoming coroutine's saved frame and its saved continuation** together. Deliver the incoming value without executing the outgoing coroutine's pending post-switch code.
3. A suspended coroutine's next instruction, local state and nested call frames must resume only when that same coroutine is activated again. Side effects between a yield and its later resumption belong exclusively to the currently active coroutine.
4. First activation requires a defined startup trampoline and synthetic frame, because a new coroutine has no previously suspended continuation. This must be designed separately from ordinary resume.
5. Shared transfer scratch may be used transiently; it must not substitute for a persistent per-context continuation. Root/parent validation, stack bounds, error paths and registers remain subject to CO.1 review.

**Not selected:** An MR10 descriptor expansion, an interpreter patch, native S/370 register-save layout, global slots or object-module implementation. The present MR10 descriptor is three words with synthetic P=C+3; expanding it without redesign risks overwriting the synthetic frame. Preserve historical fidelity where evidenced and contemporary engineering judgment otherwise. No change to native ABI or closure of CO.0 is authorized by this candidate contract.

## 5. Missing evidence and next step

The committed [experiment JCL](../../../mr10-kit-compiler/jcl/co0-continuation-divergence.jcl) prints main compiler artifacts through SVOCMAIN (OCODE) and SVINMAIN (INTCODE) to JOB 5231 SYSOUT. **Those generated records were not available through GitHub and have not yet been independently examined.** For this particular printer report, the operator can inspect the read-only window near SVINMAIN:

~~~sh
set +e
set +u
set +o pipefail

tools/mvs/dump-report-for-job 5231 |
    sed -n '835,892p'
echo "Report inspection RC=$?"
~~~

The window is based on the operator's earlier filtered line numbers; check the actual step boundaries. Next: compare generated STAGEDWAIT, COWAIT and CALLCO post-call instructions; obtain a P/C transition trace if ambiguity remains; decide separately whether the historical MR10 reconstruction should be repaired. No new JES submission is needed just to inspect existing SYSOUT.

**Status:** CO.0 **IN PROGRESS**; CO.1–CO.5 **NOT STARTED**. The probe is experimental, no regression manifest/accepted golden is promoted, and no new MVS execution or dataset modification is recorded by this documentation.
