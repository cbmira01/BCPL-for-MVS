# Clean-room reconstruction batch-population improvement — acceptance and closure

**Project:** BCPL for MVS 3.8 Reconstruction
**Record date:** 9 November 2026 (US Eastern; evidence directory dates may be 10 November UTC)
**Disposition:** **CLOSED — owner-directed completion of the clean-room reconstruction performance-improvement work.**
**Scope:** The simple `tools/reconstruction/rebuild-from-source` driver, its explicit `--batch-populate` mode and corresponding independent regression evidence. This is an engineering-workflow closure, **not** a new milestone/march, a tag, or a release.

## Source and execution authority

- GitHub `main` provides the source and documentation authority.
- **Batch reconstruction source revision:** `73c7d37585ed974881d655b4313b9289774dc0e5` (the operator's HEAD guard for the rebuild).
- **Full regression source revision:** `268600559e58defb410b7bb7719a66bc8e3c9a85` (HEAD guard for the passing campaign).
- The intervening commit `268600559e58` repaired an active QSAM sixteen-DCB JCL helper path, added an offline dependency check and documented a future helper-extraction proposal. It did not alter the native BCPLQSAM implementation, the interpreter-hosted compiler, or the MVS installed object modules.
- The operator ran the commands against the existing Hercules/TK5 MVS 3.8J system. JES, IFOX, IEWL, IEBGENER, IEBCOMPR and actual MVS execution remain the target-system verification authority.

## Accepted bounded MVS batch-population evidence

The separate [DSPAL batch-population acceptance record](dspal-batch-acceptance-plan-20261109.md) reports controlled MVS jobs:

| Managed PDS | JES jobs | Scope and result |
| --- | --- | --- |
| `DIST_DOCS` | 3136 | 7 IEBGENER steps RC=0000; 7/7 canonical read-back texts matched |
| `EXT_SOURCE` | 3145 | 3 steps RC=0000; 3/3 canonical texts matched |
| `MR10_TESTS` | 3150, 3151 | 60+1 steps RC=0000; 61/61 canonical texts matched, **qualified** for four terminal blank-record counts |

**Total:** 71/71 recovered canonical member texts. The four `MR10_TESTS`
members `T01ECHO`, `T01TEXT`, `T04MOD1`, and `T04MOD2` remain qualified:
the read-back normalizer does not prove exact trailing blank-record counts or
raw EBCDIC byte identity. Neither the batch verifications nor this closure
silently removes that limitation.

## Successful full clean-room reconstruction

The operator ran the simple driver in explicitly authorized unattended
batch mode:

```sh
tools/reconstruction/rebuild-from-source --unattended --batch-populate
```

The shell-level source guard verified `73c7d37585ed974881d655b4313b9289774dc0e5`
before execution. The operator supplied the following completion excerpt:

```text
HERC02.BCPL.EXT.OBJ:
    BCPLDEMO
    BCPLQSAM
    BCPLTIME
Command RC=0; elapsed=12s
Guide Step 9 elapsed=82s; RC=0
REBUILD COMMANDS COMPLETED. Save build evidence separately.
No regression acceptance claimed; run regression workflow separately.
Reconstruction RC=0
Elapsed seconds=766
Elapsed time=12 minutes 46 seconds
```

**Measured:** 766 seconds, **12m 46s**, driver RC=0, final Step 9 RC=0,
and expected optional System Extension object members in `EXT_OBJ`.
The controller executes guide Steps 0, 1, 2, 3, 5, 6, 7, 8, 9; it does
not perform full regressions or the manual Step 10 evidence archive.

**Comparison:** The earlier non-batched rebuild was described as approximately
**50 minutes**. Against that approximate baseline, the 12m46s run
represents about **37m14s less** (roughly **74.5% reduction**, **3.9×
faster**). Because 50 minutes is an estimate and host conditions may
differ, these are indicative comparisons, not precise controlled
paired-run benchmarks.

**Evidence limitation:** The supplied final excerpt and driver RC
do not themselves provide the complete raw JES transcript, all
intermediate IFOX severities or every IEBCOMPR receipt for this run.
Do not assert an independent line-by-line audit of all payload jobs.
The driver continues to require successful commands and its existing
JES-summary checks; independent full native regression followed.

## First regression attempt: distinct harness failure, preserved as FAIL

An earlier full six-suite campaign following the non-batched rebuild
at source revision `b41426d8a23fda67df59e3a2f3f52b8929f75793`
reported **two FAILs**, cases **166 `qsam-sixteen-finish`** and
**167 `qsam-sixteen-stop`**, while the other selected tests passed.
The run remains a failed run; it is not retrospectively recast as PASS.

The focused rerun at `73c7d37585ed974881d655b4313b9289774dc0e5`
again failed both because its active Q.1 native JCL generator imported
a missing `bootstrap-toolchain/probes/q0-qsam-dasd-probes/make-jobs.py`.
Both Cambridge compiler jobs returned RC=0 before the missing-file error.
This was a host-side path dependency, **not observed native GO failure**.

Commit `268600559e58defb410b7bb7719a66bc8e3c9a85` repaired the
path to the preserved helper under
`packaging/archive/qsam/probes/q0-qsam-dasd-probes/make-jobs.py`.
The operator then verified **2/2 offline dependency tests PASS** and
the Q.1 synthetic `Q16FIN`, `Q16STP`, `Q1NEG`, `Q1OUT`
deck checks (each RC=0). A separate real-MVS focused run of
166 and 167 returned **2 PASS, 0 FAIL**, native runner RC=0 for each.

Focused run evidence directory:
`workarea/test-suites/20261110T015754Z-70238-bcplqsam-installed-r5-t1-nadsffc1/`.

## Full independent regression acceptance

After the fix, the operator ran `tools/tests/run-project-regressions` using:

- All six independently named suites: `mr10`, `mr10-probes`, `bootstrap`, `runtime-extensions`, `bcpltime`, `bcplqsam`.
- Native profile `installed-r5-t1`, explicit `--allow-device`, and `--progress`.
- GitHub HEAD `268600559e58defb410b7bb7719a66bc8e3c9a85`.

| Suite | PASS | FAIL | SKIP | Total |
| --- | ---: | ---: | ---: | ---: |
| MR10 Regression Panel | 12 | 0 | 0 | 12 |
| Accepted MR10 Development Probes | 6 | 0 | 0 | 6 |
| Bootstrap | 145 | 0 | 1 | 146 |
| Runtime Extensions | 13 | 0 | 0 | 13 |
| BCPLTIME | 4 | 0 | 0 | 4 |
| BCPLQSAM | 14 | 0 | 0 | 14 |
| **Total** | **194** | **0** | **1** | **195** |

The **one SKIP is expected native case 083**, requiring historical
source-only instrumentation; no BLOCKED cases were reported.
Both previously failing QSAM cases **166/167** passed; the JES
printer/punch cases **175/176** also passed with explicit device
authorization. The provided coordinator output concluded:

```text
PROJECT REGRESSION RESULT: PASS
Project regression RC=0
Total runtime: 73 minutes 57 seconds
```

**Independent regression duration:** 4,437 seconds (73m57s).
**Evidence:** `workarea/project-regressions/20261110T020053Z-70445-vk1narmi/summary.json` and the accompanying suite logs. These paths are **operator-local, ignored workarea evidence**, not Git-tracked copies. The console summary is owner-reported; no separate raw JES or per-test files were copied into GitHub as part of this record.

**Scope qualifier:** The installed R.5/T.1 profile uses installed
BCPLDEMO and BCPLTIME; native BCPLQSAM tests 163–176 continue to
select BCPLQSAM **from source**. This panel does not certify an
independent installed-BCPLQSAM object-linkage acceptance job.

## Owner-directed close-out and remaining boundaries

The batch-population clean-room **performance improvement is CLOSED**
with a successful destructive rebuild, separate passing full six-suite
regression and measured elapsed time. The original default
(one IEBGENER job/member) remains available; `--batch-populate` remains
**explicit opt-in**. No behavior changes, new MVS jobs, automatic
promotion, release publication, or baseline tag are implied.

This does **not** close the separate guarded `tools/reconstruction/run`
integration plan, declare every historical QSAM exception proven,
accept the future native Cambridge compiler, or declare a complete
distribution-tape release. The latter workflows retain their own
owners, gates and source records.

Future efficiency work moves to the separate
[regression runner performance analysis](../operations/maintenance/regression-runner-performance-analysis-20261109.md).
Preserve operator-local evidence outside disposable `workarea/`
before any later reconstruction cleanup if raw logs are required.
