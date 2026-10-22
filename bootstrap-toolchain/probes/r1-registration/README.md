# Milestone Runtime Extensions — R.1 candidate

**Status:** R.1 development candidate. Positive MVS jobs 2226 (empty) and
2228 (selected) PASSED on 22 October 2026. Integrated negative tests
have begun: JOBs 2229 and 2230 emitted 1001 but ended S322. The
cause of the rejection cleanup timeout is under investigation.
Accepted BOOT_OBJ objects are unchanged.

The owner closed R.0, began R.1, and approved separation of the generic
assembler registrar from the application-specific BCPLREG table and the
single BCPLMAIN integration on 21 October 2026.

## Host checks

Run from the repository root:

```sh
python3 -m unittest discover -s tools/checks -p 'test_r1*.py' -v
python3 tools/checks/r1_prepare_candidate.py --check
python3 bootstrap-toolchain/probes/r1-registration/make-jobs.py empty --check
python3 bootstrap-toolchain/probes/r1-registration/make-jobs.py selected --check
python3 bootstrap-toolchain/probes/r1-registration/make-jobs.py no-output --check
```

The checks verify source/card constraints and synthetic JCL construction,
not IFOX assembly or executable behavior.

## Compile both test callers using the demoted Cambridge compiler

```sh
mkdir -p workarea/runtime-extensions-r1
tools/bootstrap/compile-mvs \
  bootstrap-toolchain/probes/r1-registration/empty.bcpl \
  --job-name R1ECOMP \
  --output workarea/runtime-extensions-r1/empty.s370.asm

tools/bootstrap/compile-mvs \
  bootstrap-toolchain/probes/r1-registration/selected.bcpl \
  --job-name R1SCOMP \
  --output workarea/runtime-extensions-r1/selected.s370.asm
```

## Isolate a normal FINISH without any application output

**Before changing startup ordering**, compare the failed rejection
jobs 2229/2230 against the new ordinary no-output application.
This uses the empty BCPLREG and the same candidate Core Runtime.

```sh
tools/bootstrap/compile-mvs \
  bootstrap-toolchain/probes/r1-registration/no-output.bcpl \
  --job-name R1NCOMP \
  --output workarea/runtime-extensions-r1/no-output.s370.asm

python3 bootstrap-toolchain/probes/r1-registration/make-jobs.py \
  no-output --generated workarea/runtime-extensions-r1/no-output.s370.asm

bash tools/mvs/submit-jcl workarea/runtime-extensions-r1/r1-no-output.jcl
```

Use the returned JES number (not the literal word JOBNUMBER) with:

```sh
tools/mvs/job-summary 2231
tools/mvs/dump-report-for-job 2231
```

**Replace 2231 with the actual JES job number.** The normal result is
all IFOX/IEWL steps RC=0000, GO RC=0000, with **no BCPL application
output**. S322 at the same PSW as the earlier negative jobs indicates
the no-output CLOSE problem is reproducible without registration
rejection. RC=0000 instead points to the rejection-specific cleanup
path. This is a diagnostic test; no acceptance or production
promotion follows automatically.

The [2229/2230 failure record](../../../packaging/runtime-extensions-r1-rejection-jobs-2229-2230-evidence-20261022.md)
contains the exact evidence.

## Create and submit the first test job

```sh
python3 tools/checks/r1_prepare_candidate.py \
  --output workarea/runtime-extensions-r1/bcplmain-r1.asm

python3 bootstrap-toolchain/probes/r1-registration/make-jobs.py \
  empty --generated workarea/runtime-extensions-r1/empty.s370.asm

bash tools/mvs/submit-jcl workarea/runtime-extensions-r1/r1-empty.jcl
```

Record the returned JES JOB number and inspect it:

```sh
tools/mvs/job-summary JOBNUMBER --max-rc 0
tools/mvs/dump-report-for-job JOBNUMBER
```

Require all IFOX/IEWL/GO steps RC=0000 and the actual BCPL output
`R1 EMPTY BCPLREG PASS`. Independently inspect the IEWL MAP/XREF.

**Do not submit the selected job until the empty job passes.**

```sh
python3 bootstrap-toolchain/probes/r1-registration/make-jobs.py \
  selected --generated workarea/runtime-extensions-r1/selected.s370.asm

bash tools/mvs/submit-jcl workarea/runtime-extensions-r1/r1-selected.jcl
```

Inspect the returned JOB with the same job-summary and report tools.
The selected case should print `R1 SELECTED BCPLREG PASS`, with
G!298 installed by RGINIT from the BCEX descriptor, rather than from
a synthetic application export trailer.

All candidate objects and the load module are temporary. The generator
reads BOOT_OBJ but does not update it. G!298 is test-local only; G!200
remains allocated to BCPLQSAM.

The [15-case integrated negative harness](NEGATIVE-TESTS.md) is now
available for host validation and subsequent MVS testing. Positive-path
evidence is recorded in the [JOBs 2226 and 2228 record](../../../packaging/runtime-extensions-r1-positive-jobs-2226-2228-evidence-20261022.md).

Remaining R.1 obligations include **executing** the integrated negatives,
effective-owner ledger, source-trusted callable address checks,
reverse-order and STOP(n) finalizers, and native regression. R.2 and
R.3 retain their official march names and scope.
