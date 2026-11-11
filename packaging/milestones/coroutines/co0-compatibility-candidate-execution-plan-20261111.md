# CO.0 — MR10 ICLIBC compatibility candidate execution plan

**Project:** BCPL for MVS 3.8 Reconstruction
**Milestone:** Implement coroutine support for native compiler
**March:** CO.0 — Historical Research and Behavioral Contract (IN PROGRESS)
**Recorded:** 11 November 2026
**Git revision containing the two prepared decks:** `bb836706f69f78bd6e8d17fb5c0308895224fbb5`
**Status:** Owner-authorized **staging and JES submission**; no execution
result recorded by this document.

## Scope of operator authorization

The owner instructed: "Stage, commit, submit" after review of the
positive JOB 5238 and JOB 5240 candidate results and the offline
4/4 unit-test and whitespace checks at `bb836706`.

This authorizes staging and submitting only the isolated compatibility
candidate jobs below. It is **not** authorization to replace
`MR10_SOURCE(ICLIB)`, `MR10_LIBRARY(COROUTIN)`, accepted test sources
or goldens, promote canonical runtime changes, or close CO.0.

| JCL alias | Git deck | Existing test |
| --- | --- | --- |
| `MR10_JCL(CO0CHAIN)` | `mr10-kit-compiler/jcl/co0-resumeco-chain-candidate.jcl` | `MR10_TESTS(T10CHAIN)` |
| `MR10_JCL(CO0REUS)` | `mr10-kit-compiler/jcl/co0-create-delete-reuse-candidate.jcl` | `MR10_TESTS(T10CRDEL)` |

Both decks use `MR10_SOURCE(ICLIBC)`,
`MR10_LIBRARY(COCAND)` and `MR10_LIBRARY(GETVEC)`, plus established
MR10 compiler/interpreter inputs. `ICLIBC` and `COCAND` were staged
as jobs 5232 and 5233 for the prior positive candidate executions;
the operator must establish that required existing members remain
available and current before trusting new results.

## Required MVS evidence and expected oracles

Each candidate JCL has 14 JES steps (SSYNI, STRNI, SCGI, SBLIBI,
SICLIB, COMPMAIN, SVOCMAIN, CGMAIN, SVINMAIN, COMPGET, CGGET,
COMPCOR, CGCOR and RUN). Require all 14 steps RC=0000, seven
interpreted `EXECUTION CYCLES ..., CODE = 0` records (COMPMAIN,
CGMAIN, COMPGET, CGGET, COMPCOR, CGCOR, RUN), and the ordered final
program output. Save or reference the payload JOB IDs; launcher IDs
must not be substituted for payload execution evidence.

### CO0CHAIN — existing RESUMECO golden

~~~text
A START
B START WITH 111
ROOT GOT 222
A RESUMED WITH 333
ROOT GOT 444
B RESUMED WITH 555
ROOT GOT 666
~~~

Source-of-truth golden:
`mr10-kit-compiler/tests/10-coroutines/resumeco-chain.expected`.

### CO0REUS — existing create/delete/reuse golden

~~~text
CREATED 2
LIST COUNT 3
A RETURNED 11
B RETURNED 21
DELETED A
LIST COUNT 2
DELETED B
LIST COUNT 1
C RETURNED 31
LIST COUNT 2
DELETED C
FINAL LIST COUNT 1
~~~

Source-of-truth golden:
`mr10-kit-compiler/tests/10-coroutines/create-delete-static-pool.expected`.

## Result classification and next gate

Until the operator returns JES summaries and full relevant output,
both jobs remain **UNEXECUTED / UNVERIFIED** in this record.
JES submission acknowledgement alone is not acceptance.

If each matches the established golden with all seven interpreted
phases CODE=0 and complete successful JES steps, record the
`INTERPRETED-MVS-TESTED` candidate evidence separately. The broader
candidate-aware MR10 Regression Panel remains a distinct gate:
running the default panel without `ICLIBC` cannot verify this repair.

For preceding evidence see
[JOB 5238/5240 review](co0-mr10-iclib-repair-candidate-jes-5238-5240-review-20261111.md)
and the [repair decision](co0-mr10-iclib-repair-design-decision-20261111.md).

**CO.0 remains IN PROGRESS; CO.1–CO.5 NOT STARTED.**
