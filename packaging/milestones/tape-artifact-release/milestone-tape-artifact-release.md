# Milestone — Tape artifact release

**Project:** BCPL for MVS 3.8 Reconstruction  
**Status:** **TA.0 CLOSED (qualified); TA.1 CLOSED (qualified); TA.2 — Manifest-Driven Tape Producer CLOSED (qualified); TA.3 — MVS Bootstrap and Installation CLOSED (qualified); TA.4 — MR10 Kit Compiler Distribution and Verification FORMALLY CLOSED by owner direction, 23 November 2026 EST; TA.5 — Native Runtime, Libraries, and Extensions Distribution CLOSED (qualified); TA.6 N/A for RC4; TA.7 — Clean-Target Integration and Release Acceptance OPEN / IN PROGRESS.** Candidate: `BCPL-0.1.0-rc4` / `BC0004`; original `BC0003` preserved.
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

The complete native-running Cambridge Compiler remains **unfinished**. A **release without the native compiler** is also owner-approved: it provides the complete independent MR10 compiler environment and native Runtime/BLIB/Coroutine Support/System Extensions distributed as work in progress without functional release acceptance until the full native compiler is available; it must not claim a native compiler or its self-compilation. `CAMBCOMP` is not a native compiler substitute. The [subsequent owner decision](../../distribution/release-without-native-compiler-decision-20261116.md) supersedes the unconditional native-compiler publication gate.

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
| **TA.4** | **MR10 Kit Compiler Distribution and Verification** | Installed `ICINT19` and its rebuild source/JCL operate independently; all 11 + 17 demos and the complete 12-case `MRREGRES` panel compile/run on MVS. Every case emits fixed `EXP:` expected records and distinct `RP:` actual records; a read-only automated verifier compares all 12 `TEST:`/`EXP:`/`RP:`/`CODE=` outcomes against pinned goldens and seals per-case PASS/FAIL evidence without human signatures. Preserve unchanged WSL automated `RP:`/`CODE=` checking, proven by its regression run. |
| **TA.5** | **Native Runtime, Libraries, and Extensions Distribution** | Verify distribution inventory, preservation and installation of Core Runtime, `BLIB`, `BCPLCO`/`COROUTIN` Coroutine Support and `BCPLDEMO`, `BCPLTIME`, `BCPLQSAM`, including source and supporting materials. For candidates without the full native compiler, defer native rebuild, object reproducibility, application generation, linkage, execution and regression; functional release testing is MR10-only. See the owner-directed scope decision below. |
| **TA.6** | **Native Cambridge Compiler Distribution and Self-Compilation** | Mandatory for a candidate declaring `native_compiler: included`: the genuine native executable compiles its distributed source, assembles/links through IFOX/IEWL and runs the rebuilt compiler. No `CAMBCOMP` or MR10 substitution. If absent, mark this **candidate gate N/A**, not PASS or formal TA.6 closure. |
| **TA.7** | **Clean-Target Integration and Release Acceptance** | On an isolated clean target, verify MR10-only, native-only and combined installed profiles; automatically verify all 12 MR10 cases against independent goldens and test 11+17 demos. Native runtime/BLIB/coroutine/extension functional tests and native compiler self-compilation are required **only when the full native compiler is included**; otherwise native components are installation-only work in progress. Retain JES/IFOX/IEWL/GO and tape/installation evidence. |
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

## TA.2 historical System/370 BCPL character set and Hercules mapping research — 20 November 2026

Further primary-source investigation establishes that the original
Richards Cambridge transport-tape/compiler PDS files were **EBCDIC**.
Ken Yap recorded EBCDIC-to-Unix translation problems; Nordier
later corrected source character mappings. The surviving
`MR10.PRINT(MANUAL)` Appendix C defines the historical 370
BCPL values `|` X'4F', `[` X'42', and `]` X'43'.
These differ from **both** literal CP037 and the measured
current Hercules reader mapping.

The published traditional Hercules `default` ASCII-to-EBCDIC
table maps `|`→6A, `[`→AD and `]`→BD exactly as
JOB 9330 measured. Hercules `CODEPAGE`, its no-argument
`codepage` panel query, the `HERCULES_CP` environment
fallback, and 3505 `ascii`/`ebcdic` reader settings govern
input conversion. No MVS 3.8 global source-PDS CCSID
setting establishes compiler lexical semantics. `IEBPTPCH`
`PRINT TOTCONV=XE` and the existing IFOX/QSAM reader
can independently inspect raw source bytes.

See [primary historical and Hercules research](../../distribution/compiler-source/ta2-historical-ebcdic-and-hercules-research-20261120.md).
**Revise the preceding conditional recommendation:** preserving
the verified current MVS bytes through IEBCOPY is suitable for
source-only archival transport **only if the bytes are clearly
documented**; it must not be presented as evidence that the
historical Cambridge lexer accepts all intended punctuation.
The exact deployed `CODEPAGE` remains unqueried. Compiler
character handling and source-language compatibility remain
an **open design gate**. No source rewrite, BT0021 stage,
media operation or manifest modification is authorized.
**TA.2 IN PROGRESS.**

## TA.2 BT0021 consolidated read-only MVS preflight implementation — 20 November 2026

Following qualified accepted historical `CAMB_SOURCE` record-level
fidelity from JOB 9330 (15/15 members, 6,577 FB80 records under the
observed Hercules reader translation), a new
[BT0021 read-only preflight](../../distribution/compiler-source/rc2-bt0021-readonly-preflight-design-20261120.md)
has been implemented for **the sole new staging target**
`HERC02.BCPL.TA2STG.BT0021`, TSO002. It replays
the original saved JOB 9330 MVS report/receipt and the separate
reconciliation receipt against the frozen source/rc2 manifest; the
existing selective IEBCOPY draft is validated, **not submitted**.
Only on explicit `--live` execution does it submit one read-only
MVS catalog LISTDS and one read-only IEHLIST LISTVTOC, preserving
their original reports, jobs and a SHA-256-sealed private receipt
under repository `workarea/`. A no-argument Hercules `codepage`
panel inquiry is captured as diagnostic only. **15/15 focused
assistant-workspace synthetic tests PASS** and Python syntax checks
pass. No new MVS inquiry has yet occurred.

This does not reverse qualified acceptance of JOB 9330 or open
BT0001–BT0020 for restaging. Actual MVS target preflight, the
historical-source encoding policy, separate owner authorization for
BT0021 IEBCOPY staging, rights/provenance, the final strict producer
gate and BC0002 AWS construction/independent roundtrip remain
**open**. The 21-dataset `BCPL-0.1.0-rc2` manifest and
`BC0002` reservation are unchanged. **TA.2 IN PROGRESS.**

## TA.2 BT0021 actual MVS preflight accepted; guarded stage implementation — 21 November 2026 EST

The owner ran `rc2-bt0021-preflight.py --live` after
`83ef858ce26ef346a2b89275eeff831d85d86b45`, returning
**RC=0**. Actual **MVS JOB 9331** (LISTDS) confirmed
`HERC02.BCPL.TA2STG.BT0021` catalog-absent and
**MVS JOB 9332** (IEHLIST) observed TSO002 VTOC with no
target collision. Original saved raw JES material is
`workarea/ta2-rc2-bt0021-preflight/20261121T051500Z-24489`.
The Hercules panel `codepage` response is preserved **unparsed**.
This is a target preflight PASS, **not** a new dataset or an
approved source-byte policy; original JOB 9330 source fidelity
remains 15/15 qualified under measured transport encoding.

The separately gated one-shot
[BT0021 staging runner and approval proposal](../../distribution/compiler-source/rc2-bt0021-stage-authorization-proposal-20261121.md)
are now implemented. The exact 15-member selective IEBCOPY,
frozen source/JOB 9330 evidence, original sealed JOBS 9331/9332
receipts, fresh MVS absence/VTOC checks, explicit
operator confirmation, permanent no-retry intent, and
actual JES RC/IEF142I checks have **16/16 focused
assistant-workspace synthetic tests PASS**. A separately
committed, owner-authorized `rc2-bt0021-stage-approval.json`
is required for any new write and **does not yet exist**.
The source-only archival preservation of current MVS bytes,
rather than historical compiler-lexer compatibility, is
proposed but not approved. BT0001–BT0020 remain accepted,
and no BC0002 tape construction, publication, rights approval,
or new IEBCOPY job has occurred. **TA.2 IN PROGRESS.**

## TA.2 owner-approved archive-byte policy and one-shot BT0021 stage — 21 November 2026 EST

The owner explicitly approved **both** consequential decisions following actual
read-only MVS JOBS **9331 (LISTDS)** and **9332 (IEHLIST)** and qualified
source-record verification JOB **9330**:

1. Preserve the **existing Hercules-translated FB80 bytes** of the 15
   historical Cambridge source members in `BT0021` without converting
   them to literal CP037. This is the **source-only archival transport**
   representation; it is **not** a claim that the native Cambridge
   Compiler accepts the historical lexical punctuation or that the
   source PDS uses universal CP037 or historical MR10 EBCDIC bytes.
2. Authorize **exactly one** guarded IEBCOPY staging operation creating
   `HERC02.BCPL.TA2STG.BT0021` on **TSO002**, sourcing only
   `HERC02.BCPL.CAMBRIDG.SOURCE` and selecting the release's
   exact 15 historical members. The original CAMB_SOURCE remains read-only.

The approval is tracked as
[`rc2-bt0021-stage-approval.json`](../../distribution/compiler-source/rc2-bt0021-stage-approval.json)
and is constrained to `BCPL-0.1.0-rc2` / reserved `BC0002`,
the accepted read-only MVS evidence directory
`workarea/ta2-rc2-bt0021-preflight/20261121T051500Z-24489`,
JOBS 9331/9332, 6,577 original source records and an immutable
no-retry submission-intent marker. The already tested
[`rc2-bt0021-stage-once.py`](../../distribution/compiler-source/rc2-bt0021-stage-once.py)
must replay original saved MVS evidence, require fresh LISTDS/IEHLIST and
operator confirmation, and validate exactly one real MVS IEBCOPY step;
it must never automatically retry an ambiguous or failed submission.

**Authorization is for the BT0021 stage operation only.** It does not
authorize modifying `CAMB_SOURCE`, restaging `BT0001`–`BT0020`,
writing/mounting/initializing the `BC0002` AWS tape, installing to
another MVS system, changing release rights, or publication.
The owner's approval **does not establish that IEBCOPY has executed**:
as of this record, no BT0021 staging JOB has been reported.
Inspect actual JES result before independent directory/DCB verification.
**TA.2 — Manifest-Driven Tape Producer remains IN PROGRESS.**

## TA.2 BT0021 MVS stage-input acceptance and 21-position preview — 21 November 2026 EST

The owner reported the one authorized **TA2C21ST IEBCOPY JOB 9335 RC=0000** and separate **LISTDS LABEL JOB 9336**, independently observing `HERC02.BCPL.TA2STG.BT0021` on TSO002 as PO/FB/80/800. The LISTDS MEMBERS query returned exactly the 15 historical Cambridge source names. Original private receipts are preserved under `workarea/ta2-rc2-bt0021-stage-operations/20261121T124159Z-25452` and `workarea/ta2-rc2-bt0021-verification/20261121T130011Z-23628`. See [qualified BT0021 acceptance](../../distribution/create-tape/ta2-bt0021-qualified-acceptance-20261121.md). **BT0001–BT0021 are accepted as staged MVS input datasets (qualified)**. The runner's irreversible attempt marker must not be deleted or replayed.

The [rc2 producer preview](../../distribution/create-tape/ta2-rc2-producer-preview-20261121.md) reuses the canonical TA.2 offline renderer to propose a 21-position JOB-less deck. Assistant-workspace syntax and eight focused offline tests passed. It **does not authorize** AWS initialization, mounting, writing, installation or publication. Historical Cambridge lexical encoding compatibility and redistribution rights remain unresolved. **TA.2 remains IN PROGRESS.**

## TA.2 rc2 Hercules 0480 read-only observation and combined media preflight — 21 November 2026 EST

The owner ran `tools/mvs/mvs-console tape status 480` from GitHub main and reported RC=0, observing Hercules `HHC02279I 0:0480 3420 * IO[31] maxsize=0 eotmargin=128K deonirq=N`. The emulator's device 0480 therefore reported **no mounted image at the observed instant**, but MVS guest allocation/ready status was not observed. A new [rc2 combined read-only media preflight](../../distribution/create-tape/ta2-rc2-media-preflight-20261121.md) verifies the canonical rc2 manifest/JCL preview, then on explicit `--live` performs only Hercules DEVLIST and MVS D U,TAPE inquiries, retaining SHA256-sealed private evidence. **23/23 combined rc2 preview/media synthetic tests PASS** in the assistant workspace. This is not a new AWS artifact or a media-write authorization. No accepted BT staging is reopened. TA.2 remains **IN PROGRESS**.
## TA.2 rc2 21-dataset private AWS producer and independent HETMAP reviewer — 21 November 2026 EST

The owner reported an actual **read-only** rc2 device preflight PASS: Hercules **0480 empty**, MVS **480 O-NRD**, RC=0, with the private, retained receipt at `workarea/ta2-rc2-media-preflight/20261121T133703Z-25915`. This observation is not a media write authorization.

A new [guarded rc2 candidate producer and independent AWS reviewer](../../distribution/create-tape/ta2-rc2-guarded-producer-20261121.md) have been implemented under `packaging/distribution/create-tape/scripts/`. The producer uses the canonical rc2 manifest and existing JCL renderer for **21 ordered SL datasets (1 IEBGENER; 20 IEBCOPY, 146 selective member cards)**, replays the preserved accepted MVS stage receipts, and implements a **permanently one-shot** image initialization/mount/write path with explicit owner confirmation, exact Git-committed approval, source/DASD/device/catalog/VOLSER guards, JES 21-step verification and independent HETMAP checks. The reviewer independently validates ordered VOL1/HDR1/HDR2/EOF1/EOF2 labels, 21 dataset names/sequences, 64 physical tape files and nonempty payloads. **60/60 combined rc2 offline tests PASS** in the assistant's workspace, including synthetic refusal paths. No actual 21-dataset MVS tape operation has run.

**The required `ta2-rc2-media-write-approval.json` is deliberately absent**, so `--run` is disabled. The accepted BT0001–BT0021 staging remains immutable. Unresolved Cambridge source rights, native-running compiler absence, private candidate media, full restore, clean-target installation and release publication remain distinct gates. **TA.2 — Manifest-Driven Tape Producer remains IN PROGRESS.**

## TA.2 owner-approved single private BC0002 AWS production — 21 November 2026 EST

Following a real owner-reported read-only **Hercules 0480 empty / MVS unit 480 O-NRD** PASS, the owner explicitly approved **one private BCPL-0.1.0-rc2/BC0002 candidate build**: new `mvs-state/tape/bcpl-0.1.0-rc2-BC0002.aws`, exactly 21 standard-labeled datasets, one guarded `TA2RC2WR` job, no automatic retry. The [committed media-write approval and detailed boundary](../../distribution/create-tape/ta2-rc2-private-build-authorization-20261121.md) bind the exact JOB-less producer JCL SHA-256 `85eca6f3e1e83c2d0e476f24870a20664bde2a50e2de8653606bfa351af54b4f`, the frozen candidate identity and permanent attempt marker. The writer now seals the original private JES/HETMAP output in `workarea/`; **62/62 assistant-workspace synthetic tests PASS**. **Only the private initialization/mount/single write is authorized.** No image, MVS job, clean-target install or independent AWS readback has been reported under this approval, and release publication/provenance rights remain unresolved. **TA.2 IN PROGRESS.**

## TA.2 BC0002 original media-inventory refusal and corrected VOL1 gate — 21 November 2026 EST

The owner ran the previously approved private rc2 candidate producer, which returned **RC=2** while inspecting existing `bcpl-objtest-20261108-01.aws`, before the no-retry write marker, image initialization, mount or JES submission. The original SHA256-sealed refusal evidence is `workarea/ta2-rc2-production-operations/20261121T145906Z-26113`; the underlying private HETMAP report has not been directly inspected by the assistant. The producer's original parser incorrectly required one occurrence of `Volume Serial` across an entire standard-label tape, even though HDR1/EOF1 labels repeat the physical VOL1 serial. The [incident and qualified defect correction](../../distribution/create-tape/ta2-rc2-prestateful-halt-analysis-20261121.md) preserve this distinction without claiming BC0002 had been reused. The corrected code and 73/73 assistant-workspace focused offline tests have passed. A new incident-specific owner authorization remains **absent**; no automatic restart, AWS tape creation, restoration or publication is approved. **TA.2 IN PROGRESS.**

## TA.2 owner-approved incident-bound conditional BC0002 attempt — 21 November 2026 EST

The owner approved **one new conditional pre-stateful private `BCPL-0.1.0-rc2` / `BC0002` attempt** after the earlier saved HETMAP inventory refusal. The [new recovery approval](../../distribution/create-tape/ta2-rc2-recovery-authorization-20261121.md) is committed and binds the original sealed incident, exact AWS basename, reserved VOLSER, and unmodified 21-position JCL hash. The producer now requires the original SHA256-sealed incident to exist, confirms no existing stateful attempt marker/candidate media and no genuine `BC0002` VOL1 collision, then repeats fresh media/MVS catalog/drive preflight before operator-confirmed initialization/mount and one 21-step JES write. **74/74 assistant-workspace focused rc2 tests PASS**, including a new negative test that forbids silently bypassing the original incident gate. No AWS candidate or new JES job has been reported under this renewed authorization. Tape restoration, clean-target install and publication are still outside scope. **TA.2 IN PROGRESS.**
## TA.2 owner-directed short Y/N confirmations — 21 November 2026 EST

The owner directed that both interactive confirmations for the already approved one-shot private `BC0002` producer use **`[y/N]`** instead of typed phrases. The two irreversible boundaries remain separate: initial image creation/mount and later `TA2RC2WR` 21-step JES submission. Only `Y`/`y` proceeds; No/blank/other answers refuse without automatic cleanup, rerun or recovery. The [recovery authorization record](../../distribution/create-tape/ta2-rc2-recovery-authorization-20261121.md) now documents this operator-interface amendment. The source-controlled JCL hash and both authorizations are unchanged. **76/76 focused offline tests PASS**; actual MVS media production remains pending. **TA.2 IN PROGRESS.**

## TA.2 second pre-stateful BC0002 inventory halt — 21 November 2026 EST

The owner reported `TA.2 RC2 AWS WRITE HALTED: HETMAP label contradicts physical VOL1 serial: HDR1` (RC=2), with original private evidence at `workarea/ta2-rc2-production-operations/20261121T155143Z-26237`. The code path halted during existing-media HETMAP inventory, **before image creation, permanent attempt marker, HETINIT, mount or JES submission**. The earlier refusal remains preserved. `VOL1` is the actual physical volume identity; the existing-media guard must not require the unrelated data-set serial field on existing `HDR1`/`EOF1` labels to equal `VOL1`. The [incident record and correction](../../distribution/create-tape/ta2-rc2-second-prestateful-halt-20261121.md) add read-only replay of both SHA256-sealed original incidents, fresh existing AWS physical VOLSER inspection and MVS/Hercules display verification in one `--inspect-media` operation. **82/82 focused rc2 offline tests PASS**. A *third* write is **not** authorized; a separate incident-bound owner approval file remains absent, and no existing media or accepted stage inputs were altered. **TA.2 IN PROGRESS.**

## TA.2 actual owner-reported rc2 read-only media inspection PASS — 21 November 2026 EST

The owner executed the committed `ta2-rc2-produce-once --inspect-media` after two pre-stateful `BC0002` inventory refusals. The runner returned **RC=0**, independently replayed **both sealed refusal receipts**, identified physical `VOL1 BTO001` for the previously rejected `bcpl-objtest-20261108-01.aws`, scanned **five existing tape images**, and confirmed **Hercules 0480 empty** through the read-only Hercules/MVS display inquiries. Private sealed evidence: `workarea/ta2-rc2-media-inspection/20261121T222712Z-26883`. See [the qualified inspection acceptance record](../../distribution/create-tape/ta2-rc2-media-inventory-qualified-acceptance-20261121.md). The assistant verified the committed source logic and the owner's terminal PASS but did not directly inspect private raw HETMAP/JES contents. No candidate image, permanent write marker, mount, tape write or JES job is reported. The collision-parser issue is **resolved for the inspected media at the inspected time**. A separately authorized third private candidate write remains pending; the absent Git approval file continues to **block `--run`**. **TA.2 IN PROGRESS.**

## TA.2 new owner-approved private BC0002 production attempt — 21 November 2026 EST

After the qualified owner-reported read-only `--inspect-media` PASS at `workarea/ta2-rc2-media-inspection/20261121T222712Z-26883`, the owner explicitly authorized one further **private `BC0002` tape-production attempt**. The exact [third-attempt authorization and pre-stateful safety correction](../../distribution/create-tape/ta2-rc2-third-attempt-authorization-20261121.md) bind both sealed prior refusals, the original sealed five-image inventory, unchanged frozen 21-position/JCL digest `85eca6f3e1e83c2d0e476f24870a20664bde2a50e2de8653606bfa351af54b4f`, and new `ta2-rc2-after-second-halt-approval.json`. In the producer, the first and post-confirmation existing-media scans now have **distinct exclusive-create evidence names**, avoiding a certain `O_EXCL` collision, and any differing number of images prevents the write. **14/14** additional isolated executable Python checks PASS in the assistant workspace; the producer test suite has added regression coverage. The two `[y/N]` confirmations, immutable once-only attempt marker, and separate MVS/JES/HETMAP verification are retained. No actual AWS image or JES write is reported under the new authorization yet. No release publication, rightsclearance or clean-recipient restore is implied. **TA.2 IN PROGRESS.**

## TA.2 BC0002 stateful write and HETMAP file-map audit — 21 November 2026 EST

The owner performed **one** newly authorized private `BCPL-0.1.0-rc2` / `BC0002` AWS production attempt. MVS read-only catalog preflight LISTDS JOB **9338** passed, then the operator entered `y` at both guarded `[y/N]` boundaries. The new tape was initialized/mounted, the 21-step `TA2RC2WR` job was submitted, and the script reached the HETMAP `-f` parser only after confirming 21 ordered JES/IEF142I **RC=0000** results and 21 standard-label groups. The runner halted **RC=2** at `HETMAP file number/block count missing, repeated or out of order`, with SHA256-sealed original evidence at `workarea/ta2-rc2-production-operations/20261121T231644Z-27163`. The original MVS job number, HETMAP physical layout and AWS hash are not yet independently accepted from raw files. See the [qualified incident and read-only audit record](../../distribution/create-tape/ta2-rc2-postwrite-physical-file-review-20261121.md). **DO NOT RETRY OR ALTER BC0002.** New `scripts/ta2-rc2-postwrite-audit` and 12/12 local tests implement a single original-evidence replay, independent 21-step JES check, fresh read-only HETMAP `-f/-l/-a`, exact AWS SHA-256, and a bounded file-map diagnosis; only the new evidence directory below `workarea/` is written. This is not a new write authorization and not yet TA.2 closure. **TA.2 IN PROGRESS.**

## TA.2 confirmed JOB 9339 and HETMAP Summary footer correction — 21 November 2026 EST

The owner ran the original read-only postwrite audit against the preserved `BCPL-0.1.0-rc2` AWS image. It returned **RC=0**, independently replayed original SHA256-sealed reports and found **JES JOB 9339 with 21/21 RC=0000**, **21 SL dataset groups**, **64 physical files numbered 1–64**, and an unchanged image of **1,957,296 bytes** with SHA-256 `123657b2feaeea739350853f8b8437ccb73b0e917442ddd3220589c7ae180375`. The sole parser discrepancy was in file 64: `Blocks:[0,2559]` because the HETMAP **Summary Files:64 Blocks:2559** footer was treated as another per-file count. The correction is based on actual HETMAP source semantics, preserving the terminal **0** block file, checking footer aggregate totals against all 64 physical entries, and refusing any inconsistent or duplicate fields. The [qualified forensic evidence and correction](../../distribution/create-tape/ta2-rc2-hetmap-summary-footer-correction-20261121.md) record the observed report and new read-only acceptance gate. **37/37** updated source-controlled reviewer tests and **12/12** supplemental isolated footer parser checks PASS. The **existing AWS is not rewritten**, original failure reports and no-retry marker remain intact, and revised structure acceptance remains **pending the owner's next read-only audit**. No restoration, installation or publication is authorized. **TA.2 IN PROGRESS.**

## TA.2 qualified private RC2 AWS structural acceptance — 21 November 2026 EST / 22 November UTC

The owner reran the **read-only corrected** `ta2-rc2-postwrite-audit` at GitHub `main` `ef86e0fb8b695a0344729539f5ba6e34021125f5`. The original, unique `BCPL-0.1.0-rc2` candidate passed with **RC=0**: original **TA2RC2WR JOB 9339** had **21/21 RC=0000**, all **21** SL dataset groups matched the independent AWS reviewer, **64** physical tape files were numbered correctly, and the HETMAP footer reconciled **64 files / 2,559 blocks** with a terminal zero-block file and no discrepancies. The existing image remains **1,957,296 bytes**, SHA-256 `123657b2feaeea739350853f8b8437ccb73b0e917442ddd3220589c7ae180375`; saved/fresh HETMAP reports and original sealed JES evidence were independently replayed by the verified runner. Exact owner-reported receipt: `workarea/ta2-rc2-postwrite-audit/20261122T001850Z-27778`. See [qualified private candidate structural acceptance](../../distribution/create-tape/ta2-rc2-aws-structural-qualified-acceptance-20261121.md). This supersedes the earlier *pending* structural qualification while preserving its source reports intact; **no repeat write occurred**. **TA.2 still IN PROGRESS** pending independent MVS readback, DCB/selected-member/content verification and provenance qualification; a [separate MVS readback design proposal](../../distribution/create-tape/ta2-rc2-independent-mvs-readback-proposal-20261121.md) awaits owner review and state-change authorization. TA.3 installation/publication are not implied.

## TA.2 owner-approved readback design and bounded implementation — 21 November 2026 EST

Following structural acceptance of the immutable `BC0002` AWS, the owner **approved the independent 21-dataset MVS readback design** but did **not** authorize a new scratch DASD volume or state-changing tape/DASD execution. The [design implementation and test record](../../distribution/create-tape/ta2-rc2-readback-design-implementation-20261121.md) now includes a source-controlled `ta2-rc2-readback-plan`: a 21-step IEBGENER/IEBCOPY JOB-less readback JCL plan with `LABEL=(1..21,SL)`, newly isolated `HERC02.BCPL.TA2RB.BTnnnn` targets, manifest DCBs including `BT0012 PO/U/0/6144`, and an optional *read-only* MVS LISTDS/IEHLIST/Hercules preflight. **12/12** offline design tests PASS and the Git blob matches the checked source. A new DASD volume and the reported 770 primary + 81 secondary track budget (plus screening margin) remain **proposals**, not grants. There is deliberately **no `--run`**; once MVS preflight supplies current catalog/VTOC evidence, the owner must separately approve the exact scratch allocation and one-shot readback JES submission. No existing tape/media/accepted stage was changed. **TA.2 IN PROGRESS; TA.0/TA.1 unchanged.**

## TA.2 first independent readback preflight: Hercules 0480 refusal — 21 November 2026 EST

The owner ran the approved-design `ta2-rc2-readback-plan --volume TSO002 --live`; it **refused RC=2** at `Hercules 0480 does not hold exact BC0002 candidate`, preserving sealed original evidence at `workarea/ta2-rc2-readback-preflight/20261122T005713Z-27881`. The guard halted after the original AWS/receipt and Docker checks but **before** any readback, LISTDS, IEHLIST or DASD allocation. The original TA2RC2WR write JCL did not request `RETAIN` on its final tape dataset, so a released drive is possible, **not yet proven**. The [read-only device investigation](../../distribution/create-tape/ta2-rc2-readback-device-refusal-20261121.md) adds a strict `--inspect-drive` mode to replay the sealed failure, distinguish an empty, expected, foreign, busy or unrecognized Hercules unit, display MVS 480 state, and preserve new SHA256-sealed evidence. **18/18** focused offline tests PASS. No mounts, tape positioning, production retries or restored datasets occurred. A new volume or execution permission is still absent. **TA.2 IN PROGRESS.**

## TA.2 actual empty Hercules drive and corrected read-only MVS preflight — 21 November 2026 EST

The owner executed the new `ta2-rc2-readback-plan --volume TSO002 --inspect-drive`, **RC=0**, replaying the sealed original failed device preflight and reporting **original=EMPTY, fresh=EMPTY, MVS 480=O-NRD**. Both Hercules 0480 status rows showed **`3420 *`**. Preserved evidence: `workarea/ta2-rc2-readback-preflight/20261122T010414Z-27961`. [Evidence and targeted correction](../../distribution/create-tape/ta2-rc2-empty-drive-readonly-preflight-20261121.md). This proves **no BC0002 medium is currently mounted**, not that the accepted AWS changed. The approved design's read-only DASD catalog/VTOC checks **do not require a mounted tape**, so the readback planner now allows only `EMPTY` with MVS `O-NRD` or the exact candidate `MOUNTED_BC0002` with MVS `O`, refusing inconsistent or foreign states. **23/23** focused offline tests PASS; source blobs match tested content. It still performs **no tape mount/position/read**, scratch allocation or state-changing readback job. A fresh `--live` MVS LISTDS/IEHLIST preflight is pending and the readback DASD volume/operational approval are separately gated. **TA.2 IN PROGRESS.**

## TA.2 owner-reported MVS 9340/9341 PASS and gated BC0002 readback runner — 21 November 2026 EST / 22 November UTC

The owner ran `ta2-rc2-readback-plan --volume TSO002 --live` after the empty-drive correction and reported **RC=0**: **Hercules 0480 EMPTY / MVS 480 O-NRD**, all **21** new `HERC02.BCPL.TA2RB.BTnnnn` destinations confirmed absent, original staged inputs accepted, **LISTDS JOB 9340**, **IEHLIST VTOC JOB 9341**, and **15,335 free tracks** on `TSO002`. Private original SHA256SUMS evidence: `workarea/ta2-rc2-readback-preflight/20261122T010923Z-28068`. The 770-primary/81-secondary-track proposed scratch allocation plus screening margin fits the reported free-track total, but IBM actual allocation/extents remain MVS-controlled. The [read-only acceptance and owner-gated one-shot implementation record](../../distribution/create-tape/ta2-rc2-readback-preflight-pass-and-one-shot-implementation-20261121.md) explains the Git-controlled `ta2-rc2-readback-once` runner, exact 21-step read-only-tape JCL SHA256 `226819ef3702234a1367c7a7df96399cf9fcaf32d99152061db1df98fed12e73`, replayed accepted MVS evidence and conditional exact-image 0480 mount, with 21 new restore datasets on `TSO002`. **37/37** assistant-workspace offline tests PASS and Git blob identities match tested content. Execution permission file is **intentionally absent**: no mount, restoration or new JES readback occurred. Next gate is **separate owner approval** for one `BC0002` mount iff 0480 empty and one `TA2RC2RB` readback/21 new allocations, not TA.2 closure. **TA.2 IN PROGRESS; TA.0/TA.1 unchanged.**

## TA.2 — Explicit one-shot readback operation approval (21 November 2026 EST)

The owner explicitly **approved exactly one private MVS readback** of the existing SHA-256-pinned `BC0002` AWS, conditional mount only if Hercules 0480 is empty, a single 21-step `TA2RC2RB` job, and 21 **new** `HERC02.BCPL.TA2RB.BTnnnn` restore datasets on `TSO002`. See [exact authorization](../../distribution/create-tape/ta2-rc2-readback-execution-authorization-20261121.md) and [machine-readable permission](../../distribution/create-tape/ta2-rc2-readback-execution-approval.json). The original MVS preflight JOBS **9340/9341**, 15,335 reported free tracks and frozen JOB-less JCL SHA256 `226819ef3702234a1367c7a7df96399cf9fcaf32d99152061db1df98fed12e73` are bound to the permission. The runner/JCL remain unchanged and require a new fresh target/source/device preflight, a single [y/N] operator confirmation, and permanent **NO RETRY** markers. **Execution has not occurred; TA.2 IN PROGRESS; no publication authorized.**

## TA.2 — Owner-reported JOB 9343 readback and consolidated install/usage pilot preparation (21 November 2026 EST)

The owner reported that `TA2RC2RB` JOB **9343** restored all **21** logical
BC0002 datasets as new `HERC02.BCPL.TA2RB.BT0001`–`BT0021` on
`TSO002`, with all 21 IEBGENER/IEBCOPY steps **RC=0000**.
This is an owner-reported successful MVS readback checkpoint, not independent
member-content equality or final release acceptance. Preserve original
BC0002 media, stage datasets, immutable operation markers and original JES
evidence; **DO NOT RETRY**.

The [consolidated acceptance design](../../distribution/install-from-tape/ta2-rc2-consolidated-acceptance-20261121.md)
and offline-tested `install-from-tape/scripts/ta2-rc2-acceptance` now provide
one MVS-facing entry point for an isolated installation/usage pilot.
The immediate `--live` procedure issues one **read-only** MVS LISTDS
job for all 21 restored DCBs and 21 absent proposed `TA2INS` destinations.
A stateful `--run` now performs the same read-only preflight and
requires one explicit **[y/N]** confirmation before authorizing 21 new
datasets on TSO002, one TA2INST 21-step IEBGENER/IEBCOPY job and one
TA2MR10 63-step canonical MRREGRES job. The exclusive no-retry marker
is created only after operator confirmation; no separate Git approval
file is required. The 12 interpreted regression cases and
manual `EXP:`/`RP:`/`CODE=` review remain distinct semantic gates;
this candidate declares `native_compiler: absent`. No new MVS inquiry,
allocation, installation, MR10 regression or publication is asserted by
this commit. **TA.2 remains IN PROGRESS; TA.3+ unchanged.**

## TA.2 — Consolidated acceptance gate refusal resolved (21 November 2026 EST)

The owner ran the consolidated installation/usage entry point and received
`--run CLOSED: separate owner approval for TA2INS allocations is missing`
(RC=2); no MVS operation or installation marker was created. The
corrected implementation removes the redundant approval-file prerequisite
but retains all manifest, AWS SHA, immutable JOB 9343 readback evidence,
21 restored DCB / 21 target-absence MVS LISTDS checks, explicit interactive
`[y/N]` confirmation and one-shot/no-retry protections.

The owner now confirms the **combined** 21-dataset TSO002 TA2INS installation
and single 12-case MR10 regression once, in the one `--run` procedure.
The runner writes the exclusive attempt marker **after Y** and immediately
before submitting installation JCL. An N/cancel before that point does not
consume a one-shot installation attempt. The 16 focused synthetic tests and
37 entire local install-from-tape tests passed. No MVS installation or
BCPL usage result is claimed until the owner reports actual JES evidence.
TA.2 remains IN PROGRESS.

## TA.2 — Consolidated MVS installation/usage result (22 November 2026)

The owner executed the consolidated `--run` procedure and reported **RC=0**. The saved operation is `workarea/ta2-rc2-install-acceptance/20261122T133139Z-29894`. **JOB 9344**: MVS read-only LISTDS preflight passed (21/21 restored DCBs correct; 21 installation targets initially absent). **JOB 9345**: all 21 new `HERC02.BCPL.TA2INS.*` datasets copied successfully by IEBGENER/IEBCOPY. **JOB 9346**: installed MR10 Kit Compiler/interpreter `MRREGRES` completed its JES pipeline and all 12 `R01`–`R12` execution steps at RC=0000. These are owner-reported MVS results, not independently inspected reports in this commit; the original sealed evidence must be reviewed and retained. **Do not retry or alter the original tape/readback/installation.**

The new **`ta2-rc2-acceptance --review`** mode performs no MVS submission or dataset operation. It verifies the saved report's SHA-256 evidence seal and accepted receipt, then compares ordered `TEST:`/`RP:` and interpreted `CODE=` for all 12 cases against the tracked regression-panel manifest and `.expected` files. It saves a separate sealed semantic report under `workarea/ta2-rc2-install-acceptance/review-*/`. Missing, reordered, mismatched, duplicated, or nonzero interpreted cases are reported as failures. The current 12 canonical regression BCPL programs **do not print `EXP:` records** (the approved TA.4 implementation remains pending), so a successful RP/CODE comparison is expressly **provisional**; it does not replace the required `EXP:` output nor human case-by-case review, does not certify a fresh-recipient TA.3/TA.7 installation, and does not authorize publication. **TA.2 remains IN PROGRESS** until relevant acceptance boundaries are met.


## TA.2 BC0002 semantic checkpoint and approved TA.4 EXP source preparation — 22 November 2026

The owner reported that the saved-report review of installed MR10 JOB **9346**
found **12/12 GOLDEN/CODE MATCH** (all ordered `RP:` values equal the
independently maintained golden files and interpreted `CODE=0`).
All 12 also reported **EXP ABSENT**, yielding
`GOLDEN_RP_CODE_MATCH_EXP_REQUIRED` with reviewer RC=0. This establishes
the historical RC2 MR10 behavioral comparison, **not** fulfillment of
TA.4 human-readable `EXP:` and human sign-off acceptance.

The approved 16 November TA.4 source-display contract is now prepared in
the canonical 12 BCPL panel sources: **23 fixed literal `EXP:` lines**
derived from the unchanged goldens, preceding the unchanged computed
`RP:` outputs. The source/JCL/golden contract is guarded by
`install-from-tape/scripts/mr10-exp-source-check` with isolated negative
tests in the assistant workspace. Real MVS compile/run of the *updated*
source remains pending. The immutable **BC0002** image, original MVS
staging/readback/installed data and JOB 9346 **do not** contain these new
lines; a future separately governed candidate must incorporate them.
Original sealed review evidence remains in the owner's `workarea/`;
do not rerun the one-shot RC2 installation. See
[the semantic checkpoint and source-preparation record](../../distribution/install-from-tape/ta2-rc2-12-case-comparison-and-ta4-exp-preparation-20261122.md).
No new VOLSER, publication or formal march closure is authorized.
**TA.2 remains IN PROGRESS.**


## TA.2 — Updated TA.4 EXP BCPL source regression on actual MVS (22 November 2026)

After the 23 literal `EXP:` records were committed in the 12 canonical
BCPL tests, the owner ran `tools/mr10/run-regression-panel` from repository
`main` and reported **PASS 12 / FAIL 0 / TOTAL 12 / RC=0** with
`ICINT: mr10-kit-compiler/asm/icintv19.asm` and canonical `ICLIB`.
The command ran all twelve named test cases successfully on the existing
development MVS/ICINT execution path. This is **owner-reported real MVS
compile/generate/execute verification of the revised Git-controlled
sources**, not a synthetic test, and it supersedes the pending
source-regression check identified in the prior TA.2 checkpoint.

The existing development runner verifies unchanged `RP:` semantic golden
records and interpreted `CODE=` against each test's accepted expectation.
Its summary does **not** independently attest that the new `EXP:` print
records appeared in captured MVS SYSOUT; a new recipient/distribution
candidate must verify `TEST:`, `EXP:`, `RP:`, and `CODE=` together,
and retain the approved 12-case human review/sign-off. The sealed BC0002
AWS and original MVS 9343–9346 and review evidence remain untouched,
and contain the earlier regression source version without `EXP:`.
No RC2 rerun, publication, new VOLSER or TA.2 formal closure is authorized
by this record. **TA.2 remains IN PROGRESS.**

## TA.2 — RC3 consolidated release candidate promoted for MVS verification (22 November 2026)

Following the owner-reported 12/12 MVS PASS of the EXP-enabled canonical
MR10 source panel, the next reserved candidate is
`BCPL-0.1.0-rc3` on a **new** standard-labeled AWS `BC0003`.
The registry manifest SHA-256 is
`b130e4a246cecb6d810f45febd945e3ed0e854164e83012899c86c730f365486`,
with source revision `e910de51c19c09698be139e33084a90401511cc9`.
The 21 logical datasets, 146 members, original DCB assignments, and
Cambridge historical compiler source inclusion are preserved. The native
Cambridge Compiler remains absent as a runnable native compiler.

The owner-directed [RC3 unified execution plan](../../distribution/create-tape/ta2-rc3-consolidated-candidate-20261122.md)
uses one guarded `ta2-rc3-consolidated --run` for new staging,
21-dataset tape write, **direct** tape-to-recipient dataset installation,
and installed 12-case MRREGRES with all printed TEST, EXP, RP and
interpreted CODE=0 results. Separate RC3 `TA2R3S` and `TA2R3I`
namespaces preserve the entire previously accepted RC2 environment.
The operator must explicitly confirm once; an exclusive marker enforces
no automatic retry. The implementation has **8/8 offline tests PASS**.
There has been **no RC3 MVS operation or AWS production yet**, and
no recipient acceptance, TA.4 human sign-off, formal march closure or
publication is asserted. Continue from actual MVS feedback;
**TA.2 remains IN PROGRESS.**



## TA.2 — RC3 consolidated MVS validation hardening (22 November 2026)

The existing Git-controlled `BCPL-0.1.0-rc3` / `BC0003` one-shot
producer was strengthened without changing the reserved identity,
21-position manifest, 146 selected members, tested EXP-enabled BCPL sources,
or approved original RC2 evidence. Following `TA2R3RES`, one read-only
MVS LISTDS job must verify **all 21 recipient datasets** on `TSO002`
with matching DSORG, RECFM, LRECL and BLKSIZE before interpreter execution.
The `TA2R3MR` 63-step MRREGRES must show **all 63 ordered RC=0000
summary steps and corresponding IEF142I MVS records**, in addition to
the 12 exact `TEST:` / `EXP:` / `RP:` / interpreted `CODE=0`
comparisons. The sealed semantic report uses the **actual RC3 JES job
number**, not the hard-coded RC2 JOB 9346 in the reused reviewer.

These changes and three additional positive/refusal regression test cases
are committed to GitHub `main`. The earlier 8/8 RC3 tests and isolated
executable validation are documented; the complete revised 11-case module
has **not** been rerun in an assistant-local full repository checkout.
One explicit `Y` remains required before any stateful operation;
the exclusive one-shot/no-retry marker and preservation of `BC0002`
are unchanged. **No RC3 AWS image, actual staging/write/restore/GO,
MVS acceptance, TA.4 human sign-off, or release publication is claimed.**
The next evidence must come from the owner-executed MVS one-shot and
retained JES/HETMAP/SYSOUT reports. **TA.2 remains IN PROGRESS.**


## TA.2 — RC3 pre-stateful JCL operand-width correction — 22 November 2026

The owner ran the consolidated RC3 one-shot entry point after pulling
GitHub `main`; it refused `JCL operands over column 71` before
any one-shot marker, live JES submission, AWS media initialization or
MVS state change. Direct GitHub source inspection found two 73-column
`//` comment separators in each of the 12 historical MR10 regression
BCPL test programs. Those records are in-stream FB80 source data
carried by `DD DATA,DLM=Z9`, **not** MVS JCL operands.
The RC3 `cards()` validator now tracks the exact data boundary,
checks 80-column data limits, preserves strict JCL column-71 enforcement
outside inline data and refuses unterminated/orphan delimiters.

Two new repository regression tests cover source-data width and negative
JCL/delimiter cases. A separate 9/9 executable isolated test of the exact
corrected validator passed in an assistant repository workarea. The
complete tracked RC3 test module was **not** executed against an assistant
full checkout, and no actual MVS write/restore/installed execution after
the refusal has been observed. See [RC3 candidate corrective evidence](../../distribution/create-tape/ta2-rc3-consolidated-candidate-20261122.md).
After updating `main`, the owner may reissue the single guarded RC3
operation; this is **not** a repeat of a consumed tape attempt.
**TA.2 remains IN PROGRESS** pending actual RC3 MVS evidence and TA.4 review.


## TA.2 — RC3 staging-deck inert RESTORE JCL count repair — 22 November 2026

The owner's next RC3 run after pulling the in-stream JCL width repair
returned `RC3 REFUSED: stage JCL count/safety contract altered`.
This is a second pre-stateful refusal: no one-shot marker, AWS tape
initialization, MVS preflight or JES submission occurred.

Investigation of the real producer and installer generator isolated a
safety-gate error: the staged BT0002(RESTORE) distribution member
contains 19 IEBCOPY/NEW-allocation template entries embedded within
`DD DATA,DLM=Z9`. The former whole-text counts incorrectly treated
this inert installation material as active staging JCL. The renderer
now counts only the delimiter-aware active cards and requires the exact
ordered 21 S + 4 B + 12 E steps, 21 NEW allocations and 17 data sections,
while retaining column-71 JCL and FB80 data checks. Two new repository
tests exercise embedded RESTORE and active-step-order drift; the
15-test repository module was not run in a full assistant checkout.
A 9/9 executable mock-stage safety harness passed in the assistant's
isolated repository workarea.

See [RC3 corrective evidence](../../distribution/create-tape/ta2-rc3-consolidated-candidate-20261122.md).
The owner can retry the **original, unconsumed** RC3 MVS operation after
updating GitHub `main`. No actual RC3 MVS acceptance yet.
**TA.2 is IN PROGRESS**, with TA.4 semantic review and publication pending.


## TA.2 — BC0003 original MVS write PASS (qualified) and separate recovery continuation — 22 November 2026

The owner executed the corrected consolidated `BCPL-0.1.0-rc3`
producer against real MVS 3.8J. **JOB 9359**: new-stage and
recipient-absence/21-source DCB preflight PASS. **JOB 9360**
(`TA2R3STG`): 21 new staging datasets plus 16 updated member
writes PASS. **JOB 9361** (`TA2R3WR`): all 21 ordered MVS
standard-label tape datasets and the independent 64-file HETMAP audit
PASS. `BC0003` AWS SHA-256:
`6c54c4df2b75020a698110061c4f8003b09adbe21f738848dcaed3da495d81e1`.

The original operation stopped after the successful write at
`BC0003 disappeared after write`. Owner-provided original
Hercules/MVS reports conclusively show the final tape was automatically
demounted (`0480` empty, `480 O-NRD`) after the write, not lost or
overwritten. `sha256sum -c SHA256SUMS` reported all evidence OK and
a new independent checksum of the existing AWS was unchanged.
Original original evidence is sealed at
`workarea/ta2-rc3-consolidated/20261122T202323Z-30995`;
the exclusive `BC0003` production marker is consumed.
**RC3 staging and AWS writing are PASS (qualified)**; restore,
recipient inspection and installed MR10 still await MVS execution.
Do **not** rerun the original producer or reinitialize the tape.

The owner expressly approved TA.2 readback, installed use and
continuation as a **new, distinct one-shot operation**. The
source-controlled `scripts/ta2-rc3-restore-continuation`
verifies the exact original sealed evidence and JOB 9360/9361
MVS summaries/IEF142I, reserved image SHA/HETMAP, active
Hercules/MVS empty drive, and 21 absent new recipient DSNs
before one **Y** and a new nonretry marker. It mounts only the
existing `BC0003` and executes the 21-step `TA2R3RES`;
it independently verifies all 21 target DCBs plus 146 target
PDS directory members via actual MVS LISTDS/LISTDS MEMBERS, then
runs the installed 63-step `TA2R3MR` and compares 12/12
`TEST:`/`EXP:`/`RP:`/`CODE=0` against canonical goldens.
It refuses an existing continuation marker, image/receipt drift,
foreign media, occupied targets, missing/duplicate members,
nonzero JES/IEF142I, and any semantic mismatch. No existing stage,
original `BC0002`, original `BC0003` write or release registry
content is modified. Evidence is separately sealed in repository
`workarea/`. **10/10 assistant-workspace isolated positive/negative
tests passed**, and both committed GitHub blobs match the exact
locally tested bytes. Full-repository/MVS execution remains pending.

See [the detailed RC3 MVS and recovery record](../../distribution/create-tape/ta2-rc3-consolidated-candidate-20261122.md).
**TA.2 remains IN PROGRESS.** TA.4 individual human semantic review,
TA.3/TA.7 fresh-recipient acceptance, redistribution-rights decisions
and publication remain separate release gates.


## TA.2 — BC0003 21-step MVS readback and recipient DCB halt — 22 November 2026

After the owner-approved separate TA.2 restore continuation and new
`Y`, **JOB 9362** passed initial MVS recipient-absence preflight
with the existing `BC0003` image unchanged and tape unit EMPTY.
**JOB 9363** (`TA2R3RES`) completed all **21 IEBGENER/IEBCOPY
steps RC=0000** on actual MVS 3.8J, restoring the reserved
`HERC02.BCPL.TA2R3I.*` namespace. This is a **readback/restore
JES PASS (qualified)**, not yet DCB/directory or executable MR10
acceptance. The continuation halted during its subsequent
`LISTDS LABEL` DCB check for `HERC02.BCPL.TA2R3I.BOOT`
with `recipient DCB/volume differs`. Original receipt:
`workarea/ta2-rc3-restore-continuation/20261122T232532Z-31994`.
Original stage/write and restore one-shot markers are now consumed.
**Neither production nor restore may be repeated.**

The new `scripts/ta2-rc3-recipient-diagnostic` provides a bounded
**read-only** MVS investigation: it verifies the complete original
sealed JOB 9363 evidence and immutable AWS image SHA, submits one
21-DSN `DSPALST` `LISTDS LABEL` inquiry and one 20-PDS
`DSPALLS` `LISTDS MEMBERS` inquiry, compares expected and
actual DCB/volume, prints the bounded raw BOOT block and verifies all
146 selected PDS members. The new sealed diagnostic evidence is
saved only under repository `workarea/`. This does not mount or
rewrite media, allocate datasets or execute the interpreter.
**10/10 assistant-workspace tests passed** and committed GitHub
blobs match the exact tested files; actual MVS results pending.
Do not adjust the accepted DCB contract, mark all 146 PDS members
PASS, run MR10, or advance TA.2 closure until MVS evidence
identifies the discrepancy and justifies any subsequent action.
**TA.2 remains IN PROGRESS.**


## TA.2 — MVS JOB 9365 BOOT/BOOT.JCL parsing defect and JOB 9366 146-member verification — 22 November 2026

Following successful `BC0003` tape write and one-shot restore (JOB
**9363**, all 21 IEBGENER/IEBCOPY RC0000), the owner executed the
approved `ta2-rc3-recipient-diagnostic --live`. **JOB 9365**
queried all 21 recipient DCBs. The single apparent mismatch is
a **verification defect**: the original substring-based TSO
`extract_listds_block()` matched
`HERC02.BCPL.TA2R3I.BOOT.JCL` while asked for
`HERC02.BCPL.TA2R3I.BOOT`. The raw PO/FB/80/800
`BOOT.JCL` response does **not** establish an incorrect DCB
for the separate PS bootstrap dataset. A strict exact-DSN
MVS inquiry remains required before asserting 21/21 DCB acceptance.

**JOB 9366** returned **20/20 expected PDS member directories**
with the **146 canonical PDS member identities**; this is real
MVS LISTDS MEMBERS evidence, **PASS (qualified)**. Original
evidence is retained at
`workarea/ta2-rc3-recipient-diagnostic/20261122T234725Z-32362`;
no media or restored datasets were modified by diagnosis.
No new MVS `MRREGRES` was executed in that diagnostic operation.
Both prior stateful RC3 one-shot markers remain consumed.

The owner-authorized TA.2 continuation is now committed as
`packaging/distribution/create-tape/scripts/ta2-rc3-installed-mr10-continuation`.
It replays original 9360/9361, 9363 and 9365/9366 sealed evidence,
requires preserved `BC0003` SHA-256 and the tested historical
BCPL source revision, independently reparses 9365 with exact
stand-alone DSN labels, performs fresh actual MVS `LISTDS LABEL`
for **21/21 DCB/volume** and `LISTDS MEMBERS` for **146/146**
members, and offers a single operator confirmation for **one**
installed `TA2R3MR` 63-step compile/execute and 12-case
`TEST:`/`EXP:`/`RP:`/`CODE=0` comparison. A distinct
exclusive no-retry marker is written only after Y. No tape
initialization, mount/unmount, unload, restore, restaging or rewrite
is part of this continuation. **18/18 isolated Python positive and
negative tests passed** and the tracked GitHub script/test blob
SHAs match the executable-tested files. No full checkout/MVS
GO was executed in the assistant workspace.

TA.2 is **IN PROGRESS** pending the actual BOOT exact-DSN
verification and installed MR10 results. TA.4 human sign-off,
TA.3/TA.7 fresh-recipient gates, redistribution-rights reviews and
publication are not closed.


## TA.2 — BC0003 MVS installed acceptance JOBS 9367–9369 and TA.4 human review preparation (22 November EST / 23 November UTC)

The owner executed the previously approved, source-controlled
`ta2-rc3-installed-mr10-continuation --run` on actual MVS 3.8J.
The terminal result provides the following **owner-reported, actual
MVS** acceptance evidence:

- **JOB 9367:** exact-name `LISTDS LABEL` **21/21 DCB/volume PASS**,
  including `HERC02.BCPL.TA2R3I.BOOT` as PS, correcting the
  former `BOOT.JCL` false-prefix parser result.
- **JOB 9368:** independent `LISTDS MEMBERS` **146/146 selected
  PDS members PASS** across 20 restored PDS datasets.
- After the operator's explicit `Y`, **JOB 9369** (`TA2R3MR`)
  **63/63 ordered MVS JES / IEF142I steps RC0000** and **12/12**
  installed MR10 Kit Compiler `TEST:`/`EXP:`/`RP:`/
  interpreted `CODE=0` automated semantic comparisons PASS.
- Immutable private MVS evidence:
  `workarea/ta2-rc3-installed-mr10-continuation/20261123T000015Z-32502`.

Together with accepted original production JOBS **9360/9361**,
new immutable AWS `BCPL-0.1.0-rc3` / `BC0003` (21 logical
standard-label tape datasets, 64 physical files, SHA-256
`6c54c4df2b75020a698110061c4f8003b09adbe21f738848dcaed3da495d81e1`),
and accepted 21-step readback JOB **9363**, this completes the
**TA.2 producer/readback and installed-MR10 technical verification
on the current development MVS system — PASS (qualified)**.
The successful MVS state must be preserved; stage, tape write,
readback and installed-regression one-shot markers are all consumed.

This is a **qualified acceptance checkpoint, not a formal TA.2
owner-directed closure**, a TA.3 independent recipient installation,
or full TA.4 closure. The project requires 12 individually human-reviewed
MR10 cases and identified overall sign-off; all 11 language and 17
BCPL demonstrations, distributed source rebuild and further included
native-component tests are separately governed. A recipient needs
MVS-only bootstrap/installation without developer tools, which is
not established by this same-system pilot. The candidate still
declares `native_compiler: absent`; do not claim native Cambridge
Compiler availability or TA.6 PASS. Provenance, redistribution-rights
review and publication authority remain pending.

The new `scripts/ta2-rc3-human-review` independently replays
the sealed MVS JOB 9369 regression report and original
12-case semantic comparison, displays each actual `TEST:`,
literal `EXP:`, calculated `RP:` and `CODE=` result, then
optionally takes twelve individual human PASS/FAIL verdicts,
reviewer identifier and explicit `SIGN`. Any human FAIL
blocks release acceptance. It writes a separate SHA256-sealed
review record under `workarea/` and never contacts MVS or
alters tape, source, installation or original evidence.
**17/17 local focused tests passed**, and the committed reviewer
and test Git blob IDs are exactly those exercised in the
isolated assistant workspace. The original WSL MR10 RP/CODE
automatic test contract is unchanged.

See the [RC3 evidence ledger](../../distribution/create-tape/ta2-rc3-consolidated-candidate-20261122.md).
**TA.2 remains IN PROGRESS pending formal qualified closure; TA.4
human sign-off remains pending until actual owner-reviewed evidence.**


## TA.2 — Owner-directed formal qualified closure; TA.3 immediate kickoff (22 November 2026 EST / 23 November UTC)

The owner explicitly directed **close TA.2 now and move immediately to TA.3**.
This is a **formal owner-directed closure**, not a provisional
recommendation: **TA.2 — Manifest-Driven Tape Producer: CLOSED (qualified)**.
The qualified evidence comprises immutable `BCPL-0.1.0-rc3` /
`BC0003`, 21 standard-labeled MVS datasets / 64 AWS physical files,
21-step restored tape-to-DASD roundtrip, independently verified
21/21 DCBs, 146/146 PDS directory members, and real MVS installed
MR10 JOB 9369 (63/63 JES/IEF142I RC0000 and 12/12
`TEST:`/`EXP:`/`RP:`/`CODE=0` semantic PASS).
Earlier MVS JOBS 9360, 9361, 9363, 9367 and 9368 and all
private sealed original evidence are preserved. The candidate
AWS SHA-256 remains
`6c54c4df2b75020a698110061c4f8003b09adbe21f738848dcaed3da495d81e1`.

The optional 12-case human sign-off script was separately invoked by
the owner: the terminal transcript shows **all twelve individual
PASS decisions** and reviewer identifier `cm`. A lowercase
`sign` was rejected by a case-sensitive command token. **No
sealed sign-off file was produced**; this procedural defect is **not
a reason to keep TA.2 open** or make the owner repeat accepted MVS
tests. Human review disposition and full demonstration/source rebuild
acceptance remain under TA.4, independent of the TA.2 producer.

This milestone therefore advances **TA.3 — MVS Bootstrap and
Installation: IN PROGRESS**, with the separately approved
[TA.2 formal closure](ta2-formal-qualified-closure-and-ta3-transition-20261122.md)
and [TA.3 kickoff](ta3-kickoff-20261122.md).
TA.3 must establish independent **MVS-only** recipient bootstrap and
installation from `BCPL.BT0001`/`BCPL.BT0002`, recipient
site-HLQ/allocation/overwrite safeguards and candidate-appropriate
independent profile selection. Current same-system TA.2 readback is
**not** a clean-recipient TA.3/TA.7 test. The declared native
Cambridge Compiler remains `absent`; TA.6 is candidate **N/A**,
not PASS. TA.4/TA.5/TA.7/TA.8, provenance and publication
approval retain their gates.

Do not reopen TA.2 without a specific demonstrated product defect;
do not repeat the consumed staging, tape writing, restoration or
installed MR10 one-shot operations; and do not modify the accepted
`BC0003` media or original MVS evidence.

## TA.3 — Three isolated BC0003 installation profiles PASS (qualified technical checkpoint, 23 November 2026 EST)

The owner reported the following **actual MVS 3.8J** outcomes, with
the original `BC0003` image verified unchanged:

- **MR10-only / TA3N1:** MVS JOBS 9370–9377; 11 newly restored PDSes,
  90/90 members, and installed `ICINT19` SCALVEC
  `TEST:/EXP:/RP:/CODE=0` PASS.
- **Native-only / TA3N2:** fresh MVS preflight JOB 9378 verified all
  31 TA3N2+TA3N3 targets absent. The native-only installation restored
  11 PDSes with 67/67 members verified. No native Cambridge Compiler
  execution is asserted.
- **Combined / TA3N3:** 20 newly restored PDSes with 146/146 members
  verified. Combined-recipient installed `ICINT19` SCALVEC
  `TEST:/EXP:/RP:/CODE=0` PASS. Original immutable AWS unchanged.
- Preserve the accepted `workarea/ta3-rc3-recipient/` and
  `workarea/ta3-rc3-remaining-profiles/` sealed MVS evidence on
  the owner system, existing dataset recipients, one-shot markers,
  and all preceding TA.2 acceptance evidence. No additional replay.

These results demonstrate **all three independently selected MVS-only
profile JCL paths** on isolated new dataset namespaces within the same
MVS 3.8J system. They do **not** establish an independently IPL'd
recipient, standalone native component link/execute validation, or
native Cambridge Compiler presence.

**Open TA.3 acceptance-design distinction:** `BC0003` tape-resident
`BT0002(RESTORE)` is a human-editable placeholder template; the
three successful executable installation job bodies are external
source-controlled MVS JCL. Formal march closure requires owner direction
whether this is acceptable on a **qualified** basis, or whether
tape-resident operable profile JCL is mandatory (which requires a new
authorized tape candidate, never in-place modification of `BC0003`).

The record is [TA.3 three-profile operator results](../../distribution/install-from-tape/ta3-rc3-all-profiles-operator-results-20261123.md).
**TA.3 — MVS Bootstrap and Installation remains IN PROGRESS** until
explicit formal disposition.

## TA.3 — Owner-approved RC4 operational tape-resident installer development (23 November 2026 EST)

Following the separately verified **MR10-only**, **native-only** and
**combined** `BC0003` isolated-recipient MVS installation passes,
the owner approved producing a **new candidate** to remove the frozen
`BT0002` inert installation-template limitation, rather than
closing TA.3 with that limitation.

The corrective `BCPL-0.1.0-rc4` / `BC0004` identity is now
reserved in the authoritative registry. The RC4 manifest preserves
all 21 tape positions and all accepted MR10, native
runtime/library/extension and Cambridge source members.
Only the `BT0001` bootstrap and `BT0002` installer library are to
be replaced. The new installer has eight members, three
executable MVS `PROC` profile job bodies, and one reusable `COPY`
control member to avoid unsupported in-stream data inside procedures.
The source-controlled generator produces only offline artifacts
and proposed new-stage/new-image JCL.

**Immediate MVS gate:** execute the read-only PROC/symbolic
`HERC02.BCPL.TA3N1.DIST.INST(INSTALL)` probe on actual MVS 3.8J
before any RC4 staging, tape initialization or write.
This probe is a new, non-destructive test of the installer
mechanism; it is **not** a repeat of accepted TA.2/TA.3 jobs.

Design and acceptance boundaries are documented in
[TA.3 RC4 operational installer](../../distribution/create-tape/ta3-rc4-tape-resident-installer-design-20261123.md).
The original `BC0003` AWS and every one-shot receipt remain
immutable; the new candidate is not yet written or MVS-accepted.

**Status: TA.3 — MVS Bootstrap and Installation remains IN PROGRESS.**

## TA.3 — RC4 historical MVS PROC verification passed; new BC0004 production ready (23 November 2026 EST)

The owner ran the read-only `ta3-rc4-proc-probe` after pulling
GitHub `main`. **Actual MVS JOB 9392 PASS:** in-stream `PROC`
symbolic substitution and IEBGENER from
`HERC02.BCPL.TA3N1.DIST.INST(INSTALL)` returned RC0000.
Saved evidence: `workarea/ta3-rc4-proc-probe/20261123T054327Z-35363`.
No MVS datasets or tape media were changed by this probe.

The approved `BCPL-0.1.0-rc4` / `BC0004` corrective candidate is
separate from immutable `BC0003`. The source-controlled
`ta3-rc4-production` runner stages **only two new RC4 datasets**
(`BT0001` and eight-member `BT0002`), draws all **19 unchanged**
payload PDSes from accepted RC3 staging, and writes a **new** 21-position
standard-label AWS tape under one operator approval/no-retry marker.

Preflight checks MVS source DCBs, absence of both new stage datasets,
original BC0003 SHA, empty or verified original tape on 0480,
and new VOLSER/media collision. The post-stage gate checks actual JES
completion including the IEFBR14 PDS-allocation step and independent
MVS directory/record attributes. The post-write gate uses the
original independent HETMAP auditor for 21 logical datasets and
64 physical AWS files, and rehashes original BC0003.

All acceptance and safety gates remain **pending actual new MVS
execution**; RC4 has not yet been written or recipient-installed.
The next operation is this new guarded RC4 stage/write process,
followed by fresh-tape recipient tests of the three **tape-resident**
profile JCL members. No accepted TA.2/TA.3 job may be rerun.

See [TA.3 RC4 MVS installation design and JOB 9392](../../distribution/create-tape/ta3-rc4-tape-resident-installer-design-20261123.md).
**TA.3 — MVS Bootstrap and Installation remains IN PROGRESS.**

## TA.3 — RC4 first offline production gate corrected before MVS state (23 November 2026 EST)

The owner's first `ta3-rc4-production --run` invocation halted at
`RC4 plan identity/21-position payload selection changed`
**before any MVS job, confirmation, new stage dataset, one-shot
marker or tape image creation**. The validator incorrectly treated
39 IEBCOPY/`DISP=(NEW,CATLG,DELETE)` records embedded in the
new BT0002 profile members as executable outer-stage JCL.
The outer staging job has only **two** allocations.

The guarded producer now reuses the accepted TA.2
`jcl_control_cards` parser to exclude `DD DATA,DLM=Z9` payload
records from staging allocation and step counts. Targeted offline
regression checks show 41 raw allocation strings versus two active
allocations, 39 embedded IEBCOPY steps excluded, nine actual
IEBGENER steps, and one required IEFBR14 step.

**No stateful trial was consumed**; the corrected original
`--run` operation may be executed with normal fresh preflight and
one explicit operator approval. Preserve BC0003 and all accepted
earlier TA.2/TA.3 evidence. Further RC4 production and installation
remain outstanding. See the
[RC4 incident/implementation record](../../distribution/create-tape/ta3-rc4-tape-resident-installer-design-20261123.md).
**TA.3 remains IN PROGRESS.**

## TA.3 — RC4 BC0004 first MVS production PASS (23 November 2026 EST)

The owner reported successful actual MVS 3.8J guarded production of
the revised tape-resident MVS installer candidate,
**`BCPL-0.1.0-rc4` / `BC0004`**:

- **9393** read-only preflight: 19 accepted RC3 PDSes, two absent
  new stage destinations, unused BC0004 identity and empty tape drive.
- Owner confirmed the one-time stateful operation.
- **9394** BT0001/BT0002 staging PASS, **9395** staged DCB PASS,
  **9396** eight-member staged installer PDS directory PASS.
- **9397** 21 standard-labeled tape datasets and 64 physical AWS
  files PASS under the independent HETMAP structural auditor.
- New AWS `mvs-state/tape/bcpl-0.1.0-rc4-BC0004.aws` SHA-256:
  `7cc5a1d61882bf88469fd9f9e38512f1976ef1a775e3095e12e3988600c57af1`.
- Owner evidence:
  `workarea/ta3-rc4-production/20261123T130731Z-36363`.

**Production ACCEPTED as operator-reported actual MVS evidence**.
The exact raw JES and HETMAP files remain in owner `workarea/` and
have not been directly re-read by the assistant; job numbers and SHA
above are not inferred. The one-shot RC4 stage/write marker has been
consumed. No producer replay, BC0003/BC0004 rewrite, or repeat of
prior accepted installations is authorized.

**TA.3 next gate:** independently restore *BC0004* BT0001/BT0002
into fresh MVS recipient namespaces; verify and execute the three
**on-tape** profile JCL members `MR10`, `NATIVE`, `COMBINED`
using the restored `COPY` IEBCOPY control member, MVS directory/DCB
results and installed BCPL SCALVEC `TEST:/EXP:/RP:/CODE=0`.
This is distinct from the accepted BC0003 external-JCL installs.
No native compiler is claimed. The independent fresh IPL,
full TA.4/TA.5 and TA.7/TA.8 release gates are not pre-accepted.

See [TA.3 RC4 production operator result](../../distribution/create-tape/ta3-rc4-production-operator-result-20261123.md).
**TA.3 remains IN PROGRESS** pending actual tape-resident MVS
recipient installation acceptance.

## TA.3 — BC0004 tape-resident three-profile recipient acceptance trial prepared (23 November 2026 EST)

The original BC0004 production operation **succeeded** on actual
MVS JOBS 9393–9397; the 21-dataset standard-labeled, 64-file AWS
candidate has SHA-256
`7cc5a1d61882bf88469fd9f9e38512f1976ef1a775e3095e12e3988600c57af1`.
That one-shot operation is closed for repetition.

A new, separately guarded `ta3-rc4-recipient` implementation
now prepares a true **on-tape** MVS installation verification.
The operator's one confirmation follows an actual LISTDS
preflight of 42 absent recipient PDSes, source SHA verification
and sealed producer evidence checking. The runner independently
restores BC0004 `BT0002` three times to isolated
`HERC02.BCPL.R4MR`, `HERC02.BCPL.R4NT`, and
`HERC02.BCPL.R4CB` namespaces.

For each profile it prints the tape-restored source member
`MR10`, `NATIVE` or `COMBINED` and `COPY` using actual
MVS IEBGENER. The **read-back exact card sequence**, not
external source-controlled profile JCL, is submitted to JES
with the site's authenticated JOB card. Acceptance requires
actual IEBCOPY execution and JES IEF142I steps, LISTDS DCB
and member inventories (11/11/20 PDSes; 94/71/150 members),
and the combined installed MR10 `ICINT19` SCALVEC
`TEST:`/`EXP:`/`RP:`/`CODE=0` semantic contract.

Nine focused source-controlled offline tests cover source
isolation, missing/altered JCL cards, procedure-step identities,
and signed production evidence; a separate targeted assistant
workspace check of exact readback/IEF142I logic passed.
**Actual BC0004 recipient MVS execution is still pending.**
The runner creates a fresh no-retry receipt and never writes
BC0003/BC0004 tape media or replays the earlier TA.2/TA.3
acceptance jobs.

See [TA.3 BC0004 tape-resident recipient run](../../distribution/install-from-tape/ta3-rc4-tape-resident-recipient-run-20261123.md).
**TA.3 — MVS Bootstrap and Installation remains IN PROGRESS.**

## TA.3 — BC0004 on-tape first-recipient evidence halt and guarded no-replay continuation (23 November 2026 EST)

The owner reported **JOB 9398** RC4 recipient MVS preflight PASS
(42 recipient PDSes absent, BC0004 hash verified, tape drive empty),
then approved the original once-only installation attempt. The
first on-tape MR10 profile was submitted; the runner halted at
`MVS job summary IEBCOPY executed-step count differs`.
The source code demonstrates that it had first validated exact
ordered `IEF142I` execution/RC0000 evidence and then incorrectly
required a program-name label which the project's `IEFACTRT`
summary parser treats as optional. This is a **runner evidence
interpretation defect**, not demonstrated IEBCOPY malfunction.
The original run remains **STATEFUL_NO_RETRY**, with evidence at
`workarea/ta3-rc4-recipient/20261123T133542Z-36979`.

A corrected source-controlled `profile_result` now requires
the exact MVS IEF142I ordered Rnnnn/RC0000 sequence and a clean
JES summary without requiring optional `IEBCOPY` text.
A **new**, separately marked `ta3-rc4-continuation` has been
implemented. Before new consent/state it must:

- Authenticate the unchanged SHA256-sealed **original failure**,
  consumed marker, first on-tape MR10 JCL and actual MVS JES receipt.
- Freshly check that the first MR10 installation has **11 valid
  PDSes / 94 members** on MVS; no first-profile acceptance is
  presumed from the console halt alone.
- Check all **31 remaining** NATIVE/COMBINED recipient PDSes absent
  on MVS, media integrity and drive readiness.
- If and only if all gates pass, request **one fresh approval** to
  complete just NATIVE and COMBINED from verified on-tape JCL;
  preserve and never replay accepted RC4 production or first MR10
  installation, marker and evidence.

Targeted local Python regression checks passed for PROC IEF142I
with omitted summary-program labels, duplicates, missing steps,
nonzero return codes and native/combined profile step sequences.
The dedicated repository tests also include sealed incident
acceptance/tamper-refusal and no-replay selection fixtures.

The exact first MR10 JES job number will be obtained only from
original sealed local evidence. No further state-changing
continuation has yet been executed; **TA.3 remains IN PROGRESS**
pending actual MVS recovery results. See
[RC4 interrupted recipient recovery](../../distribution/install-from-tape/ta3-rc4-interrupted-recipient-recovery-20261123.md).

## TA.3 — BC0004 tape-resident three-profile MVS technical acceptance PASS (23 November 2026 EST)

The owner-reported actual MVS **TA.3** continuation finished successfully:

- **JOB 9403** read-only forensic preflight independently verified
  that the original on-tape `MR10` installation was intact:
  **11 PDSes / 94 directory members**, with the 31 NATIVE and
  COMBINED recipient datasets still absent and drive empty.
- After a separate explicit `Y` authorizing only the unfinished
  profiles, **NATIVE tape-resident install PASS**: **11 PDSes,
  71 members**, ten ordered actual MVS IEBCOPY steps.
- **COMBINED tape-resident install PASS**: **20 PDSes, 150 members**,
  nineteen actual MVS IEBCOPY steps. Executed installed
  `ICINT19` SCALVEC and observed `TEST:`/`EXP:`/`RP:`/
  `CODE=0` semantic PASS.
- Total: **three MVS-native on-tape installation profiles,
  42 isolated PDSes and 315 verified directory members**.
  The original MR10 restore was **not replayed**.
- Original `BC0004` AWS was rehashed unchanged at end. SHA-256:
  `7cc5a1d61882bf88469fd9f9e38512f1976ef1a775e3095e12e3988600c57af1`.
- Private preserved evidence:
  `workarea/ta3-rc4-continuation/20261123T163929Z-37828`.
  The earlier original interrupted receipt
  `workarea/ta3-rc4-recipient/20261123T133542Z-36979`
  and consumed no-retry marker are unmodified.

The source-controlled continuation explicitly verifies original
sealed MVS `IEF142I` records, tape-restored byte-checked
installer JCL, fresh MVS `LISTDS`/DCB and directory/member
inventories, and actual installed BCPL execution. The MVS
job numbers for the final NATIVE/COMBINED restores are retained
in the private receipt; only **9403** was reported on the console
and no additional job IDs are inferred.

**TA.3 acceptance gate: TECHNICALLY SATISFIED (qualified).**
The default MVS 3.8J site HLQ/volume was tested on the existing
MVS system in **fresh isolated namespaces**. Other site overrides
were not independently tried; independent clean IPL/new-system
installation belongs to TA.7. The complete MR10 11+17 demos,
12-case human-signed semantic review and distributed interpreter
rebuild belong to TA.4; native runtime/BLIB/coroutine/extension
tests belong to TA.5. The candidate declares
`native_compiler: absent`; TA.6 is N/A.

**No formal owner-directed TA.3 closure is yet recorded.**
Preserve both `BC0003` and `BC0004`; never rerun the consumed
producer, original recipient or continuation operations. No
publication or advancement of TA.4/TA.5 acceptance is inferred.

See [qualified TA.3 all-profile MVS acceptance](../../distribution/install-from-tape/ta3-rc4-all-profiles-accepted-20261123.md).


## TA.3 formal qualified closure and TA.4 march opening — 23 November 2026 EST

**Owner direction:** “Close TA3 and open TA4. Give me a handoff
prompt.”

**TA.3 — MVS Bootstrap and Installation is formally CLOSED
(qualified).** This explicitly accepts the
[RC4 all-profile technical gate](../../distribution/install-from-tape/ta3-rc4-all-profiles-accepted-20261123.md)
with its stated qualifications: on actual MVS 3.8J, the
standard-labeled `BCPL-0.1.0-rc4` / `BC0004`
tape delivered operable MVS-only `BT0001`/`BT0002`
bootstrap and three tape-resident installation profiles.
All **42 PDSes / 315 members** were installed and
verified; combined installed `ICINT19` SCALVEC
`TEST:`/`EXP:`/`RP:`/`CODE=0` passed. The
no-replay recovery validated first MR10 (11/94) before
executing NATIVE (11/71) and COMBINED (20/150).
Owner-provided continuation evidence:
`workarea/ta3-rc4-continuation/20261123T163929Z-37828`.
Immutable `BC0004` SHA-256 remains
`7cc5a1d61882bf88469fd9f9e38512f1976ef1a775e3095e12e3988600c57af1`.

Closure does **not** certify an independently IPLed clean target,
different recipient site parameters, the complete MR10
demonstrations/regression human sign-off, included native
component link/execute, provenance/rights clearance, or
publication. These belong to their distinct TA.4, TA.5,
TA.7 and TA.8 gates. The native Cambridge Compiler remains
`absent`; TA.6 is N/A for this candidate, not PASS.
Preserve all TA.2/TA.3 one-shot receipts and never replay
successful prior MVS or tape operations.

**TA.4 — MR10 Kit Compiler Distribution and Verification is
OPEN / IN PROGRESS** under the approved milestone gate.
Begin with read-only audit of distributed `ICINT19`
rebuild source/JCL, 11 language/17 BCPL demonstrations,
12-case `MRREGRES` semantic evidence and missing
human-identified sign-off. The already accepted RC3
**JOB 9369** 63-step/12-case MVS test is predecessor
evidence only; do not repeat it. TA.4 acceptance remains
separately unproven.

See the [formal TA.3 acceptance and transition](ta3-formal-qualified-closure-and-ta4-transition-20261123.md)
and the [TA.4 kickoff](ta4-kickoff-20261123.md).

## TA.4 — RC4 owner-reported rebuilt-interpreter and 28 demonstrations PASS (23 November 2026 EST)

Owner-reported actual MVS 3.8J `BC0004` verification succeeded: read-only
`T4R1PRE` **JOB 9418** checked 9 installed MR10 PDSes and two absent
verification targets; isolated IFOX/IEWL rebuild **JOB 9419** (4 steps),
rebuilt `ICINT19` SCALVEC **JOB 9420** (8 steps), 11 language demos
**JOB 9421** (38 steps), and 17 BCPL demos **JOB 9422** (62 steps),
all reported PASS. Original `R4MR` installation and media remained
unchanged. Owner-reported sealed evidence:
`workarea/ta4-mr10-verification/20261123T212347Z-39337`.

The successful TA.4 verification is **accepted as a qualified technical MVS
checkpoint**, not a formal TA.4 closure. Preserve and do not rerun the
one-shot verification. The existing **JOB 9369** 63-step/12-case
`MRREGRES` remains accepted predecessor evidence; **twelve individual
human verdicts plus identified, sealed overall `SIGN` receipt** remain
outstanding. See the [TA.4 RC4 MVS technical checkpoint](ta4-rc4-mvs-technical-verification-checkpoint-20261123.md).
**TA.4 remains IN PROGRESS.** TA.5/TA.7/TA.8, rights and publication
acceptance remain independent; TA.6 is N/A for this candidate.

## TA.4 — compact twelve-verdict human sign-off ready (23 November 2026 EST)

The original sealed RC3 JOB 9369 twelve-case manual verification remains a
required **human** acceptance gate. The existing read-only reviewer now
supports `--compact-signoff`: display all twelve `TEST:/EXP:/RP:/CODE=`
cases, then accept **twelve individual ordered P/F case verdicts,
reviewer identity and literal `SIGN` in one human response**. Original
`--signoff` and unsigned review remain available. It neither submits
MVS jobs nor mutates original evidence; any human FAIL blocks acceptance.
A signed receipt has **not yet been supplied**. See the
[TA.4 compact sign-off preparation](ta4-compact-human-signoff-preparation-20261123.md).
**TA.4 remains IN PROGRESS until the actual identified human receipt is
presented, verified and accepted by the owner.**

## TA.4 — historical RC3 sign-off review compatibility correction (23 November 2026 EST)

The first `--compact-signoff` invocation halted before any signature with
`RC3 registry reservation or manifest checksum changed`. The original
RC3 tape producer's three-candidate-only `plan()` was incorrectly reused
by a historical **read-only** review after RC4 had been appended to the
release registry. Both RC3 and RC4 manifest SHA-256 values were checked
against the current authoritative registry and match. The reviewer now
reconstructs the canonical RC3 regression deck through a dedicated
historical helper, retaining full RC3 manifest/source/JES/semantic/seal
checks and verifying later append-only reservations separately; the
original RC3 producer is **unchanged**. Focused local execution 7/7 PASS.
See the [signed-review compatibility correction](ta4-rc3-signed-review-historical-registry-correction-20261123.md).
**No human receipt has yet been reported; TA.4 remains IN PROGRESS.**

## TA.4 — automatic twelve-case acceptance contract (23 November 2026)

Owner supersedes the earlier human per-case verdict and SIGN gate. Keep all 12 literal EXP:, computed RP:, TEST: and interpreted CODE= results, and compare the original sealed MVS JOB 9369 evidence against independent golden records with fail-on-difference behavior. The new read-only TA.4 acceptance runner independently verifies preserved RC4 JOBS 9418-9422 and seals twelve automatic verdicts. Human sign-off is not required. No historical jobs are rerun and no release is published. TA.4 remains IN PROGRESS until actual automated receipt verification. See ta4-automatic-semantic-acceptance-decision-20261123.md.

## TA.4 — RC4 saved-evidence automated acceptance PASS; technical closure ready (23 November EST / 24 November UTC)

The owner ran the new read-only automated verifier from `main`
`145da0e3f0306cf0573216cffa8f1e6d5b37029e`. It reported
**12/12 MRREGRES PASS**, all **11 language + 17 BCPL** demos PASS,
rebuilt `ICINT19` PASS, and sealed a new independent acceptance receipt:
`workarea/ta4-mr10-automatic-acceptance/accept-20261124T003512Z-40183`.
It checks already accepted MVS JOB 9369 and RC4 JOBS 9418–9422;
no MVS operation was repeated. The unchanged WSL regression panel
was previously owner-reported **12 PASS / 0 FAIL / RC=0** (22 November).
All TA.4 technical gates are therefore supported. The prior manual
`SIGN` obligation was expressly superseded by owner decision.

**TA.4 technical acceptance PASS; READY FOR FORMAL OWNER CLOSURE.**
The explicit closure decision is separate; no assertion that the owner
already ordered formal closure is made. See the
[TA.4 accepted technical evidence](ta4-automatic-acceptance-pass-and-closure-readiness-20261123.md).
The [TA.5 read-only entry audit](ta5-entry-audit-and-design-preparation-20261123.md)
prepares the next approved march without opening it or authorizing
state-changing MVS operations. TA.6 remains N/A for the absent native
compiler; TA.7/TA.8 and publication are separate.

## TA.4 formal closure and TA.5 march opening — 23 November 2026 EST

**Owner direction:** “Close TA4, proceed to TA5. Give me a handoff prompt.”

**TA.4 — MR10 Kit Compiler Distribution and Verification is FORMALLY CLOSED.**
The accepted read-only automated receipt
`workarea/ta4-mr10-automatic-acceptance/accept-20261124T003512Z-40183`
verifies all 12 historical MVS `MRREGRES` cases, independently seals
12 per-case semantic decisions, and verifies RC4 `ICINT19` rebuild,
SCALVEC, 11 language and 17 BCPL demos. The earlier unchanged WSL
regression was reported as 12 PASS / 0 FAIL. Human case-by-case
signatures were expressly removed by the superseding owner decision.
See [TA.4 formal closure](ta4-formal-closure-and-ta5-transition-20261123.md).
No accepted MVS job, original recipient or tape operation is to be replayed.

**TA.5 — Native Runtime, Libraries, and Extensions Distribution is
OPEN / IN PROGRESS.** Begin with a read-only source/provenance audit
and design review of the actual installed native release libraries.
See the [TA.5 kickoff](ta5-kickoff-20261123.md) and
[TA.5 entry audit](ta5-entry-audit-and-design-preparation-20261123.md).
Native Core Runtime, Base Library, Coroutine Support and extensions are
not yet TA.5-accepted. TA.6 is N/A (`native_compiler: absent`);
TA.7, TA.8 and controlled publication remain independently gated.

## TA.5 — Owner-directed distribution-only scope and technical acceptance (23 November 2026 EST)

The owner limits functional release testing to the MR10 Kit Compiler until a full native Cambridge Compiler is available. Native sources and supporting artifacts are distributed as work in progress; no new native builds, object reproducibility tests, native application generation, linkage, execution or regression are required for RC4. This supersedes earlier TA.5 and TA.7 native test obligations, including those in historical checkpoints. Existing RC4 objects are preserved. The manifest's eight native PDSes / 41 members and accepted TA.3 NATIVE and COMBINED installation evidence satisfy the revised TA.5 distribution gate (qualified). TA.5 remains open pending formal owner closure; TA.6 N/A; TA.7 clean-target installation and MR10-only functional acceptance, TA.8 and publication remain separate. See [binding scope and evidence review](ta5-distribution-only-scope-and-acceptance-20261123.md). No new MVS operation is required for TA.5.

## TA.5 formal qualified closure and TA.7 march opening — 23 November 2026 EST

**Owner direction:** “Close TA5 and proceed to TA7. Give me a handoff prompt.”

**TA.5 — Native Runtime, Libraries, and Extensions Distribution is FORMALLY CLOSED (qualified)** under the owner-approved distribution-only gate. All eight native-group PDSes / 41 members are included in the accepted RC4 NATIVE and COMBINED profiles. Native functional acceptance and rebuild/reproducibility are deferred until the full native compiler is available. No new MVS operation was required. **TA.6 remains N/A for RC4**, not PASS or formal closure. **TA.7 — Clean-Target Integration and Release Acceptance is OPEN / IN PROGRESS**: independent clean MVS recipient, all three installation profiles, MR10-only functional verification, no native functional tests. See [formal closure and transition](ta5-formal-qualified-closure-and-ta7-transition-20261123.md) and [TA.7 kickoff](ta7-kickoff-20261123.md). Existing evidence and BC0004 remain immutable; TA.8 and publication remain separate. No new stateful MVS operation is authorized here.


## TA.7 — Owner-approved clean-namespace scope (24 November 2026)

The owner supersedes independent-system IPL with fresh, disjoint PDS namespaces on the existing MVS system: HERC02.BCPL.T7MR, T7NT and T7CB. See the [binding clean-namespace decision](ta7-clean-namespace-decision-20261124.md). The RC4 tape remains unchanged; all three profiles and both full MR10 functional panels are required. Native components remain distribution-only. TA.7 remains OPEN / IN PROGRESS pending actual MVS evidence; TA.8 and publication are separate.


## TA.7 — Clean-namespace MVS technical acceptance PASS (24 November 2026 EST)

Owner-reported MVS JOB 9423 established all 42 fresh PDS targets absent. All three RC4 installations passed exact manifest-selected inventory/DCB checks (MR10 11/94, NATIVE 11/71, COMBINED 20/150). MR10 JOBS 9431/9433/9435 and COMBINED JOBS 9447/9449/9451 passed 56 demonstrations and 24 automatic semantic regression verdicts, 80/80 total. RC4 remains unchanged. Evidence: `workarea/ta7-clean-namespace/20261124T133036Z-41593`. The [technical acceptance record](ta7-clean-namespace-acceptance-20261124.md) documents the owner-reported result and scope qualification. TA.7 technical PASS (qualified); formal closure awaits owner direction. Do not replay accepted operations. TA.8 remains pending; publication is not authorized.
