# BCPLIO dynamic streams — M5.5 final acceptance gate

**Status: STAGED; first operator self-test FAILED, parser correction prepared (17 October 2026); no M5.5 panel run or final acceptance.**
M5.0 through M5.4 are closed. The last **measured** full
DEVOBJ BCPLM6+BCPLIO panel is still M4.4 (00..145:
145 PASS, 0 FAIL, expected SKIP 083 and 145/145
saved log audit). M5.5 must generate its **own fresh**
execution evidence and obtain the owner's explicit
acceptance. This is a final compatibility run,
**not** a destructive purge-to-clean-room rebuild.

## Frozen boundary

- Candidate from **NATIVE_DEVOBJ(BCPLM6 + BCPLIO)**;
  other service objects resolve as documented in
  [current DEVOBJ runbook]
  (../packaging/clean-room-mvs-reconstruction.md#10-m54-addendum--reproduce-the-accepted-dynamic-bcplio-candidate).
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
[M5.4 runbook](../packaging/clean-room-mvs-reconstruction.md)
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
