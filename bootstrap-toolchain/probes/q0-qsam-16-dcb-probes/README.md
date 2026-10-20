# Milestone QSAM — March Q.0 concurrent-DCB storage probes

**Status:** Q.0 test-only 1/3/8/16-DCB profiles **PASSED on
MVS 3.8J/TK5 (JOBs 2183–2186, 20 October 2026)**. Each had six
RC=0000 steps and the actual expected QOUT marker. The 512K fallback
is prepared but **not run**. No production BCPLQSAM or Runtime
Extensions code was implemented.

## Observed MVS results (20 October 2026)

**Owner-confirmed PASS on MVS 3.8J/TK5:**

| Profile | JES JOB | Simultaneous DCBs | GO REGION | Actual QOUT |
| --- | --- | ---: | --- | --- |
| `one` | 2183 / `Q0H1` | 1 | 256K | `Q0 01 DCB F1024 2 RECORDS PASS` |
| `three` | 2184 / `Q0H3` | 3 | 256K | `Q0 03 DCB F1024 2 RECORDS PASS` |
| `eight` | 2185 / `Q0H8` | 8 | 256K | `Q0 08 DCB F1024 2 RECORDS PASS` |
| `sixteen` | 2186 / `Q0H16` | 16 | 256K | `Q0 16 DCB F1024 2 RECORDS PASS` |

Each job's **ASMWR, ASMRD, LKWR, LKRD, WGO and RGO**
steps returned **RC=0000**. The optional `sixteen-512` fallback
was not needed or run. For the evidence scope and limitations see
[JOBs 2183–2186](../../../packaging/qsam-q0-concurrent-dcb-evidence-20261020.md).

The old planning guidance below is retained as a
**reproduction procedure**, not an unexecuted work plan.

## What is tested

A generated assembler writer and a separately assembled reader each
own **N simultaneous MVS QSAM DCBs** for independent temporary
`RECFM=F,LRECL=1024,BLKSIZE=1024` datasets. Before opening the DCBs,
each program conditionally acquires a **separate 1024-byte private stage
per DCB** using `GETMAIN RC`; the stages remain allocated while all
DCBs are OPEN. QSAM owns its internal block buffers.

The writer opens all N DCBs for OUTPUT, writes one record to each
in order, then a second record to each in order. It CLOSEs in reverse
order and FREEMAINs all owned stages. The reader opens all N DCBs
for INPUT, GETs the corresponding records in two interleaved passes,
checks each full 1024-byte record (unique dataset/record header,
blank-fill data, binary final-byte sentinel), then checks EODAD
once for each stream. It CLOSEs in reverse order, FREEMAINs the
stages, checks acquisition/free counts and emits a single QOUT marker.

There is **no failed-CLOSE recovery claim**: an unrecovered MVS OPEN,
GET, PUT or CLOSE abend can terminate an individual test job.
A conditional GETMAIN refusal returns RC=8 with guarded stage cleanup
before any QSAM DCB is opened. The test is deliberately not the
production transactional handle-table implementation.

| Profile | JES JOB name | Simultaneous DCBs | GO region | Expected QOUT |
| --- | --- | ---: | ---: | --- |
| `one` | `Q0H1` | 1 | 256K | `Q0 01 DCB F1024 2 RECORDS PASS` |
| `three` | `Q0H3` | 3 | 256K | `Q0 03 DCB F1024 2 RECORDS PASS` |
| `eight` | `Q0H8` | 8 | 256K | `Q0 08 DCB F1024 2 RECORDS PASS` |
| `sixteen` | `Q0H16` | 16 | 256K | `Q0 16 DCB F1024 2 RECORDS PASS` |
| `sixteen-512` | `Q0H16B` | 16 | 512K | Same 16-DCB marker |

**For reproduction:** Run `one`, `three`, `eight`, then
`sixteen`. All four have already **passed at 256K**; the
`sixteen-512` fallback is optional and was **not executed**.

## From repository root

```sh
PROBE=bootstrap-toolchain/probes/q0-qsam-16-dcb-probes
for profile in one three eight sixteen sixteen-512; do
    python3 "$PROBE/make-jobs.py" "$profile" --check
done

# Example: normal authenticated deck, under ignored workarea only:
python3 "$PROBE/make-jobs.py" one
bash tools/mvs/submit-jcl workarea/qsam-q0-16-dcb/q0-one.jcl
# Retrieve the actual returned JOB number:
tools/mvs/dump-report-for-job JOBNUMBER
```

**Expected step sequence:** ASMWR, ASMRD, LKWR, LKRD, WGO, RGO,
all RC=0000, plus the *actual* reader QOUT PASS record. An assembler
listing containing the PASSREC constant alone is not a PASS.
The generated decks use in-stream IFOX, temporary object/load data,
and temporary `&&Q0Hnn` DASD only; **no PDS updates**. Completed
datasets are deleted at RGO. Authenticated JCL is mode 0600 under
ignored `workarea/qsam-q0-16-dcb/` and must never be committed.

`--check` does not read local credentials or write any JCL. It
checks IFOX card lengths and ASCII, DD allocations, deck structure,
and the eight-column JOB name.

## Interpretation

These probes improve the evidence for the **16 concurrently open
handles functional requirement**, with fixed 1024-byte records and
separate 1024-byte stages. They still do not include the BCPL
application, the production BCPLQSAM handle table, generic
registration, or finalizer. They establish neither an all-devices
memory bound nor a universal MVS 256K requirement. Inspect JES
step codes, allocation failures and abend diagnostics rather than
inferring capacity from the standalone 16-stage JOB 2182.

See [Q.0 owner-approved error and R.0 policy](../../../packaging/qsam-q0-error-and-r0-design-decisions-20261020.md).
**March Q.0 remains open; Q.1 has not started.**

## Corrected dry-run validation

The original `make-jobs.py --check` mistakenly required a raw
count of `DISP=(OLD,DELETE)` equal to the number of QSAM DCBs.
The assembler-link steps also delete **two temporary object datasets**,
so the expected raw count was N+2, not N. This caused
`ValueError: temporary dataset cleanup missing` before any job
submission. The corrected check verifies every exact
`//Qnn DD DSN=&&Q0Hnn,DISP=(OLD,DELETE)` card once and does
not count the two linker cleanup DDs. After this correction, the owner executed the 1/3/8/16 profiles
and all returned actual RC=0000 and QOUT PASS markers in JOBs 2183–2186.
