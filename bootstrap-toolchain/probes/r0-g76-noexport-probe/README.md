# Milestone Runtime Extensions — R.0 G!76 no-export fallback probe

**March:** R.0 — Evidence and contract (**open**). Next march R.1 — Generic
registration foundation (**not started**). **Status: host-tested, MVS
execution pending.** Owner approved this specific isolated fixture on
21 October 2026 after the [effective ownership follow-up]
(../../../packaging/runtime-extensions-r0-effective-owner-followup-20261021.md).

## Exact question

The installed bootstrap `BCPLMAIN` requires the **BLIB external symbol**
for startup. It installs native `WRITEST` into G!76 only when no earlier
application/BLIB G!76 export was imported. JOB 2199 already proved the
**installed BLIB-present** WRITEF precedence. This test verifies the
opposite **no-G!76-export** branch, NOT the ability to run without any
BLIB symbol or a complete optional-Base-Library facility.

The test creates a **temporary `BLIB` CSECT** containing only a valid
24-byte CG370-style prefix and 8-byte empty export-trailer sentinel
(`F'2796'`, `F'0'`). It exports **no** BCPL procedures or globals.
A minimum BCPL `START` uses **only** G!76 `WRITEF` with `%N` numeric
formatting and `FINISH`, no BLIB `WRITES`/`NEWLINE` dependency.
The exact expected real output record is:

```
R0 G76 FALLBACK 31415 PASS
```

`31415` is *not* in the compiler source as a literal substring of
that output; the source has the `%N` formatting directive. A native
`WRITEST` fallback capable of formatting the argument is required to
produce the final GO record.

## Link and protection boundary

The probe assembles: (1) the compiled application's renamed
`R0APP` CSECT; (2) the *temporary* `BLIB` CSECT. IEWL uses the two
sequential temporary FB/80 objects followed by explicitly included
**installed** `BOOT_OBJ(BCPLMAIN)`, `(BCPLIO)`, `(BCPLMEM)`,
`(BCPLBYTE)`, `(BCPLAPT)` **read-only**. It must **not** include
`BOOT_OBJ(BLIB)`. `NCAL,LIST,XREF,MAP` links into `&&R0LOAD` only.
Only the temporary load module is executed; no object is installed,
replaced, promoted or exported from MVS.

The fixture defines the same prefix fields that `BCPLMAIN` reads:
10-byte entry prologue, halfword at byte offset +10 declaring the
module's complete length (24 bytes), relocated byte address of
`BCPLMAIN` at +12, and a single `(2796,0)` sentinel pair at +16.
The generator rejects any extra exports or changes to that exact
source body and rejects an application with exports other than START.

## Run on Morkies (TK5 running)

```bash
cd ~/Source/Repos/BCPL-for-MVS
git pull --ff-only
bash bootstrap-toolchain/probes/r0-g76-noexport-probe/run.sh
```

The script first runs unit tests and a synthetic JCL check. It then:

1. Compiles `source.bcpl` under the interpreter-hosted **demoted Cambridge
   compiler** (a distinct first JES job, `R0G76FC`).
2. Generates the authenticated IFOX/IEWL/GO job `R0G76F` into ignored
   `workarea/runtime-extensions-r0-g76-noexport/` (mode 0600).
3. Submits `R0G76F`, retrieves the full report, checks ASMA/ASMB/LKED/GO
   each RC=0000, nonempty assembled objects, and one exact formatted
   GO output marker.
4. Retains the full IEWL MAP/XREF for operator review.

**Do not call it MVS PASS until the actual report is inspected.** In
particular, verify that `BLIB` is defined by `ASMB`'s *temporary*
object, length `000018` (hex), has no exported G!76 global pair, and
that the five included core CSECTs resolve from installed `BOOT_OBJ`.
Any unresolved symbol, wrong CSECT owner, extra entry in the empty
trailer, unexpected return code or absent GO marker is a failure.

### Offline checks only

```bash
probe=bootstrap-toolchain/probes/r0-g76-noexport-probe
python3 -B -m unittest discover -s "$probe" -p 'test_*.py' -v
python3 -B "$probe/make-job.py" --check
bash -n "$probe/run.sh"
```

Host tests verify structural/source guards, generated JCL, and report
parser failure cases. They do not prove IFOX accepts the source or
that `WRITEST` executes under MVS. No untrusted object pointer is
dereferenced by any new probe code. Job cards may contain credentials:
**do not commit `workarea/` JCL or full JES reports.** Keep Git
revision, hashes, job numbers and actual GO/MAP evidence in the
engineering record after MVS execution.

## Interpretation limits

This is an actual installed `BCPLMAIN` **branch test** if MVS passes,
not production registration or proof that a physically absent BLIB
can link. It does not resolve G!150 (`DEBUGINT`/`FORMTREE`) or
prove collision transactionality. The accepted `BOOT_OBJ` remains
unaltered. **R.0 open; R.1 not started.**
