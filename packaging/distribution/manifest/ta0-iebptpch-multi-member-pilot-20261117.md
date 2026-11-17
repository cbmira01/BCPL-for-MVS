# TA.0 — Controlled IEBPTPCH multiple-member MVS pilot

**Milestone:** Tape artifact release  
**March:** TA.0 — Release Architecture, Inventory, and Manifest  
**Status:** Implemented and mock-tested host-side generator/runner; actual multi-member MVS output pending.

## Justification and MVS authority

Actual MVS/JES JOB **9044** executed `IEBPTPCH` `TA0HEX` with RC=0000, printing
`EXT_OBJ(BCPLDEMO)` as ten FB80 records. The original save-report readback
produced a differing SHA-256 from the manual transcription; both claims remain
recorded without reconciliation in [JOB 9044 evidence](ta0-iebptpch-job9044-evidence-20261117.md).

IBM *OS/VS2 MVS Utilities*, Release 3.8, GC26-3902-1, chapter 11 (pp. 11-3 to
11-6) explicitly permits **any number of MEMBER statements** per IEBPTPCH step
and requires `MAXNAME` for `MEMBER NAME=`. This authorizes an experiment, not
an assumption about the exact printed layout, total pages or member order:
https://bitsavers.org/pdf/ibm/370/OS_VS2/Release_3.8_1978/GC26-3902-1_OS_VS2_MVS_Utilities_Rel_3.8_Sep83.pdf

## Approved source selection and safety

The existing canonical design inventory, `ta0-inventory.yaml`, remains the
sole selector. `prepare-iebptpch-readback.py` now accepts repeated `--member`
arguments, preserving single-member behavior. It validates that every member
appears in the selected source PDS, member names are unique and legal, and both
the manifest and `config/dspal.yaml` agree on PO/FB/80/800. `MR10_LOAD` (PO/U)
is explicitly excluded. No output member, new MVS dataset, tape write or
production system operation is requested.

For the next pilot, select only `EXT_OBJ(BCPLTIME)` and `EXT_OBJ(BCPLQSAM)`:

    //TA0HEX   EXEC PGM=IEBPTPCH
    //SYSPRINT DD SYSOUT=*
    //SYSUT1   DD DSN=HERC02.BCPL.EXT.OBJ,DISP=SHR
    //SYSUT2   DD SYSOUT=*
    //SYSIN    DD *
             PRINT TYPORG=PO,TOTCONV=XE,MAXNAME=2
             MEMBER NAME=BCPLTIME
             MEMBER NAME=BCPLQSAM
    /*

The authenticated JOB card is produced only at runtime from the existing
`dspal-core.py` local configuration; it is never persisted in Git or in the
pilot's evidence directory. The new explicit-operation script
`tools/distribution/submit-iebptpch-pilot.py` invokes the existing
`core.submit_and_wait` (which uses `submit-jcl` and cursor-scoped
`job-summary`), extracts a cursor-scoped report, preserves the exact printer
**window bytes** and writes SHA-256-pinned private evidence. Output must be a
new absolute directory outside the checkout, with restrictive permissions,
without overwrite. The runner submits exactly one JES job when invoked, and
does **not** automatically retry on an ambiguous failure. Console output is a
short summary, not the JES report.

## Evidence gate before expanding the decoder

1. Confirm exact JCL requested and the MVS-assigned JOB number; no JCL errors,
   ABENDs or nonzero `TA0HEX` RC.
2. Check that `SYSUT2` has exactly the two requested member headings (or
   document the period utility's actual format) and examine member boundaries,
   pagination and block delimiters without assuming the requested order is
   preserved.
3. Preserve `printer-window.raw`, `job-report.txt`, `job-summary.txt`,
   `cursor.json` and `receipt.json` outside Git. Raw files may contain the
   authenticated JOB card and must not be publicly committed.
4. Only then generalize the fail-closed host decoder to support multiple
   members, followed by additional selected FB80 readback. Member record count
   and SHA256 must be explicitly qualified as extracted from printer text,
   not independently verified source/DASD identity.
5. Verify the selected MVS source DCB using the separately captured
   LISTDS/LABEL reports; retain all outstanding eight historical build-job
   inputs, object-source lineages, release rights and PO/U load verification.

The host-side generator's legacy 20 cases, the additional 11 multi-selection
cases, 20 original decoder tests, 4 digest-pin cases and 9 mocked runner cases
all pass in the assistant workspace: **64/64**, with Python syntax checks.
These are **not** simulated MVS execution results and do not close TA.0.

No TA.1 tape operations, VOLSER reservation, candidate promotion or publication
are permitted by this pilot. Only `BCPL.BT0001` and `BCPL.BT0002` have frozen
roles; later proposed positions remain unfrozen.
