# TA.2 — Guarded one-shot selective IEBCOPY staging preparation

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.2 — Manifest-Driven Tape Producer  
**Date:** 19 November 2026  
**Status:** TSO002 plus all 18 staging SPACE triples and conditional-retry IEBCOPY submission owner-approved; actual MVS staging pending.

## Owner-reported MVS readiness

The owner reported a successful `ta2-stage-readiness --live` on GitHub
`main` `31050fd6ce95820e08511dc1e222c44f58bb26e5`:

- 18/18 PDS staging targets and 127 selected members;
- proposed TSO002 with **16,045 IEHLIST-reported empty tracks**;
- fresh source/catalog/VTOC MVS inquiries PASS;
- **645 primary tracks + 65 secondary reserve = 710** proposed tracks;
- retained private evidence:
  `workarea/ta2-stage-readiness/20261119T210718Z-18180`.

The 18 exact proposed `SPACE=(TRK,(primary,secondary,directory))` triples
are recorded as structured **PROPOSED_ONLY_NOT_APPROVED** data in
`ta2-stage-space-proposal-20261119.json`, bound to the owner's exact
saved MVS readiness and allocation evidence. The proposal is not a
release dataset/member manifest. The TA.0 inventory remains authoritative
for all 127 selected members.

**TSO002 was approved first (19 November 2026); in a subsequent
explicit decision the owner approved the exact 18 per-PDS SPACE triples
and retryable IEBCOPY submission.** The MVS free-track
total alone does not establish free-extent contiguity or guaranteed 18
successful allocations.

## Implementation

`scripts/ta2-stage-once --readiness-evidence <saved-run>` defaults to
independent **saved-evidence replay only**. With `--live` it repeats
read-only source `dspal stat`, TSO LISTDS absence for all 18 targets,
and IEHLIST VTOC for TSO002. It refuses changed source attributes,
selected members, exact allocation amounts, saved/current VTOC inventory
or free tracks, or any catalog/uncataloged target collision.

For a future separately approved `--run`, it requires an additional,
explicit **Git-tracked on `main`**
`packaging/distribution/create-tape/ta2-stage-write-approval.json`.
That file is **deliberately absent** from the repository at this stage.
The runner refuses the write mode until such an approved file is separately
committed, matches the full staging proposal SHA-256, the pinned readiness
receipt SHA-256, and authorizes precisely the one TSO002/18-PDS operation.
It additionally requires an interactive confirmation, a second fresh MVS
preflight, and exclusive creation of
`workarea/ta2-stage-operations/TA2STG-TSO002-attempt.json`
**before** any possible JES submission. Never delete this marker or retry
a partly successful staging. Earlier `DISP=(NEW,CATLG,DELETE)` outputs
may remain cataloged even if a later IEBCOPY step fails.

On a future authorized attempt the runner derives 18 IEBCOPY steps and
127 `SELECT MEMBER` controls from the canonical source manifest, attaches
an authenticated MVS job card, and requires all 18 IEBCOPY RC=0000 steps
and distinct IEF142I confirmations. Full JES and private evidence stay in
ignored `workarea/`; never persist an authenticated password-bearing deck.
RC=0000 is **not** final acceptance of the staged payload: independently
verify exact 127-member sets without extras, DCB and partitioned-library
directory attributes, the `MR10_LOAD` PO/U/0/6144 case, source-to-staged
record/binary fidelity, and executable-use where applicable.

All generated files from this workflow are inside repository-root
`workarea/` or tracked `packaging/`. No tape image, `BCnnnn` production
VOLSER, candidate registry entry, or publication operation is included.

## Assistant offline checks

**35/35 focused synthetic tests passed** under the assistant's isolated
repository-root workspace. Coverage includes exact 18 proposed allocations,
checksum and path integrity, forbidden symlinks, source/job receipt mismatch,
owner approval absent or forged, Git-main binding, budget drift, raw JCL
counts/card widths, one-shot attempt marker, all 18 MVS step RCs, IEF142I
completeness, ABEND refusal and simulated live VTOC drift. Python syntax
checks also pass. The actual private MVS evidence has not been imported
into the assistant workspace and the live one-shot runner has **not** been
executed on MVS; no acceptance of staging execution is claimed.

**The subsequent explicit owner decision approves all 18 exact SPACE triples and
conditional-retry IEBCOPY submission; actual MVS staging and readback remain
pending. TA.2 remains IN PROGRESS.**

## Subsequent explicit owner decision: TSO002 volume only

After the successful read-only `ta2-stage-once --live` gate, the owner
explicitly stated **“TSO002 approved.”** The preserved private
read-only MVS evidence is
`workarea/ta2-stage-operations/20261119T234105Z-18708`:
18/18 source/target checks, 127 selected members, fresh MVS PASS.
The canonical volume-only decision is recorded in
[`ta2-stage-volume-approval-20261119.json`](ta2-stage-volume-approval-20261119.json).
The unchanged 18 proposed allocation amounts are retained in
[`ta2-stage-space-proposal-20261119.json`](ta2-stage-space-proposal-20261119.json),
whose status is now `VOLUME_APPROVED_SPACE_AND_WRITE_UNAPPROVED`.

This **does not** approve the 18 `SPACE` triples or the non-retryable
IEBCOPY stage. The missing `ta2-stage-write-approval.json` remains
a mandatory fail-closed gate for `--run`; a committed volume approval
cannot satisfy it. The runner now validates the exact source-controlled
volume-only decision and refuses an altered decision that purports to
authorize SPACE, JES write or production tape operations. In a
hypothetical future authorized write, it also verifies both authorization
records are committed unchanged on GitHub `main`.

**42/42 focused offline staging-runner tests passed** following the
new approval distinction (seven new refusal/identity tests).
No MVS operation was performed by the assistant; neither PDS
allocation nor IEBCOPY/tape write is claimed.

## Latest owner-operated MVS read-only stage gate

**Owner report, 19 November 2026:** After the Git-controlled volume-only
approval was committed, the owner ran the updated
`ta2-stage-once --readiness-evidence ... --live` on the current MVS
system. The concise console receipt was:

```text
TA.2 STAGING WRITE GATE: 18/18 source/targets, 127 selected, fresh MVS PASS; TSO002.
Read-only; TSO002 approved, 18 SPACE triples and IEBCOPY unapproved; no submission.
Private MVS evidence: workarea/ta2-stage-operations/20261119T234948Z-18994
```

This confirms the volume-only approval contract did not block
legitimate read-only MVS verification. The assistant has not directly
inspected the private MVS JES reports. It does **not** accept any of
the 18 proposed `SPACE` triples or authorize `--run`.
`ta2-stage-write-approval.json` remains intentionally absent.
Do not submit the 18-step IEBCOPY deck or infer tape/installer
acceptance from this read-only PASS.

### Separate local repository observation

The owner also showed an empty root-level `FETCH_HEAD` last modified
11 November 2026. The actual Git metadata path is
`.git/FETCH_HEAD`; root `FETCH_HEAD` is absent from the GitHub
`main` tree and is not matched by the tracked `.gitignore`.
No current tracked-code reference was found in the GitHub code search.
Its creator is not established by this evidence. This unrelated
local file should not be ignored merely to disguise it, and no
automatic deletion was added to the staging tooling.


## Owner approval: all 18 SPACE triples and conditional-retry IEBCOPY

**Explicit owner decision, 19 November 2026:** “18 triples and retryable
IEBCOPY submission approved. Get rid of FETCH_HEAD.”

This *supersedes* earlier no-write / absolute no-retry gates **for the
exact existing staging dataset selection only**. The single original
TA.0 member inventory remains authoritative, and the 18 triples in
`ta2-stage-space-proposal-20261119.json` remain unchanged. Their
provenance is still the saved actual MVS `ta2-stage-readiness --live`
receipt at
`workarea/ta2-stage-readiness/20261119T210718Z-18180`, followed by
the later owner-reported fresh MVS `ta2-stage-once --live` PASS at
`workarea/ta2-stage-operations/20261119T234948Z-18994`.

The exact, Git-tracked [staging write approval](ta2-stage-write-approval.json)
pins the original proposal's SHA-256
`526b98745e77a557e86d5af1fc61d894a7e8db5ab5ff385041844066218e2a18`,
the private readiness run path, TSO002, 18 targets and 127 members.
Because the private `readiness.json` is not committed, its actual
SHA-256 is independently checked at runtime and preserved in each
attempt's private journal rather than guessed in the approval file.
All earlier source/capacity/target evidence is independently replayed
and two fresh MVS read-only preflights still precede submission.
The user must type the runner's explicit confirmation.

### Conditional retry safety

The new `ta2-stage-once --run` can issue the *first* approved
18-step selective IEBCOPY job. A subsequent invocation is a **new
attempt** only if **each prior** JES job has a checksum-pinned complete
report, a recognized JOB-number match, clear `$HASP373` STARTED and
`$HASP395` ENDED banners, a nonzero failed result and no detected
ABEND/JCL error. A second fresh MVS source, LISTDS and IEHLIST query
must independently establish that **all 18** stage target names
remain absent both from the catalog and formatted VTOC, and that
the original VTOC inventory/free-track observation is unchanged.
The original 18-step JCL uses `DISP=(NEW,CATLG,DELETE)`; it never
overwrites an existing PDS. Each retry has an exclusive new, sequential,
per-attempt marker and private SHA256-sealed evidence.

This is **retryable, not blind/automatic resubmission**. Unknown JES
outcome, incomplete evidence, an unended job, any cataloged or
uncataloged staging target, a success result, JCL/ABEND diagnostics,
or source/VTOC drift **halts further submission**. Partial staging
requires a separately verified recovery method; deleting, resetting,
or overwriting prior PDSes is not authorized. There is no caplessly
automated retry loop; only the owner can invoke a subsequent attempt.

### Root-level FETCH_HEAD cleanup

The user showed an empty **untracked root-level** `FETCH_HEAD` file
separate from Git's actual `.git/FETCH_HEAD`. On an authorized
`--run`, after Git-tracked approvals and prior attempt checks but
before any new MVS submission, the script checks the exact repository
root, confirms the file is untracked and a zero-byte single-link
regular file with stable identity, and unlinks it. Symlinks, tracked
files and nonempty/changed files fail closed. No `.git/` contents
are modified. The assistant cannot directly observe the user's WSL
file until that on-host runner executes.

### Verification boundary

**54/54 focused synthetic/offline tests passed** in the assistant's
isolated repository-root workspace, plus Python syntax checks.
Coverage includes owner/volume/proposal/hash refusal, all 18 exact
allocations, MVS source/target evidence replay, positive and failed
JES result parsing, prior-attempt checksum identity, unresolved/partial
retry refusal, parallel attempt marker exclusion and root `FETCH_HEAD`
cleanup conditions. **No state-changing MVS job has been submitted
or independently verified by the assistant.** Actual MVS IEBCOPY
output, 18 cataloged PDS attributes, 127 exact member sets and
record/binary fidelity must be verified before using the staged
datasets in a release tape. No production VOLSER, AWS tape or
publication authorization is granted.
