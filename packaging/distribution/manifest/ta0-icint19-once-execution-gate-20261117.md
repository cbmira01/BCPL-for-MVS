# TA.0 — ICINT19 once-only execution/review gate

**Project:** BCPL for MVS 3.8 Reconstruction  
**March:** TA.0 — Release Architecture, Inventory, and Manifest  
**State:** Safety orchestration implemented and tested offline; actual `TA0ICEX` result remains unverified. **TA.0 IN PROGRESS.**

## Situation

The owner reported successful one-time relocation of 168 retained evidence files
(979,963 bytes) from a historical `$HOME` collection into ignored repository
`workarea/ta0-mvs-evidence-20261117/`. The subsequent executable-use
pilot reported only `ExecEvidenceError`, with no JES number or specific phase.
That error alone does **not** establish whether `TA0ICEX` was submitted.
No new System/370 execution result may be inferred from it.

The existing non-submitting `inspect-icint19-failed-pilot.py` classifies the
saved output when available, but the operator has directed that command
stanzas be reserved for MVS-facing operations rather than separate host checks.

## Consolidated gate

`tools/distribution/run-or-review-icint19.py` is the single operational
entry point. It has only these branches:

1. **Existing output directory, including incomplete or failed evidence:**
   invoke the existing **read-only** failure inspector; **never** submit JES
   or alter the saved files. A saved receipt is reported but not reaccepted
   without revalidation. Any ambiguous cursor remains `SUBMISSION_STATUS_UNCERTAIN`.
2. **No output directory:** call the original guarded `ICINT19` pilot once.
   It validates pinned JOB 9060 `IEHLIST` evidence, the saved directory
   review, the development load DCB, canonical `MRREGRES` source identity,
   and the scalar/vector expected results **before** creating output or
   submitting a new MVS job. A preflight refusal makes no JES call.
3. **An error during that single attempt:** perform one **read-only**
   classification of whatever original evidence exists; never resubmit.
   A failed or uncertain report does not become acceptance evidence.

This gate does not rewrite original JES output, mutate persistent MVS PDSes,
use tape, adjust the accepted 12-case MR10 test contract, or infer source
lineage or `RECFM=U` byte equality. It prints a short state/job/preflight
summary only. Paths are enforced by the existing symlink-safe
`workarea/` policy; output files remain mode 0600 in a private directory.

The underlying MVS workload is **exactly** the original eight-step
scalar/vector subset from the canonical `MRREGRES` source:
`SSYNI`, `STRNI`, `SCGI`, `SBLIBI`, `SICLIB`, `C01A`, `G01A`, `R01`.
For a new validated result, JES RC, `IEF142I`, interpreted `CODE=0`, and
both golden `RP:` records must agree. `NEW_EXECUTION_VALIDATED` and `SAVED_EXECUTION_VERIFIED` are the only
success exits; all other states return a nonzero exit status.

## Verification

Assistant-workspace tests: **11 new gate tests** plus **32 previously
implemented executable-pilot/inspector tests**: **43/43 PASS**.
All tests simulate the MVS runner; no actual MVS job was submitted by those
tests. The gate was checked for syntax and symlink/old-output rejections.
Actual JOB 9060 directory evidence remains accepted only as directory
metadata; subsequent TA.0 binary provenance, unload/restore, and release
gates remain open.

## Live follow-up and saved-receipt validation — 17 November 2026

The owner ran the consolidated gate against the migrated, ignored-workarea
collection. It reported:

    TA.0 ICINT19 GATE: RECEIPT_ALREADY_PRESENT JOB=unknown
      PREFLIGHT=OK_NOW REPORT=NOT_APPLICABLE
      SUBMITTED_IN_THIS_INVOCATION=NO

The previous inspector stopped at the existence of a `receipt.json` file
without checking its contents, the saved MVS report or the JES job number.
This was a **tooling gap**: it established only that a receipt file exists.
It neither proved nor disproved interpreter execution. The actual private
receipt and SYSOUT have not been directly inspected in the assistant workspace.

The corrected inspector recomputes and checks the exact receipt schema, the
five pinned evidence hashes, previously reviewed JOB 9060 directory identity,
source JCL/Git blob and golden fixture identities, the saved extracted eight
JCL steps and all eight `job-summary` RC=0000 results. It re-runs the exact
MVS report validator (JES start/end, IEF142I RC=0000, interpreted CODE=0 and
both golden RP: lines) and compares the fresh result with the saved receipt.
A retained `failure.txt`, missing/linked evidence, inconsistent hashes or a
changed current preflight results in `SAVED_RECEIPT_REJECTED` and nonzero exit.
Only `SAVED_EXECUTION_VERIFIED` with a bounded JES job number permits the
existing receipt to count as a **development-load executable-use observation**.
No JCL is submitted by this existing-output path, and no file is modified.

The reviewed receipt remains an assertion tied to the retained printer/JES
report, **not** independent RECFM=U byte identity, source-to-DASD binding,
IEBCOPY unload/restore, or recipient tape acceptance. No TA.0 march closure.
The improved path was verified with offline, adversarial fixtures in the
assistant's isolated workarea, not the owner's private SYSOUT. Actual MVS
result classification is the next live gate.


## Live verification: JOB 9061, 17 November 2026

The owner executed the corrected read-only receipt review **twice** against
the same saved workarea evidence. Each review returned:

    TA.0 ICINT19 GATE: SAVED_EXECUTION_VERIFIED JOB=9061
      PREFLIGHT=OK_NOW REPORT=PINNED_JES_AND_BCPL_RESULT_VERIFIED
      SUBMITTED_IN_THIS_INVOCATION=NO

This supersedes the earlier **unknown** execution-result status in this
document. The eight-step development MR10 ICINT19 executable-use gate is
**PASS (qualified)**. The saved receipt verifier confirms the original
JES/IEF142I RC=0000, interpreted CODE=0 and scalar/vector RP results;
neither subsequent check submitted a new MVS job. The user's private
underlying report remains under ignored workarea/, not in Git or directly
available in the assistant workspace. See the
[TA.0 binary evidence reconciliation record](ta0-binary-evidence-reconciliation-20261117.md).

No RECFM=U byte identity, original-source-to-DASD binding, restored
load-library execution, recipient/tape verification, TA.0 closure or rights
clearance follows from this narrow pass.
