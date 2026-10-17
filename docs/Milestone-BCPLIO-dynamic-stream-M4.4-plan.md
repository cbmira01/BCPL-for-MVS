# BCPLIO dynamic streams — M4.4 compatibility verification

**Status: M4.4.0 SOURCE-ONLY PREFLIGHT ACCEPTED (2026-10-17); M4.4.1 complete candidate-panel execution owner-deferred; M4.4 OPEN.**
Date: 2026-10-17
Predecessor: M4.3 CLOSED (returned-control resource accounting).

## What M4.4 must prove

M4.4 is a complete DEVOBJ native compatibility checkpoint, not
another stream implementation. The candidate remains the separately
linked DEVOBJ BCPLM6 + BCPLIO combination. Preserve ordinary
BCPL G slots, generated code, BLIB, compiler smoke tests, special
streams, dynamic DD behavior, and previously accepted fixtures.

Last complete accepted candidate suite: 00..132, **132 PASS,
0 FAIL, 1 expected SKIP 083**. Individually focused regressions
133..145 also passed. The current corpus 00..145 includes 146
tests; the next complete checkpoint must show **145 PASS,
0 FAIL, 1 expected SKIP 083**. Do not substitute the focused
results for this complete-run evidence.

The owner explicitly deferred the full suite at M4.1. Nothing
in M4.3's focused results cancels that decision. This march
stages the procedure and read-only tests but does not submit the
entire panel without a separate owner decision.

## M4.4.0 — source and runner preflight

The committed source checker uses the existing native runner's
numbering and discovery routine and verifies all 146 test dirs,
candidate-only 124..145, expected SKIP 083, test-only M4.3 modes,
the synthetic fault fixtures, 141's GO RC0008 expectation, the
private source/link strategy, and the absence of test-only
accounting instrumentation in canonical BCPLIO.

Read-only audit:

~~~sh
cd ~/Source/Repos/BCPL-for-MVS
git pull --ff-only
python3 tools/checks/check-m44-compatibility.py
python3 tools/checks/check-bcplio-m43-account.py
tools/native/run-regression --check-numbering
~~~

An observed preflight PASS establishes only *readiness*,
not IFOX, link-edit, GO, JES or full compatibility acceptance.

## M4.4.0 acceptance — 2026-10-17

The operator pulled `7d718d1` and ran all three source-only
checks locally, without accessing MVS/JES:

```text
M4.4 source-only compatibility preflight: PASS
Corpus: 00..145, 146 numbered cases; no gaps
Expected full panel: 145 PASS / 0 FAIL / 1 SKIP (083)
Candidate-only cases: 124..145
Private test-only accounting: 139..145; canonical BCPLIO clean
Candidate environment: NOT CHECKED
MVS/JES execution: NOT PERFORMED
Full-panel compatibility: NOT VERIFIED
M4.3 post-IODRAIN terminal assertions: source check PASS
M4.3 native counter shim base setup: source check PASS
M4.3 counted BCPL source records: <=80 columns PASS
M4.3 combined counted failure/terminal source checks: PASS
M4.3 private source accounting checks: PASS
native regression numbering: OK
52->RG052C/RG052R; 53->RG053C/RG053R;
99->RG099C/RG099R; 100->RG100C/RG100R;
999->RG999C/RG999R
```

**M4.4.0 ACCEPTED** as a read-only source and runner
readiness gate. The four candidate environment values were
deliberately *not* checked by this invocation; that belongs
to the `--candidate` preflight preceding an approved panel.

**M4.4.1 remains unexecuted**. The owner-deferred full
DEVOBJ 00..145 panel must not be launched by default.
Its expected 145 PASS / 0 FAIL / 1 SKIP is **not**
a measured full-suite result. The final M4.4 closure and
M5 lossless physical DD attribution remain separate.

## M4.4.1 — complete candidate regression (owner-deferred)

When the owner explicitly releases the full-suite deferral,
execute against the already installed development candidate:

~~~sh
cd ~/Source/Repos/BCPL-for-MVS
BCPL_RUNTIME_PDS=1 \
BCPL_RUNTIME_LIBRARY=DEVOBJ \
BCPL_RUNTIME_CANDIDATE=1 \
BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6 \
python3 tools/checks/check-m44-compatibility.py --candidate && \
BCPL_RUNTIME_PDS=1 \
BCPL_RUNTIME_LIBRARY=DEVOBJ \
BCPL_RUNTIME_CANDIDATE=1 \
BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6 \
tools/native/run-regression 0 145 --show-output
~~~

Expected: 145 PASS, zero unexpected FAIL, one SKIP 083.
Case 141 has intentionally nonzero GO RC0008 (STOP(8)),
which is a passing controlled completion, not an abend.

Preserve the entire console summary and fresh per-case logs under
workarea/native-regression/logs/. Review all differences from the
previous accepted 00..132 panel. Do not call known abends a
clean PASS; investigate failures by their first compiler, assembler,
link-editor, GO, output fixture or JES diagnostic. Record commit,
candidate PDS members, actual job IDs and step RCs. Never promote
a runtime object as a side effect of regression testing.

## M4.4.2 — disposition and M5 boundary

M4.4 closes only after the fresh full panel is accepted against
the original baseline with any deviations explicitly reconciled.
No canonical runtime, object PDS or public G-vector modification
is required by this readiness stage.

M5 still owns lossless DD-specific JES/physical FB132 record
attribution. Combined printer report logical assertions alone
do not establish the source DD or retain significant trailing blanks.
M4.4 verification does not waive that separate acceptance gate.
