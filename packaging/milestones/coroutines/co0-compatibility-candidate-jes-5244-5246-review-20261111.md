# CO.0 — Compatibility candidate execution review, JOBS 5244 and 5246

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.0 — Historical Research and Behavioral Contract (IN PROGRESS)  
**Observation date:** 11 November 2026  
**Git revision checked by operator before staging:** `ae430d10386f7d5f857c901dbf9aff93365b903e`  
**Evidence class:** INTERPRETED-MVS-TESTED, **candidate only**; not a canonical runtime or native System/370 acceptance.

## Provenance and scope

The operator reported a successful `git pull --ff-only origin main`, exact HEAD match to the revision above, and `git diff --check HEAD^ HEAD` RC=0. The prepared decks were staged from Git using `dspal put`:

| Candidate | MVS JCL member | Staging JOB | Launcher JOB | Payload JOB |
| --- | --- | ---: | ---: | ---: |
| RESUMECO parent chain | `HERC02.BCPL.MR10KIT.JCL(CO0CHAIN)` | 5241 | 5243 | **5244** |
| CREATE/DELETE/reuse | `HERC02.BCPL.MR10KIT.JCL(CO0REUS)` | 5242 | 5245 | **5246** |

Source JCL: `mr10-kit-compiler/jcl/co0-resumeco-chain-candidate.jcl` and `mr10-kit-compiler/jcl/co0-create-delete-reuse-candidate.jcl`. Both decks explicitly use staged candidate `MR10_SOURCE(ICLIBC)` and `MR10_LIBRARY(COCAND)`, the unchanged `MR10_LIBRARY(GETVEC)`, and existing accepted tests `T10CHAIN` and `T10CRDEL`. Prior staging of ICLIBC/COCAND was reported as JOBS 5232/5233; this review does not independently verify resident member hashes. No canonical `ICLIB`, `COROUTIN`, accepted test, or golden replacement is evidenced.

The operator supplied complete isolated JES printer reports using `tools/mvs/dump-report-for-job 5244` and `5246`; both report-extraction commands returned RC=0. This review records the observed outputs and job numbers, not the full 899- and 924-record printer reports in Git.

## Execution evidence

Both jobs executed the same 14 steps successfully: SSYNI, STRNI, SCGI, SBLIBI, SICLIB, COMPMAIN, SVOCMAIN, CGMAIN, SVINMAIN, COMPGET, CGGET, COMPCOR, CGCOR, RUN. **28/28 step RC=0000** collectively.

| Interpreted phase | JOB 5244 cycles / CODE | JOB 5246 cycles / CODE |
| --- | --- | --- |
| COMPMAIN | 352917 / 0 | 433249 / 0 |
| CGMAIN | 152696 / 0 | 218095 / 0 |
| COMPGET | 458262 / 0 | 458262 / 0 |
| CGGET | 161267 / 0 | 161267 / 0 |
| COMPCOR | 494752 / 0 | 494752 / 0 |
| CGCOR | 155522 / 0 | 155522 / 0 |
| RUN | 4721 / 0 | 7202 / 0 |

**14/14 interpreted phases CODE=0** collectively.

### CO0CHAIN — JOB 5244

The final RUN output exactly matched the unchanged `mr10-kit-compiler/tests/10-coroutines/resumeco-chain.expected`:

```text
A START
B START WITH 111
ROOT GOT 222
A RESUMED WITH 333
ROOT GOT 444
B RESUMED WITH 555
ROOT GOT 666
```

**Result:** PASS for the existing RESUMECO parent-chain oracle.

### CO0REUS — JOB 5246

The final RUN output exactly matched the unchanged `mr10-kit-compiler/tests/10-coroutines/create-delete-static-pool.expected`:

```text
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
```

**Result:** PASS for the existing create/delete/reuse oracle. This demonstrates observed lifecycle and list-count behavior; it does not prove physical reuse of a particular storage address.

## Classification, limits and next gate

Both candidate tests satisfy the [preapproved execution plan](co0-compatibility-candidate-execution-plan-20261111.md): 14 successful JES steps each, seven successful interpreted phases each, and complete ordered golden output. This is **INTERPRETED-MVS-TESTED candidate evidence**, not native System/370 execution, a canonical `ICLIB`/`COROUTIN` promotion, or full historical compatibility.

The existing 12-case MR10 Regression Panel still needs an **explicit candidate-aware** execution path using `ICLIBC` and `COCAND` for affected programs. The default runner does not prove the candidate repair. Before any new JES submissions, review its candidate selection, staging provenance, output oracle and isolation. CO.0 also retains the behavioral-contract and historical-source unknowns listed in [research/design gates](coroutine-research-and-design-gates.md).

**Disposition:** CO.0 remains **IN PROGRESS**; CO.1–CO.5 remain **NOT STARTED**. No native runtime implementation or canonical object promotion is approved or claimed by this record.
