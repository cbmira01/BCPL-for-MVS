# BCPLIO dynamic streams — M5.1 acquisition feasibility

**Status: M5.1.1 printer routing ACCEPTED (JOB 8184, 2026-10-17); M5.1.2 dual-dataset QSAM FB132 probe STAGED for offline review, not submitted; JES2 raw spool remains UNVERIFIED.**
Predecessor: M5.0 evidence contract **ACCEPTED** by the owner.
[M5.0 contract](Milestone-BCPLIO-dynamic-stream-M5.0-contract.md).

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
