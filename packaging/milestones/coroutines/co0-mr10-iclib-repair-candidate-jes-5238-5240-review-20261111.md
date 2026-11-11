# CO.0 — MR10 ICLIBC candidate MVS verification, JOBS 5238 and 5240

**Project:** BCPL for MVS 3.8 Reconstruction
**Milestone:** Implement coroutine support for native compiler
**March:** CO.0 — Historical Research and Behavioral Contract (IN PROGRESS)
**Git source revision tested:** 39b0e857fc725699dad849ddc0d26bf9fbc2d5ce
**Observation date:** 11 November 2026
**Evidence level:** Operator-supplied JES summary and filtered printer report;
MVS/ICINT19 observed, **candidate only**; not canonical acceptance.

## Source and MVS staging provenance

The operator fast-forwarded the local WSL checkout to the stated Git
HEAD, obtained `git diff --check HEAD^ HEAD` RC=0, and ran the four
offline instruction-model unit tests (4/4 PASS, runner RC=0).

Only candidate members were staged, using `dspal put` successfully:

| MVS member | Staging job | Source |
| --- | ---: | --- |
| `MR10_SOURCE(ICLIBC)` | 5232 | `source/iclib-co0-candidate.int` |
| `MR10_LIBRARY(COCAND)` | 5233 | `library/coroutines-co0-candidate.bcpl` |
| `MR10_TESTS(T10FIXC)` | 5234 | `tests/10-coroutines/fixed-stack-co0-candidate.bcpl` |
| `MR10_JCL(CO0CAND)` | 5235 | `jcl/co0-iclib-repair-candidate.jcl` |
| `MR10_JCL(CO0FSTK)` | 5236 | `jcl/co0-fixed-stack-candidate.jcl` |

Paths in this table are relative to `mr10-kit-compiler/`. Canonical
`SOURCE(ICLIB)`, `LIBRARY(COROUTIN)` and accepted test sources were
not replaced.

## JOB 5238 — CO0CAND

Launcher JOB 5237; payload JOB **5238**; 11 NOV 26,
17.12.31–17.12.33. **14/14 JES steps RC=0000**: SSYNI, STRNI,
SCGI, SBLIBI, SICLIB, COMPMAIN, SVOCMAIN, CGMAIN, SVINMAIN,
COMPGET, CGGET, COMPCOR, CGCOR and RUN.

Seven interpreted invocations were reported with CODE=0:

| Step | Cycles | CODE |
| --- | ---: | ---: |
| COMPMAIN | 500295 | 0 |
| CGMAIN | 264940 | 0 |
| COMPGET | 458262 | 0 |
| CGGET | 161267 | 0 |
| COMPCOR | 494752 | 0 |
| CGCOR | 155522 | 0 |
| RUN | 9841 | 0 |

The operator's filtered report preserves these final execution
records in order:

~~~text
NORMAL ENTER 10
ROOT A1 101
TRACE A1 G9=101 G10=175820
NORMALLEAF RESUMED 17
NORMAL CALC 118
ROOT A2 103
STAGED ENTER 20
ROOT B1 201
TRACE B1 G9=201 G10=175820
STAGEDWAIT RETURNED 27
STAGEDLEAF RESUMED 27
STAGED CALC 228
ROOT B2 203
~~~

**INTERPRETED-MVS-TESTED (operator-reported):** The corrected bridge
defers `STAGEDWAIT RETURNED 27` until after `ROOT B1 201`.
The original JOB 5231 had instead printed `STAGEDWAIT RETURNED 201`
before `ROOT B1 201`. All reported main program values and order
match the candidate oracle. The G!9/G!10 numbers are incidental
observed state, not fixed golden constants.

## JOB 5240 — CO0FSTK

Launcher JOB 5239; payload JOB **5240**; 11 NOV 26,
17.12.34–17.12.35. **10/10 JES steps RC=0000**: SSYNI,
STRNI, SCGI, SBLIBI, SICLIB, COMPMAIN, SVOCMAIN, CGMAIN,
SVINMAIN and RUN.

All three interpreted phases returned CODE=0: COMPMAIN
(338180 cycles), CGMAIN (144274), RUN (5442).

The operator's reported program output exactly matches the
previously accepted fixed-stack producer/consumer ten-line
golden from `tests/10-coroutines/fixed-stack-producer-consumer.expected`:

~~~text
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
~~~

## Outcome and remaining acceptance

**OBSERVED positive candidate verification:** JOB 5238 and JOB 5240
together comprise **24/24 zero-RC JES steps** and **10/10 interpreted
CODE=0** invocations. The supplied filtered outputs matched their
selected behavioral oracles. The full printer reports, saved OCODE/
INTCODE decks, and an automated candidate-suite result have not been
independently archived in Git; do not claim this is a canonical or
full-regression acceptance record.

**Next isolated compatibility checks:** Run the existing, unchanged
`T10CHAIN` (`RESUMECO` parent chain) and `T10CRDEL`
(`CREATECO`/`DELETECO`/reuse) through `ICLIBC` and `COCAND`.
New candidate JCL mappings `CO0CHAIN` and `CO0REUS` are only
prepared; no execution is claimed. Compare complete ordered outputs
against the existing goldens, seven interpreted phases each,
and all 14 JES step results for each job.

**Broader MR10 gate (not executed):** A full candidate-mode run of
the 12-case MR10 Regression Panel and other affected interpreted
workloads is required. The existing `tools/mr10/run-regression-panel`
uses its normal default compilation path and **does not by itself
substitute candidate ICLIBC**. Do not claim default-panel success
as evidence for the repaired interpreter-hosted runtime. Prepare
a separately reviewable candidate selection mechanism or equivalent
isolated JCL before requesting that JES run.

The previously accepted five MR10 coroutine probes retain their
original identities and goldens; their current canonical acceptance
does not automatically promote this candidate.

**Disposition:** CO.0 IN PROGRESS. CO.1–CO.5 NOT STARTED.
No modification to canonical ICLIB/COROUTIN, interpreter, native
runtime, installed accepted objects, or regression manifest.
