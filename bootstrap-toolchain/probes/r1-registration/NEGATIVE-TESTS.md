# Milestone Runtime Extensions — R.1 integrated negative-test candidates

**Status:** 15 host-generated fixtures. Diagnostic 1001 was exercised
in MVS JOBs 2229 and 2230 and correctly issued its WTO, but both jobs
ended with GO ABEND S322 instead of the required RC=0012. **No
integrated negative has passed**. This remains a candidate harness.
It follows the owner-approved [Decision G contract](../../../packaging/runtime-extensions-r0-decision-g-contract-20261021.md).

All jobs link the same compiled BCPL caller used by JOB 2228, the
candidate BCPLMAIN and generic registrar, and a deliberately malformed
BCRG or BCEX test object. Each case is independent and deterministic.

| ID | Malformation | Expected GO | Expected WTO |
| --- | --- | --- | --- |
| 1001 | Registry end address not word-aligned | RC=0012 | BCPLREG 1001 |
| 1002 | Registry magic invalid | RC=0012 | BCPLREG 1002 |
| 1003 | Registry count inconsistent with span | RC=0012 | BCPLREG 1003 |
| 1004 | Package end address not word-aligned | RC=0012 | BCPLREG 1004 |
| 1005 | Package magic invalid | RC=0012 | BCPLREG 1005 |
| 1006 | Export count inconsistent with span | RC=0012 | BCPLREG 1006 |
| 1007 | Blank package identifier | RC=0012 | BCPLREG 1007 |
| 1008 | Invalid export to G!0 | RC=0012 | BCPLREG 1008 |
| 1009 | Collision with application START G!1 | RC=0012 | BCPLREG 1009 |
| 1010 | Required package absent | RC=0012 | BCPLREG 1010 |
| 1011 | Second package requires wrong API major | RC=0012 | BCPLREG 1011 |
| 1012 | Dependency listed after its requester | RC=0012 | BCPLREG 1012 |
| 1013 | Nonzero misaligned finalizer address | RC=0012 | BCPLREG 1013 |
| 1014 | Self-referential dependency record | RC=0012 | BCPLREG 1014 |
| 2001 | Valid finalizer returns status 8 at FINISH | RC=0008 | BCPLREG 2001 |

For each 1001–1014 rejection, `START` must **not** run, so
`R1 SELECTED BCPLREG PASS` must be absent. A **test-only** injection
in the temporary BCPLMAIN rejection path inspects G!298 and G!299:
both must retain their uninitialized sentinel. If either changed, the
job produces `R1 NEGATIVE PARTIAL GLOBAL PUBLICATION` and returns
**RC=0016**, failing the test. For 1011 and 1012 a separate, valid
`R1BASE` descriptor (G!299) enables a late validation failure.

For 2001, START **must** run and print its PASS marker, then the
finalizer's nonzero return must trigger WTO 2001 and change an ordinary
FINISH completion to RC=0008. This does not yet test STOP(n), multiple
finalizers, or reverse order.

## Host preparation

Run from repository root after obtaining `selected.s370.asm` with the
[positive-case instructions](README.md). First confirm all profiles
can be built without credentials or writing JCL:

```sh
python3 -m unittest discover -s tools/checks -p 'test_r1*.py' -v
python3 bootstrap-toolchain/probes/r1-registration/make-negative-jobs.py all --check
```

**MVS rerun required for candidate R10 correction.** JOBs 2229
and 2230 failed with S322. No negative has yet passed. The following
regenerates and submits the corrected first case:

```sh
python3 bootstrap-toolchain/probes/r1-registration/make-negative-jobs.py \
  1001 --generated workarea/runtime-extensions-r1/selected.s370.asm
bash tools/mvs/submit-jcl workarea/runtime-extensions-r1/r1-neg-1001.jcl
```

Use `tools/mvs/job-summary JOBNUMBER` and
`tools/mvs/dump-report-for-job JOBNUMBER`. Reject any assembly or IEWL
failure, missing matching WTO, S0C4 or other ABEND, wrong GO return
code, premature START, or G!298/G!299 sentinel failure. Once one case
is verified on MVS, repeat for each remaining ID; never infer a batch
pass from generated JCL alone. `--check` does **not** execute IFOX.

The generated JCL reads `BOOT_OBJ` with `DISP=SHR` and uses temporary
assembly objects/load modules only. JCL with machine-local credentials
is generated only under ignored `workarea`, mode 0600; do not commit it.

See the [failure evidence for JOBs 2229 and 2230](../../../packaging/runtime-extensions-r1-rejection-jobs-2229-2230-evidence-20261022.md).
**JOB 2232 R1NOOUT passed** with GO RC=0000, proving ordinary
no-output FINISH does not hang. Review of the R.1 rejection adapter
found it failed to restore R10 around IOFIN; the ordinary FINISH
path already restores R10. A temporary candidate now preserves R10
in both the R1BAD and test-only R1LEAK cleanup paths. This is a
host-tested correction, **not yet an MVS pass**. Re-run 1001 at the
original GO CPU limit, verify RC=0012, and only then proceed with
the other diagnostics. See the [JOB 2232 evidence](../../../packaging/runtime-extensions-r1-no-output-job-2232-evidence-20261022.md).
