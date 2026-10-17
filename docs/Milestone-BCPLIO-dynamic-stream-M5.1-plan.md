# BCPLIO dynamic streams — M5.1 acquisition feasibility

**Status: M5.1.0 A/Z printer-routing probe STAGED (2026-10-17); no MVS job executed; raw JES2 spool and FB132 fidelity UNKNOWN.**
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
