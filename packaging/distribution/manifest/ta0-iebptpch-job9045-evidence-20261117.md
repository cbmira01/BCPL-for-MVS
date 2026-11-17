# TA.0 — IEBPTPCH two-member JOB 9045 result and readback gate

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.0 — Release Architecture, Inventory, and Manifest  
**Status:** Live MVS read-only utility execution confirmed by owner; exact two-member record decoding not yet demonstrated against the retained original report.

## Actual MVS result — 17 November 2026

The owner ran the previously committed `tools/distribution/submit-iebptpch-pilot.py`
with logical dataset key `EXT_OBJ`, requesting members `BCPLTIME` and `BCPLQSAM`
in one `IEBPTPCH` operation. After a prior invocation failed to start because the
new script had not yet been pulled locally, an updated checkout successfully
ran the tool. The operator's resulting terminal output was:

> TA.0 IEBPTPCH RC=0000: JOB 9045 (TA0MULT) EXT_OBJ(BCPLTIME,BCPLQSAM)
>
> Private readback evidence: /home/calvin/ta0-mvs-evidence-20261117/ta0multi-ext-pilot
>
> No binary comparison or release acceptance asserted.

**Established:** the JES pilot submission completed successfully with the
runner-reported `TA0HEX` / `IEBPTPCH` RC=0000, using a read-only input PDS
`HERC02.BCPL.EXT.OBJ`. The runner persisted its `cursor.json`, `job-body-redacted.jcl`,
`job-summary.txt`, `job-report.txt`, `printer-window.raw`, and `receipt.json`
under that private evidence directory with SHA-256 pins for five attachments.
These statements are based on the operator-reported runner result and known
code behavior, **not an independent inspection** of the actual saved files.

**Not established:** whether both printed member headings have the expected
shape and order, each member's actual FB80 record count or bytes, a verified
hash of either object, current MVS DASD object equality, build/source Git
lineage, redistribution rights, tape write/readback, or release acceptance.
The real saved report and raw printer bytes are not available in the assistant
workspace. Do **not** equate the 9045 runner's RC=0000 with successful binary
readback or claim independent member-content identity.

The preceding JOB 9044 `BCPLDEMO` evidence is qualified separately in
[the JOB 9044 evidence](ta0-iebptpch-job9044-evidence-20261117.md); its
pasted-transcription and saved-report digests still disagree, and neither
value should be reused as a 9045 oracle.

## Verified next-stage implementation

`tools/distribution/decode-iebptpch-multi.py` is a **non-submitting** reader for
files produced by `submit-iebptpch-pilot.py`. It validates every original
SHA-256 receipt pin before parsing; demands matching JES START/END, job number,
job name, IEBPTPCH step RC=0000, IEF142I, control statement, selected member
order, and printed member headings. It strictly parses observed 80-byte records
as 12 groups of eight hex digits on the first printed line followed by eight
groups and `*`/`**` delimiters on the second. Recognized page headings are
permitted only between complete records. Each member must finish on a `**`
block boundary. Unknown inter-member content, broken binary lines, duplicate
headers, damaged receipts and unexpected records after the final member fail
closed. The raw printer-window hash and report hash are retained in its output
receipt. It never prints the JES listing or private JOB-card text to stdout.

The decoder emits `<MEMBER>.fb80`, per-member `<MEMBER>.fb80.json` and an
overall `decode-receipt.json` into a **new private directory outside Git**. It
never alters resident MVS datasets or tape. Each byte hash identifies the
decoded **printer listing** only. Record counts are derived from the listing.
Optional `--expected-records MEMBER:COUNT` entries (one for every selected
member) validate externally asserted counts; the program **cannot certify**
that those assertions were independently measured. Output never overwrites
existing files or a preexisting directory.

Because the exact multi-member format of JOB 9045 has not yet been inspected,
this is a **fail-closed candidate decoder**, rather than a declaration of
live-MVS readback acceptance. If it rejects the 9045 report, preserve the
original evidence and determine which specific format assumption failed
before relaxing the parser. Do not silently repair the output or assume
additional members have been printed.

## Offline verification

The decoder was tested in the assistant's isolated workspace against a
synthetic two-member fixture assembled from the *old JOB 9044 transcription*
(its records are **not BCPLTIME or BCPLQSAM**, and it is not JOB 9045 output).
Thirty-six new tests cover: successful two-member extraction and SHA-256
receipts; optional record-count checks; CLI invocation; incorrect/missing
JES identity or completion; bad RC, source JCL or summary; unexpected,
missing, reordered or duplicated member headings; corrupt hex data, markers,
page-break location, extra data, symlink/report tampering, SHA-pin mismatch,
output-directory safety and file permissions. These are offline tests only.

The new 36 tests and 64 existing focused IEBPTPCH tests were rerun together:
**100/100 PASS** on 17 November 2026. Python syntax/static checks passed.
The historical 73-test TA.0 suite is **not** claimed rerun in this checkpoint.

## Next live decision gate

Run the decoder against the already-saved JOB 9045 private evidence, specifying
a new private output directory. If it passes, record the two decoded member
counts and SHA-256 hashes as qualified printer readback evidence. The following
read-only FB80 tasks can then be grouped by PDS using the same existing runner:
`MR10_OBJ(ICINT19)` and all ten selected `BOOT_OBJ` members. Keep the independent
`MR10_LOAD(ICINT19)` PO/U inspection and source-build receipt verification
separate. The output and evidence remain outside Git and may contain
sensitive JES details; do not publish them.

**TA.0 remains IN PROGRESS; TA.1 and release publication remain separately
gated.** No new VOLSER is reserved, no tape is written, and all release
positions after `BCPL.BT0002` remain proposed.
