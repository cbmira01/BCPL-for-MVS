# JES SYSOUT/DD attribution investigation (2026-10-10)

## Question

Can the BCPL native regression runner determine whether a physical FB132
record came from GO step `SYSPRINT` or `BCPALT`, rather than merely
locating its text in a flattened Hercules/JES printer report?

## Evidence presently established

- The user ran the native panel 000–119 successfully (120/120) under
  `check-combined-jes-records.py`. That checker preserves *logical*
  line order and leading/interior spaces, but it has no DD provenance.
- In the actual RG114R job log supplied on 2026-10-10 (JOB 4989), the
  GO-step allocation messages show separate `SYSPRINT` and `BCPALT`
  allocations. IEF285I reported separate JES spool identifiers
  `JES2.JOB04989.SO0105`, `SO0106`, and `SO0107` for the GO step.
  Those are **separate SYSOUT spool datasets**, but the combined report
  does not explicitly assign each application's output record to one
  identifier. Do not assume the suffix number is the DD name.
- `tools/dump-report-for-job` reads `mvs-state/prt/prt00e.txt`, strips
  the Hercules per-job start/end banners, and returns a flattened report.
  This is a printer image, not an IBM QSAM DD-by-DD read interface.
- Hercules/TK5 has multiple emulated printers available in its
  historical configuration (000E, 000F, 0002); the actual active JES
  writer routes and output classes must be inspected before use.

## Source corroboration

Jay Moseley's *MVS FAQ: JES2* describes JES2 spool datasets being queued
and then selected by output-class-specific printer writers; the
physical Hercules printer file only receives the processed output.
It documents `$D U,PRTS`, `$S PRTn`, and `$T PRTn,Q=...` for
inspecting and controlling writer queues:
https://www.jaymoseley.com/hercules/faq/mvsfaq02.htm

The *MVS FAQ: Application/User Tasks* describes TSO `OUTPUT` and
`QUEUE` as ways to retrieve or save spooled SYSOUT datasets, usually
with carriage-control attributes:
https://www.jaymoseley.com/hercules/faq/mvsfaq04.htm

Tim Pinkawa's discussion of a Hercules printer pipe explicitly
describes the ordinary printer file as a combined stream and a
`prtspool` helper as primarily splitting *jobs*, not identifying
an individual GO-step DD:
https://timpinkawa.net/hercules/prtspool.html

## Candidate approaches

**A. Separate SYSOUT classes routed to distinct Hercules printers**
(recommended for a first isolated experiment). Route GO SYSPRINT to
one SYSOUT class and BCPALT to another; configure JES2 printer queues
so each class prints exclusively to a distinct emulated printer,
each with a different host-side output file. This establishes *routing
provenance* only if the queue membership is known, there are no other
writers consuming those classes, and no unrelated jobs use them.
The printer output format still may not preserve 132 physical bytes
or explicit record-count semantics, so this is an intermediate result.

**B. Extract individual JES2 spool datasets under MVS before printing.**
Use TK5's TSO OUTPUT/QUEUE facilities (or appropriate system spool
reader) on held jobs. This may preserve which SOxxxx object is saved,
but the saved print dataset is typically carriage-control-formatted
and may not be identical to the original FB132 application records.
The mapping from SOxxxx to the original DD must be established with a
controlled two-DD experiment rather than by guessing suffixes.

**C. Direct data-set output.** For byte-accurate FB132 testing, allocate
separate ordinary sequential datasets on user DASD for the two GO
output DDs instead of SYSOUT, and inspect via a supported in-guest copy
or host-side DASD transfer. This gives explicit DSNs and DCB geometry
but tests an alternate allocation path rather than the default
SYSOUT printer route. Requires a repeatable transfer tool, so is not
yet implemented.

## Read-only next-step probe

`tools/checks/inspect-jes-attribution.py` reads the raw Hercules
printer file, locates one job using existing `****A START/END`
markers, prints JES SO spool identifiers and allocation-related
messages, and displays the raw post-link records with byte lengths.
It changes no runtime source, JES writer configuration, or spool
datasets. Example (use a completed native GO job number, **not**
the Cambridge compiler job number):

```bash
python3 tools/checks/inspect-jes-attribution.py 4989 --sample 10
```

The example number is historical; use a recent job present in your
local printer file. Check actual active Hercules config and queue
before attempting option A:

```bash
grep -nE '^(0002|000E|000F)[[:space:]]' mvs-state/conf/tk5.cnf
```

Issue `$D U,PRTS` at the MVS console to discover the writers and
their queues (this does not change any configuration). **Do not**
reconfigure writers or output classes in the production-running TK5
instance before documenting the current assignments and a safe
reversal procedure.

## Outcome / decision

**Investigated, not resolved.** Separate JES2 SO identifiers and
independent DD allocations have been observed. The existing combined
report is insufficient to attribute physical application records to
their DDs or prove exact FB132 bytes. Do not retrofit a fictitious
DD identity into the existing text checker. Next controlled TK5 gate
should establish class-to-printer routing or a true spool-dataset
retrieval using the read-only evidence first.

The 120/120 functional regression baseline and
`native-stream-contract.md` remain valid and untouched. Neither
stream behavior nor regression fixture expectations were changed.

## Live TK5 printer topology confirmed — 2026-10-10

Operator inspected `$D U,PRTS`: PRINTER1 / 00E / Q=A; PRINTER2 / 00F / Q=Z; PRINTER3 / 002 / Q=X. All showed `INACTIVE` (idle, not evidence of being drained). Operator separately verified the **running container's** `/tk5/conf/tk5.cnf`: `0002 3211 prt/prt002.txt`, `000E 1403 prt/prt00e.txt`, `000F 1403 prt/prt00f.txt`. The host-side `mvs-state/conf/tk5.cnf` is not mounted/present, so earlier advice to grep it was incorrect. Class A and class Z are already mapped to distinct printer writers and host files; no system configuration change is required for the candidate experiment.

Added `tools/checks/prepare-dd-attribution-probe.py`: starting with the generated native GO deck for accepted regression 114, it creates a separate job AT114R with **only GO SYSPRINT class A and GO BCPALT class Z**. It fails closed on missing or ambiguous GO DD definitions. It never submits a job or modifies the original deck. Operator protocol:

```sh
python3 tools/checks/prepare-dd-attribution-probe.py
# Inspect GO DD cards in generated output.
grep -nE '^//(GO|SYSPRINT|BCPALT)' workarea/native-regression/114-interleaved-stream-records/dd-attribution-probe.jcl | tail -12
# Optional: snapshot sizes; submission may print additional unrelated work.
wc -c mvs-state/prt/prt00e.txt mvs-state/prt/prt00f.txt
bash tools/submit-jcl workarea/native-regression/114-interleaved-stream-records/dd-attribution-probe.jcl
# Use resulting JOB number; inspect both printer files and job-summary.
```

Expected logical data from regression 114 is SYSPRINT records `AB` then `C`, and BCPALT records `1` then `2`. The job's JES log and IFOX/linker report may be in the A file; Z file should contain BCPALT spool section bracketed by JES printer metadata. **Do not claim this establishes byte-for-byte FB132 evidence** until printer carriage control and FF/text transformations are analyzed. Do not run the full 120-panel merely to execute this isolated output attribution experiment.

## Class-separated printer experiment accepted — 2026-10-10, JOB 5512

Operator generated the isolated AT114R deck from regression 114, retaining the existing assembler/runtime. GO DD cards were verified as SYSPRINT SYSOUT=A and BCPALT SYSOUT=Z, both FB132. The operator recorded printer file lengths before submission: class A `prt00e.txt` 474,587,507 bytes, class Z `prt00f.txt` 165,817 bytes, then submitted **JOB 5512 AT114R**. `tools/job-summary 5512` reported **ASM=0000, LKED=0000, GO=0000; SUCCESS**.

The appended class Z printer image begins with `****Z START JOB 5512 AT114R ... PRINTER2`, contains successive standalone logical output records `1`, `2`, and closes with the class Z END banner. The appended class A printer image begins with `****A START JOB 5512 AT114R ... PRINTER1` and contains standalone `AB` and `C` records in the GO output suffix (along with the ASM/LKED/job listing). Its JES job log confirms three separately allocated GO SYSOUT DDs (SYSPRINT, BCPALT, SYSUDUMP) and three SO spool identifiers. After the run the A file measured 474,819,465 bytes; the Z file 172,176 bytes. The two printer outputs are independent files verified in the active Hercules config: device 00E to `prt00e.txt`, device 00F to `prt00f.txt`. JES2 `$D U,PRTS` independently established Q=A for PRINTER1 and Q=Z for PRINTER2.

**Conclusion:** positive experimental proof of DD/class-to-writer-to-distinct-host-printer-file attribution for this dedicated, class-separated GO job. The GO-level output records appear at the expected respective destinations. This does **not** make the original combined-class-A regression harness DD-attributed, and printer images alone still do **not** prove exact 132-byte physical FB132 records (trailing padding, carriage control). No JES2, Hercules, BCPLMAIN, or regression fixture changes were made. Historical 120/120 PASS baseline remains intact. Next optional engineering work: automate bounded per-job A/Z printer extraction and run fail-closed positive/negative record/destination tests; separate path for byte-accurate 132-byte dataset verification.

## Reusable class-separated checker — 2026-10-10

Added `tools/checks/check-dd-attribution.py` and offline self-test
`tools/checks/test-dd-attribution.py`. This is an independent, opt-in
acceptance path for class-separated probe jobs: the ordinary
`tools/run-native-regression` runner remains unchanged.

The checker requires separate A and Z host printer files, pre-submit
byte offsets, the exact job number and job name, complete START/END
banners attributing the A and Z files to PRINTER1 and PRINTER2,
respectively, a contiguous occurrence of expected logical records in
each stream, and absence of each stream's expected records in the
opposite printer section. It fails closed for missing/incorrect job
identity, wrong destination, incomplete sections, invalid offsets and
foreign job banners. It does not interpret print carriage controls or
claim proof of 132-byte unmodified QSAM records.

First run the offline self-tests:

```sh
python3 tools/checks/test-dd-attribution.py
```

A new real TK5 experiment, if desired, uses the previously accepted
regression 114 generated GO job deck:

```sh
python3 tools/checks/prepare-dd-attribution-probe.py
wc -c mvs-state/prt/prt00e.txt mvs-state/prt/prt00f.txt
bash tools/submit-jcl workarea/native-regression/114-interleaved-stream-records/dd-attribution-probe.jcl
tools/job-summary JOBNUMBER
python3 tools/checks/check-dd-attribution.py JOBNUMBER \
  --a-offset A_BYTES_BEFORE_SUBMISSION \
  --z-offset Z_BYTES_BEFORE_SUBMISSION
```

The operator must substitute the real returned job number and
pre-submission sizes and **must** verify job-summary shows ASM/LKED/GO
RC=0000 separately. The checker is a spool-output attribution check,
not a substitute for validating GO completion. Do not reuse prior
offsets for a new job, and do not run the whole regression suite to
exercise this isolated mechanism.

**Validation status:** New automated checker and its offline tests
are committed, but no new TK5 run against this checker has been
reported. JOB 5512 previously demonstrated routing manually.
