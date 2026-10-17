# BCPLIO dynamic streams — M4.4 compatibility verification

**Status: M4.4 CLOSED (2026-10-17). Full DEVOBJ(BCPLM6) 00..145: 145 PASS / 0 FAIL / 1 expected SKIP 083; 145/145 saved-log audit PASS with BCPLM6/D6 GO-RC expectations reconciled. M5 OPEN.**
Date: 2026-10-17
Predecessor: M4.3 CLOSED (returned-control resource accounting).

## M4.4 formal closure — ACCEPTED 2026-10-17

**M4.4.0 (preflight), M4.4.1 (full panel), and M4.4.2
(saved-log reconciliation) are ACCEPTED.** This closes
the M4 failure/lifecycle compatibility march for
the independently linked **DEVOBJ(BCPLM6 + BCPLIO)**
candidate. No production or development PDS object
installation, runtime source modification, BCPL global
ABI change, or object promotion was required.

### Execution and saved-log evidence

The operator pulled through `a572e77` and ran the
full 00..145 native regression panel after the
candidate-environment preflight passed:
**145 PASS / 0 FAIL / 1 expected SKIP 083, TOTAL 146**.
The individually accepted 133..145 tests all passed
again in this same complete sweep. The user then
pulled through `48c6012` and ran:

```sh
bash -n native-compiler/regression/run-test.sh
python3 tools/checks/check-m44-compatibility.py
python3 tools/checks/check-m44-full-panel-logs.py
```

Bash syntax check and compatibility source preflight
passed. The corrected saved-log audit reported:

```text
M4.4 existing regression logs: 145/145
Expected runner skip: 083 (source-only)
Compile-only: 048 (no GO or LKED)
GO-RC profile: DEVOBJ BCPLM6/D6; 052 and 093 expected RC0000
GO RC distribution: 0000=139, 0008=3, 0012=1, 0100=1
Log mtime UTC: 2026-10-17T14:00:32.266583+00:00 .. 2026-10-17T14:10:26.972715+00:00
Saved JES job/step manifest: workarea/native-regression/m44-00-145-jobs.tsv
M4.4 detailed log audit: PASS (no detected known-defect/abend exceptions)
```

Exactly **144 GO executions**, **one intentional
compile-only case 048**, and **one intentional source-only
SKIP 083** account for the 146 cases. The detailed audit
checked saved per-case `RESULT: PASS`, normal versus
expected nonzero GO codes, reported LKED codes, available
assembler step codes, and abend/known-runtime-defect
signatures. The locally generated 145-row TSV records
the available job and step detail but is not committed as
a source artifact.

### Reconciled return-code contract

The initially detected 048 missing-GO report was a
checker error: 048 must terminate at Cambridge code
generation, before link/edit or GO.

Tests **052 and 093** generated `STACK OVERFLOW`
and GO RC0000 under **BCPLM6/D6**; their historical
generic fixtures require RC0012 for **BCPLM7/D7**.
The separate `expected-go-rc-bcplm6.txt` fixtures
retain the correct RC0000 candidate contract without
changing the D7 fixtures. The runner was changed to
enforce profile-appropriate GO RC on its normal
success path, preventing the earlier false-positive
acceptance. The saved-log audit passed *after* these
corrections. Neither the changed harness nor the D7
runtime was claimed to have been newly MVS-executed
in this final verification; the prior full-run GO evidence
was evaluated against the explicit BCPLM6 expectation.

**M4.4 CLOSED.** The passing full suite and detailed
audit establish compatibility under the tested candidate
and current harness contracts. They do **not** prove
lossless DD-specific physical record attribution,
preservation of trailing FB132 blanks, or successful
handling of genuinely unrecoverable host errors.
Those remain outside this gate; **M5 is OPEN** and
retains the lossless per-DD SYSOUT acceptance work.
No overall dynamic-stream milestone completion or
production OBJ promotion is implied.

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

The owner deferred the full suite at M4.1; that deferral
remained in place through M4.4.0. On 2026-10-17 the owner
explicitly lifted it for the full 00..145 candidate panel.
Authorization is not execution evidence.

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

## M4.4.1 authorization — 2026-10-17

**Owner decision: the prior complete-panel deferral is lifted.**
The owner explicitly directed: "Let's go for full panel."
This authorizes one complete unchanged-candidate
`BCPL_RUNTIME_PDS=1`, `BCPL_RUNTIME_LIBRARY=DEVOBJ`,
`BCPL_RUNTIME_CANDIDATE=1`, `BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6`
native regression **00..145**, after the read-only
`check-m44-compatibility.py --candidate` check.

**No panel execution has yet been reported for this authorization.**
The successful M4.4.0 source-only preflight is not a substitute
for JES compile/assemble/link/GO evidence. Expected:
146 cases, **145 PASS / 0 FAIL / 1 intentional SKIP 083**.
Test 141's `STOP(8)` GO RC0008 is expected PASS.
Capture individual log/job/step diagnostics and the final
runner summary; on any failure preserve the first diagnostic.
A green full panel completes **M4.4.1 evidence**, not
M4.4.2 review or M5 DD-attribution.
No PDS rebuild, promotion, production overwrite, ABI
change or compiler change is authorized by this decision.

## M4.4.1 — complete candidate regression (authorized; execution pending)

The owner has explicitly released the full-suite deferral.
Execute against the already installed development candidate:

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

## M4.4.1 acceptance — full candidate panel PASS (2026-10-17)

The operator pulled main through `a572e77`, exported
`BCPL_RUNTIME_PDS=1`, `BCPL_RUNTIME_LIBRARY=DEVOBJ`,
`BCPL_RUNTIME_CANDIDATE=1`, and
`BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6`, then ran
`python3 tools/checks/check-m44-compatibility.py --candidate &&`
`tools/native/run-regression 0 145 --show-output`.

The supplied complete 146-case console report recorded:

```text
M4.4 source-only compatibility preflight: PASS
Candidate environment: PASS
NATIVE REGRESSION  00..145  (146 tests)
...
SKIP  083  083-instrumented-storage-reclamation
           (source-only instrumentation)
...
PASS  145  145-dynamic-dd-open-denial-counted
NATIVE REGRESSION COMPLETE
PASS  145
FAIL  0
SKIP  1
TOTAL 146
```

**M4.4.1 ACCEPTED** against the previously accepted
00..132 complete panel (132 PASS / 0 FAIL / SKIP 083).
All thirteen later tests 133–145 passed within the *same*
complete candidate run. The intentional SKIP remains 083.
No PDS rebuild, ABI change or production OBJ promotion
was required.

**M4.4.2 remains an evidence-disposition gate.** The
145-pass console summary does not show individual
compiler/GO JES job IDs or IFOX/IEWL/GO return codes.
The runner also contains a fallback that can report
`PASS WITH KNOWN RUNTIME DEFECT` for an S322,
which its outer driver still counts as a PASS.
Therefore the count summary alone does not prove
that no accepted test took that exception.
Audit existing per-test logs and explicitly report
any S322/known-defect acceptance and unexpected step
status *before formal M4.4 closure*. **No second
full regression run is requested.**

## M4.4.2 saved-log audit — initial reconciliation (2026-10-17)

The operator's full-panel saved-log audit examined all
145/145 existing logs and reported five findings:

```text
048: fewer than two compiler/GO job IDs
048: GO RC=MISSING; expected 0000
048: LKED RC=MISSING
052: GO RC=0000; expected 0012
093: GO RC=0000; expected 0012
```

**048 is an audit error, now corrected.** The test includes
`compile-only.txt` and explicitly stops after Cambridge
code generation. The revised audit requires its
`TERMINATION: COMPILE-ONLY` marker and rejects
unexpected GO or LKED instead of requiring them.

**052 and 093 remain real fixture/GO mismatches**:
both have `expected-go-rc.txt` of `0012`, but the
full DEVOBJ(BCPLM6) GO steps completed with RC0000.
The outer native runner's RC0000-success branch ignores
nonzero GO-RC fixtures, so both were counted PASS.
Their BCPL output fixtures expect `STACK OVERFLOW`.
The 052 README distinguishes the older BCPLM6/D6
RC0000 behavior from BCPLM7/D7 RC0012; the 093 README
states RC0000 despite its 0012 fixture. This strongly
suggests that the fixture requirement is conflating two
candidate runtimes, but it is not resolved by assertion.

**M4.4 cannot formally close until the correct BCPLM6
stack-overflow RC contract is reconciled and the runner
is made to enforce that contract.** No fixture, runtime
object or production assembler was changed to hide the
discrepancy. The revised audit should be rerun against
the existing saved logs only; no MVS re-execution is
required for this investigation.

## M4.4.2 candidate-specific GO-RC contract (2026-10-17)

For this native stream milestone the tested candidate is
**DEVOBJ(BCPLM6)**, not the separately developed BCPLM7/D7.
The test 052 historical account explicitly distinguishes
BCPLM6/D6's normal RC0000 controlled stack-overflow
completion from BCPLM7/D7's GO RC0012 cleanup path.
Test 093's original README expects RC0000, while its
generic `expected-go-rc.txt` was later set to 0012.

Accordingly, 052 and 093 now retain their original
`expected-go-rc.txt` = 0012 **for the D7 profile**
and each adds a separate
`expected-go-rc-bcplm6.txt` = 0000.
The candidate harness consults that override only when
`BCPL_RUNTIME_CANDIDATE=1`,
`BCPL_RUNTIME_LIBRARY=DEVOBJ`, and
`BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6`.
The ordinary runner now validates the expected GO
code even on the normal success branch, eliminating
the false-PASS loophole that concealed both discrepancies.
The M4.4 saved-log audit explicitly audits the BCPLM6
profile and requires both profiles' fixture values
unchanged, plus a correctly marked compile-only 048.

**Scope:** This is a regression harness/fixture correction,
not a change to BCPLMAIN, BCPLIO, G slots, installed
object libraries, or observed MVS behavior.
The earlier reported complete runner result remains
145 PASS / 0 FAIL / 1 SKIP. Post-hoc acceptance still
requires **an actual rerun of the revised log audit
against the existing 145 test logs**, not another
MVS regression sweep. If that audit is clean, the
GO RC evidence is reconciled for BCPLM6 alone;
no BCPLM7/D7 acceptance is claimed.

## M4.4.2 — disposition and M5 boundary

### Audit existing per-case logs (without rerunning MVS)

Run the repository-owned read-only log verifier:

~~~sh
cd ~/Source/Repos/BCPL-for-MVS
python3 tools/checks/check-m44-full-panel-logs.py
~~~

It reads the existing 145 regression logs, checks per-test
`RESULT: PASS`, GO RC expectations (including expected
STOP exits), LKED RC, observed assembler codes and obvious
`ABEND`/`PASS WITH KNOWN RUNTIME DEFECT` signatures.
It generates a local 145-row job/step index at
`workarea/native-regression/m44-00-145-jobs.tsv`
without modifying canonical assembler, PDS objects, JCL,
or executing any MVS job. Report any anomalies; do not
weaken the checker to conceal legitimate known defects.
Keep the manifest for M4.4.2 evidence reconciliation.



The new complete panel and its corrected saved-log audit
both passed; **M4.4 is formally CLOSED** under the
candidate-specific contracts recorded above.
No canonical runtime, object PDS or public G-vector modification
is required by this readiness stage.

M5 still owns lossless DD-specific JES/physical FB132 record
attribution. Combined printer report logical assertions alone
do not establish the source DD or retain significant trailing blanks.
M4.4 verification does not waive that separate acceptance gate.
