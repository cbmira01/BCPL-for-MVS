# Milestone Runtime Extensions — R.0 batched dependency/finalizer probes

**March:** R.0 — Evidence and contract (open).
**MVS-validated test-only batch: JOB 2195, 21 October 2026.**
See the [verified evidence](../../../packaging/runtime-extensions-r0-batch-job-2195-evidence-20261021.md).
No production registrar or finalizer was installed.
Owner requested batching remaining test-only R.0 probes after JOBs 2187–2192
passed. This package submits **one JES job**, with six independent IFOX
assemblies, one IEWL link-edit, and one GO step; that GO reports **20**
individually checked outcomes. It does **not** install a registrar, change
`BCPLMAIN`, publish globals, or update persistent MVS PDSes.

## What one job actually tests

The dependency validation subprogram (`dependency.asm`) operates on
independently relocatable package descriptors and scenario lists.
`make-batch.py` builds ten descriptor CSECTs and fourteen scenarios from
explicit test-only data. It checks full identifier equality,
major/minor compatibility, missing dependencies including a transitive
chain, strict dependency-first order (which rejects a cyclic fixture),
duplicate package IDs/globals, occupied G!14, reserved G!200, and
required packages. These fixtures use **G!299–305 only as local test
numbers**; the official Global Number Registry does not allocate them.
Each case compares the *actual assembler validator return code* with
its expected status before writing its QOUT PASS marker.

The finalizer subprogram (`finalizer.asm`) calls two **separately linked
assembler hooks** (`hooks.asm`) through a parameter block containing
reason, requested STOP code, trace pointer and injected-error mask.
The hooks preserve caller registers using MVS save areas and return status
in R15; the driver checks reverse order **B then A**, exactly one call
each, the returned failure summary and ordinary FINISH versus STOP(n)
status policy. Six cases cover empty set, successful reverse order,
FINISH returned-error RC=8, STOP(4), STOP(8) and STOP(0), including
returned finalizer errors.

The subprograms are invoked from `master.asm`. Each prints test QOUT lines;
`master.asm` aggregates their overall RC so one failure makes GO RC=8.
Only the actual QOUT lines in the JES report count, **not constants in
IFOX listings**.

## One command after git pull

From repository root:

```bash
bash bootstrap-toolchain/probes/r0-batch-probes/run-batch.sh
```

The runner checks the clean Git worktree; runs **nine Python unit tests**
and a credential-free generator dry-run; generates one authenticated,
mode-0600 JCL deck under ignored `workarea/runtime-extensions-r0-batch/`;
submits it to JES; retrieves the actual JOB number/report; verifies
**all eight steps at RC=0000**, each of the **20 exact QOUT markers**
and the total number of marker lines; preserves the complete report.
JCL and its output never enter Git. It uses the established `submit-jcl`,
`job-summary`, and `dump-report-for-job` tools.

For offline-only verification without submitting a job:

```bash
PROBE=bootstrap-toolchain/probes/r0-batch-probes
python3 -B -m unittest discover -s "$PROBE" -p test_batch.py -v
python3 -B "$PROBE/make-batch.py" --check
```

**Expect:** JOB `R0BATCH`, steps ASMM, ASMD, ASMF, ASMH, ASMP, ASMR,
LKED and GO, each `RC=0000` (eight steps). The runner
checks the whole step summary. Expected QOUT records all start `R0 Dnn`
or `R0 Fnn`. The numbered case titles are embedded in the generated
ignored file `expected-markers.txt` and independently checked.

## Correction after the first Morkies dry run

The first batch execution passed five Python tests and the 824-card
credential-free dry-run, but stopped **before JES submission** with
`ValueError: wrong job card`. The authenticated JOB helper pads the
seven-character name `R0BATCH` to eight columns, producing two spaces
before `JOB`. The generator had matched only the one-space synthetic
card. It now parses the first two JOB-card tokens, and the unit suite
includes a synthetic three-line authenticated card (no real credentials).

The report verifier also now accepts trailing blanks on the actual
80-byte FB QOUT records while requiring each complete expected marker
at the start of its own line. The prior exact-line grep could reject a
legitimate padded record. Both corrections were exercised locally:
**seven unit tests PASS**, both dry-run and synthetic authenticated
paths accepted, and `bash -n` passed. **That historical failed attempt preceded JOBs 2193–2195; the batch
subsequently passed on MVS in JOB 2195.**

## Explicit evidence boundaries

1. These are **standalone assembler tests**. FINISH/STOP return codes
   are simulated according to the *approved observable policy*; no
   end-to-end execution of BCPL's `FINIMPL`, `STOPENT`, `FINEXIT`,
   `BCPLIO.IOFIN`, or `BCPLMEM.MEMDRAIN` occurs. Their exact integration
   and finalizer ABI remain subject to acceptance tests and owner review.
2. The dependency validator handles **at most three packages, one
   export per package and one package-local dependency**. Its scenario
   object/layout uses the proposed 48-byte package-header and 16-byte
   dependency fields. This is not a production-general parser or
   validated arbitrary-pointer protection.
3. A cyclic fixture is rejected by the approved dependency-first order
   requirement; **no general cycle-reporting algorithm is claimed**.
4. The true app/BLIB/core runtime export ledger, general negative
   malformed-span tests, and runtime startup publication are separate
   R.0 gates. The prior JOBs 2187–2192 cover bounded single-descriptor
   tests; they did not close R.0.
5. **Actual IFOX/IEWL/GO outcomes are observed and recorded** in
   [JOB 2195 evidence](../../../packaging/runtime-extensions-r0-batch-job-2195-evidence-20261021.md):
   all eight steps RC=0000, zero flagged statements and all 20 exact
   GO/QOUT markers. This is isolated-harness evidence only; no
   application/BLIB ledger, BCPLMAIN startup importer or true
   FINISH/STOP runtime path was exercised.

Sources: [R.0 testing decision](../../../packaging/runtime-extensions-r0-testing-decision-20261020.md),
[three-question review](../../../packaging/runtime-extensions-r0-three-design-questions-review-20261020.md),
[prior single-descriptor probes](../r0-registration-probes/README.md).
