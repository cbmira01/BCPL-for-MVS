# DR.2 — System Extensions manuals: migration and evidence

**Date:** 25 November 2026 EST  
**Baseline:** 76d169317324435df6e547be692933c93260d455  
**Status:** Four substantive working drafts; no authority transfer or march closure.

## Evidence alignment

Eighteen tracked files (three package assemblers, three headers, three BCX macros and source/expected/selection for 148,149,151) match both CO.6 tested revision 216b6707c404a91c796ed8f1419a99ef172b184a and RC4 frozen revision e910de51c19c09698be139e33084a90401511cc9 by path/blob SHA. Not installed binary identity or native RC4 functional acceptance. Tutorial reproduces three complete accepted clients, selection card and expected records; predicted modification and illustrative JCL untested.

## Migration ledger

| Original authority | Destination | Mapping / remaining work |
| --- | --- | --- |
| R.0 A–H, Decision G, QUERY v1 | Reference 1–2; explanation 2–5 | Binary layouts, limits, 15 IDs, precedence, all-or-nothing query, append-only format, finalizer and ownership. Exhaustive fault precedence pending |
| R.1–R.5 and expanded closure | Explanation 3–5,8; reference 2,6; how-to 3–4,8 | Transactional registration, known-package macro selection, duplicate upgrade, explicit ENTRY, reverse finalization; historical failure and raw MAP/rollback qualifications |
| BCPLDEMO public header/README/source and permanent support | Tutorial; reference 3 | Exact operations, outputs/errors, guard examples and independent selection |
| BCPLTIME header/README/source T.0/T.1 | How-to 6; reference 4; explanation 6 | Raw return words, capacity, register preservation, aligned scratch; date interpretation and DD attribution unverified |
| QSAM public specification sections 1–17,21,24 and header/source | Reference 5; how-to 5,7; explanation 6–7 | All 33 constants, request/result words, dispatch-level exception, formats, geometry, staging, retry, EOF, handles, error/lifecycle exclusions |
| Q.1–Q.5 closure and installation/source-mode records | Reference 5–6; how-to 3,5,7–8 | Preserve 16 slots and 1024 total-byte ceiling, RDW/ASA, device evidence and failure/retry chronology, actual/injected refusal distinction, independent installed receipt gap |
| Registry and current BCXCAT | Reference 2,6–7; explanation 2,5,8 | Current three-package catalog supersedes dated DEMO-only description; registry owns allocation; G!202 reserved, G!299 coroutine, R2TESTB fixture |
| RC4 and CO.6 | All manuals | Release versus development, no new native execution or release |

## Outstanding reconciliation

- QSMDISP rejects unsupported opcodes and nonpositive request/result pointers before clearing result; source-derived qualification to broad result-zero wording. QCVFORM geometry is source-observed, not universal device acceptance.
- Q.5 injection after successful CLOSE does not establish genuine exceptional OS ownership; combined rollback error precedence unresolved, source retains primary error. No software correction.
- Q.5 independent installed selected/unselected proof remains unestablished by that record. Current installation/catalog and later reported clean-room do not independently establish that specific gate; numbered QSAM tests source-selected, Q5QVFY retired.
- Complete register preservation, exhaustive fault matrix, exact extension GET transport and raw receipts require additional review before normative transfer. No new JES, IFOX, IEWL, ICINT19 or GO execution.
- Existing contracts, sources, oracles, allocation, releases and historical evidence unchanged. DR.0 dependency qualification retained; explicit owner approval required for authority transfer and DR.2 closure.

### DR.5 — Native tutorial newline qualification

The [DR.5 language investigation](candidates/language-verification/README.md) confirms native *N=37 while the accepted BCPLIO delimiter is numeric 10. The System Extensions tutorial retains its exact accepted 148/149/151 fixture extracts and adds an explicit warning: short output followed by FINISH does not prove a NEWLINE() physical record boundary. New multi-record examples should use the current WRCH(10) contract pending resolution. Existing regression results and extension APIs are unchanged; no extension suite rerun or physical record verification claimed.

### DR.5 — Verified logical newline correction

Owner-reported MVS PASS at `828cf88dcd080868d7f126267f3650613571951d`: CAMBBLD 9498, BLIBBLD 9500, original compile 9501/native GO 9502, independent newline compile 9503 and native FB132 exact readback 9504. The unchanged original source and oracle now pass MR10 9489 and native 9502. The second candidate confirms logical newline 10, ordinary EBCDIC A=193, input/output boundaries and exact sequential-dataset records. See the [verification record](candidates/language-verification/README.md). Earlier failures and pre-fix 37 observations retained. Affected manuals distinguish rebuilt development environment from older objects. Focused defect verification complete; full post-change regression, clean-room reconstruction and normative transfer not established. No software or oracle change in this update.

### DR.5 — Post-correction supported regression PASS

Owner-reported production-profile eight-suite campaign following documentation checkpoint `f8ff445bf034d565a22ecee3af34ad0cd4cd5f77`: 208 PASS, 0 FAIL, 1 expected SKIP (083), 0 BLOCKED; BCPLQSAM 175/176 PASS; elapsed 10m 42s. See [verification record](candidates/language-verification/README.md) for private summary location and suite counts. The logical newline correction has focused and full supported-regression evidence in the existing development installation. No clean-room rebuild, release acceptance, or independent installed-image identity established. No normative transfer or march closure. Other reconciliation qualifications remain.

### DR.5 — System Extensions implementation reconciliation (26 November 2026)

Reviewed current source checkpoint `0d54ff4139dde495735e775ed4ac1da8a49b03a9`, including BCPLRGS,
BCPLMAIN startup/finalization, BCXPRE/BCXCAT/BCXPOST, the three public
headers and their assembler descriptors/dispatchers, BCPLQSAM public
specification, R.0 Decisions A–H and G/QUERY contracts, R.1/R.2 closures,
R.2 negative/dependency generator, Q.5 closure and case 164. Updated the
reference, explanation, how-to and the registry's obsolete G!200
implementation-status cell; allocation and approved ABI unchanged.

The three descriptors agree with public declarations: BCPLQSAM QSAMSVC
G!200, BCPLTIME TIMESVC G!201, BCPLDEMO DEMOSVC G!203. Each has API 1.0,
56-byte descriptor, one export and zero dependencies; only BCPLQSAM
has QSMFIN. G!202 remains assigned to proposed BCPLDEC with no
public dispatcher spelling. QUERY returns respectively (1,1,0,6,31,7),
(1,1,0,6,3,0), (1,1,0,6,1,0). BCX catalog selects precisely these
three packages. The common numeric return conventions, capacity checks
and finalization policy agree at the reviewed scope. Preserve prior
MVS evidence; no independent receipt for installed-only QSAM, genuine
exceptional CLOSE, or general register-preservation matrix is inferred.

#### Open registrar discrepancies

1. DEDUPE compares the current dependency ID against itself at RGSCAN=0
   when RGDEPI>0. Thus any second dependency reaches ERR1014 even if
   distinct and already selected. R.2 make-negatives.py constructs
   one dependency for validdep, missdep, major, minor, ordering and
   selfdep; it does not test two distinct dependencies.
2. DEPKGLP traverses RGCNT descriptors and reads the ID at +16 from
   a later selected descriptor before PKNEXT validates that descriptor's
   extent/header. This violates the required bounded validation before
   reading descriptor fields and can change the Decision G error order.
   A linked malformed later descriptor can expose an unchecked read;
   no unsafe pointer execution is authorized.
3. DEPMATCH uses signed comparison of minimum minor without rejecting
   negative values. The approved field is a version number, not an
   unrestricted signed minimum. Clarify malformed-version diagnostic
   classification before changing behavior. Full ID grammar validation
   also remains a build responsibility; do not broaden it without
   owner review.

Proposed correction, subject to owner approval: retain BCEX/BCRG v1,
limits, ownership ledger, diagnostic IDs and transactional PUBLISH.
Perform bounded descriptor structural preflight before dependency search;
compare the current dependency with preceding records, not itself; reject
malformed dependency version fields with the approved diagnostic policy.
Verify a private IFOX/IEWL candidate before replacing BCPLRGS. Add a
focused MVS fixture for two valid earlier dependencies, an actual
duplicate, missing/forward dependency, malformed later linked extent,
and malformed version; preserve all earlier negative and finalization
oracles. No global assignments or package source/API changes necessary.
Do not use the historical G!298/299 fixture allocation in a native
coroutine-composed executable. Exact permanent case assignment and
candidate mechanism follow owner design approval.

DR.5 production campaign at a0efe9a204e1f3f3968b60cb8c7065e9b423bce7
reported 212 PASS, one expected SKIP 083, no failures/blocked; all
13 Runtime Extensions, four BCPLTIME and 14 BCPLQSAM cases passed.
See [BCPLIO verification and campaign ledger](dr2-runtime-library-manual-migration-20261125.md).
The maintained packages have no dependencies, so these passes do not
test the new findings. Source inspection only in this increment; no
new MVS execution, implementation change, normative transfer, release
change or march closure.

### DR.5 — Owner-approved registrar correction candidate

Owner directed correction and continuation after the preceding findings.
Canonical BCPLRGS now performs three bounded passes over every selected
descriptor (extent, fixed header, counts/exact length), then validates
identities, exports, ownership and finalizer addresses before resolving
dependencies. No later descriptor ID is read before structural validation.
DEDUPE addresses prior dependency records from the table base, not the
current record. A nonpositive required major or negative minimum minor
is a malformed dependency record (1014); well-formed incompatible versions
remain 1011. This diagnostic classification is a scoped implementation
decision consistent with the existing invalid-record identifier. No
BCEX/BCRG v1 layout, public ABI, limit, global allocation, publication or
shutdown interface changes. Complete multi-fault precedence beyond the
structural categories is still qualified.

Permanent direct MVS assembler regression
[registrar-contract.asm](../../../bootstrap-toolchain/probes/dr5-registrar/registrar-contract.asm)
uses private relocated tables and a private G vector/owner ledger; it
does not link BCPLMAIN or register real package names. Eighteen exact
RGINIT status/publication assertions cover valid two dependencies,
duplicates, missing/forward/self/blank dependencies, structural precedence,
malformed and incompatible versions, ownership collision and recovery.
The two successful cases also check reverse finalization and no repeat.
All three G slots and REGCOUNT must remain unpublished on rejection.
GO RC=0 only after every assertion. Existing R.1/R.2 fixtures/oracles
preserved, except the obsolete static duplicate-loop assertion updated
to check the corrected table-base addressing. No new regular suite or
numbered native case; the permanent focused probe is separately invoked.
The 212-pass regular baseline is unchanged pending post-install regression.

The dedicated driver privately assembles the canonical BCPLRGS with the
probe, links and runs it, and only in explicit rebuild mode stages and
readbacks BOOT_ASM(BCPLRGS), assembles and replaces BOOT_OBJ(BCPLRGS),
verifies installed bytes by IEBCOMPR and runs the same probe linked
against that installed member. It reuses the accepted BCPLIO single-member
installation deck shape and exact ordered JES receipt helper. No
other persistent member is written; no compiler, BLIB or extension
rebuild. Stop on failure; retain private evidence and no automatic retry
or rollback.

Host checks: card hygiene, unique labels, case status sequence,
dependency-loop addressing and structural/dependency/publication control
flow inspected against exact proposed Git blobs. Exact driver copy verified
against its Git blob, Python syntax compilation passed, and mocked private
and installed deck construction, one-member write scope, offline check
and invalid configuration rejection passed. Local clone unavailable
(DNS). These are not IFOX/IEWL/GO tests; first target verification pending.
No normative transfer, release change or march closure.

### DR.5 — Private registrar JOB 796 failure and instruction correction

Owner-reported 26 November 2026: source revision `02b8ffa8d0e23774d99e5858e9f9eefeed15305a`,
`workarea/dr5-registrar-fix/run-1asz91v4`, ASMT/ASMR/LKED RC0,
GO RC9 (case 1), live WTO BCPLREG 1006 INVALID PACKAGE COUNTS and
DR5 REGISTRAR ASSERTION FAILED. Candidate stage stopped before any
production write. Registrar SHA-256
`c3abcbb2797fc1473ead131278bf3d38de30fc8e43c90dca3442efb80fd55d0c`;
probe SHA-256
`d474b1cb408abb61e505129ad1b91a75e3e8f29960d54efafc05dc074e34077b`.

Source review identifies the newly introduced PFCOUNT instruction
`L 3,4` as an absolute low-storage load, rather than the intended
`LR 3,4` register copy (as used in PFSPAN and the previous registrar).
This corrupts the calculated descriptor extent before the count/length
comparison. Correct only that assembler instruction; add a static
regression assertion for the register copy and absence of bare numeric
absolute L operands. Existing probe and all eighteen oracles unchanged.
Source/card checks passed; target reexecution required. The reported
diagnostic establishes the failure category, not an independently
inspected instruction trace. No production installation or new
acceptance claimed.

### DR.5 — Private registrar JOB 797: dependency ordinal correction

Owner-reported 26 November 2026, revision `6b80d87c5efea1c2b06da56093aa5e641037d78e`,
`workarea/dr5-registrar-fix/run-5sxiywjk`: ASMT/ASMR/LKED RC0,
GO RC9, live WTO BCPLREG 1012 DEPENDENCY ORDER FAILURE, then
DR5 REGISTRAR ASSERTION FAILED. Structural validation progressed
beyond the earlier 1006 failure. No production write occurred.
Registrar SHA-256
`b34ee44aba07cc14196aa37f74d8a07b4b7cdf1f7a8d98820bef8835b1ffbc1c`.

DEPKGLP shifted the selected-package ordinal in R4 by three to
form the eight-byte registry-entry offset, then DEPMATCH compared
that offset against the dependent package ordinal RGIDX. With
TESTA/TESTB/TESTC in order, TESTB index 1 became offset 8, falsely
rejecting TESTC index 2. The same instruction sequence predates DR.5
and the original single-dependency fixture selected index 0.
Preserve R4 as an ordinal and form the offset in scratch R2,
which is overwritten by the required API major in DEPMATCH.
No ABI, diagnostics, probe expectations or installation driver changes.
Add static coverage of the register distinction. The focused host
instruction model checks the actual search/match block for ordered,
forward and missing dependencies across selection counts 1–32; it
is not a System/370 emulator or substitute for MVS verification.
Target reexecution required before any production write.

### DR.5 — Corrected registrar installed and supported regression accepted

Owner-reported source revision `e19d03b4bd8443fe1c2fa22f97189cba897289ef`, 26 November 2026:
`workarea/dr5-registrar-fix/run-iy218a5e` PASS, complete.
DR5RGPR JOB 798 (18 assertions and finalization), BLDRGFIX JOB 801
(IFOX, installation, readback and IEBCOMPR), DR5RGIN JOB 802
(18 assertions and finalization) all PASS. Canonical registrar
SHA-256 `a04b9d910582f644f01e0a663a8ef1c49e763506af759a1f4f87c918f21b2b34`;
unchanged probe SHA-256
`d474b1cb408abb61e505129ad1b91a75e3e8f29960d54efafc05dc074e34077b`.
Preserve JOB 796/797 failure history. Four original defects (including
dependency ordinal) resolved at the exercised scope; no claim of
exhaustive hostile pointer, maximum dependency or multi-fault validation.

Subsequent eight-suite production campaign, owner-reported
`workarea/project-regressions/20261126T185752Z-17755-75zd5gej/summary.json`,
PASS in 12m51s: MR10 12, supported MR10 coroutines 5, Bootstrap
149 PASS/1 expected SKIP 083, Runtime Extensions 13, BCPLTIME 4,
BCPLQSAM 14 (including 175/176), Coroutines 13, paired contract 2.
Total 212 PASS, 0 FAIL/BLOCKED, one expected SKIP; 213 selected.
Private receipts not independently inspected. No clean-room or release
acceptance inferred.

Owner then directed addition of four permanent numbered regression tests.
Runtime Extensions retains 146–158 and appends 194–197. The shared
previously accepted direct assembler probe remains byte-identical; the
numbered runner derives distinct test bodies and links the installed
BCPLRGS in both native profiles. 194 covers multiple dependencies,
duplicates/missing/ownership/repeat and finalization; 195 isolates the
nonzero ordinal using a single dependency; 196 checks structural
preflight and precedence; 197 isolates malformed/incompatible versions
using one dependency on ordinal zero. Every check verifies exact status,
REGCOUNT and transactional publication, with reverse finalization
where applicable. A case is counted once, regardless of internal
assertion count. The regular inventory grows to 198 numbered cases
(17 Runtime Extensions), 217 selected across eight supported suites
with expected 216 PASS and one SKIP. First numbered MVS execution
pending; the existing 212-PASS campaign is historical and is not
relabeled. No implementation or installed member change in this
increment; no new march, release change or normative transfer.

Host validation before commit: exact Git-blob-verified run-suite and
test_stage2b_suite.py copies passed nine host tests (including all four
new identities through both synthetic profile wrappers and rejection of
a mismatched marker). Exact numbered runner and unchanged original
probe copies matched their Git blobs; Python compilation and four
host-only tests using mocked driver/configuration/JES boundaries passed,
covering derived source/oracles, isolated dependency layouts, JCL
read-only linkage, marker validation, and rejection of invalid modes
and fixture inputs. All 198 manifest identities/physical directories
were checked against the proposed Git tree. Git clone unavailable
(DNS); no claim of a full local repository checkout or MVS execution
of the four numbered variants. The previous probe and installed
registrar source remain unchanged.

### DR.5 — Numbered registrar regression integration accepted

Owner-reported 26 November 2026 EST (receipt directory timestamp
27 November UTC), revision pulled `94574c422fcdc097aeb43a1054727b3eeaa12ac8`:
`workarea/test-suites/20261127T000418Z-38933-runtime-extensions-production-qoiim7ne`.
Runtime Extensions, production profile: 17 PASS, 0 FAIL, 0 SKIP,
0 BLOCKED. All cases 146–158 and 194–197 reported native runner RC0.
This establishes first numbered MVS execution of the four new
installed-BCPLRGS cases and continued success of the thirteen earlier
Runtime Extensions cases. No change to the registrar or shared probe
since the accepted JOBs 798/801/802. Individual JES receipts and
summary JSON not independently inspected; the owner-provided suite
output is the evidence for this acceptance.

The last complete eight-suite campaign remains 212 PASS and one
expected SKIP at `e19d03b4bd8443fe1c2fa22f97189cba897289ef`.
The later 17-case suite supersedes its 13-case Runtime Extensions
result for that suite only. Across the two reported runs, all 216
distinct supported passing identities and expected SKIP 083 are
accounted for; do not describe this as a single 216-PASS campaign.
The expanded eight-suite inventory contains 217 selected cases;
a consolidated run at the expanded inventory has not yet been
reported. Installed-r5-t1 execution of the new numbered cases has
not been reported. No release, clean-room, exhaustive ABI or
normative-transfer claim. DR.5 remains in progress.

### DR.5 — Installed BCPLQSAM selection and exclusion verified

Owner-reported MVS execution at Git revision
`2cd7d8fa281c0a99659445278d1483e12618ca50`:
`workarea/dr5-qsam-installed/run-fxc8sbn1`, status PASS, stage complete.
The [verification driver](../../../tools/checks/run-dr5-qsam-installed.py)
passed its synthetic JCL/XREF self-check before executing the following jobs.

| Case | Compiler JOB | Native JOB | Exact GO marker |
| --- | --- | --- | --- |
| 163 selected | DR5QSC 1260 | DR5QS 1261 | BCPLQSAM Q4 QUERY CARRIAGE PASS |
| 146 unselected | DR5QNC 1262 | DR5QN 1263 | R5 EXT 146 PASS |

| Case | BCPL source SHA-256 | Generated assembler SHA-256 |
| --- | --- | --- |
| 163 | `8a0c3a79f8c877893bb1fb77a365da7a1a6b69a562293056b604f931b8110ea6` | `1aa569da8cfe27002631aaf3bf5aefc7cd2fcdb9154fa786d13e486adc3f0820` |
| 146 | `d34773015f38a96510f95ae7a844785d678a58d983877210382c846b3db682a6` | `703952546a24d416f7eb6552d60ae1ede868da86a9dc4a49e60120ecb87f0926` |

The reported driver PASS establishes its checked compiler completion,
IFOX/IEWL/GO zero RCs, IFOX severity, installed BOOT_OBJ and resident
EXT_MAC selection, IEWL entry, selected EXTLIB(BCPLQSAM) and all QSAM
CSECTs with 44-byte BCPLREG, and absence of those sections and INCLUDE
with 28-byte empty BCPLREG. Exact standalone GO markers occur once.
This is the subsequent installed-object selection/exclusion evidence
missing from the historical Q.5 closure; that closure is not rewritten.
The private reports were not independently inspected. No installed
member replacement, fresh object build/readback comparison, record I/O
through the installed BCPLQSAM object, device execution, genuine
exceptional CLOSE, clean-room or release acceptance is claimed by
this campaign. The numbered 163–176 suites remain source-selected;
these two supplemental executions do not increase the numbered inventory
or change the supported campaign totals. No normative transfer.

### DR.5 — QSAM dual-mode regression integration (MVS verification pending)

Owner approved extension of the existing numbered QSAM fixtures before
adding genuinely distinct numbered behavior tests. The historical
`installed-r5-t1` profile name is retained. Cases 163–176 now have
source-selected production and installed-object execution paths. The
installed adapter removes only private BCPLMAIN, BCPLRGS and BCPLQSAM
assemblies, reads resident BCXPRE/BCXCAT/BCXPOST, links installed runtime
and extension members and retains the original application, independent
IFOX reader/writer/verifier, GO DD and device contracts. Case 170 retains
both required packages. Installed maps require the correct registry,
QSAM CSECTs and symbols, exclude unrelated packages, and check independent
verifier exclusion. The R.5 map checker now rejects unintended QSAM
inclusion, including case 146. No fixture, public ABI, installed member,
case ID, historical closure or release artifact changes.

Host adapter compilation and synthetic query, two-application and
mixed-package transformations passed locally, including malformed deck
and map rejection. Exact adapter Git blob verified against local tested
file. Full repository clone blocked by DNS; integrated generator preflight
runs before installed native compilation. Actual numbered installed
record I/O and device results remain pending. Do not count these proposed
executions as new unique cases or as a passing full campaign. Distinct
rollback/cleanup/competing-status coverage is a subsequent design and
verification task; genuine exceptional CLOSE remains qualified.

### DR.5 — First numbered installed QSAM attempt blocked in host preflight

Owner-reported revision `8530087dc4dbf3ef31faf76b7891accf0f228ffb`:
installed-r5-t1 Runtime Extensions case 146 PASS (evidence
`workarea/test-suites/20261127T031219Z-41171-runtime-extensions-installed-r5-t1-ruqaxxgd`).
The immediately following installed BCPLQSAM suite reported 0 PASS,
14 FAIL (evidence
`workarea/test-suites/20261127T031221Z-41269-bcplqsam-installed-r5-t1-pfqkwtsf`).
Case 163 runner log reports `unexpected BCX requirements` before compiler
submission. The adapter's initial synthetic fixtures omitted the actual
BCXREQ macro prototype; its selection test incorrectly treated
`BCXREQ &PKG` in BCXPRE as an invocation. All fourteen cases share this
preflight; the other thirteen individual logs were not inspected.
This is not evidence of a native BCPLQSAM failure. Fix the adapter to
recognize MACRO/MEND boundaries and verify the exact top-level selection,
BCXEND and END cards; retain strict rejection of unexpected invocations.
Add host regression coverage for actual tracked BCX streams and all
fourteen generator shapes. No MVS object or oracle changes. The focused
installed JOBs 1261/1263 remain accepted; full numbered installed-mode
execution remains pending.

### DR.5 — Numbered installed BCPLQSAM regression accepted

Owner-reported revision `c96523d970d433cb045e58c11d4d70b7836809f0`,
26 November 2026 EST (receipt directory timestamp 27 November UTC):
all fourteen actual generator shapes passed the dual-mode synthetic JCL
preflight. The subsequent installed-r5-t1 BCPLQSAM suite reported
14 PASS, 0 FAIL, 0 SKIP, 0 BLOCKED, cases 163–176, each native runner RC0.
Evidence: `workarea/test-suites/20261127T031901Z-41500-bcplqsam-installed-r5-t1-jg1q738t`.
Together with the prior installed case 146 PASS, this establishes installed
selection/exclusion and the exercised record-I/O, lifecycle, interoperability
and device-output contracts. The initial failed host-preflight campaign
is retained above; its defect is resolved at the reported scope. The
private individual JES reports and summary JSON were not independently
inspected. The reported PASS includes the runner's installed MAP/XREF,
exact GO output, expected STOP RC and independent IFOX/device checks
as applicable. The earlier source-selected fourteen-case production
result remains valid at its tested revision; no new full source-mode
MVS rerun after the adapter change is claimed. Both profiles retain the
same case IDs and expected-output contracts. The supplemental installed
run does not change the 198 numbered identities or the 216 distinct
supported passes plus expected SKIP 083 accounted for across earlier
production runs. No fresh installed-object rebuild/readback, genuine
exceptional CLOSE, full clean-room or release acceptance, or normative
transfer is inferred. New distinct rollback/cleanup/status-precedence
coverage remains to be designed and verified. DR.5 remains in progress.

### DR.5 — Numbered QSAM fault-regression integration

Owner approved the three remaining areas. Append cases 198 (injected
stage refusal with real successful rollback CLOSE, historical Q5RBFIN),
199 (genuine conditional 1024-byte GETMAIN RC4 under bounded pressure,
historical Q5RGM plus final zero-counter check) and 200 (combined primary
stage refusal and one test-injected nonzero R15 after real successful
rollback CLOSE, explicit counter and quarantine checks). Case 200
requires -11 and no published handle despite private CLOSE -14, surviving
Q00, successful Q01 reopen with the next public ID, one quarantined
unpublished slot, no stage retained there, no CLOSE retry, and finalizer
RC8. The existing source's primary-status rule is provisional; these
assertions characterize that behavior, not a normative transfer or new
production policy. Genuine exceptional CLOSE remains qualified.

All three compile from checked fixtures on every execution. Both profiles
use a private temporary ASMQ overlay and existing temporary BCX/runtime
source construction with read-only BOOT_OBJ; 163–176 keep dual modes.
Exact native GO and expected return codes, job-bounded console and
hardcopy WTO sequences, and the historical IFOX fall-through proof for
198 are mandatory. No historical workarea dependency, device operation,
production source or installed member change, or release change.

Host validation: exact Git-blob-verified diagnostic helper compiled
locally, passed synthetic combined overlay/card checks and eight missing
anchor negatives, and passed bounded console-pair checks for each kind
plus wrong-job, missing/duplicate marker negatives. All eight anchors
were independently checked unique in the unchanged actual GitHub
BCPLQSAM assembler. Full checkout DNS unavailable; integrated synthetic
JCL preflight and new numbered MVS execution pending. Do not relabel
prior accepted Q.5 jobs or earlier DR.5 campaign as these new results.
Inventory 201 native cases (17 QSAM); supported eight-suite target
219 PASS, 1 expected SKIP 083 (220 selected), not yet demonstrated.

### DR.5 — First numbered QSAM fault results, 26 November 2026 EST

Owner-reported revision `261e6b403e1f7956a7cd4cad256fd9a4708bb3ea`,
production profile evidence
`workarea/test-suites/20261127T033236Z-43074-bcplqsam-production-s07a477d`:
198 PASS, 199 PASS, 200 FAIL (2 PASS, 1 FAIL). The three actual generator
preflights passed. Case 200 compiler JOB 1299 RC0, native DR5QCOM JOB
1300 all nine preceding steps RC0, GO RC8 as expected, zero IFOX
statements flagged/severity, JES SUCCESS, exact BCPL PASS, both independent
job-bounded diagnostic traces PASS. The sole failure was the registrar
message checker. Owner supplied report line 20 (job-attributed WTO),
line 621 (standalone message), and line 10747 (exact BCPL PASS); the
report organizes JES output by section, not native execution chronology.
Corrected validator requires exactly one job-attributed registrar WTO
matching the summary's JOB and exactly one standalone registrar message;
assembler listing strings cannot satisfy either. Local isolated parser
checks passed observed record layout and nine negative scenarios.
Full checkout remains unavailable locally. Retained original report and
console/hardcopy records can be rechecked without JES submission using
`--review-combined` on
`workarea/native-regression/200-qsam-combined-rollback-quarantine/native-4yq8znnp`.
Native behavior accepted at owner-reported scope; automated replay still
pending. Original campaign summary remains 2 PASS, 1 FAIL; no fresh native
run or revised historical summary claimed. No implementation, fixture,
installed member or production precedence policy change. Genuine MVS
exceptional CLOSE still unverified. DR.5 remains in progress.

### DR.5 — Case 200 retained evidence reconciliation accepted

Owner-reported revision `e9f0f7380fcf743c748dcc8f3e3fad246f2d4329`:
`CASE 200 JOB 1300: RETAINED NATIVE EVIDENCE PASS (no JES submission)`.
The corrected checker accepted the original summary, report and both
job-bounded diagnostic records. Cases 198–200 therefore all have accepted
native evidence; the initial suite receipt remains 2 PASS / 1 FAIL and
is not rewritten. No new JES job, production object change or actual
exceptional MVS CLOSE is claimed. The combined injected-status case
characterizes existing provisional precedence, not normative approval.
All 17 QSAM cases have accepted evidence across separate runs; 163–176
also passed installed mode. The 219 distinct supported passes and one
expected SKIP 083 are accounted for across the earlier campaigns and
this retained-evidence reconciliation, not one consolidated 220-case
campaign at current HEAD. A consolidated supported campaign remains
outstanding. No normative transfer or release acceptance. DR.5 remains
in progress.

### DR.5 — First normative decision and transfer proposal

At source checkpoint `1ea630fc8ed1a188d8a7533824006731b41f5d43`, reread the shared QUERY v1 owner decision,
reference chapter 1, all three maintained dispatcher implementations,
case 160, 163, 164 and 170 fixtures, and the QSAM OPEN/CLOSE rollback
paths. The [proposal](dr5-query-authority-and-qsam-precedence-proposal.md)
maps common QUERY clauses and their evidence to chapter 1 and separately
requests explicit acceptance of primary-error precedence for failed OPEN
rollback. The existing approved returned-CLOSE/finalizer policy and the
qualification on genuine exceptional MVS CLOSE are preserved. Neither
proposal is effective before explicit owner approval. No source change
or repeat execution required for proposal review.

### DR.5 — Owner approval: QUERY and rollback precedence

On 27 November 2026 the owner explicitly approved both proposals and
commits. See [effective decision](dr5-query-authority-and-qsam-precedence-acceptance-20261127.md).
Reference chapter 1 becomes normative for common QUERY v1; chapter 5.4
records the separate primary OPEN error precedence policy. Original
contracts and native evidence remain intact; all other transfers remain
pending. Only BCPLQSAM comments changed; non-comment cards and line count
are identical. No fresh IFOX/IEWL/GO result or installed binary change.

### DR.5 — Common registration authority transfer proposal

At `ed04ba40b7155ca0032d9bf0548de547c58d72db` the first QUERY transfer and rollback decision are effective.
The [registration proposal](dr5-registration-authority-transfer-proposal.md)
maps A–H and Decision G to reference chapter 2 and identifies a bounded
post-structural diagnostic-order qualification. Current source traversal
and structural case 196 are distinguished from an unverified exhaustive
multi-fault matrix. Explicit owner approval remains required; no further
transfer, code change or native execution in this proposal.

### DR.5 — Common registration and finalization authority effective

The owner approved the transfer and stated diagnostic-order qualification
on 27 November 2026. See [effective decision](dr5-registration-authority-transfer-acceptance-20261127.md).
Reference chapter 2 now governs the transferred A–H/Decision G provisions;
original decisions and evidence are preserved. Structural precedence and
post-structural linked traversal are explicitly distinguished. Macro/tool
interfaces and package APIs remain outside this transfer. No code change,
new MVS execution or march closure.

### DR.5 — Package-specific API transfer proposals

At `6aec1d9558368e59d4604e3cad8e38c58060e1fa` common registration and finalization authority is effective.
Reconciled the three package headers and existing dispatcher/source review,
public README APIs, BCPLDEMO support decision, T.0/T.1 and Q.0–Q.5 public
contracts and closures. See [three bounded API transfer proposals](dr5-extension-package-api-authority-transfer-proposal.md).
Retain support governance, private implementation details, allocation
registry, headers and evidence as separate authorities. Identified stale
candidate wording in current BCPLQSAM README/header; corrected current
status while preserving dated design history and all constants. No
normative transfer before owner approval; no MVS execution or behavior
change.
