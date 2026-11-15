# CO.4 — Safe negative-path candidate: owner-reported native PASS

**Project:** BCPL for MVS 3.8 Reconstruction  
**March:** CO.4 — Robustness and Edge-Case Verification (**IN PROGRESS**)  
**Tested source revision:** `cc3b2c6c2c96d77d7b12be1779ae005b79c8ebdf`  
**Evidence class:** OWNER-REPORTED NATIVE-MVS-TESTED (qualified)  
**Local observation:** 14 November 2026, after 20:00 EST (15 November UTC)

The owner executed the committed `tools/coroutines/run-co4-safe-negative.py
--run` after a guarded fast-forward to the exact expected revision.
Console transcript:

```text
CO.4 safe negative PASS
CO.4 native execution RC=0
CO.4 evidence: /home/calvin/Source/Repos/BCPL-for-MVS/workarea/co4-safe-negative/20261115T020420Z-l_m4a5gu
CO.4 safe negative RC=0
```

The strict runner requires two independently compiled Cambridge source
modules, four IFOX RC=0000 steps, IEWL RC=0000, GO RC=0000,
JES SUCCESS/highest RC=0000, and exactly sixteen ordered `CO4SAFE`
application records. The observed PASS/RC=0 establishes the
**owner-reported strict-runner outcome**, not independently reviewed
JES evidence. Raw listings, specific compiler/native JES JOB numbers,
`result.json` and `co4-result.json` remain in the local evidence
path; their contents have not been supplied to this conversation.

This result validates recoverable size, root, capacity and deletion
refusals plus survivor continuity at the source revision. It does not
prove exact allocation-accounting rollback, stack overflow policy,
raw live `STKLIM`/`APLIMIT` checks, stale/freed descriptor safety,
or a general failure-recovery contract. No CO.4 closure or production
promotion follows automatically. CO.5 remains NOT STARTED.
