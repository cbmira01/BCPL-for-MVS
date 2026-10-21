# Milestone Runtime Extensions — R.1 candidate

**Status:** Development candidate on GitHub main. Not assembled, linked, or
executed under MVS. It does not modify accepted BOOT_OBJ objects.

The owner closed R.0, began R.1, and approved separation of the generic
assembler registrar from the application-specific BCPLREG table and the
single BCPLMAIN integration on 21 October 2026.

## Host checks

Run from the repository root:

```sh
python3 -m unittest discover -s tools/checks -p test_r1_source.py -v
python3 tools/checks/r1_prepare_candidate.py --check
python3 bootstrap-toolchain/probes/r1-registration/make-jobs.py empty --check
python3 bootstrap-toolchain/probes/r1-registration/make-jobs.py selected --check
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

The next R.1 tasks are integrated negative tests, effective-owner ledger,
source-trusted callable address checks, live finalizer coverage and
the existing native regression panel. R.2 and R.3 retain their official
march names and scope.
