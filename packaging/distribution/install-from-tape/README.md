## TA.3 — BC0004 tape-resident installation technical PASS

The owner reported actual MVS completion of the separately guarded
`ta3-rc4-continuation --run` after the original post-MR10
`IEFACTRT` summary-label halt. **JOB 9403** verified the preserved
first MR10 installation (11 PDSes/94 members) and absence of the
other 31 targets. Following one new approval, actual MVS
**NATIVE 11 PDSes/71 members/10 IEBCOPY steps PASS** and
**COMBINED 20 PDSes/150 members/19 IEBCOPY steps PASS**.
The combined `ICINT19` SCALVEC `TEST:/EXP:/RP:/CODE=0`
semantic check passed; `BC0004` remained unchanged.

**Three on-tape profiles PASS: 42 PDSes, 315 members.**
Technical TA.3 qualified acceptance is recorded in
[all-profile MVS results](ta3-rc4-all-profiles-accepted-20261123.md).
The [qualified closure/TA.4 preparation](../../milestones/tape-artifact-release/ta3-qualified-acceptance-and-ta4-preparation-20261123.md)
awaits explicit owner formal transition direction.

Do **not** rerun `ta3-rc4-production`,
`ta3-rc4-recipient` or `ta3-rc4-continuation`
in stateful mode. All their one-shot authorizations are consumed;
preserve both AWS images, the incident and recovery receipts.
The full TA.4/TA.5/TA.7 gates and release-publication approval
are **not** implied by TA.3 technical acceptance.

## TA.3 — BC0004 interrupted on-tape recipient: no replay; guarded recovery

The owner reported **MVS JOB 9398 recipient preflight PASS** (42 targets
absent) and authorized the first BC0004 tape-resident profile trial.
The run halted after the first MR10 profile job at the
optional **job-summary `IEBCOPY` program-name count** validator.
The MVS `IEF142I` step evidence had already passed before that
redundant count. The original recipient one-shot marker was consumed:
**NEVER rerun `scripts/ta3-rc4-recipient --run`.**

The corrected validator relies on exact ordered MVS `IEF142I`
procedure-step and condition-code evidence, not a program label that
the `IEFACTRT` summary parser may omit for in-stream procedures.

The [separately guarded continuation](scripts/ta3-rc4-continuation)
first checks the **original SHA256-sealed incident** and consumed
marker, verifies the actual first MR10 restore job's ten MVS
`IEF142I` RC0000 steps, then runs **read-only MVS LISTDS and
directory checks** to confirm the original 11 MR10 PDSes/94 members
and **all 31 remaining NATIVE/COMBINED targets absent**.
Only after those gates does it ask one new explicit `Y`
confirmation to submit the two **unfinished on-tape** profile jobs
and the combined installed SCALVEC test. It never reruns MR10,
stages anything, or rewrites the BC0004 tape.

See the [original incident and approved no-replay recovery contract](ta3-rc4-interrupted-recipient-recovery-20261123.md).
**Actual continuation is pending; TA.3 remains IN PROGRESS.**

## TA.3 — BC0004 tape-resident installer: MVS production PASS, recipient pending

The owner reported **actual MVS 3.8J RC4 production PASS**
on **JOBS 9393–9397**: two new BT0001/BT0002 stage datasets,
eight installer PDS members, 21 standard-labeled datasets and
64 AWS physical tape files. Candidate `BCPL-0.1.0-rc4`, VOLSER
`BC0004`, SHA-256
`7cc5a1d61882bf88469fd9f9e38512f1976ef1a775e3095e12e3988600c57af1`.
See [production evidence record](../create-tape/ta3-rc4-production-operator-result-20261123.md).
**Do not repeat production or overwrite either BC0003 or BC0004.**

The [one-shot BC0004 recipient runner](scripts/ta3-rc4-recipient)
performs one MVS absence preflight for 42 fresh datasets, then
with a single operator confirmation restores three separate
eight-member installer libraries and obtains each **actual
on-tape** `MR10`, `NATIVE`, `COMBINED` JCL body using MVS
IEBGENER SYSOUT. Every recovered card is checked before it is
submitted back to actual JES. MVS IEBCOPY profile restoration,
LISTDS/DCB/member-directory verification, and combined installed
`ICINT19` SCALVEC `TEST:/EXP:/RP:/CODE=0` follow.

The [recipient trial contract](ta3-rc4-tape-resident-recipient-run-20261123.md)
details the 11/11/20 PDS and 94/71/150 member targets.
**The recipient run is not yet executed; TA.3 remains IN PROGRESS.**
No executable native Cambridge Compiler is implied.

## TA.3 — RC4 MVS PROC proof and guarded tape producer

**MVS JOB 9392 PASS** (owner-reported): the read-only
`ta3-rc4-proc-probe` demonstrated in-stream `PROC` expansion,
symbolic PDS-member DSN substitution and IEBGENER RC0000 on
actual MVS 3.8J. Evidence:
`workarea/ta3-rc4-proc-probe/20261123T054327Z-35363`.

The source-controlled
[RC4 production runner](../create-tape/scripts/ta3-rc4-production)
preflights 19 accepted RC3 staging PDSes, two absent new stage
targets, the immutable BC0003 SHA, unused BC0004 identity and
MVS/Hercules tape drive. One `Y` confirmation authorizes:
new `TA3R4S.BT0001` and `BT0002` staging; MVS DCB and eight-member
directory verification; and **a new BC0004** 21-step standard-label
AWS tape write, independently checked against 64 physical files.
Full reports are sealed under `workarea/ta3-rc4-production/`.

The runner accepts an idle empty drive or the **verified original
BC0003** already mounted, dismounting only that accepted image
after confirmation. Foreign media, existing output datasets,
existing BC0004, nonzero JES steps or ambiguous results are refused
without retry. Original BC0003, accepted TA.2/TA.3 jobs and
one-shot markers are not repeated or replaced.

**Actual RC4 staging and tape write remain pending.** Following
MVS production, a separate fresh-recipient tape-resident profile
installation must be verified before TA.3 closure. See
[RC4 implementation and execution contract](../create-tape/ta3-rc4-tape-resident-installer-design-20261123.md).

## TA.3 — RC4 replacement tape-resident installer (in development)

The owner approved replacing the inert `BC0003` on-tape
`BT0002(RESTORE)` template with real MVS-native profile jobs **in
a separate candidate**. The RC4/BC0004 manifest and authoritative
registry reservation are committed. Original BC0003 and all TA.2/TA.3
receipts remain immutable.

The [RC4 installer design](../create-tape/ta3-rc4-tape-resident-installer-design-20261123.md)
documents eight tape-resident BT0002 members, including
`MR10`, `NATIVE`, `COMBINED` and the shared `COPY` SYSIN member.
The source-controlled [offline generator](../create-tape/scripts/ta3-rc4-installer)
builds the changed BT0001/BT0002 members and candidate JCL. The
[read-only MVS PROC probe](scripts/ta3-rc4-proc-probe) tests
historical JCL procedure symbols against existing TA3N1 PDS data
before any new stage/tape write.

**No BC0004 image has been created or written yet.**
TA.3 remains IN PROGRESS pending actual MVS probe, candidate
production and independent recipient installation.

## TA.3 all three installation profiles — MVS PASS (qualified)

**Owner-reported actual MVS 3.8J results (23 November 2026 EST):**
the native-only TA3N2 recipient restored and verified **11 PDSes / 67
members**; combined TA3N3 restored and verified **20 PDSes / 146
members** and executed installed `ICINT19` SCALVEC with
`TEST:/EXP:/RP:/CODE=0` PASS. MVS preflight **JOB 9378** verified all
31 destinations absent and BC0003 intact. The original TA3N1 MR10-only
recipient previously passed **11 PDSes / 90 members**, with installed
SCALVEC execution (JOBS 9370–9377).

See the [complete three-profile operator evidence](ta3-rc3-all-profiles-operator-results-20261123.md).
New profile evidence is sealed locally under
`workarea/ta3-rc3-remaining-profiles/20261123T050551Z-34032`.
Do not repeat any accepted stateful job or overwrite the immutable tape.

**TA.3 remains IN PROGRESS:** These are namespace-isolated trials on
one running MVS system, not independent clean-IPL acceptance. The
`BT0002(RESTORE)` tape-resident member remains an inert site-parameter
template, whereas the successfully executed profiles are separate
source-controlled MVS JCL decks. That distinction needs formal owner
disposition before any qualified march closure. No executable native
Cambridge Compiler or TA.5 native link/execute proof is claimed.

## TA.3 recipient report and remaining profiles

The owner reported **TA3N1 MR10-only PASS** on actual MVS JOBS
9370–9377: the `BT0001`/`BT0002` bootstrap, 10/10 restored
MR10/documentation PDSes, 90/90 members, and actual installed
`ICINT19` SCALVEC `TEST:/EXP:/RP:/CODE=0`. See the
[operator result record](ta3-rc3-n1-operator-result-20261122.md);
the sealed local JES files have not been separately inspected here.

The committed [remaining-profile runner](scripts/ta3-rc3-remaining-profiles)
performs one guarded native-only `TA3N2` install (11 PDSes,
67 members) and one separate combined `TA3N3` install (20 PDSes,
146 members). It first verifies the prior sealed `TA3N1` receipt,
all 31 new destinations absent on MVS, and the unchanged BC0003
image. Each profile re-reads the bootstrap and independently restores
`BT0002`; the combined profile additionally executes installed MR10
SCALVEC. The [execution and evidence contract](ta3-rc3-remaining-profiles-run-20261122.md)
records the one-confirmation/no-retry policy. **Actual TA3N2/TA3N3 MVS
execution is still outstanding.** The tape is unchanged; no native
Cambridge Compiler is claimed.

# Install from tape

## TA.3 authorized isolated MR10 recipient trial

The [isolated BC0003 recipient-run preparation](ta3-rc3-isolated-recipient-run-20261122.md)
and `scripts/ta3-rc3-recipient` now implement a guarded, single-confirmation,
no-retry MVS execution path. The operator invokes `--run` after updating to
current GitHub `main`; all host-side readiness checks and JCL substitutions
are handled by the runner, not by the owner.

The target is the **new** `HERC02.BCPL.TA3N1.*` namespace. The MVS path
reads BT0001, restores and prints BT0002, restores the MR10-only profile,
verifies exact recipient DCBs and all 90 installer/docs/MR10 members,
then uses the restored ICINT19 in a source-controlled eight-step
SCALVEC compile/generate/execute demonstration. All JES, LISTDS, IEBGENER,
IEBCOPY and TEST/EXP/RP/CODE evidence is saved under repository
`workarea/ta3-rc3-recipient/`; console output is limited to outcomes
and evidence location.

Offline checks passed, but **no actual new TA.3 MVS job has yet run**.
The owner has authorized the one isolated stateful operation.
The accepted `BC0003` image is never rewritten and TA.2 one-shot jobs
are not repeated. An ambiguous post-approval failure is **NO RETRY**.
A successful isolated MR10 proof would not establish a fully independent
system or yet verify the native-only/combined profiles.

## TA.3 — BC0003 bootstrap and profile restoration implementation

**Current status:** TA.3 — MVS Bootstrap and Installation IN PROGRESS.
The immutable `BCPL-0.1.0-rc3` / `BC0003` image was accepted
under TA.2 (qualified); its original tape, records and receipts are preserved.

Six MVS-only job bodies are now source-controlled in [`jcl/`](jcl/):
`TA3BOOT` reads `BT0001` using IEBGENER; `TA3BT2` restores
`BT0002` using IEBCOPY; `TA3VIEW` displays its four installer members;
`TA3MR10`, `TA3NATV`, and `TA3BOTH` implement independently selectable
MR10-only, native-component/source-only, and combined IEBCOPY restores.
All outputs must be absent and are allocated with `DISP=(NEW,CATLG,DELETE)`.

Read the [TA.3 BC0003 MVS installation record](ta3-bc0003-mvs-installation-20261122.md)
for the exact profile contents, site job-card/HLQ/unit/VOLSER contract,
allocation policy and current acceptance limitations. Static source/JCL
checks passed; **no new TA.3 MVS execution has yet occurred**.
A separately authorized isolated recipient run is the next requirement.
The on-tape `BT0002(RESTORE)` remains a 19-step site-parameter template,
not a selectable installer; the present JCL is external support material,
and changes to the frozen image are not authorized.

The older sections below are historical TA.2 development checkpoints;
their earlier descriptions of unexecuted staging must not be read as
the present BC0003 acceptance status.


Consumer-side source intended to be carried on distribution media.

- `jcl/`: MVS dataset allocation, IEBCOPY restore, and verification jobs.
- `scripts/`: installation-support source, if needed; any tape-resident executable dependency must be available on the target MVS installation.
- `tests/`: clean-target restoration and verification cases.

The installer must be usable without GitHub, WSL, Python, TSO or project development utilities. The tape bootstrap arrangement must make installation instructions and JCL accessible before BCPL is installed. Per the [approved distribution direction](../native-cambridge-compiler-distribution-decisions-20261108.md), the recipient supplies a site-specific HLQ and the installation uses the same position-based `BCPL.BTnnnn` mapping as the producer. The initial read-only bootstrap and all installation procedures remain to be implemented and verified. No executable installation procedure or overwrite policy is approved yet.

The [expanded release scope](../release-payload-scope-decision-20261116.md) requires **independent MVS-only installation and verification** for both the native Cambridge Compiler and the MR10 Kit Compiler. MR10 must ship with its 11 language demonstrations, 17 BCPL demonstrations, and 12-case regression panel. Its existing `MRREGRES` job runs on MVS. The [subsequent owner decision](../mr10-regression-exp-manual-verification-decision-20261116.md) requires fixed `EXP:` and actual `RP:` report records and **human per-case review of all 12 plus interpreted `CODE=`** on MVS, with recorded PASS/FAIL and sign-off; an automatic MVS semantic comparator is **not** required. This report format and manual acceptance procedure remain to be implemented and proven. Host-side `dspal` and Python verification are not acceptable recipient dependencies.

## TA.2 proposed installer materials; recipient acceptance pending

The manifest-derived [offline installer material generator](../create-tape/ta2-bootstrap-installer-materials-20261119.md)
now provides four proposed MVS PDS members (INSTALL, DATASETS, RELEASE,
RESTORE), an 18-step IEBCOPY restoration template, and the BT0002
bootstrap restoration job body. This is an **unexecuted, site-parametric
proposal**; placeholders for HLQ, tape unit, DASD unit and each allocation
must be supplied and checked before use. TA.3 must still establish safe
recipient installations and independent profile selection on actual MVS.
No installer PDS has yet been created or written to tape.

## Proposed pre-staging installer job preparation

The [TA.2 preparatory material and target preflight](../create-tape/ta2-bootstrap-prestaging-mvs-preflight-20261119.md)
adds a **not-submitted** MVS IEBGENER/IEFBR14 staging job for BT0001
bootstrap text and four BT0002 installer PDS members. `DD DATA,DLM=ZZ`
preserves the proposed RESTORE member's JCL statements as in-stream
**data**. It is not a recipient installation approval. The recipient
must still supply site parameters, and TA.3 must verify actual installation
with MVS-only tools. No live stage or tape test has been executed.

## TA.2 BC0002 isolated installation/usage pilot — designed, not executed

The [consolidated acceptance record](ta2-rc2-consolidated-acceptance-20261121.md)
and tested `scripts/ta2-rc2-acceptance` provide a single MVS-facing entry
point. `--live` performs a read-only catalog/DCB preflight of the 21
JOB-9343 readback datasets and confirms 21 new installation destinations
absent. The consolidated `--run` phase performs the same read-only preflight and
then requires one explicit operator **Y** confirmation before allocating a new `HERC02.BCPL.TA2INS.*` environment,
copy all 21 restored datasets with IEBGENER/IEBCOPY, and run the canonical
12-case MRREGRES from the independently installed MR10 inputs/load module.
The installation is a same-system pilot, not a clean-target TA.3/TA.7 PASS.
No new MVS operation is claimed.

The first operator invocation of `--run` refused at a redundant Git approval-file gate (RC=2, no MVS operation or one-shot marker). The revised procedure removes that gate; the explicit `[y/N]` response is the sole stateful authorization and the durable no-retry marker is created only after `Y`. No stateful MVS installation result has been reported.

## Post-run semantic review of installed MR10 (read-only)

Owner-reported JOBS **9344** (21 source DCBs and 21 absent targets PASS), **9345** (21 installed datasets, RC=0000) and **9346** (`MRREGRES` 12 execution steps, JES RC=0000) completed on 22 November 2026; no rerun is permitted. Run the **same** `scripts/ta2-rc2-acceptance` entry point with **`--review`** to inspect its original SHA-256-sealed JOB 9346 report; this performs no MVS submission. It writes only a fresh sealed semantic comparison under repository `workarea/`. Its golden `RP:` and interpreted `CODE=` comparison is diagnostic; current BCPL tests do **not** emit the owner-approved `EXP:` lines, and individual human sign-off remains pending. See [consolidated acceptance record](ta2-rc2-consolidated-acceptance-20261121.md).

## MR10 regression golden/display contract preparation

The 22 November 2026 [TA.2 installed MR10 evidence and TA.4 EXP source preparation](ta2-rc2-12-case-comparison-and-ta4-exp-preparation-20261122.md) records **12/12** saved MVS `RP:`/`CODE=0` comparisons against the immutable `BC0002` tape. The revised canonical BCPL panel sources now contain **23 fixed literal `EXP:` records** matching the tracked golden files. The read-only `scripts/mr10-exp-source-check` guards those source literals; new MVS compilation is required. These changes are *not* present on original `BC0002` or its accepted installation.

## Updated TA.4 EXP source MVS regression — 22 November 2026

The owner executed `tools/mr10/run-regression-panel` against the
post-`83620618` 12-case BCPL source panel using `icintv19.asm`
and canonical ICLIB: **12 PASS / 0 FAIL / RC=0** on the development
MVS path. This verifies the modified source's compile/run behavior
and unchanged computed golden results, but the automated runner does
not independently validate the newly printed `EXP:` lines. That
requires captured MVS report inspection and human sign-off for an
updated future distribution candidate; the earlier BC0002 tape and
its installed sources are immutable. See
[the consolidated checkpoint](ta2-rc2-12-case-comparison-and-ta4-exp-preparation-20261122.md).
