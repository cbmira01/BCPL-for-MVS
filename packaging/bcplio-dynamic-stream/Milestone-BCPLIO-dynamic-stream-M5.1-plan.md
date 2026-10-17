# BCPLIO dynamic streams — M5.1 acquisition feasibility

**Status: M5.1 CLOSED (2026-10-17): M5.1.1 A/Z printer routing JOB 8184 ACCEPTED; M5.1.2 exact QSAM FB132 disk dataset readback JOB 8185 ACCEPTED. Prior M5.1.3 JES2 internals investigation WITHDRAWN from BCPLIO acceptance.**
Predecessor: M5.0 evidence contract **ACCEPTED** by the owner.
[M5.0 contract](Milestone-BCPLIO-dynamic-stream.md).

## M5.1 — CLOSED, owner responsibility-boundary decision (2026-10-17)

The owner explicitly confirmed that **BCPLIO's responsibility ends at
correctly delivering application records to MVS QSAM**. JES2's
internal spool storage and subsequent printer delivery are MVS/JES2
responsibilities, not obligations to reverse-engineer or test in
this BCPL reconstruction milestone.

**Accepted evidence:**
- **M5.1.1 / JOB 8184 AT114R:** IFOX ASMAP, IEWL LKED and GO all
  RC0000. SYSPRINT's two logical output records appeared in the
  class-A/PRINTER1 image; BCPALT's two appeared in the
  class-Z/PRINTER2 image, without detected cross-class mixing.
  This is an observed route check, **not** raw JES2 spool-byte proof.
- **M5.1.2 / JOB 8185 M5D124B:** original compiled BCPL
  regression-124 GO against DEVOBJ BCPLM6+BCPLIO, with REPORT and
  REPORT2 assigned to distinct temporary sequential FB132
  datasets; ASMAP, LKED, GO, VASM, VLINK and independent VCHK
  each RC0000, without reported abend. VCHK's QSAM GET/CLC
  comparisons accepted the complete 132 EBCDIC bytes of all
  records and exact EOF: REPORT two records; REPORT2 one.
  The six offline v2 tests and exact generated-JCL/ASM/hash
  preflight also passed.

**Decision:** M5.1.3 (internal JES2 SYSOUT spool acquisition) is
**withdrawn as a required acceptance gate**, not declared proven.
It can be separately investigated later by MVS/JES2 tooling projects;
this milestone will not depend on it. A class printer image cannot
demonstrate unmodified raw spool bytes, and the dataset
readback proves dataset-level QSAM output, not raw SYSOUT internals.
These caveats remain explicit.

**M5.1 ACCEPTED and CLOSED.** M5.2 will test that the existing
physical record verifier actually rejects bad data, using a
small number of negative controls. No runtime change, ABI change,
PDS update or production OBJ promotion is authorized.

## Intent

Separate two outcomes:
- **Route observation:** original regression 114 GO SYSPRINT and GO
  BCPALT intentionally carry different logical output. Temporarily
  direct SYSPRINT to JES SYSOUT=A and BCPALT to SYSOUT=Z, then seek
  distinct completed JOB sections on TK5 PRINTER1 and PRINTER2.
- **Raw-record fidelity:** whether the original QSAM FB132 EBCDIC
  record, every trailing X'40' pad and the record count are
  recoverable. The above printer-file check **does not** prove this.

M5.1 must later address dynamic REPORT/REPORT2, and either
demonstrate unchanged DD-labelled spool retrieval or document
the limitations of physical sequential FB132 dataset proof.

## Existing implementation and important correction

The accepted full panel uses the installed-PDS strategy.
For regression 114 its generated candidate GO deck is:

  workarea/native-regression/114-interleaved-stream-records/runtime-pds-go.jcl

The older tools/checks/prepare-dd-attribution-probe.py defaults to
native-test-heavy.jcl, which is for a different source-assembly route.
**Do not use that default for this DEVOBJ BCPLM6 experiment.**
The new tools/checks/m51-route-probe.py locates the correct source deck,
requires the DEVOBJ BCPLM6 + BCPLIO links, and invokes the existing
non-submitting A/Z JCL transformation. It changes only the probe
JOB name and the two GO SYSOUT class allocations; it does not
recompile, assemble or install anything.

Git tracks the Docker Compose bind mount mvs-state/prt -> /tk5/prt.
The active /tk5/conf/tk5.cnf is **not** in the Git repository.
The class-A/Z to PRINTER1/PRINTER2 mapping must be checked against
the *live* operator environment and then observed through the
isolated job. Do not infer it from file names alone.

## M5.1.1 physical A/Z printer route — ACCEPTED 2026-10-17

The operator updated Git through `31dbeaa`, ran
`test-dd-attribution.py` **10/10 PASS** and
`test-m51-route-probe.py` **6/6 PASS**. The
read-only live-device inspection found:
```text
class A / PRINTER1: mvs-state/prt/prt00e.txt (74,902,995 bytes)
class Z / PRINTER2: mvs-state/prt/prt00f.txt (91,029 bytes)
000E 1403 prt/prt00e.txt ${TK5CRLF}
000F 1403 prt/prt00f.txt ${TK5CRLF}
```

The checker separately noted that device definitions alone
do not prove JES writer class routing. The operator then
prepared the unchanged candidate regression-114 class
probe, capturing offsets **A=74902995 and Z=91029**,
submitted exactly one isolated GO deck `AT114R` via
socket reader and received **JOB 8184**.
The real MVS/JES job summary was:
```text
JOB 8184 AT114R
ASMAP IFOX00 RC=0000
LKED  IEWL   RC=0000
GO    PGM=*.DD RC=0000
JOB RESULT SUCCESS; highest RC 0000
Statements flagged 0; highest assembler severity 0
140 cards; 340 SYSOUT records
```

The independent printer image checker reported:
```text
PASS job 8184 AT114R: class A / PRINTER1 matched
2 SYSPRINT records; class Z / PRINTER2 matched
2 BCPALT records; cross-destination contamination absent
M5.1 route evidence: PASS for separate A/Z printer images
Saved: workarea/native-regression/
  114-interleaved-stream-records/m51-class-route-result.json
```

**ACCEPTED, scoped to observed class A/Z physical
printer routing under this JOB, plus absence of
cross-class logical record contamination.** This is
real runtime/JES evidence, beyond the offline
tests. It is NOT proof of unmodified original FB132
EBCDIC bytes, original JES2 spool substream format,
or dynamic REPORT/REPORT2 DD routing. The two local
formatted-printer captures and JSON manifest should
be retained as operator evidence.

## M5.1.0 — read-only offline and live device checks

~~~sh
cd ~/Source/Repos/BCPL-for-MVS
git pull --ff-only
python3 tools/checks/test-dd-attribution.py
python3 tools/checks/test-m51-route-probe.py
python3 tools/checks/m51-route-probe.py inspect
~~~

Inspect reads the two host printer files and obtains **only**
the live Hercules configuration using docker exec mvs38j cat.
It expects one 1403 at 000E writing prt00e.txt and one at
000F writing prt00f.txt, but does not claim that those device
lines establish JES spool routing. If the check reports
UNCONFIRMED or UNAVAILABLE, **do not submit** until the actual
device definitions have been reconciled.

## M5.1.1 — exactly one isolated A/Z probe

Only after inspection and review of routing assumptions,
stage the probe (still no JES submission):

~~~sh
python3 tools/checks/m51-route-probe.py prepare
~~~

This **fails closed** if the existing DEVOBJ candidate 114 GO
JCL is missing or wrong, or if the two physical printer files
are absent or aliased. It saves offsets, inode identities,
Git SHA, source/probe JCL hashes and fixture hashes in:

  workarea/native-regression/114-interleaved-stream-records/m51-class-route.json

It writes a separate JCL deck and refuses to overwrite
previous work. Never delete an evidence bundle to rerun silently.

Submit **only this one probe** explicitly using:

~~~sh
tools/mvs/submit-jcl workarea/native-regression/114-interleaved-stream-records/m51-class-route.jcl
~~~

The submitter prints JOB N. On its completion, check job
steps using tools/mvs/job-summary N and then verify:

~~~sh
python3 tools/checks/m51-route-probe.py verify N
~~~

The verifier checks the same printer device/inodes and staged
JCL/fixture hashes; extracts the complete post-offset printer
sections; invokes the existing strict class A/Z routing checker,
saves two **formatted printer** binary samples and a JSON evidence
manifest. No printable capture is described as raw QSAM.

Expected SYSPRINT class A logical records: AB, C.
Expected BCPALT class Z logical records: 1, 2.
The routing checker rejects misplaced records, wrong job
banners, foreign jobs and cross-destination contamination.
The experiment succeeds only with distinct sections and the
intended GO RC0000, not merely a matching combined report.
Record actual JES job ID and return codes separately.

## Boundaries and next technical decision

A successful class-separated test proves *printer route
separation for this probe*, subject to verified live mapping,
not individual JES DD-labelled raw record export. It does
not prove REPORT/REPORT2 separately or unmodified FB132 bytes.

After M5.1.1, inspect actual JES2/TK5 spool capabilities
before choosing an implementation. If raw DD-labelled
SYSOUT capture cannot be shown, investigate **distinct
scratch sequential FB132 datasets**, with a verified
binary export or readback from MVS and explicit control
of each JCL DD/DSN. Do not assume tools/datasets/dspal get
can export binary sequential records.

**M5.1 remains OPEN** until actual, repeatable DD-specific
capture exists, its provenance and raw-byte limitations
are recorded, and the chosen acquisition strategy is
accepted. M5.0 approval does not authorize promotion to
production OBJ or runtime/ABI changes.

## M5.1.2 — ACCEPTED: physical FB132 QSAM dataset readback (JOB 8185, 2026-10-17)

The operator pulled Git `07f536d` and ran the
M5.1.2 offline fixture tests and exact generated-deck
review against the v2 workarea artifacts:

```text
Ran 6 tests in 0.001s — OK
M5.1.2 v2 offline artifact review: PASS
  Job M5D124B, DEVOBJ BCPLM6 + BCPLIO
  Step order ASMAP / LKED / GO / VASM / VLINK / VCHK
  REPORT / REPORT2 distinct temporary FB132 dataset write/read
  JCL, assembler and fixture SHA256 match staged manifest
  Regenerated exact v2 assembler/JCL compare: PASS
  MVS assembly/execution and JES raw SYSOUT: NOT VERIFIED
```

The operator then submitted **exactly the reviewed
`m51-fb132-dataset-v2.jcl`** and received
**JOB 8185**, job name `M5D124B`. The
MVS/TK5 `tools/mvs/job-summary 8185` reported:

| Step | Program | Return code |
|---|---|---|
| ASMAP | IFOX00 | 0000 |
| LKED | IEWL | 0000 |
| GO | compiled BCPL load module | 0000 |
| VASM | IFOX00 | 0000 |
| VLINK | IEWL | 0000 |
| VCHK | independent FB132 GET/CLC verifier | 0000 |

JES job result **SUCCESS**; highest RC0000;
assembler statements flagged **0** and highest
severity **0**; 334 cards and 888 reported
SYSOUT print records. Neither runtime source
nor PDS member was modified.

**What the accepted VCHK result means:** the
compiled BCPL program opened its named REPORT
and REPORT2 DDs, which in this isolated job
resolved to *distinct* temporary QSAM FB132
sequential datasets. The subsequent independent
MVS assembler verifier opened those datasets
by their corresponding DDs and used QSAM
`GET` followed by `CLC` over all 132 bytes
of each expected record, including EBCDIC
X'40' padding. It rejected missing/extra
records by using EODAD plus explicit count
checks. The resulting RC0000 proves this
**specific positive dataset-level experiment**:
REPORT has exactly two records
(`BCPL REPORT A`, `BCPL REPORT B`);
REPORT2 has exactly one
(`BCPL REPORT2 PART`), each with byte-exact
CL132 padded contents. The readback does not
depend on right-trimmed printer output.

**M5.1.2 ACCEPTED, scoped to distinct FB132
sequential-dataset attribution, byte-for-byte
readback, order, and EOF.** This is a
positive integration probe; its verifier
negative-control matrix is still an M5.2
requirement, not claimed to have run here.
The VCHK verifier's own success is inferred
from its assembled source and RC; the individual
raw records were not exported to the host.
The report only covers the explicitly tested
dataset-backed GO allocations, not every
arbitrary DD.

**No JES2 spool claim:** this job redirects
REPORT/REPORT2 from SYSOUT to temporary
physical datasets, and therefore cannot
establish unchanged original JES2 SYSOUT
data record bytes or metadata. The prior
JOB 8184 showed A/Z printer routing,
not raw spool. Both forms of evidence are
preserved and not conflated.

## Historical proposal superseded by M5.1 closure: JES2 SYSOUT extraction

**Purpose:** investigate whether the actual
MVS 3.8J/TK5 JES2 SYSOUT spool can provide
DD-labelled raw record payloads (or a demonstrably
lossless transform), without inferring such
capability from the newer z/OS API.

Historical Hercules/MVS JES2 documentation
describes the writer transferring spooled output
to emulated printer/punch devices on job completion.
The MVS 3.8 TSO `OUTPUT` command can copy
spooled SYSOUT to a dataset described as
RECFM=VBA/LRECL=137; the QUEUE utility has
a `SAVE` function described as producing
RECFM=FBM/LRECL=133. Neither format, by its
mere appearance, proves the unmodified
FB132 bytes written by the BCPL QSAM DCB.
Investigate original carriage-control and
record representation **before** asserting that
a conversion preserves all 132 bytes.
[Historical JES2 FAQ](https://www.jaymoseley.com/hercules/faq/mvsfaq02.htm);
[Historical TSO/QUEUE output FAQ](https://www.jaymoseley.com/hercules/faq/mvsfaq04.htm).

Modern IBM `SPOOL Read Service` documentation
describes SSI functions on *z/OS*. It **must
not be assumed available on MVS 3.8J**.
[IBM z/OS SPOOL Read Service](https://www.ibm.com/docs/en/zos/2.5.0?topic=71-spool-read-service).

**Proposed gate:** inventory the live TK5
JES2 writer/held-class setup, exact installed
TSO OUTPUT and QUEUE behavior, existing
printer/spool format and whether any
**DD-specific** SYSOUT-record extraction is
available. Preserve a source/target
DD-to-queue record identity chain. Prefer a
read-only inventory before any new spool
job or destructive spool access. If no lossless
DD-labelled extraction exists, document the
technical barrier and obtain an explicit
owner decision about satisfying the final
SYSOUT obligation with combined A/Z route
and QSAM dataset proof versus requiring
additional native JES2 tooling.

**M5.1.3 NOT EXECUTED. M5.1 remains OPEN.**
There is no M5.1.3 acceptance merely because
JOB 8185 succeeded.

## M5.1.2 — separate FB132 sequential dataset readback (STAGED)

The owner-approved scope requires physical record contents, not
just formatted printer text. As the next acquisition *feasibility*
experiment, the non-submitting source generator
`tools/checks/m51-fb132-dataset-probe.py` reuses
regression 124's existing DEVOBJ BCPLM6
`runtime-pds-go.jcl` and immutable REPORT/REPORT2
expected fixtures. It changes only the GO DD allocation targets:

- REPORT -> unique temporary FB132 sequential dataset &&M5RPT1;
- REPORT2 -> unique temporary FB132 sequential dataset &&M5RPT2.

It appends separate IFOX `VASM`, IEWL
`VLINK` and independent native QSAM
`VCHK` steps. The verifier GETs both
datasets independently; each record's full **132 EBCDIC
bytes** are compared using `CLC` against
explicit assembler CL132 blank-padded literals.
The checker fails if a record differs, is missing,
is reordered, or is added unexpectedly.

**Preparation only — offline, no submission:**

```sh
cd ~/Source/Repos/BCPL-for-MVS
git pull --ff-only
python3 tools/checks/test-m51-fb132-dataset-probe.py
python3 tools/checks/m51-fb132-dataset-probe.py prepare
```

Generator fail-closed checks include the exact
RG124R candidate GO job, BCPLM6 and BCPLIO
linkage, original DD placement and the immutable
regression 124 fixtures. It refuses to overwrite
staged outputs. It writes only untracked files under
`workarea/native-regression/124-dynamic-dd-selected-output/`:

- m51-fb132-dataset.jcl — isolated job M5D124R;
- m51-fb132-verifier.asm — independent machine-byte checker;
- m51-fb132-dataset.json — source/fixture/probe hashes.

**No job is authorized for automatic submission by
this tool.** Review the generated assembler and JCL,
and report the five offline unit-test results plus
whether the candidate deck was prepared before
deciding to run the one isolated job. If submitted
later, acceptance requires ASMAP, LKED, GO, VASM,
VLINK, VCHK all with RC0000 and no abend.

A successful result would prove the identity and
byte-for-byte contents of two *physically separate
temporary sequential QSAM datasets*. It would
**not** prove unchanged JES2 SYSOUT spool content.
Original DD-labelled raw spool fidelity remains
a distinct evidence obligation under the strict
M5.0 contract, not silently waived by a dataset test.

**M5.1.2 remains STAGED, not executed. M5.1 OPEN.**

## M5.1.2 source review and linkage correction — 2026-10-17

The operator ran **5/5 original offline generator unit
tests PASS**, and staged the initial unsubmitted three-file
bundle `m51-fb132-dataset.jcl`,
`m51-fb132-verifier.asm`, and
`m51-fb132-dataset.json`.
Preparation alone does not validate the IFOX assembler.

A source review identified a serious MVS linkage convention
problem in the generated verifier: it saved only R14, instead
of using the repository's proven standard 18-fullword
save-area prologue/epilogue. Such a program cannot be
accepted as a reliable independent MVS checker, even if
a simple offline string-oriented generator test passes.

**The v1 bundle MUST NOT BE SUBMITTED.** The fixed
generator now emits a separate `M5D124B` job and
three **v2** artifact names, preserving the v1
untracked workarea files without overwrite:
`m51-fb132-dataset-v2.jcl`,
`m51-fb132-verifier-v2.asm`, and
`m51-fb132-dataset-v2.json`.

The verifier now uses the established
`STM 14,12,12(13)`, `LR 12,15`,
`USING M5V124,12`, `ST 13,OLDSAVE+4`,
`LA 13,NEWSAVE`, and 18F save areas.
Both normal RC0000 and failure RC0012 exits
restore R13 and R14..R12, then set R15 only
*after* restoring saved registers, matching
earlier accepted native assembler probes.
The five offline tests now also assert the
critical MVS linkage statements.

**Next operator source-only step (no new JES job):**

```sh
cd ~/Source/Repos/BCPL-for-MVS
git pull --ff-only
python3 tools/checks/test-m51-fb132-dataset-probe.py
python3 tools/checks/m51-fb132-dataset-probe.py prepare
```

Only when this passes should the **v2** generated JCL
and assembler be reviewed for submission. Do not
submit either v1 or v2 yet; M5.1.2 is still a
new verifier program without first-run IFOX evidence.
No BCPL compiler, BCPLIO, BCPLMAIN or PDS object
was modified to make this correction.

## M5.1.2 additional read-only deck integrity gate (2026-10-17)

The v2 operator preparation passed **5/5 offline tests** and
staged its JCL, ASM and JSON under distinct v2 paths,
without any MVS submission. The generator's source review
found the six-step sequence, distinct REPORT and REPORT2
FB132 temporary allocations and the corrected MVS save-area
linkage consistent with the existing independent assembler
probe convention. Because the actual untracked workarea
files cannot be inspected from Git, **the repo now provides
a read-only exact-artifact verifier**:

```sh
cd ~/Source/Repos/BCPL-for-MVS
git pull --ff-only
python3 tools/checks/test-m51-fb132-dataset-probe.py
python3 tools/checks/m51-fb132-dataset-probe.py review
```

It verifies the staged manifest's hashes for original GO,
generated deck, assembler and both expected fixtures,
regenerates the entire JCL and ASM and requires byte-for-byte
agreement, enforces exact ASMAP/LKED/GO/VASM/VLINK/VCHK
order and one physical sequential dataset writer/reader
allocation for each of REPORT/REPORT2. It does **not**
submit jobs or change any staged evidence. The unit tests
also include tampering/rejection cases. **Do not submit**
unless this final offline gate is PASS; the first MVS
execution is still an independent experiment, not a
prior success claim.
