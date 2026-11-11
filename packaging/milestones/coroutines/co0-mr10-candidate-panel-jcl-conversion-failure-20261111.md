# CO.0 — MR10 candidate panel JCL-conversion failure and staging correction

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.0 — Historical Research and Behavioral Contract (IN PROGRESS)  
**Date:** 11 November 2026  
**Status:** Root cause confirmed from operator-provided JES reports; source-level correction committed, host test execution and repeat MVS run pending.

## Failed first candidate-aware panel

Git HEAD `465f0a51080903fce999f09f9f671c2a12ce3cd7` was confirmed on the operator's WSL checkout. The four candidate-selection host unit tests passed (4/4, RC=0). The 12-case `tools/mr10/run-regression-panel` selected `source/iclib-co0-candidate.int` and replaced only the coroutine-module path with `library/coroutines-co0-candidate.bcpl`, as intended.

The runner submitted payload JOBS **5247–5258**, but every job had **JCL ERROR, no executed steps**. The panel reported 0 PASS / 12 FAIL, RC=1, because there were zero `INTCODE SYSTEM ENTERED` records in every report. These are **JCL-preparation failures**, not observed BCPL execution failures.

The operator's complete JOB 5247 (BCSCALAR) and JOB 5258 (BCBASICC) reports both showed `IEF452I ... JOB NOT RUN - JCL ERROR`. In each case the JES converter reported:

```text
42 IEF605I UNIDENTIFIED OPERATION FIELD
43 IEF605I UNIDENTIFIED OPERATION FIELD
44 IEF605I UNIDENTIFIED OPERATION FIELD
45 IEF605I UNIDENTIFIED OPERATION FIELD
```

Statements 42–45 are the four leading `//` comment records copied verbatim from the candidate `ICLIB` source into a `//SYSUT1 DD *` in-stream JCL data section. JES interpreted these column-one `//` lines as JCL rather than as IEBGENER data, thereby rejecting the job before IFOX, IEWL or ICINT could run.

## Host source correction

`tools/mr10/compile-and-run-core.py` now has a separate `read_intcode_records` staging helper. It first validates the original ASCII input record widths and delimiter constraints, then removes standalone `//` INTCODE comment lines before creating the `DD *` body. Non-comment executable records retain their original contents and order, and a comment-only input is rejected. The helper is used for the five staged INTCODE inputs SYNI, TRNI, CGI, BLIBI, and ICLIB, **not for BCPL/SYSIN sources**.

The original candidate and canonical files remain unchanged; no MVS member or accepted object was overwritten.

The host-only tests in `tools/checks/test_mr10_candidate_selection.py` were extended to verify comment filtering, executable record preservation, the actual tracked candidate source, and the generated ICLIB staging section. They do not submit JES jobs.

## Next bounded gate

First fast-forward the WSL checkout and run host unit tests, syntax inspection and whitespace checks. After those checks pass, submit **one** candidate-aware panel case (`--test scalar-vector`) to confirm JES conversion and the compiler/ICINT execution path. Only if its JES result, interpreted completion codes and golden output pass should the complete 12-case candidate panel be rerun under separately confirmed operator authorization.

Do not classify the initial 0/12 JCL-error run as a candidate semantic regression. All earlier positive candidate observations remain scoped to their recorded jobs. **CO.0 IN PROGRESS; CO.1–CO.5 NOT STARTED.**
