# BCPLIO dynamic streams — M5.5 final acceptance gate

**Status: M5.5 FORMALLY CLOSED by project owner 17 October 2026. Final run 145 PASS / 0 FAIL / expected SKIP 083 with 145/145 fresh-log audit PASS. Follow-up interrupted duplicate altered current on-disk artifacts after verification; caveat retained.**
The earlier M4.4 145/0/1 DEVOBJ result was the
pre-final compatibility baseline. The later fresh
M5.5 00..145 run at `57c7354` also produced
**145 PASS, 0 FAIL, one expected SKIP 083** with
**145/145 fresh logs audited**. The owner accepted
those final results. The procedures and earlier
pending statements below are preserved as
dated preparation/execution history, **not as
outstanding work**. This was not a destructive
clean-room purge/rebuild.

## Formal gate closure — 17 October 2026

The project owner agreed to close M5.5 based on
the previously reported **successfully completed**
fresh 00..145 run at `57c7354` and its strict
independent 145/145 log verification. The accepted
result is **145 PASS, 0 FAIL, 1 expected SKIP 083**.
The original verifier's
`VERIFIED_AWAITING_OWNER_ACCEPTANCE` receipt has
now been satisfied by the owner's explicit
acceptance. See the
[final milestone acceptance record]
(Milestone-BCPLIO-dynamic-stream-final-acceptance.md).

The second, interrupted repeat is not an invalidation
of the accepted first run. It did, however, modify
the on-disk evidence after success; the original
receipt and terminal paste should be retained.
Procedures and earlier OPEN/pending states in this
document remain dated historical context,
**not newly outstanding exit criteria**.

**M5.5 CLOSED; parent milestone CLOSED.** No
production OBJ promotion or new MVS tests authorized.

## Frozen boundary

- Candidate from **NATIVE_DEVOBJ(BCPLM6 + BCPLIO)**;
  other service objects resolve as documented in
  [current DEVOBJ runbook]
  (../clean-room-mvs-reconstruction.md#10-m54-addendum--reproduce-the-accepted-dynamic-bcplio-candidate).
- Do not promote any candidate to NATIVE_OBJ.
- No new BCPL global numbers, QSAM/VSAM library,
  compiler changes, JES2 spool investigation,
  raw internal spool byte requirement or normal
  runner/JCL change.
- The three physical experiments already accepted
  are **JOB 8184** (A/Z printer route),
  **JOB 8185** (FB132 QSAM disk readback),
  and **JOB 8186** (intentional RC0012 when
  the verifier expects a wrong last padding byte).
  Preserve these existing proofs; running the
  full logical regression does **not** reproduce
  them and need not do so.

## Before submitting jobs

Confirm the installed DEVOBJ(BCPLM6/BCPLIO)
candidate and NATIVE_OBJ runtime state:

```sh
cd ~/Source/Repos/BCPL-for-MVS
git pull --ff-only
git status --short
git rev-parse HEAD
tools/datasets/dspal status --probe
tools/datasets/dspal ls NATIVE_DEVOBJ
tools/datasets/dspal ls NATIVE_OBJ

export BCPL_RUNTIME_PDS=1
export BCPL_RUNTIME_LIBRARY=DEVOBJ
export BCPL_RUNTIME_CANDIDATE=1
export BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6

python3 tools/checks/test-m55-final-evidence.py
python3 tools/checks/m55-final-evidence.py begin
```

The **offline `begin` step** runs
`check-m44-compatibility.py --candidate`,
`check-bcplio-m43-account.py` and
`tools/native/run-regression --check-numbering`.
It requires a clean Git tree, records the current Git
commit, candidate settings and all 145 old per-case log
timestamps in `workarea/native-regression/m55-begin.json`.
It refuses to overwrite existing M5.5 evidence files.
**No job is submitted by the preparation tool.**

If DEVOBJ members are missing or stale, follow the
[M5.4 runbook](../clean-room-mvs-reconstruction.md)
for the approved BLDDEVM6 and BLDDEVI rebuilds before
beginning. Check the build *payload* RCs and the
installed PDS members. Do not perform an automatic
runtime/PDS rewrite in the preflight.

## One complete operator run

Use Bash so `pipefail` ensures that `tee`
cannot hide a nonzero runner exit:

```bash
set -o pipefail
tools/native/run-regression 0 145 \
  | tee workarea/native-regression/m55-full-panel.log

python3 tools/checks/m55-final-evidence.py verify
```

If the runner fails, **stop**; examine
`workarea/native-regression/logs/` and
the JES step reports. Do not call an incomplete
suite accepted merely because old M4.4 logs
still exist. If the runner completes, `verify`
requires all of:

1. Exactly one 00..145 banner, 145 distinct ordered
   RUN and PASS entries, SKIP 083 only, final
   **145 PASS / 0 FAIL / 1 SKIP / 146 TOTAL**.
2. **Every one** of the 145 case logs has a
   new mtime after the recorded `begin` timestamp,
   later than the snapshot and is nonempty.
3. Git commit and four candidate profile
   variables agree with the initial checkpoint.
4. The existing
   `tools/checks/check-m44-full-panel-logs.py`
   audits all 145 logs and confirms expected
   JCL/IFOX/IEWL/GO return codes, including
   compile-only 048, the BCPLM6 profiles for
   052/093, intentional nonzero STOP, and
   no accepted known-defect/abend results.
5. The audit writes the job/step manifest
   `workarea/native-regression/m44-00-145-jobs.tsv`
   (existing audit naming retained for reuse).

On successful verification, the *only new file*
beyond the transcript/checkpoint and prior
audit artifacts is
`workarea/native-regression/m55-verification.json`,
with SHA-256 of the complete transcript and the
job/step TSV. Its state reads
**VERIFIED_AWAITING_OWNER_ACCEPTANCE**.
That receipt is **not** itself an owner
decision to close the milestone.

## Evidence and acceptance

The operator should provide at least the M5.5
runner's completion summary and
`m55-final-evidence.py verify`
output. For a failure, provide the first bad
case's saved log and relevant job summary.
Existing JOBS 8184/8185/8186 and their
historical positive/negative proof do not
require repetition.

**M5.5 EXIT REQUIRES:** measured fresh
candidate 145/0/1, all-new 145/145 audited logs,
documented limits and owner's decision.
Only then update the master milestone to
**CLOSED**. DEVOBJ -> NATIVE_OBJ promotion
is a **distinct later authorization**.

## M5.5 first operator preflight: parser correction and safe restart

At commit `969acf8`, the operator confirmed Hercules/JES2 ready (probe
JOB 8187), DEVOBJ containing BCPLAPT, BCPLBYTE, BCPLIO, BCPLM6
and BCPLM7, and OBJ containing BCPLMAIN, BCPLMEM and BLIB.
The first offline M5.5 unit suite reported **6/8 passed**,
**one ERROR** and **one FAIL**; the positive-fixture parser
mistakenly treated the aggregate `PASS  145` footer
and following `FAIL  0` line as another per-case result.
The wrong-SKIP negative fixture consequently failed for the
same reason. No BCPLIO or native runner issue was observed.

The first `begin` command nevertheless produced a
`m55-begin.json` snapshot at Git `969acf8`
because the operator shell proceeded after the test failure.
This **is not accepted as a valid final-panel start**,
and no 00..145 MVS panel has been submitted.
The corrected checker uses **horizontal-only separators**
for RUN/PASS/SKIP/FAIL and adds tests against the
real discovered case names and the exact aggregate footer.
`begin` now invokes its offline self-test internally:
an offline failure cannot create another successful
M5.5 checkpoint.

**Archive, do not delete or overwrite, the original
pre-parser-fix `begin` evidence**, but only if no
`m55-full-panel.log` or `m55-verification.json`
has been created:

```bash
cd ~/Source/Repos/BCPL-for-MVS
git pull --ff-only

# Check before touching the existing snapshot:
test ! -e workarea/native-regression/m55-full-panel.log
test ! -e workarea/native-regression/m55-verification.json
test ! -e workarea/native-regression/m55-begin-before-fix.json

# Archive the stale original BEGIN under a new name:
mv workarea/native-regression/m55-begin.json \
   workarea/native-regression/m55-begin-before-fix.json

python3 tools/checks/test-m55-final-evidence.py
python3 tools/checks/m55-final-evidence.py begin
```

The `test` guards are intentionally independent commands
for inspection; **if any returns nonzero, stop, do not
execute mv or begin**. Run in `set -e` mode if you
want the shell to halt automatically on failure.
The new begin checkpoint must name the **new Git
commit**, not the old `969acf8`. Only after the
new offline tests and begin succeed should the
single full 00..145 panel proceed. Historical
M5.1/M5.2 proofs remain unchanged.

## M5.5 second operator self-test correction — numeric case order

At `eb7f14a`, the operator reran the 10-test
offline suite. Nine tests passed; the added
real-repository case-name test failed with
`RUN lines do not identify all 145 cases in order`.
Because the shell command used `&&`, it **stopped
before archiving the old BEGIN and before any fresh
`begin` or MVS 00..145 panel execution**.

The remaining issue was in the test's fabricated
transcript, not the production regression runner:
`discover()` inserts directory names in
**lexicographic** order (e.g. 05, 053, ..., 06).
The actual runner visits **numeric** case order
(05, 06, ..., 052, 053), printing the separate
test ID first and the directory's full name
second. The original fixture printed the
directory name in both columns and preserved
the lexicographic iteration order. Fix
`fixture()` to sort numeric keys, derive the
two/three-digit test ID, and retain the
descriptive case name only in column two.
Added a focused regression that asserts this
difference with the actual 146 directory names.

Locally reconstructed the parser and both
synthetic+descriptive/lexicographically ordered
fixture variants: **three positive** and
**three corrupted-case rejection** checks
passed. Checked the live Git tree's 146
directory names: 145 ordered RUN records
matched the expected IDs and names.
The complete amended Python unit suite **still
requires operator execution**. No BCPL
runtime/runner/JCL/PDS change has been made.

The original `m55-begin.json` created
at `969acf8` should still be present because
the shell short-circuited before `mv`.
Follow the guarded archive-and-rebegin commands
above after pulling this correction. Do not
accept the old checkpoint for the new run.

## M5.5 fresh operator execution and successful verifier (2026-10-17)

After pulling and using `57c7354`, the operator
achieved **11/11 offline self-tests PASS twice**,
M4.4 candidate source preflight PASS, M4.3 checks
PASS and numbering PASS, then recorded a new
`m55-begin.json` at `57c7354`. The first fresh
`tools/native/run-regression 0 145` finished with:

```text
NATIVE REGRESSION COMPLETE
PASS  145
FAIL  0
SKIP  1
TOTAL 146
```

Immediately afterward, the strict evidence verifier
reported **145 newly written logs, 145/145 passed
M4.4 job/step audits and M5.5 PASS**, writing
`m55-verification.json`. There were no detected
known-defect or abend exceptions. Expected GO
RC distribution: 0000=139, 0008=3, 0012=1,
0100=1. Case 048 is compile-only, and 083
was the expected source-only skip. The exact
case-by-case runner output was supplied in an
operator terminal paste; the observed first-run
logs had UTC mtime range 16:22:25 to 16:32:04
on 17 October 2026.

**Second run caution:** after this verified success,
the operator ran the same full-panel command again,
which re-created `m55-full-panel.log`, ran cases
00 and 01 successfully, then interrupted case 02.
The second transcript is partial and **must not**
replace the first-run accepted test outcome.
Because `tee` truncated the transcript and the
runner rewrote at least two individual logs, the
on-disk artifacts should no longer be described as
a fully intact, directly re-auditable first-run set.
The receipt remains a record that `verify` DID
pass before the second run; the operator terminal
paste independently reports both events.

A 298-line first-run transcript can be extracted
from the user-supplied terminal paste. Its SHA-256
is `5623d6949629ccfa38833b8f4765c42053bd18a54bed795e4ec989a80eff63fe`.
**This recovery SHA is not known to match the
receipt's saved transcript digest.** Compare
them before restoring any file or claiming a
verified bit-for-bit recovery; avoid overwriting
the partial second-run artifact until preserved.

**Technical exit conditions are met** on the
documented first run. The final explicit owner
acceptance decision is outstanding. No
production OBJ promotion, source change or
further JES2 experiment is required for that
decision.
