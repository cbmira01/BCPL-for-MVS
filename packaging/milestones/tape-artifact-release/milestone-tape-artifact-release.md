# Milestone — Tape artifact release

**Project:** BCPL for MVS 3.8 Reconstruction  
**Status:** **TA.0 CLOSED (qualified); TA.1 CLOSED (qualified), 19 November 2026; TA.2 — Manifest-Driven Tape Producer IN PROGRESS (all 20 staging inputs MVS directory/DCB accepted; release provenance and candidate-media gates pending) — no candidate production authorized**
**Authoritative source:** GitHub `main`  
**Target:** Standard-labeled Hercules AWS virtual tape distribution of the **Cambridge BCPL Programming System for MVS 3.8J**

**TA.1 operator-reported write checkpoint (17 November 2026):**
The new uncataloged BTA101 scratch image was initialized and written by
TA1AWRIT JOB 9076; the guarded runner reported both logical standard-label
datasets and SHA-256 d5900cbccaaa2f7eb1bcc59ae30847540e6911c577dafa5e131c0b3a9c8e3fe2.
See [Track A write evidence](../../distribution/create-tape/ta1-track-a-write-evidence-20261117.md).
Readback and both independent IEBCOMPR steps subsequently completed with
MVS JOBS 9084, 9086 and 9089, all RC=0000, and the AWS SHA unchanged.
The [Track A round-trip record](../../distribution/create-tape/ta1-track-a-roundtrip-review-20261117.md)
now records Track A PASS (qualified): read-only review of the actual
saved tape-map reports found seven physical tape files containing
3, 3, 2, 2, 25, 2 and 0 blocks, with both datasets and original image
SHA-256 preserved. Track B remains pending. Owner approved its design on 18 November 2026;
source-controlled JCL and read-only preflight are implemented but no Track B
stateful operation has been authorized. No further stateful operation
is authorized here.

**TA.1 saved physical-file review checkpoint (18 November 2026):**
The owner executed the Git-controlled read-only reviewer at
`4845be9db79ecaa6b8dd4e777ba32bbcf4983886`; it reported
`TA.1 TRACK A: saved MVS evidence PASS (qualified)`, confirmed all
four actual MVS JES jobs 9076/9084/9086/9089 at required RC=0000,
seven physical tape file block counts `3,3,2,2,25,2,0`,
both expected standard-label dataset sequences, the restored seven-member
PDS and unchanged SHA-256. This is an actual owner-reported MVS/Hercules
evidence review, not an offline simulation. Track A is PASS (qualified);
**TA.1 remains open for Track B**. No new MVS operation is authorized.

**TA.1 Track B implementation checkpoint (18 November 2026):**
The owner approved the [separate RECFM=U selected ICINT19 load-library tape design](../../distribution/create-tape/ta1-track-b-design-proposal-20261117.md).
Tracked `TA1BWRIT.jcl` and `TA1BREST.jcl`, pinned canonical MRREGRES/IEHLIST
job generation and strictly read-only MVS/Hercules preflight are staged.
The [implementation record](../../distribution/create-tape/ta1b-implementation-20261118.md)
reports 44/44 synthetic/negative offline tests passing. No BTA102 image,
MVS tape job, remount, new load PDS or restored ICINT19 GO was executed.
Track B remains IN PROGRESS, and separate explicit authorization is required
for all stateful media and MVS operations.

**TA.1 Track B read-only MVS/Hercules evidence checkpoint (18 November 2026):**
The owner executed `ta1b-preflight --live` on GitHub main
`eb0a26e489255e43a1bdc5089589dc53fa8347a0`, reporting PASS.
`MR10_LOAD(ICINT19)` is PO/U/0/6144 on TSO003; BTA102 was absent among
four inspected existing images and the new filename was absent; Hercules
0480 was empty, MVS unit 480 reported, and the uncataloged tape DSN and
new target DASD load library were absent in the MVS catalog.
A new fail-closed one-shot `run-ta1-track-b-write` runner was isolated
and synthetic-tested 27/27 PASS, retaining the required fresh checks,
exclusive media creation, no-retry receipts, live JES/hetmap evidence
and protection of the existing BTA101 image. This is a new implementation
checkpoint, **not** proof that BTA102 was initialized or written.
See [TA.1B live-preflight and write gate](../../distribution/create-tape/ta1b-readonly-preflight-and-write-gate-20261118.md).
**No Track B stateful initialization, mount, write, restore or GO is authorized
by this design/preflight result.** TA.1 remains IN PROGRESS.

**TA.1 Track B stateful-experiment gate correction (18 November 2026):**
The owner approved ONE new `BTA102` initialization/mount and ONE
`TA1BWRIT` unload, but the first invocation at GitHub
`51c56b326fc48a1f47d9e4b19101f0694f333387`
stopped at the FIRST read-only `unit_ready()` inquiry with:
`MVS tape unit 480 is not unambiguously online/ready`.
The failure occurred before any operator confirmation, no-retry marker,
tape image creation, mount, or production job submission. No
MVS `D U,TAPE` raw status row was supplied; `O-NRD` is a grounded
hypothesis from the preflight/writer disagreement, not a measured claim.
The guard has been corrected to accept `O-NRD` for an **empty,
unallocated, online Hercules 0480** ONLY, while retaining strict
`O` status after BTA102 mount. Negative tests exercise offline,
busy, ambiguous and foreign-media refusal. See
[TA.1B first gated run and correction](../../distribution/create-tape/ta1b-first-write-gate-correction-20261118.md).
The approved scope is unchanged: the corrected live runner still
refuses any preexisting attempt receipt or AWS image. **No Track B
write, restoration or GO has been observed.** TA.1 remains IN PROGRESS.

**TA.1 Track B second read-only guard halt (18 November 2026):**
The owner invoked the corrected `run-ta1-track-b-write --run` from GitHub
main `efab256a987512b9e524557293faff99f206fac2`. It reported
`TA.1B WRITE HALTED: MVS tape unit 480 status row missing/ambiguous`;
private evidence was written to
`workarea/ta1b-operations/BTA102-track-b-write-20261118T232154Z-8887/`.
This was the FIRST `unit_ready(mounted=False)` inquiry, before the
operator confirmation, no-retry receipt, AWS file creation, mounting,
or JES submission. The previous read-only preflight searched for
`480 3400` anywhere within an output line and passed, whereas this
writer revision anchored it to the beginning of a line. A console
message prefix is a source-supported explanation, **not** an
assertion that a particular raw MVS status row was observed.
The revised writer counts in-line unit matches, still rejects
duplicates and unexpected statuses, accepts `O-NRD` only on
verified empty Hercules 0480, and requires `O` after mount.
It now includes a bounded observed-line diagnostic on a future
mismatch. Source and safety tests committed; no BTA102 tape
initialization, mount, write, restore or executable GO observed.
See [second guard correction](../../distribution/create-tape/ta1b-second-write-gate-correction-20261118.md).
TA.1 is still IN PROGRESS.

**TA.1 Track B third guarded read-only halt (18 November 2026):**
With GitHub `main` at `5bae753128c3f79f7e7cace74190c554a167a9a9`,
the owner ran `run-ta1-track-b-write --run`; the first
`unit_ready(mounted=False)` check stopped with `matches=2`.
The exact diagnostic contained *two byte-identical* console lines:
`23:36:00 / 480  3400 O-NRD              /REMOV 481  3400 OFFLINE`.
Thus 480 is `O-NRD` and separate unit 481 is `OFFLINE`; the duplication,
not a contradictory state, caused the halt. Owner-local private evidence:
`workarea/ta1b-operations/BTA102-track-b-write-20261118T233538Z-9227/`.
No operator confirmation, attempt marker, image, mount or production
JES submission was reached. The corrected guard requires one **distinct**
unit-480 record, collapsing only byte-identical echoed lines and
rejecting conflicting states, timestamps, different prefixes and
two instances on the same line. It isolates unit-480 allocation flags
from adjacent 481 output and retains the empty-Hercules and
post-mount MVS-`O` safety conditions. **24/24 focused offline tests
PASS**, with the tracked unit-test module expanded to 50 test methods;
the full suite was not separately asserted as executed.
See [third gate evidence](../../distribution/create-tape/ta1b-third-write-gate-correction-20261118.md).
TA.1 IN PROGRESS; no BTA102 write/restore/GO has been verified.

**TA.1 Track B BTA102 write checkpoint (18 November 2026, 23:52 UTC / 18:52 EST):**
The owner invoked the authorized, guarded one-shot writer at GitHub
`702617a30c765df06815bcf9c028930dfa3d91c8`. After fresh
read-only preflight and explicit initialization/JES confirmations,
BTA102 was initialized and mounted at Hercules 0480.
`TA1BWRIT` JOB **9120** completed `UNLOAD IEBCOPY RC=0000`;
the runner verified one complete standard-labeled `BCPL.BT0001`
data set, four Hercules physical-file segments with block counts
**3, 8, 2, 0**, and AWS SHA-256
`c3b235ca78d221432199adcde1f7a83aead4f76bab0e0eaa19d77c81d9912210`.
Source `MR10_LOAD(ICINT19)` remained read only and the tape DSN was
not cataloged. Original private evidence:
`workarea/ta1b-operations/BTA102-track-b-write-20261118T235204Z-9548/`.
This owner-reported success is the **Track B unload/write PASS
(qualified)**, not a restored executable proof.
A separately authorized restore to
`HERC02.BCPL.TA1B.LOAD` (PO/U/0/6144), followed by IEHLIST
directory comparison and actual restored-STEPLIB ICINT19 execution,
is still required. The new `run-ta1-track-b-restore` script defaults
to **read-only live preflight** and forbids a stateful restore
without its own explicit owner authorization and typed confirmations.
Its 26 synthetic/negative offline tests PASS. See
[Track B write receipt and restore staging](../../distribution/create-tape/ta1b-write-evidence-and-readback-preparation-20261118.md).
TA.1 remains IN PROGRESS; no restore/GO acceptance is claimed.

**TA.1 Track B independent restore read-only preflight checkpoint (18 November 2026, 19:24 EST / 19 November 00:24 UTC):**
The owner ran the newly committed
`packaging/distribution/create-tape/scripts/run-ta1-track-b-restore`
without `--run`, on GitHub `main`
`52c128ca4dac2b82549114976f4f4eee807aa9d6`.
Its live saved-receipt and MVS/Hercules checks reported
`BTA102 JOB 9120 write receipt and immutable SHA-256 PASS; drive empty`
and `TA.1 Track B restore preflight PASS (new DASD PDS still absent)`.
Evidence path:
`workarea/ta1b-operations/BTA102-track-b-restore-20261119T002435Z-10407/`.
The runner did NOT mount/remount BTA102, allocate a new DASD load
library, submit `TA1BREST`, run IEHLIST or execute ICINT19 GO.
The checksum validated is the original
`c3b235ca78d221432199adcde1f7a83aead4f76bab0e0eaa19d77c81d9912210`.
This is **owner-reported live preflight evidence**, not independent
restoration acceptance. The separately approved design provides for
one conditional exact-volume remount and one IEBCOPY `TA1BREST`
into **new** `HERC02.BCPL.TA1B.LOAD` (PO/U/0/6144).
**Stateful restoration is not yet authorized**; directory comparison
and restored STEPLIB execution remain separate MVS verification gates.
See [TA.1B restore preflight record](../../distribution/create-tape/ta1b-restore-readonly-preflight-20261118.md).

**TA.1 Track B independent restore PASS checkpoint (18 November 2026, 21:11 EST / 19 November 02:11 UTC):**
The owner separately authorized one conditional BTA102 remount and one
IEBCOPY `TA1BREST` into a new DASD load-library PDS.
On GitHub main `b99395e19dcd3264351c753ce285b035c9a5c008`,
the `run-ta1-track-b-restore --run` runner repeated its live safety
preflight, conditionally mounted the original BTA102 on Hercules 0480,
and reported `TA1BREST` **JOB 9136**, `RESTORE IEBCOPY RC=0000`.
It verified `HERC02.BCPL.TA1B.LOAD(ICINT19)` on **TSO002**
with **PO/U/0/6144** dataset attributes. The original BTA102 AWS
SHA-256 remained
`c3b235ca78d221432199adcde1f7a83aead4f76bab0e0eaa19d77c81d9912210`.
Private restore evidence:
`workarea/ta1b-operations/BTA102-track-b-restore-20261119T021135Z-10863/`.
This establishes independent **Track B unload/restore PASS (qualified)**
at the MVS IEBCOPY/dataset level; it does **not** establish a matching
IEHLIST directory or successful program fetch/execution from the
restored load library. The new
`scripts/run-ta1-track-b-directory` performs read-only MVS source/
target library inquiries by default and, **after distinct owner
authorization only**, can submit two one-shot read-only IEHLIST FORMAT
jobs to compare nonalias ICINT19 entry point `000000` and attributes
`02E2` on source TSO003 and restored TSO002. It never touches tape.
**35/35 assistant-workspace offline tests PASS** (27 extended guards
and 8 tracked contract checks). Neither directory jobs nor the
restored eight-step MRREGRES scalar/vector GO have been submitted.
See [restore acceptance and IEHLIST preparation](../../distribution/create-tape/ta1b-restore-evidence-and-directory-gate-20261118.md).
TA.1 remains IN PROGRESS.

**TA.1 Track B source-versus-restored directory live read-only preflight PASS (18 November 2026 EST / 19 November UTC):**
The owner executed the committed
`packaging/distribution/create-tape/scripts/run-ta1-track-b-directory`
**without `--run`** from GitHub `main`
`58f98db10dd5b790ea52c488070c6de2a98b98d5`.
The MVS-facing runner reported:
`TA.1B IEHLIST preflight PASS: MR10_LOAD TSO003; restored LOAD TSO002; both PO/U/0/6144`;
`BTA102 SHA-256 and JOB 9136 receipt PASS; no tape media operation`.
It explicitly confirmed **NO IEHLIST JES submission or ICINT19 GO**.
Private evidence:
`workarea/ta1b-operations/BTA102-track-b-directory-20261119T023717Z-11735/`.
This is a live read-only source/restored dataset and original
tape/restore receipt check, **not** a comparison of IEHLIST
directory entry `000000` and attribute `02E2` yet.
The existing source-controlled guarded `--run` workflow, requiring
a **separate explicit owner authorization and interactive confirmation**,
will submit exactly two read-only `IEHLIST LISTPDS FORMAT` JES jobs:
`TA1BSRC` against source `HERC02.BCPL.MR10KIT.LOAD` on TSO003,
and `TA1BDST` against restored `HERC02.BCPL.TA1B.LOAD` on TSO002.
It preserves all existing BCPL data, requires independent
MVS success/IEF142I, and performs no tape, restoration or GO operation.
TA.1 remains IN PROGRESS.
See [live directory preflight record](../../distribution/create-tape/ta1b-directory-readonly-preflight-20261118.md).

**TA.1 Track B IEHLIST comparison authorization (18 November 2026, 21:46 EST):**
Following the live read-only directory preflight PASS at
`58f98db10dd5b790ea52c488070c6de2a98b98d5`,
the owner explicitly approved the next gate: exactly **one
`TA1BSRC`** IEHLIST `LISTPDS FORMAT` JES job against
`HERC02.BCPL.MR10KIT.LOAD` on **TSO003**, and exactly
**one `TA1BDST`** against restored `HERC02.BCPL.TA1B.LOAD`
on **TSO002**. Both use `DISP=SHR`; the approved scope
includes read-only MVS JES/SYSPRINT output and independent
`ICINT19` directory comparison, **not** a tape operation,
load-library modification, `TA1BREST` rerun or `ICINT19` GO.
The pre-existing, source-controlled, offline-tested
`scripts/run-ta1-track-b-directory --run` already enforces
fresh MVS inquiry, exact confirmation
`COMPARE ICINT19 DIRECTORIES`, durable exclusive-create
no-retry marker and strict individual JES RC/IEF142I checks.
A fresh source review reconfirmed all 12 relevant safeguards
(no source edits needed); the established offline isolated tests
were reported 35/35 PASS in the previous commit.
**Neither IEHLIST job has yet been observed to execute**.
See [this authorization record](../../distribution/create-tape/ta1b-directory-submission-authorization-20261118.md).
TA.1 remains IN PROGRESS.

**TA.1 Track B actual source/restored IEHLIST directory comparison PASS (18 November 2026 EST / 19 November UTC):**
Following the separately authorized single pair of read-only IEHLIST jobs,
the owner ran `run-ta1-track-b-directory --run` at GitHub main
`a296b8b60d1c3459a1c263ea4c4487632644277b` and typed
`COMPARE ICINT19 DIRECTORIES`. Actual MVS `TA1BSRC`
**JOB 9151** on source **TSO003** and `TA1BDST` **JOB 9152**
on restored **TSO002** both returned IEHLIST `DIRLIST RC=0000`.
Both independently reported nonalias `ICINT19`
**entry `000000` and attributes `02E2`**. The runner reported
`TA.1B SOURCE/RESTORED ICINT19 DIRECTORY MATCH (IEHLIST FORMAT only)`.
The original BTA102 AWS SHA-256 remained
`c3b235ca78d221432199adcde1f7a83aead4f76bab0e0eaa19d77c81d9912210`.
Private actual JES/SYSPRINT evidence:
`workarea/ta1b-operations/BTA102-track-b-directory-20261119T024927Z-11906/`.
This establishes **Track B load-module directory preservation
PASS (qualified)**, not load byte equality or restored execution.

The new `packaging/distribution/create-tape/scripts/run-ta1-track-b-go`
provides a separate **read-only-by-default** restored-`STEPLIB` GO
preflight. It revalidates the preserved BTA102 SHA, successful 9136
receipt, actual IEHLIST 9151/9152 source/target job reports and
typed `000000/02E2` entries, exact DASD DCB/volumes, and the pinned
MRREGRES eight-step scalar/vector JCL generator. The authorized
`--run` mode remains **gated by distinct owner approval** and would
submit one `TA1BGO`, with `HERC02.BCPL.TA1B.LOAD` in all three
ICINT19 `STEPLIB` DDs. It only creates temporary `&&` working
datasets, never touches tape or persistent source/target libraries,
and insists on 8 steps RC=0000 and exact semantic RP output.
**32/32 isolated synthetic/refusal tests PASS; both promoted source/test
Git blobs match tested workspace bytes.**
**No restored ICINT19 GO has yet been submitted or approved.**
See [Track B directory PASS and GO preflight](../../distribution/create-tape/ta1b-directory-match-and-go-preparation-20261118.md).
TA.1 stays IN PROGRESS.

**TA.1 Track B live restored-STEPLIB GO preflight PASS (19 November 2026, 06:49 EST / 11:49 UTC):**
The owner ran `packaging/distribution/create-tape/scripts/run-ta1-track-b-go`
in its default read-only mode at GitHub `main`
`acae8bd36b222bc4e3ef7ac5bee57ea482c1dcf3`. The tool reported:
`TA.1B RESTORED GO READ-ONLY PREFLIGHT PASS: IEHLIST jobs 9151/9152, entry 000000 attrs 02E2`;
`MVS source TSO003 / restored TSO002 PO/U/0/6144; original BTA102 SHA-256 preserved`.
It confirmed no `ICINT19` GO JES submission and no MVS dataset
or tape change. Original private evidence:
`workarea/ta1b-operations/BTA102-track-b-go-20261119T114903Z-13321/`.
The runner revalidates both actual IEHLIST receipts against the
stored MVS reports, the independent JOB 9136 restore, BTA102 SHA
`c3b235ca78d221432199adcde1f7a83aead4f76bab0e0eaa19d77c81d9912210`,
and the source/restored PDS identities. A further **14/14 static
safety contract checks** of the already committed GO runner PASS;
no code edits were necessary. The earlier 32/32 offline test
result was not rerun in this documentation-only checkpoint.
The remaining TA.1 Track B acceptance gate is **one** separately
authorized `TA1BGO` JES job: pinned eight-step MR10 scalar/vector
sequence, all three interpreter `STEPLIB` DDs bound to the
restored `HERC02.BCPL.TA1B.LOAD`, RC=0000, three successful
ICINT19 executions, and exact scalar/vector `RP:` records.
**No GO submission has been authorized or executed yet.**
See [actual GO preflight record](../../distribution/create-tape/ta1b-go-readonly-preflight-20261119.md).
TA.1 remains IN PROGRESS.

**TA.1 Track B restored ICINT19 GO authorization (19 November 2026):**
The owner explicitly approved **one** `TA1BGO` JES submission
after the real read-only GO preflight PASS at
`acae8bd36b222bc4e3ef7ac5bee57ea482c1dcf3`.
The unmodified, source-controlled
`scripts/run-ta1-track-b-go --run` must repeat preflight,
require typed `RUN RESTORED ICINT19 SCALVEC`, and atomically
record a no-retry attempt before submitting the canonical
eight-step MRREGRES scalar/vector case. All three interpreter
`STEPLIB` DDs are bound to the restored
`HERC02.BCPL.TA1B.LOAD` on TSO002; all created work datasets
are temporary. No tape action or permanent MVS dataset change
is authorized. The source/test package retains its prior
32/32 isolated offline PASS; an additional 19/19 source-level
safety review checks PASS without code changes. No MVS
`TA1BGO` execution result has yet been received, so Track B
executable-use and TA.1 closure remain pending. See
[TA.1B GO authorization](../../distribution/create-tape/ta1b-go-submission-authorization-20261119.md).

**TA.1 Track B restored-STEPLIB GO actual MVS PASS (19 November 2026, 12:10 UTC / 07:10 EST):**
After specific one-shot approval, the owner ran
`packaging/distribution/create-tape/scripts/run-ta1-track-b-go --run`
from GitHub `main` `199ea8536bb0ece10ad04c0a32020a18335b60b5`
and confirmed `RUN RESTORED ICINT19 SCALVEC`. The runner reported
**`TA1BGO` JOB 9165**, **all eight ordered MRREGRES scalar/vector
steps RC=0000**, **three `ICINT19` invocations** using the
independently tape-restored `HERC02.BCPL.TA1B.LOAD` via all three
`STEPLIB` DDs, and **scalar/vector `RP:` PASS**.
The pinned golden expected records are `RP: SCALAR 17 42` and
`RP: VECTOR 5 10 15 20`; the guarded runner checks exact records
and interpreted `CODE=0`, full JES step sequence and IEF142I messages.
The original BTA102 AWS SHA-256 remained unchanged:
`c3b235ca78d221432199adcde1f7a83aead4f76bab0e0eaa19d77c81d9912210`.
Private actual-MVS evidence:
`workarea/ta1b-operations/BTA102-track-b-go-20261119T121015Z-13509/`.
This establishes **restored executable-use PASS (qualified)**,
not load-module byte identity. See [Track B GO evidence](../../distribution/create-tape/ta1b-restored-go-evidence-20261119.md).

**TA.1 formal qualified acceptance candidate (19 November 2026):**
Track A independently exercised two logical standard-label datasets
on BTA101, restored and IEBCOMPR-verified both, and reviewed the
physical files `3,3,2,2,25,2,0`; the immutable BTA101 SHA was
preserved. Track B independently exercised `RECFM=U` load-library
selective IEBCOPY unload/restore on BTA102 (JOBS 9120/9136),
source/restored IEHLIST directory match (JOBS 9151/9152),
and the executed canonical MR10 scalar/vector case using the
**restored** `ICINT19` (JOB 9165).
Both bounded tracks now satisfy the actual MVS/Hercules acceptance
criteria on a **qualified** basis, with source-level evidence
summarized from owner-reported runner output; the assistant has
not independently inspected private raw JES/HETMAP artifacts.
No unsupported raw load-module byte equality is claimed.
**Owner approval of formal TA.1 closure is pending**; this is a
review-ready candidate, not a declaration of TA.1 CLOSED.
Release producer, recipient installer, complete distribution
acceptance, permissions and publication remain later marches.
See [TA.1 qualified acceptance candidate](ta1-qualified-acceptance-candidate-20261119.md).

**TA.1 — Multi-Dataset Tape Mechanics FORMALLY CLOSED (qualified), owner decision 19 November 2026:**
The owner directed **“Move to TA.1 closure without delay. Give me a handoff prompt for TA.2.”**
This expressly accepts the bounded **Track A PASS (qualified)** on BTA101:
two ordered standard-label logical datasets, independent MVS restore
and two IEBCOMPR RC=0000 verifications, file/label map
`3,3,2,2,25,2,0`, and unchanged BTA101 image SHA-256.
It also accepts the bounded **Track B PASS (qualified)** on BTA102:
IEBCOPY unload **JOB 9120**, restore **JOB 9136**,
source/restored IEHLIST matching **JOBS 9151/9152** with `ICINT19`
entry `000000` and attributes `02E2`, and restored
`HERC02.BCPL.TA1B.LOAD` scalar/vector execution
**TA1BGO JOB 9165**, 8 steps RC=0000, 3 restored
`ICINT19` calls and golden `RP:` records.
The tested AWS images retain their checksums and are **scratch
evidence, not releasable candidate media**. The assistant's
review rests on actual owner-reported MVS/Hercules runner results
and verified committed source, not a direct independent reading
of private JES/SYSPRINT/HETMAP files. Exact RECFM=U load-module
byte identity is unproven; TA.2–TA.8 obligations remain open.
**TA.1 is not to be reopened without demonstrated regression/defect.**
See [formal TA.1 closure](ta1-formal-qualified-closure-and-ta2-transition-20261119.md)
and [TA.2 kickoff](ta2-kickoff-20261119.md).

**TA.2 — Manifest-Driven Tape Producer, READY FOR DESIGN AND READ-ONLY PREFLIGHT (19 November 2026):**
Begin with the one TA.0 approved schema/inventory and producer/recipient
architecture, independently analyze actual MVS source DCB,
member selection/provenance and the TA.1 label/IEBCOPY evidence.
Agree on major producer, freeze/registry and validation choices
before implementing. No frozen candidate manifest or identity,
new VOLSER allocation, AWS image production, MVS tape operation,
installation or publication is authorized by this transition.
See [TA.2 kickoff](ta2-kickoff-20261119.md).

**TA.2 read-only MVS source-inventory checkpoint (19 November 2026):**
After correcting the live preflight's managed-`dspal stat` heading parser,
the owner reported `18/18 checked; 0 blocker(s); 76 unselected development
members`, with the full private read-only MVS evidence in
`workarea/ta2-source-preflight/20261119T140206Z-15135`.
All 127 curated PDS members are reported present; the 76 development
extras remain excluded from selection. A separate saved-evidence reviewer
and strict candidate evidence gate have been implemented and synthetic
tested, but have not re-reviewed these private files in the assistant
environment. No source bytes, legal provenance, isolated staging, tape
production or candidate identity is accepted by this checkpoint.
See the [TA.2 implementation record](../../distribution/create-tape/ta2-offline-producer-implementation-20261119.md).


**TA.2 staging capacity inspection prepared (19 November 2026):**
The new [read-only source-capacity preflight](../../distribution/create-tape/ta2-capacity-preflight-20261119.md)
chains the saved-source reviewer to a fresh `dspal stat` MVS
LISTDS/IEHLIST all-managed-dataset inventory. It refuses missing source
DCB/volume/track/high-water/directory observations and preserves private
SHA-256-pinned evidence. **94/94 synthetic TA.2 tests PASS** in the
assistant workspace; no actual new source-capacity inquiry or MVS staging
has occurred. Source VTOC high-water and directory allocations are planning
observations only, not exact curated-library footprint measurements.
No candidate identity or stateful production is authorized here.


**TA.2 source-capacity live checkpoint and staging worksheet (19 November 2026):**
The owner reported **18/18 source PDSes; 127 selected; 76 excluded; 0
blockers** from a real read-only MVS `dspal stat`/LISTDS/IEHLIST
capacity run, saving original private evidence at
`workarea/ta2-capacity-preflight/20261119T150315Z-16868`.
The assistant did not inspect the private numeric values.
The [TA.2 staging worksheet tool](../../distribution/create-tape/ta2-stage-plan-20261119.md)
now independently replays both saved source and capacity receipts,
checksum-checks their MVS reports and demands a fresh read-only capacity
match before writing a private, **non-executable** staging worksheet.
31/31 focused synthetic tests passed, but this new tool has **not**
been run on the owner's MVS. No staging DSN or `SPACE` size is approved;
no DASD/tape modification, release identity or VOLSER reservation is
authorized. TA.2 remains IN PROGRESS.

**TA.2 staging preflight PASS and selective-copy draft (19 November 2026):**
The owner reported `18/18 source PDSes; 127 selected; 76 excluded; 0
blockers` from a fresh read-only MVS stage-plan inquiry, with private
evidence at `workarea/ta2-stage-plan/20261119T155947Z-17087`.
The stage capacity allocations and underlying bytes were not inspected
by the assistant; the result does not authorize DASD writes. The
[TA.2 draft-only staging-deck implementation](../../distribution/create-tape/ta2-selective-staging-deck-20261119.md)
replays all original MVS receipts against the one canonical manifest,
then requires an independently approved isolated namespace and exact
target volumes/SPACE allocations before it can emit a JOB-less
18-IEBCOPY-step/127-SELECT draft. Its 42/42 new synthetic tests passed.
There is **no staging allocation map, JES execution, VOLSER reservation
or candidate tape**. TA.2 remains IN PROGRESS.

**TA.2 owner-approved namespace/VOLSER naming and target safety preflight (19 November 2026):**
The owner approved exactly `HERC02.BCPL.TA2STG.BT0003` through `BT0020`
for isolated staging and `BCnnnn` (`BC0001`–`BC9999`) for future,
distinct, non-reused **production tape** identities. No VOLSER was
reserved. The offline producer now rejects nonconforming candidate/registry
VOLSERs; the selective staging deck renderer refuses any other
staging namespace. The new [read-only MVS target-collision
preflight](../../distribution/create-tape/ta2-namespace-volser-and-target-preflight-20261119.md)
first replays the original owner-reported MVS source/capacity/stage-plan
receipts, then queries 18 destination names with TSO LISTDS and saves
a raw IEHLIST LISTVTOC report for a separately specified *proposed*
DASD volume. **69/69 tested focused staging/target synthetic cases PASS**
(43 staging + 26 target) in the assistant's repository-root workspace.
Nine additional direct VOLSER-pattern assertions PASS; the amended
offline-producer regression suite has not been rerun in that workspace.
No MVS stage data set, tape image, candidate reservation or allocated
DASD volume is accepted by these checks. TA.2 remains IN PROGRESS.

**TA.2 MVS catalog-absence checkpoint and VTOC evidence review (19 November 2026):**
The owner reported the real `ta2-target-preflight` result of
**18/18 absent staging DSNs** and one saved raw **TSO002 IEHLIST VTOC**
in `workarea/ta2-target-preflight/20261119T170234Z-17334`.
These are private read-only JES results, not assistant-reviewed raw
bytes. The new [independent saved-VTOC reviewer](../../distribution/create-tape/ta2-target-saved-vtoc-review-20261119.md)
validates original SHA-256 evidence and source/capacity/stage ancestry,
reconstructs formatted VTOC dataset-name inventory, optionally rechecks
two MVS read-only jobs and retains new private evidence. The assistant
tested **103/103 focused synthetic cases**; no live reviewer run or
free-DASD-space/fragmentation acceptance has yet occurred.
`TSO002` remains proposed only; no staging `SPACE` is authorized.
No DASD stage allocation, candidate identity/VOLSER reservation or
tape operation occurred. TA.2 stays IN PROGRESS.

**TA.2 saved VTOC FORMAT-1 parser correction (19 November 2026):**
The owner ran `ta2-target-review --live` twice against the immutable
`20261119T170234Z-17334` target evidence. Both runs refused before a
new MVS inquiry because the reviewer did not recognize FORMAT-1
dataset rows. Investigation found a mismatch between the new
reviewer's synthetic row format and the established
`tools/datasets/dspal-space.py` MVS IEHLIST parser: genuine
FORMAT-1 rows include DSCB type `1` between DSN and SER NO.
The reviewer and regression fixture were corrected without relaxing
catalog, VOLSER or staging collision refusals. **17/17 focused
isolated parser/inspector tests passed**; the private IEHLIST evidence
has not yet been successfully reviewed using the correction.
See the [TA.2 parser correction record](../../distribution/create-tape/ta2-target-format1-parser-correction-20261119.md).
No staging SPACE, DASD allocation, candidate VOLSER or tape operation
is authorized. TA.2 remains IN PROGRESS.

**TA.2 verified TSO002 VTOC checkpoint and draft SPACE sizing (19 November 2026):**
The owner reported a successful corrected `ta2-target-review --live`:
**18/18 catalog-absence checks, 30 formatted VTOC dataset rows**, fresh
MVS match and **16,045 IEHLIST-reported free tracks** on *proposed*
`TSO002`. Private receipt:
`workarea/ta2-target-review/20261119T181059Z-17632`. The assistant
did not inspect the private underlying reports. The new
[source-bounded offline/read-only staging SPACE planner](../../distribution/create-tape/ta2-source-bounded-staging-space-20261119.md)
replays the entire original evidence chain, proposes 18 explicit
primary/secondary/directory allocations against source PDS capacity,
requires combined primary+secondary to fit within half of the
MVS-reported free tracks, repeats source and target MVS inquiries, and
writes only ignored private draft allocations/JCL and checksums.
**40/40 new focused synthetic tests PASS.** Contiguous free extent
suitability, target-volume selection, SPACE approval, JES staging,
record fidelity and release-media acceptance remain open. No staging
PDS, candidate identity or VOLSER was allocated. TA.2 IN PROGRESS.

**TA.2 owner-reported source-bounded staging SPACE proposal and read-only readiness (19 November 2026):**
The owner reported one real MVS-backed proposal: 18 PDSes, 127 selected
members, **645 primary plus 65 secondary = 710 proposed tracks** on
TSO002, against **16,045 IEHLIST-reported free tracks**. Private
original evidence:
`workarea/ta2-allocation-plan/20261119T204153Z-17905`.
The 18 individual SPACE triples and VTOC extents are not in the
assistant context and are **not approved**. The new
[TA.2 stage readiness evidence gate](../../distribution/create-tape/ta2-stage-readiness-review-20261119.md)
independently replays exact saved allocation, canonical 127-member
IEBCOPY JCL, original MVS source/capacity/stage and target history,
then (with `--live`) repeats read-only source and target MVS
inquiries and prints all 18 proposed primary/secondary/directory
triples. **35/35 focused offline tests PASS**; a live MVS readiness
run is pending. No new DASD PDS, IEBCOPY staging submission, production
VOLSER or tape image has been created. TA.2 IN PROGRESS.

**TA.2 actual MVS staging-readiness pass and one-shot staging gate (19 November 2026):**
The owner reported the read-only `ta2-stage-readiness --live` PASS:
18/18 target PDSes, 127 selected members, fresh MVS source/catalog/VTOC
PASS, and TSO002 reporting 16,045 available tracks. The exact owner-reported
18 `SPACE=(TRK,(primary,secondary,directory))` triples total
**645 primary + 65 secondary = 710 proposed tracks**.
Private MVS evidence:
`workarea/ta2-stage-readiness/20261119T210718Z-18180`.
The exact proposals are source-controlled in
[TA.2 stage SPACE proposal](../../distribution/create-tape/ta2-stage-space-proposal-20261119.json)
as `PROPOSED_ONLY_NOT_APPROVED`. The new
[guarded one-shot preparation](../../distribution/create-tape/ta2-stage-once-design-20261119.md)
implements a read-only MVS preflight and a separately owner-gated
18-IEBCOPY one-shot mechanism, with an immutable source/evidence binding,
an absent-until-approved tracked approval file, TTY confirmation,
double fresh MVS recheck, and permanent no-retry attempt marker.
The owner's TSO002 allocation choice and each SPACE triple **have not
been approved for writes**, and no approval file has been committed.
The assistant's isolated **35/35 focused offline tests PASS**; the
actual saved private JES reports were not directly inspected by the
assistant and the one-shot runner has not run against live MVS.
No new PDS, release candidate, `BCnnnn` VOLSER or tape image was
created. TA.2 remains IN PROGRESS.

**TA.2 staging-volume-only owner approval (19 November 2026):**
The owner ran the read-only `ta2-stage-once --live` gate:
18/18 source/staging names and 127 selected members with fresh
MVS PASS; original evidence:
`workarea/ta2-stage-operations/20261119T234105Z-18708`.
The owner subsequently stated **“TSO002 approved.”**
The source-controlled
[volume-only decision](../../distribution/create-tape/ta2-stage-volume-approval-20261119.json)
therefore approves **TSO002 as the staging DASD volume**, but it
does **not** approve any of the 18 distinct `SPACE` triples,
state-changing IEBCOPY or tape operation. The
[allocation proposal](../../distribution/create-tape/ta2-stage-space-proposal-20261119.json)
now says `VOLUME_APPROVED_SPACE_AND_WRITE_UNAPPROVED`, while the
separate `ta2-stage-write-approval.json` remains deliberately absent.
The guarded staging runner enforces this distinction with
**42/42 focused local tests PASS**, including seven new approval
refusals. **No MVS staging writes were performed.** TA.2 IN PROGRESS.

**TA.2 owner-reported repeat staging write-gate PASS (19 November 2026):**
With **TSO002 volume-only approval** recorded on GitHub `main`,
the owner reran the guarded `ta2-stage-once --live` workflow and
reported **18/18 source and destination checks, 127 curated members,
fresh MVS PASS**, with private original evidence
`workarea/ta2-stage-operations/20261119T234948Z-18994`.
The run performed **read-only** source/catalog/VTOC inquiries;
it **did not** allocate a stage PDS, submit IEBCOPY, reserve a
production tape identity or modify media. All 18 proposed `SPACE`
triples and the state-changing one-shot submission **remain separately
unapproved**. TA.2 IN PROGRESS.

**TA.2 explicit 18-PDS SPACE and retryable IEBCOPY owner authorization (19 November 2026):**
After the owner-reported fresh MVS read-only staging checks (18/18,
127 selected, TSO002), the owner authorized **all 18 exact
source-bounded SPACE triples and a retryable IEBCOPY submission**.
The
[Git-tracked write approval](../../distribution/create-tape/ta2-stage-write-approval.json)
pins the original unchanged allocation proposal SHA-256, exact
readiness evidence, TSO002, 18 target PDSes and 127 selected
members. The improved [TA.2 staging runner and retry contract](../../distribution/create-tape/ta2-stage-once-design-20261119.md)
permit one manually invoked 18-step IEBCOPY job; retries are allowed
**only after each previous failed job is conclusively ended with
private pinned evidence and a fresh MVS inquiry proves all 18 stage
targets absent**. No automatic replays, PDS overwrite or
recovery of partially staged libraries is authorized. The runner
also performs the owner's specifically requested safe deletion
of the **empty, untracked, root-level** `FETCH_HEAD`, not
`.git/FETCH_HEAD`, as part of an authorized `--run`.
**54/54 focused synthetic tests PASS**; the write path has not
yet been run against MVS and no staged PDS or tape candidate
is claimed. TA.2 remains IN PROGRESS.

**TA.2 owner-reported staged PDS IEBCOPY success and simplified confirmations (19 November 2026 EST / 20 November UTC):**
The owner executed the already authorized `ta2-stage-once --run`
against approved TSO002, confirming the original
`TA2STAGE` **MVS JOB 9310, all 18 IEBCOPY steps RC=0000**
and 127 manifest-selected members. Exact original saved
evidence: `workarea/ta2-stage-operations/20261120T002516Z-19547`.
This is operator-reported MVS/JES success, **not yet independent
DCB, member directory, record-byte or load-module verification**;
no tape candidate or production VOLSER exists. The owner also
directed an operator-interaction rule: **zero typed confirmations
for read-only evidence probes**, and **one `Y` character** as the
maximum necessary interactive confirmation for separately
authorized state-changing submissions. The staging runner
now uses `[y/N]`, and the new
[read-only staged directory/DCB verifier](../../distribution/create-tape/ta2-staged-directory-verification-20261119.md)
replays the SHA256-sealed JOB 9310 receipt and asks MVS two
consolidated TSO `LISTDS` jobs to verify exact 18 PDS attributes
and 127-member inventories. **75/75 synthetic focused tests
PASS**; no new live MVS verification job has yet been run.
The accepted staging JOB 9310 must not be resubmitted.
TA.2 remains IN PROGRESS.

**TA.2 staged-success evidence replay correction (19 November 2026 EST):**
The owner's initial read-only `ta2-stage-verify --live` was
refused before any new JES inquiry because the shared immutable
attempt reader incorrectly invoked the failed-job validator on
the successful **JOB 9310** receipt. The
[verification design record](../../distribution/create-tape/ta2-staged-directory-verification-20261119.md)
documents the correction: validate successful receipts through the
full 18-step `validate_job` logic; validate failed receipts through
the existing conclusive-end rules; refuse unknown or altered results.
**Successful staged jobs remain ineligible for IEBCOPY retry.**
Focused offline checks passed **80/80**, including a true
SHA256-sealed JOB 9310-style success replay. No staging or tape
operation was repeated. **Live staged catalog/member verification
remains pending.** TA.2 IN PROGRESS.

## 1. Objective and product boundary

Deliver reproducible, independently installable releases. The **complete** configuration contains two usable, independent programming environments:

1. **Native Cambridge Compiler:** A ready-to-run, native System/370 compiler with its own source, supporting assembly, MVS build/link JCL, examples, verification procedures and the required Core Runtime and historical Base Library (`BLIB`).
2. **MR10 Kit Compiler:** A ready-to-run `ICINT19` with assembler source/build JCL; `SYNI`, `TRNI`, `CGI`, `BLIBI`, `ICLIB` INTCODE decks; supporting sources/libraries/JCL; 11 language demonstrations (`MRLANGDM`); 17 BCPL demonstrations (`MRBCDEMO`); and the standard 12-case regression panel (`MRREGRES`), including input data and expected results.

The native environment also includes the **Coroutine Support Library** (`coroutines.bcpl`, `coroutines.h`, `COROUTIN`) and its associated Core Runtime bridge `BCPLCO`; the three accepted optional **System Extensions** `BCPLDEMO`, `BCPLTIME`, and `BCPLQSAM`; and BCEX/BCRG v1 selection/registration instructions and assets. Coroutine Support remains logically distinct from historical `BLIB`. System Extensions are distributed, but remain optional at application link-edit time.

The two environments must be independently selectable, installable and usable; they do not share a binary ABI. Interpreted-versus-native coroutine equivalence is guaranteed only over the previously accepted common behavioral domain. Preserve accepted interfaces and prior milestone closures.

**Excluded/deferred:** `BCPLDEC` (indefinitely deferred); the unimplemented BCPL Standard Library; the interpreter-hosted/demoted Cambridge compiler `CAMBCOMP` unless separately approved; full development/reconstruction history and host-side Python, WSL, `dspal`, or Hercules tooling as *recipient* requirements.

The complete native-running Cambridge Compiler remains **unfinished**. A **release without the native compiler** is also owner-approved: it provides the complete independent MR10 compiler environment and accepted native Runtime/BLIB/Coroutine Support/System Extensions but must not claim a native compiler or its self-compilation. `CAMBCOMP` is not a native compiler substitute. The [subsequent owner decision](../../distribution/release-without-native-compiler-decision-20261116.md) supersedes the unconditional native-compiler publication gate.

## 2. Approved tape and source-of-truth architecture

- Preserve a single authoritative, Git-controlled, **per-release manifest** for selected inputs and member ownership, dataset attributes, source-to-tape-to-recipient mapping, validation, dependencies, declared `native_compiler: absent | included` capability, and ordered 1-based *logical MVS tape dataset* sequence. `config/dspal.yaml` describes development datasets; it is **not** the release-selection authority.
- All standard-label tape DSNs follow `BCPL.BTnnnn`, continuously numbered by logical tape dataset sequence. `BCPL.BT0001` is human-readable EBCDIC FB80 installation/bootstrap text; `BCPL.BT0002` is the installation JCL/procedure PDS unload; `BCPL.BT0003` onward is selected by the manifest. The `BT` number is **not** a Hercules physical file number.
- Producer and consumer installation materials must come from the same manifest. A recipient provides an authorized site-specific HLQ and receives MVS-native bootstrap, allocation, restoration, instructions and verification without Git, TSO, Python, WSL or `dspal`. Initial bootstrap is read-only.
- Initial design is a single standard-labeled AWS tape volume. A candidate receives a frozen Git SHA, reviewed release/version identity, newly reserved unique six-character VOLSER, ordered inventory, and SHA-256 checksum; use one cross-release version/VOLSER registry. Publish **only the exact image bytes that passed acceptance**, with separate owner approval.
- Existing accepted PDS/object-library round trips validate only bounded single-dataset behavior; they do **not** establish multi-dataset production, recipient installation or complete release acceptance.

## 3. Formal marches and acceptance gates

| March | Name | Acceptance gate |
| --- | --- | --- |
| **TA.0** | **Release Architecture, Inventory, and Manifest** | Reviewed schema, inventory method and ownership for each required source/member; exact DCB/transport requirements; producer/consumer mapping, dependency and uniqueness checks, reserved bootstrap positions, and native-compiler work-to-be-completed identified. Approve major architectural choices before implementing the producer/installer. |
| **TA.1** | **Multi-Dataset Tape Mechanics** | On explicitly approved new scratch media, write two ordered standard-label logical datasets, preserve the first while writing the second, inspect logical labels/physical filemarks, independently restore/compare both. Separately establish a `RECFM=U` load-library transfer, restore and executable-use path. Record retention, positioning and safe failure behavior using MVS/JES/Hercules evidence. |
| **TA.2** | **Manifest-Driven Tape Producer** | From frozen Git-controlled inputs and validated MVS source artifacts, produce a *new* AWS candidate with generated JCL, contiguous aliases and correct label sequence, independent inventory/readback/structure validation, checksum, provenance, and fail-closed immutable artifact handling. |
| **TA.3** | **MVS Bootstrap and Installation** | `BT0001` can be read on a recipient without BCPL; `BT0002` yields operable MVS-only installation jobs; site HLQ/allocation and overwrite policy validated; independently selectable MR10-only, native-only or combined install paths, all without developer tools. |
| **TA.4** | **MR10 Kit Compiler Distribution and Verification** | Installed `ICINT19` and its rebuild source/JCL operate independently; all 11 + 17 demos and the complete 12-case `MRREGRES` panel compile/run on MVS. Every case emits fixed `EXP:` expected records and distinct `RP:` actual records; a human reviews expected versus actual and `CODE=` for *all 12*, recording per-case PASS/FAIL and explicit sign-off. Preserve unchanged WSL automated `RP:`/`CODE=` checking, proven by its regression run. |
| **TA.5** | **Native Runtime, Libraries, and Extensions Distribution** | Restore/link/execute the Core Runtime, `BLIB`, `BCPLCO`/`COROUTIN` Coroutine Support and `BCPLDEMO`, `BCPLTIME`, `BCPLQSAM` from the distribution; prove correct object/source provenance, BCEX/BCRG selection, optional-link behavior, build procedures and relevant native tests. |
| **TA.6** | **Native Cambridge Compiler Distribution and Self-Compilation** | Mandatory for a candidate declaring `native_compiler: included`: the genuine native executable compiles its distributed source, assembles/links through IFOX/IEWL and runs the rebuilt compiler. No `CAMBCOMP` or MR10 substitution. If absent, mark this **candidate gate N/A**, not PASS or formal TA.6 closure. |
| **TA.7** | **Clean-Target Integration and Release Acceptance** | On an isolated clean target, verify MR10-only, native-only and combined installed profiles; human-review all 12 MR10 cases and test 11+17 demos plus native runtime/BLIB/coroutine/extension linkage/execution. Require native compiler self-compilation **only if included**. Retain JES/IFOX/IEWL/GO and tape/installation evidence. |
| **TA.8** | **Release Audit and Controlled Publication** | Audit provenance/redistribution, scope disclosure, version/VOLSER registry, documentation, checksum, manifest and evidence. With separate publication approval, publish exactly tested bytes. A verified release without the native compiler is eligible. |

**Milestone structure and march identifiers TA.0–TA.8 were owner-approved on 16 November 2026.** This approval establishes the work plan, not an accepted implementation, an MVS/tape write permit, or public-release authorization. No march is yet formally closed.

## 4. MR10 reporting and human verification — subsequent owner decision

The owner-approved [MR10 `EXP:` and human-verification decision](../../distribution/mr10-regression-exp-manual-verification-decision-20261116.md) **supersedes the previously proposed requirement for an MVS-resident automatic PASS/FAIL verifier** in the 16 November release payload decision, for the standard 12-case `MRREGRES` panel only.

Use `TEST:` to identify the test, `EXP:` for **fixed literal expected results**, and `RP:` for evaluated actual results. Keep `EXP:` text free of the substring `RP:`; the existing WSL runner collects lines containing `RP:` and compares them with tracked `.expected` golden files, and separately verifies interpreted `CODE=`. No unnecessary WSL runner changes. The `EXP:` display must match the independently retained golden records; do not generate expected values by repeating the computation under test.

On the recipient MVS system, a person must inspect all 12 cases against the adjacent `EXP:` lines, check the `ICINT19` completion `CODE=` (expected zero for the current standard panel), and retain a per-case review and a signed/identified overall verdict. **JES RC=0 is not a semantic PASS.** Human-reviewed divergence is a release failure, even though a separate automatic MVS comparator and nonzero semantic-mismatch step code are no longer required. Do not claim the source programs have already been updated or the manual procedure verified.

The earlier historical MR10 diagnostic/probe suites are not automatically part of the release; do not reclassify their known failures.

## 5. Dependencies, parallel work and critical path

The tape/installer path is **TA.0 → TA.1 → TA.2 → TA.3 → TA.7 → TA.8**. MR10 TA.4 and native library TA.5 can advance after inventory architecture review, in parallel with tape mechanics and producer work; their *installed-recipient* acceptance requires TA.3.

TA.6 depends on completion of the unfinished native-running Cambridge Compiler. **It is an unconditional TA.7/TA.8 gate only for a candidate with `native_compiler: included`.** Candidates declaring `absent` may proceed to clean-target acceptance and controlled publication after all included MR10/native-component/redistribution requirements and separate approval; they must not claim two compilers. The native compiler remains mandatory for any **complete** release.

The first TA.1 diagnostic experiment should use a **fresh, uniquely named scratch image**, two distinct fixtures approximating `BT0001` FB80 and `BT0002` IEBCOPY-PDS, explicit `LABEL=(1,SL)` and `LABEL=(2,SL)`, followed by label inspection and independent restore/comparison. Investigate `VOLUME=RETAIN`, `DISP=PASS`, MVS allocation/demount, step boundaries and positioning before execution; do not assume an append/resume protocol. Test load-library `RECFM=U` transport separately.

## 6. TA.0 open design decisions

**Owner-approved design direction:** curated exact-member inventories, one canonical per-candidate manifest, MR10-only/native-only/combined installation profiles, site-HLQ parameterization, non-reusable VOLSERs and immutable artifacts, and a releasable no-native-compiler configuration. See [TA.0 inventory/architecture](../../distribution/manifest/ta0-release-architecture-and-inventory.md) and [manifest schema](../../distribution/manifest/schema-v1-design.md). **TA.0 verification checkpoint:** [read-only provenance/JCL dependency review](../../distribution/manifest/ta0-provenance-and-dependency-audit.md) confirms 110 Git-backed selected members have existing paths, identifies 2 generated and 15 resident binary members needing source-to-MVS provenance, and finds development `HERC02` references in ten release-selected JCL members. The updated offline validator passes 24 synthetic-fixture tests; these are not MVS readback or redistribution approval. **Still open:** final candidate identity, native source/JCL provenance, executable site-specific HLQ JCL, transport/DCB evidence, multi-dataset retention/positioning, MR10 `EXP:` implementation/human review, redistribution audit. TA.1 is separately gated.

**TA.0 implementation checkpoint, 17 November 2026:** [Read-only provenance/JCL dependency review](../../distribution/manifest/ta0-provenance-and-dependency-audit.md) identifies all ten selected Git JCL jobs and their declared source references. GitHub source inspection found no unselected or cross-profile permanent-dataset dependencies, but all ten remain tied to the development HLQ and lack standalone JOB cards. The [JCL scanner](../../../tools/distribution/audit-jcl-dependencies.py) and offline tests document these dependencies; they do **not** prove recipient MVS operation. The MVS binary/readback and source-generation receipts, site-safe release JCL and redistribution decisions remain outstanding. **TA.0 is not formally closed.**

**Further TA.0 binary provenance checkpoint, 17 November 2026:** the [read-only 15-member build-chain audit](../../distribution/manifest/ta0-provenance-and-dependency-audit.md#6-binary-source-to-build-chain-and-saved-inventory-checks--17-november-2026) reconciles source/build JCL and `tools/reconstruction/verify.py` step contracts. Historical CO.5 acceptance is acknowledged but not reclassified as a verified new candidate image. `BLIBBLD` remains unshipped and source rebuild of historical `BLIB` or Coroutine Support from BCPL requires compiler functionality not supplied by the scoped release. No new resident binary or redistribution evidence was produced; **TA.0 remains IN PROGRESS**.

**Further TA.0 retained-evidence preflight, 17 November 2026:** the [read-only evidence intake contract](../../distribution/manifest/ta0-mvs-build-evidence-intake.md) defines SHA-256-pinned operator-supplied JES reports and exact member listings. The offline suite passes 73/73 synthetic tests; no actual MVS evidence, binary record bytes, DCB correspondence, or redistribution approval was supplied. **TA.0 remains IN PROGRESS.**

The approved single-manifest/bootstrap/naming rules, independent environments, and manual MR10 verification decision are binding. Other architecture details in this section remain **proposals**, not presumed owner approvals.

**TA.0 qualified binary evidence checkpoint, 17 November 2026:** The
[consolidated development-evidence reconciler](../../distribution/manifest/ta0-binary-evidence-reconciliation-20261117.md)
now passes against the saved MVS evidence: **14/14** selected FB80 objects,
**902** FB80 records / **72,160** decoded printer bytes; two original
pre-pagination receipt schemas were accepted without rewriting the private
files. JOB **9060** confirms `MR10_LOAD(ICINT19)` formatted directory metadata,
and JOB **9061** confirms development interpreter executable use on the
bounded eight-step scalar/vector case. **This is qualified development
evidence, not TA.0 closure or binary-source/tape acceptance.** Eight historical
build-job source/provenance receipts, generated `BLIB`/`COROUTIN` lineage,
recipient JCL transformation/target DCB, rights clearance, and owner review of
the proposed post-`BT0002` dataset order remain open. No tape write, new
VOLSER or publication is authorized by this checkpoint.

## TA.0 formal closure and TA.1 transition — 17 November 2026

Owner direction authorizes formal **TA.0 CLOSED (qualified)** at the
[17 November 2026 acceptance/transition record](ta0-formal-acceptance-and-ta1-transition-20261117.md).
The architecture and inventory design baseline and the owner-reported live
14-member FB80 reconciliation plus JOB 9060/9061 evidence are accepted
**only in their specified development scope**. Binary/source provenance,
rights clearance, transport verification, recipient JCL, final artifact
identity and release acceptance remain explicitly unproven and are assigned
to their existing later marches. The TA.0 design record is not a frozen
candidate manifest. TA.0 is not a retroactive claim of test/tape production.

**TA.1 — Multi-Dataset Tape Mechanics is READY FOR DESIGN/PREFLIGHT.**
Its [kickoff and acceptance tracks](ta1-kickoff-20261117.md) require both a
two-logical-dataset standard-label scratch tape roundtrip and a separate
`RECFM=U` load-library unload/restore/executable-use experiment.
**No scratch AWS media initialization, JCL submission that changes MVS state,
tape mount/write, dataset overwrite, VOLSER reservation or publication is
authorized by this closure.** Obtain separate explicit approval for the
specific safe scratch operation.

## 7. Safety, verification and authority

- GitHub `main` owns all source/JCL/specification/decision files; MVS 3.8J, IFOX, IEWL, JES and actual program execution own target-system evidence.
- Demand separate owner authorization for destructive MVS operations, tape initialization/writes, dataset installation, existing production object replacement, and release publication. Do not silently reuse VOLSERs or overwrite tape images.
- Fail closed on incomplete candidates; never automatically reinitialize, append, seek, remount or resume a possibly written tape. Use separate new identities for replacement candidates.
- Test source/JCL and offline checks before commits where possible; never commit/push without explicit approval. This document's recording is documentation-only.
- Preserve earlier accepted milestone closures and qualifications; a scratch round-trip is not release acceptance.

## Governing references

- [Approved expanded payload](../../distribution/release-payload-scope-decision-20261116.md)
- [MR10 reporting decision](../../distribution/mr10-regression-exp-manual-verification-decision-20261116.md)
- [Native Cambridge distribution design](../../distribution/native-cambridge-compiler-distribution-decisions-20261108.md)
- [Version/VOLSER design](../../distribution/release-version-and-volser-registry-decisions-20261108.md)
- [Multi-dataset experiment guidance](../../distribution/multi-dataset-tape-and-append-experiment-20261108.md)
- [Distribution overview](../../distribution/README.md)
- [Runtime/library nomenclature](../../architecture/runtime-and-library-nomenclature.md)


## TA.2 owner-accepted staging and focus on producer integration — 19 November 2026 EST

The owner accepted TA2STAGE JOB 9310 (18 IEBCOPY RC=0000, 127 selected members on TSO002) together with independent MVS LISTDS JOBS 9311/9312 (18 exact PDS DCBs/directories and 127 exact members). Original private evidence remains at `workarea/ta2-stage-operations/20261120T002516Z-19547` and `workarea/ta2-stage-verification/20261120T005732Z-20183`.

Owner engineering direction: trust established IBM MVS system utilities when their actual operations succeed; investigate failures when there is a concrete anomaly, not speculative corruption. The previously proposed 126-member IEBCOMPR panel and special load-module byte extractor are **not required routine staging gates** and are not promoted. Source-to-staging copy fidelity is accepted on the bounded IEBCOPY and directory/DCB results; no separate per-member byte hash is asserted. The independent **new AWS tape structure, label/position, restoration, checksum and provenance acceptance gates remain mandatory** because those test this project's producer integration.

The new read-only `create-tape/scripts/ta2-release-input-plan` derives the accepted BT0003–BT0020 source associations from the canonical TA.0 manifest and the saved JOBS 9311/9312 receipt; its 16/16 isolated tests passed. `BT0001` release-specific bootstrap, `BT0002` MVS-only installer, frozen candidate source/rights and version/VOLSER remain open. See [TA.2 accepted staging and release-input preparation](../../distribution/create-tape/ta2-accepted-stage-and-release-inputs-20261119.md). No candidate production, staging retry, tape initialization, remount, publication or owner authorization is inferred. **TA.2 remains IN PROGRESS.**

## TA.2 BT0001/BT0002 offline generator checkpoint — 19 November 2026 EST

The accepted BT0003–BT0020 stage result remains unchanged (MVS JOB 9310,
independent JOBS 9311/9312). Under the owner's trust-MVS-utilities
direction, source-to-stage byte recomparison remains unnecessary absent
an actual anomaly. The new [offline bootstrap/installer material tool](../../distribution/create-tape/ta2-bootstrap-installer-materials-20261119.md)
uses the frozen-candidate gate, validated canonical 20-position inventory,
candidate identity and planned `BCPL.BT0001` FB80 text and `BCPL.BT0002`
MVS-only installer PDS. It creates no MVS datasets or media. A proposed
18-step site-parameterized IEBCOPY restore template is not executable
until the recipient supplies site settings and the later installation
acceptance is demonstrated. **20/20 focused local synthetic tests PASS**.
No version/VOLSER has been reserved or production tape authorized.
**TA.2 IN PROGRESS**.

## TA.2 release-input pre-staging correction and MVS read-only gate — 19 November 2026 EST

A real preparatory/final-gate dependency cycle was identified: the strict
frozen-candidate gate requires actual MVS receipts for BT0001/BT0002,
but the old material generator would not emit them until that gate passed.
This is resolved by adding an **offline-only** `--prepare` path for a
proposed identity-complete candidate manifest, with the existing strict
`ta2-offline --candidate` retained for final production.
A proposed six-step IEBGENER/IEFBR14 JCL deck prepares two **new**
BT0001/BT0002 staging inputs on approved-volume TSO002, subject to a
**separate explicit MVS allocation/submission approval**. The read-only
`ta2-bootstrap-target-preflight --live` queries catalog/VTOC for
the two absent targets, retaining original JES evidence privately.
See [pre-staging design/evidence](../../distribution/create-tape/ta2-bootstrap-prestaging-mvs-preflight-20261119.md).
**43/43 assistant-workspace synthetic tests PASS; no new MVS execution,
candidate reservation, AWS media or recipient installation accepted.**
Earlier 18 PDS / 127 member staging remains accepted and untouched.
**TA.2 remains IN PROGRESS.**

## TA.2 BT0001/BT0002 read-only MVS receipt — 19 November 2026 EST

The owner ran `ta2-bootstrap-target-preflight --live` on GitHub main `3c97e6f7f0c943ca4f5268bd4922536ea697a008` and reported **2/2 proposed staging DSNs catalog-absent; TSO002 VTOC observed**, with unmodified private original MVS output at `workarea/ta2-bootstrap-target-preflight/20261120T025333Z-20572`. This is read-only preflight success, not space-allocation or production authorization; the assistant has not directly inspected that private raw report.

The new offline `scripts/ta2-bootstrap-preflight-review` reviews this exact kind of saved MVS receipt and the 31-track initial+one-secondary planning allowance (5+1 tracks for BT0001, 20+5 for BT0002). Its 14/14 focused synthetic tests pass, and **57/57** tests pass including the prior two bootstrap suites. No IBM utility internals are retested. The original accepted JOB 9310 and JOBS 9311/9312 results remain trusted and unchanged. See [MVS receipt review record](../../distribution/create-tape/ta2-bootstrap-preflight-review-20261119.md). Actual BT0001/BT0002 allocation, version/VOLSER reservation and full AWS candidate are **not** yet authorized or completed. **TA.2 IN PROGRESS.**

## TA.2 owner-reported read-only BT0001/BT0002 source-target preflight accepted — 20 November 2026 UTC

The owner reported MVS `LISTDS` and `IEHLIST` read-only preflight with **2/2** new staging DSNs absent and TSO002 VTOC observed; the independent saved-MVS reviewer reported **15,400 free tracks**, against a **31-track first primary plus one-secondary allowance**. Original evidence paths: `workarea/ta2-bootstrap-target-preflight/20261120T025333Z-20572` and `workarea/ta2-bootstrap-preflight-review/20261120T030402Z-20698`. Accept this bounded **preflight**, preserving actual IBM MVS utility results; do not repeatedly retest absent anomalies. Existing 18-PDS stage remains accepted. The proposed next release identity and two new staging allocations are listed in [the TA.2 owner decision proposal](../../distribution/create-tape/ta2-bootstrap-next-write-decision-proposal-20261120.md). **No** version/VOLSER reservation, BT0001/BT0002 write authorization, JES staging submission or AWS production approval is inferred. **TA.2 IN PROGRESS.**

## TA.2 bounded BT0001/BT0002 one-shot stage — owner approval, 20 November 2026

The owner approved the **one-shot, six-step** creation of only `HERC02.BCPL.TA2STG.BT0001` (PS/FB/80/800, TRK 5+1) and `BT0002` (PO/FB/80/800, TRK 20+5 with 10 directory blocks) on TSO002. Original read-only MVS LISTDS/IEHLIST checkpoint and saved review reported **2/2 names catalog-absent** and **15,400 free tracks**, against the 31-track initial-plus-one-secondary allowance. No catalog/DASD write occurred in this report.

The exact operation-only decision is Git-tracked at [`ta2-bootstrap-stage-approval.json`](../../distribution/create-tape/ta2-bootstrap-stage-approval.json); the new [`ta2-bootstrap-stage-once`](../../distribution/create-tape/scripts/ta2-bootstrap-stage-once) runner is fail-closed, non-retryable, requires source-controlled release identity and candidate manifest, reviews saved MVS evidence and performs a fresh read-only MVS absence/VTOC check before any submitted JES. The separate candidate ID/version/source SHA and VOLSER proposal **was not accepted by this operation-only response**, so no identity-approval file, manifest or production VOLSER reservation was created. **28/28 focused local tests PASS** including synthetic positive/failing MVS jobs; no new JES operation was run. Record: [TA.2 stage authorization](../../distribution/create-tape/ta2-bootstrap-stage-authorization-20261120.md). TA.2 remains **IN PROGRESS**; TA.0/TA.1 closures unchanged.

## TA.2 approved candidate identity and next MVS stage — 20 November 2026

The owner approved version `0.1.0-rc1`, candidate ID `BCPL-0.1.0-rc1`, source SHA `146ae09a58398c9b4d685500760f85592e770e1e` and production VOLSER `BC0001`. The canonical preliminary candidate manifest was derived from the accepted TA.0 20-position/127-member inventory unchanged; the single registry on `main` reserves BC0001 for this candidate and pins the manifest digest, and a separate identity-approval record binds the four values. Offline identity/inventory checks passed 10/10. This is an **approved identity and reservation, not a finished, provenance-accepted release or a tape artifact**.

The owner separately approved the exact **one-shot** six-step IEBGENER/IEFBR14 BT0001/BT0002 MVS staging on TSO002. The saved MVS LISTDS/IEHLIST preflight showed 2/2 catalog-absent and 15,400 reported free tracks. The existing guarded runner may now be used with the approved candidate manifest for that **DASD stage only**, with fresh preflight and permanent no-retry intent. **No staging JES job has yet been reported as executed; no repeat of the accepted JOB 9310 BT0003–BT0020 stage is authorized.** See [the identity and next MVS step](../../distribution/create-tape/ta2-approved-identity-and-bootstrap-stage-20261120.md). No AWS tape production, installation or publication is authorized. Per-member rights, lineage, MVS source receipts and full TA.2 producer acceptance remain open. **TA.2 IN PROGRESS.**

## TA.2 BT0001/BT0002 JOB 9317 stage and follow-up verification — 20 November 2026

The owner executed the separately authorized one-shot six-step creation of BT0001 (PS/FB/80/800) and BT0002 (PO/FB/80/800) on TSO002: **JOB 9317, 6/6 steps RC=0000**. Fresh preflight again reported both names absent before allocation and 15,400 IEHLIST free tracks. Saved original MVS evidence: `workarea/ta2-bootstrap-stage-operations/20261120T132013Z-21957`. This owner-reported execution proves the stage job completed successfully; directory/DCB acceptance remains open. **Never rerun the one-shot stage job**. Prior BT0003–BT0020 staging is unchanged.

The new [read-only bootstrap-stage verifier](../../distribution/create-tape/ta2-bootstrap-stage-job9317-and-verification-20261120.md) replays the original immutable JOB 9317 receipt and submits only `LISTDS LABEL` for both and `LISTDS MEMBERS` for BT0002 (exact INSTALL/DATASETS/RELEASE/RESTORE). **16/16 focused local synthetic tests PASS**. Live MVS verification is pending. The full 20-input candidate, final rights/provenance, strict producer gate and AWS tape write/readback are not accepted; no media production authorization is inferred. **TA.2 IN PROGRESS.**

## TA.2 all 20 producer staging inputs accepted — JOBS 9318/9319, 20 November 2026

The owner executed the read-only `ta2-bootstrap-stage-verify --live` after the one-shot JOB 9317 staging and reported **2/2 DCB PASS, 4/4 installer PDS members, TSO002, MVS PASS**. The actual MVS inquiry jobs were **catalog 9318 and members 9319**. Original private evidence remains at `workarea/ta2-bootstrap-stage-verification/20261120T132703Z-22108`. Together with accepted JOB 9310 and read-only JOBS 9311/9312, **all 20 logical input datasets are staged and their MVS DCB/directory interfaces verified** (one PS plus 19 PDSes; 127 selected payload PDS members and four installer members). Do not rerun any accepted staging or add hypothetical IBM utility fidelity tests.

The new [read-only all-input reconciler](../../distribution/create-tape/ta2-all-inputs-accepted-20261120.md) uses the accepted saved receipts plus the frozen TA.0 selection, Git-controlled candidate manifest and unique BC0001 registry reservation. Its 10/10 local synthetic tests PASS; it performs **no** new JES inquiry or tape operation. **TA.2 IN PROGRESS**: release rights/provenance, verified source/transfer metadata, strict final producer gate and AWS write/readback remain open. TA.3 has not begun.

## TA.2 selected Git-source freeze identity — 20 November 2026

The owner-reported MVS JOBS 9318/9319 PASS accepted the two remaining staged sources, completing **all 20 input DCB/directory staging checks** (JOBS 9310–9312 and 9317–9319). No more MVS utility fidelity tests are required absent a concrete anomaly.

In the next read-only source-lineage increment, a direct GitHub comparison of complete Git trees at approved source SHA `146ae09a58398c9b4d685500760f85592e770e1e` and then-current `main` `2f951e2ec1ce023173d258710e0bcc7b3114c14f` confirmed **110/110 selected Git-backed source blobs unchanged** (0 missing/0 drift). The newly committed `create-tape/scripts/ta2-source-lineage` generates an optional, derived, 127-member review worksheet from the original TA.0 validator and enforces frozen Git source identities, without changing the reserved candidate manifest or asserting redistribution permission. **21/21 local synthetic tests PASS**.

The two generated and fifteen resident object/load sources still require evidence linking actual BCPL/IFOX/IEWL build outputs; all 127 redistribution reviews remain unresolved. Historical tape materials are not automatically MIT-licensed by the repository. See [TA.2 frozen-source lineage record](../../distribution/create-tape/ta2-source-lineage-evidence-20261120.md). **No BC0001 AWS media production or new MVS submission was authorized or performed. TA.2 IN PROGRESS.**

## TA.2 MVS source-to-build evidence bridge — 20 November 2026

After owner-reported accepted staging of all 20 logical datasets and independent 110/110 Git-source blob freeze confirmation, the new `create-tape/scripts/ta2-build-chain-reconcile` reuses the authoritative TA.0 binary build-chain auditor. It binds the 15 selected binary targets to eight known build-job JCL contracts and the two generated source inputs, while retaining **zero accepted candidate-specific build receipts** and **127 unreviewed redistribution decisions**. It preserves the distinction between historical Base Library `BLIB` and separate Coroutine Support Library `COROUTIN`, the unshipped `BLIBBLD` development procedure, and the absent native-running compiler. **19/19 focused local synthetic tests PASS; no additional JES, DASD or tape operations occurred.** See [the reconciled source/build-evidence queue](../../distribution/create-tape/ta2-build-chain-reconciliation-20261120.md). Rights policy and existing retained BCPL/IFOX/IEWL receipts need review before a controlled final manifest/registry amendment. No `BC0001` production AWS operation is authorized; **TA.2 IN PROGRESS**. TA.0/TA.1 qualified closures unchanged.

## TA.2 compiler-source successor identity and layout — 20 November 2026

The owner approved the **`BCPL-0.1.0-rc2`** successor and
**`BC0002` VOLSER reservation** to distribute Cambridge Compiler
work-in-progress source in addition to the intact independently usable
MR10 Kit Compiler environment. The new frozen source commit is
`0a4f169f734e22acfa2a55653fd49942e38f9f05` and the canonical
successor manifest appends `BT0021` (`CAMB_SOURCE`, fifteen historical
members) and `BT0022` (`CAMB_DEMOTED`, eleven demoted, three bootstrap
support, and `SNOTICE`). The exact twenty previously selected datasets
are preserved in order, while their accepted MVS stage results remain
historically associated with `rc1`/`BC0001`.

The validator now distinguishes **Cambridge source included** from
**native Cambridge executable absent**. Both source PDSes belong to
`cambridge-source`, independent of the future native-running Compiler.
The MR10-only profile remains unchanged. This is a preservation-first
source distribution, not a claim of a blanket historical license;
individual redistribution-rights and MVS generator/build evidence remain
open. The historical MAKEOBJ/MAKELIB materials are archival, not
MVS-ready installation jobs.

The supplementary source-family and two-new-PDS selective IEBCOPY
**draft-only** generators do not submit JES or allocate DASD.
The accepted 20-input MVS staging remains intact and is not retested.
No stateful new MVS staging, initialized `BC0002` AWS tape,
native compiler executable, recipient installation, or public release
has been authorized or accomplished. **TA.2 IN PROGRESS**;
**TA.0 and TA.1 remain CLOSED (qualified)**.

## TA.2 owner correction: historical Cambridge source only — 20 November 2026

**This decision supersedes the preceding two-PDS rc2 source proposal.**
The owner retained `BCPL-0.1.0-rc2` and the reserved `BC0002`
VOLSER but expressly excluded the demoted Cambridge Compiler and
its filtered, instrumented, GitHub-specific development context
from the MVS distribution tape. The only extra release selection is
**`BT0021`: `CAMB_SOURCE` with 15 historical Cambridge source
members (PO/FB/80/800)**. There is no `BT0022` or
`CAMB_DEMOTED` release PDS. The existing 20 accepted inputs are
unchanged, making 21 logical datasets and 142 selected PDS members.

The historical sources remain distinct from an executable native
Cambridge Compiler: `cambridge_source: included` does not change
`native_compiler: absent`. The MR10 Kit Compiler retains independent
operation. Repository-specific demotion recipes, generated sections,
regression instrumentation and support are kept in GitHub for
reproduction in repository context rather than misleading MVS restore.

The owner reported a read-only `dspal stat CAMB_SOURCE` RC=0 and
`dspal stat CAMB_DEMOTED` RC=2, evidence path
`workarea/ta2-rc2-mvs-20261120T194333Z-855`. The report text
was not independently inspected here; neither return code
proves historical member contents or staging acceptance. Only
`CAMB_SOURCE` merits further rc2 MVS read-only directory and
record investigation. No new JES/DASD writing or BC0002 AWS
operation was performed or authorized by this design correction.
**TA.2 remains IN PROGRESS; TA.0 and TA.1 CLOSED (qualified).**

## TA.2 owner-reported CAMB_SOURCE empty PDS and source population preflight — 20 November 2026

The owner's read-only `dspal ls CAMB_SOURCE` inquiry returned **RC=0** and
`HERC02.BCPL.CAMBRIDG.SOURCE: (empty)`, preserving the actual saved
MVS listing at
`workarea/ta2-rc2-cambsource-20261120T202805Z-855/mvs-members.txt`.
This demonstrates an existing **empty source PDS**, not a ready or
staged `BT0021` input. The 15 historical Git sources were separately
inspected at the frozen rc2 source SHA; 15/15 are representable as FB80
and together contain 6,577 records.

The maintained `dspal populate CAMB_SOURCE --batch` mechanism can
partition the 15 members into **two** bounded IEBGENER jobs (8 + 7
members, 3,985 and 2,697 counted JCL cards), after its own live MVS
target-attribute checks. A new **read-only** historical-source preflight
checks frozen Git bytes and saved MVS directory identity before any
population decision. Python compilation and **10/10 focused synthetic
tests PASS**; no MVS job was submitted by this change.

**Separate owner authorization is required before population**, since
writing 15 members changes an MVS PDS. Never blindly retry a partial
batch. After population, verify exact MVS member names and records
before separately authorizing selective IEBCOPY staging to BT0021.
Existing BT0001–BT0020 staging remains accepted and untouched.
See [the source population decision/evidence](../../distribution/compiler-source/rc2-cambsource-empty-source-evidence-20261120.md).
**TA.2 remains IN PROGRESS.**

## TA.2 owner-authorized historical Cambridge source population — 20 November 2026

The owner explicitly **approved one-time source population** of the
15 archival Cambridge source members in existing
`HERC02.BCPL.CAMBRIDG.SOURCE`, after actual read-only MVS
`dspal ls CAMB_SOURCE` RC=0 confirmed **(empty)**.
This is limited to the original 15 historical members and does not
authorize the separate `BT0021` staging dataset, tape writing or
release publication.

The tracked
[one-shot MVS population runner](../../distribution/compiler-source/rc2-populate-cambsource-once.py)
validates the frozen source and release selection, guards the exact
empty MVS source directory, then calls the established `dspal`
population mechanism for **two** bounded IEBGENER batches (8+7).
It retains original MVS receipts under a persistent private
`workarea/ta2-rc2-cambsource-population-once/` attempt marker,
verifies both batch receipts and requires the exact 15-member
post-write directory. Failure or ambiguous state is **not** an
authorization for an automatic retry.

**8/8 new synthetic guard tests and 15/15 earlier compact rc2
tests PASS in the assistant workspace**; code was compiled and Git
object identities were checked. The MVS population has not yet
been executed by the owner or independently verified. Read-only
record-content verification and a separate BT0021 staging decision
remain future gates. See the
[formal source-population authorization](../../distribution/compiler-source/rc2-source-population-authorization-20261120.md).
**TA.2 IN PROGRESS; TA.0/TA.1 CLOSED (qualified).**

## TA.2 historical CAMB_SOURCE population complete — JOBS 9325/9326, 20 November 2026

The owner executed the single approved `rc2-populate-cambsource-once.py`
operation, reporting MVS **JOB 9325** and **JOB 9326** with
**15 historical member writes** and an exact **15/15 MVS directory
PASS** for `HERC02.BCPL.CAMBRIDG.SOURCE`. Original private evidence:
`workarea/ta2-rc2-cambsource-population-once/`. The preserved
post-write LISTDS member check establishes the bounded population
milestone, but record-level content matching was **not yet performed**.
Do **not** repeat this one-time operation.

The new [read-only record verifier](../../distribution/compiler-source/rc2-cambsource-record-readback.py)
reuses `dspal get` / MVS IEBGENER to compare all 15 restored member
texts against the frozen original Git sources, saving per-member MVS
job IDs, normalized hashes and text in private `workarea/` evidence.
**28/28 compact local synthetic rc2 tests PASS.** This text readback
cannot assert exact raw EBCDIC byte identity because the existing
get path strips trailing FB80 padding blanks. See the
[population acceptance and readback plan](../../distribution/compiler-source/rc2-population-accepted-readback-design-20261120.md).

The separate `BT0021` stage input is still **unverified and unwritten**.
No new AWS tape image, public release, rights approval or native-running
Cambridge Compiler is implied; previously accepted BT0001–BT0020
staging remains untouched. **TA.2 IN PROGRESS.**

## TA.2 read-only historical Cambridge source readback mismatch — 20 November 2026

Following accepted MVS **JOBs 9325/9326** and exact 15/15
`CAMB_SOURCE` directory inventory, the owner executed the
read-only `rc2-cambsource-record-readback.py`. It **HALTED** with
`MVS readback differs from frozen normalized source`, retaining
private original MVS evidence at
`workarea/ta2-rc2-cambsource-record-readback/`.
Record-content acceptance is therefore **open**. The mismatch
does not retroactively invalidate successful MVS directory staging
evidence, but `BT0021` must not be staged.

A new **offline, saved-evidence-only** diagnostic was tested
**10/10 PASS** against synthetic mismatch and tampered-receipt
cases. It reports the differing member/record/column and
content-independent codepoint/length metadata, without making
new JES calls or changing the original evidence. No new MVS
writing, re-population, IEBCOPY or AWS production has been
authorized or attempted. See
[the evidence boundary and diagnostic](../../distribution/compiler-source/rc2-readback-mismatch-evidence-20261120.md).
**TA.2 IN PROGRESS.**

## TA.2 Cambridge historical-source end-of-member diagnostic — 20 November 2026

The owner returned actual MVS saved-readback analysis: **BCPL**
normalized records match under JOB 9328; **BLIB** readback JOB 9329
returned 472 of its frozen 474 records, with the mismatch beginning
at the first of **two final empty records**. The frozen `LIBHDR`
and `TRNHDR` sources each also end in one empty record. The
readback cannot distinguish MVS source-PDS record loss from a
SYSOUT/extraction trimming effect.

Rather than relaxing record fidelity or repeating successful
source population, the project now has a **read-only QSAM
full-FB80 fingerprint verifier** in
`packaging/distribution/compiler-source/rc2-qsam-fidelity.asm`
and its JCL/verification runner. One temporary IFOX/IEWL build
reads exactly the 15 approved PDS members, counting physical
80-byte records and trailing all-blank records and computing
two raw CP037 byte checksums, compared with independently
calculated frozen historical source expectations. The runner
refuses source-selection drift, permanent destination updates,
or a repeated/overwritten evidence location. **10/10 focused
assistant-workspace synthetic tests PASS.** No actual assembler,
link-editor, or MVS verification result has been observed yet.

See [the end-of-member investigation](../../distribution/compiler-source/rc2-qsam-fidelity-investigation-20261120.md).
Do not repeat MVS JOBs 9325/9326 or stage `BT0021` until
the real QSAM results identify the cause. BT0001–BT0020 and the
rc2 manifest/BC0002 registry are unchanged.
**TA.2 IN PROGRESS.**

## TA.2 MVS JOB 9330 empirical source-reader mapping — 20 November 2026

The owner executed read-only IFOX/IEWL/QSAM **JOB 9330**.
All 15 historical Cambridge source members have **exact
expected 80-byte record counts and trailing blank counts**.
The earlier `dspal get` text readback was responsible for
omitting `BLIB`'s two blank tail records; no PDS repair
or repeat of accepted population JOBs 9325/9326 is justified.

The reported **7/15 raw CP037 checksum PASS** can be
fully explained by three actual TK5/Hercules reader byte
substitutions: `|` **4F→6A**, `[` **BA→AD**, `]`
**BB→BD**. Assistant-side reconstruction of all 15
historical source FB80 byte streams under this narrow
empirical translation profile matches **15/15 actual
MVS JOB 9330 record counts, trailing blanks, additive
sums and FNV-1a fingerprints**, including all eight
initially failing members. This establishes a compelling
transport-fidelity explanation, **not literal CP037
byte equality**.

A new fail-closed, read-only saved-JES reconciliation
script, with **10/10 focused assistant-workspace tests
PASS**, will independently verify the preserved full
MVS report and receipt before documenting a reconciled
result. See
[JOB 9330 transport evidence and pending source-encoding decision](../../distribution/compiler-source/rc2-qsam-job9330-transport-reconciliation-20261120.md).
The owner must choose whether the final release accepts
and documents the reader's observed source encoding or
requires literal CP037 correction. No source-PDS rewrite,
BT0021 IEBCOPY staging or BC0002 tape production
has been authorized. **TA.2 remains IN PROGRESS.**

## TA.2 JOB 9330 original MVS evidence reconciled — 20 November 2026

The owner executed the committed saved-evidence tool
`rc2-qsam-reconcile-transport.py --saved-job9330`, reporting
**RC=0** and **15/15 full FB80 member fingerprints reconciled**,
comprising **6,577 historical Cambridge source records**. This
verification cross-checked the preserved JOB 9330 summary,
actual JES report and original failed CP037 receipt against the
frozen historical Git source. The original MVS QSAM examination
confirmed **15/15 physical record counts and trailing blanks**.
The only identified differences in expected byte fingerprints
were the MVS reader substitutions `|`: 4F→6A, `[`: BA→AD,
and `]`: BB→BD. Original literal CP037 matching remains
**7/15**, while **15/15** match the observed transport profile.
This accepts the actual-source-transport verification on a
**qualified** basis; it does not claim universal EBCDIC codepage
identity or collision-free byte equality.

Source PDS population in JOBs 9325/9326 is accepted; no
repopulation or adjustment to BT0001–BT0020 is needed.
A [formal acceptance and encoding-policy proposal](../../distribution/compiler-source/rc2-job9330-reconciliation-acceptance-and-encoding-decision-20261120.md)
recommends preserving the verified native MVS bytes through IEBCOPY
instead of rewriting the PDS to host CP037. **That significant
design choice is not yet approved by the owner**; the `BT0021`
staging PDS has not been written and requires separate authority.
Source redistribution rights and final recipient installation
remain independent open release gates. The `BCPL-0.1.0-rc2`
21-dataset manifest and reserved `BC0002` identity remain
unchanged. **TA.2 IN PROGRESS.**
