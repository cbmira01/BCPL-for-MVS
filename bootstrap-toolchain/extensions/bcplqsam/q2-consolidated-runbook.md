# Milestone QSAM — Q.2 consolidated native campaign

**March:** Q.2 — Fixed logical records  
**Status:** Source-controlled native campaign candidate, **NOT MVS EXECUTED**  
**Target:** MVS 3.8J / Hercules, native GO REGION=256K  
**Job:** **Q2FULL**, one conditional build/link/WRITE/READ/verify job  
**Scope:** F80 and blocked FB80, 23 records each, independently verified FB copy

## Source-controlled components

- test-q2-write.bcpl: opens output F80, FB80 and empty F80; verifies
  output geometry, rejects short/long writes and wrong direction,
  emits 23 full binary records in each dataset, and closes them.
- test-q2-read.bcpl: opens three inputs and an FB80 copy output; checks
  empty EOF twice, interleaved short-read retries and unchanged
  buffers, exact bytes, repeated EOF, invalid direction/length,
  stale handles and a complete 23-record FB80 copy.
- q2-verify-copy.asm: independent QSAM reader of copied FB80 data;
  compares all 80 bytes of each of 23 records and requires EODAD.
- prepare-q2-consolidated.py: builds authenticated temporary-only
  Q2FULL JCL from two actual compiled CG370 assembler inputs, reusing
  the established Q.1 BCX/IEWL generator. Never submits JES.
- test_prepare_q2_consolidated.py: synthetic JCL and fault tests.
- check-q2-consolidated-evidence.py and
  test_q2_consolidated_evidence.py: post-JES 13-step and exact
  PASS-record checks. Never submit or modify MVS datasets.

## Thirteen native steps in ONE Q2FULL job

| Steps | Purpose |
| --- | --- |
| ASMA, ASMB, ASMV | IFOX writer, reader, independent verifier |
| ASMN, ASMR, ASMQ, ASMG | IFOX BCPLMAIN, BCPLRGS, BCPLQSAM/QSMIO and BCX |
| LKED, LKRD, LKVR | IEWL writer, reader, verifier executables |
| WGO | BCPL writes F80, FB80 and empty F80 temporary datasets |
| RGO | BCPL reads/verifies datasets, tests pending/EOF, copies FB80 |
| VGO | Independent assembler compares every copied FB80 byte |

All GO phases have dependency guards, using REGION=256K. F80 has
RECFM=F,LRECL=80,BLKSIZE=80 and blocked FB80 has
RECFM=FB,LRECL=80,BLKSIZE=800; reader DDs repeat explicit geometry.
Only temporary object, load and record datasets are created.
SYS1.MACLIB and existing BOOT_OBJ are read-only; no installed
object library is overwritten.

## Compiler prerequisite and execution boundary

The established native-code workflow uses tools/bootstrap/compile-mvs
to run the demoted Cambridge compiler under MVS ICINT19. It yields
CG370 assembler requiring the proven R0APP adaptation before IFOX.
To avoid inventing an untested in-JOB assembler-text rewriting
mechanism, compile each of the two BCPL fixtures first using that
existing tool. **These are two separate JES compiler submissions
requiring operator authorization.** The demoted compiler is not the
separately reconstructed native Cambridge compiler.

Once their assembler is available, the **single Q2FULL JES job**
performs every IFOX, IEWL, and record-verification phase. There is
no preliminary assembler-only job.

## WSL offline checks — no JES submission

Run from repository root with a clean main checkout after syncing the
announced campaign commit. No fail-fast and no installed MVS writes:

    set +e
    set +u
    set +o pipefail
    q2=bootstrap-toolchain/extensions/bcplqsam
    python3 -m py_compile "$q2/prepare-q2-consolidated.py" \
      "$q2/test_prepare_q2_consolidated.py" \
      "$q2/check-q2-consolidated-evidence.py" \
      "$q2/test_q2_consolidated_evidence.py"
    echo "Python syntax RC=$?"
    python3 "$q2/prepare-q2-consolidated.py" --check
    echo "Synthetic Q2FULL RC=$?"
    python3 "$q2/test_prepare_q2_consolidated.py" -v
    echo "JCL unit tests RC=$?"
    python3 "$q2/test_q2_consolidated_evidence.py" -v
    echo "Evidence unit tests RC=$?"

## Native preparation, JCL and later evidence — separate gates

After approval of the two compiler JES jobs, run the established
tools/bootstrap/compile-mvs for test-q2-write.bcpl and
test-q2-read.bcpl with unique job names Q2WCOMP and Q2RCOMP,
saving generated assembler respectively at:

- workarea/bcplqsam-q2/write-generated.asm
- workarea/bcplqsam-q2/read-generated.asm

Then materialize the complete **authenticated JCL locally**,
without JES submission:

    python3 bootstrap-toolchain/extensions/bcplqsam/prepare-q2-consolidated.py \
      --writer workarea/bcplqsam-q2/write-generated.asm \
      --reader workarea/bcplqsam-q2/read-generated.asm

This creates workarea/bcplqsam-q2/q2full.jcl exclusively with mode
0600 and prints its card count and SHA-256. Real compiler output
and manifest authentication cannot be committed into a generic
static JCL file; the generator and all static source inputs are
source-controlled, and the concrete deck is a reproducible
operator-local output. Do not overwrite an existing deck or erase
an attempt marker to force resubmission.

**Submitting Q2FULL is not authorized by this runbook.** When
separately approved, submit it exactly once, record the JOB number,
and preserve full JES summary/report on both failure and success.
On an uncertain submission result, inspect JES before any retry.

Once summary and report are saved:

    python3 bootstrap-toolchain/extensions/bcplqsam/check-q2-consolidated-evidence.py \
      --summary workarea/bcplqsam-q2/q2full-summary.txt \
      --report workarea/bcplqsam-q2/q2full-report.txt

A native PASS requires all thirteen named steps at RC=0000 and the
three exact ordered records:

1. BCPLQSAM Q2 WRITE 23 F80 FB80 PASS
2. BCPLQSAM Q2 READ COPY EOF RETRY PASS
3. BCPLQSAM Q2 COPY 23 FB80 EXACT PASS

Review full IFOX severity, IEWL MAP and JES details independently.
This test does not itself constitute Q.2 acceptance. The carried
Q.1 negative/STOP regressions and full native baseline panel remain
separate required acceptance evidence. No permanent MVS datasets or
Core Runtime objects are changed.
