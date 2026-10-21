# Milestone Runtime Extensions — R.0 G!150 startup owner observer

**March:** **R.0 — Evidence and contract (open)**. Next march:
**R.1 — Generic registration foundation (not started)**.
**Status:** approved isolated *test-only* implementation; host checks
pass. **Actual MVS execution and IEWL MAP/XREF review are pending.**
See [owner-approved design](../../../packaging/runtime-extensions-r0-g150-startup-ownership-review-20261021.md).

## Exact question and interpretation

The real installed bootstrap `BCPLMAIN` imports application and BLIB
globals and then unconditionally publishes its provisional `DEBUGINT`
address at **G!150** before invoking `START`. The **full Cambridge
compiler** historically declares `FORMTREE:150`. The latter is not
run by this test; this measures one synthetic application's G!150 at
`START`, not a fully linked compiler's subsequent `LOADSEG("SYN")`.

The interpreter-hosted **demoted Cambridge compiler** compiles a small
BCPL application. A tightly guarded assembler adapter retains its
compiler-generated G!1 `START` export and adds two relocated pairs:

- **G!150** (byte offset 600): independent test symbol `R0MARK`;
- **G!151** (byte offset 604): *test-local only* `R0CK15` verifier.

The separate `R0O150` IFOX object exports `R0MARK` and `R0CK15`.
`R0CK15` takes a numeric opcode in R7:

- **0:** Verify real G!150 is neither `R0MARK` nor the uninitialized
  sentinel, and that **the installed BLIB's trailer does not export
  G!150**. Return 0 on success, 8 otherwise.
- **1:** Return the observed G!150 value (a byte address).
- **2:** Return the independent relocated `R0MARK` address.

No function pointer read from G!150 is called. No G!150 write occurs
in `R0CK15`. The application exits `STOP(8)` on a failed check.
On success, it calls *installed BLIB* `WRITEF` with `%X8` formatting
to print both observed addresses (different across runs):

```
R0 G150 OVERWRITE ACT=hhhhhhhh APP=hhhhhhhh PASS
```

Both hex fields are eight uppercase hexadecimal digits. The report
verifier rejects absent/duplicate output, equal addresses, sentinel,
zero actual pointer, any failed step, missing punched objects, or
assembler errors. It does **not** claim to prove the exact address
of the private `DEBUGINT` routine. The observed replacement's likely
owner is explained by inspected BCPLMAIN source order; a future
full-compiler and overlay test remains necessary.

## Accepted object safety and linker evidence

The job assembles the adapted application and observer to separate
temporary FB/80 objects and links a temporary `&&R0LOAD` module.
IEWL explicitly includes only installed
`BOOT_OBJ(BCPLMAIN)`, `(BCPLIO)`, `(BCPLMEM)`, `(BCPLBYTE)`,
`(BCPLAPT)`, and **`(BLIB)`**, through an input-only `DISP=SHR`
DD. This is not an optional-package registrar or an accepted-object
installation. The imported BLIB trailer is checked for any G!150
export at runtime, and the prior [JOB 2197 ledger](../../../packaging/runtime-extensions-r0-trailer-job-2197-evidence-20261021.md)
independently documented its 21 exports, none at G!150.

Require actual IEWL `MAP,XREF,LIST` proof that `R0MARK` and
`R0CK15` belong to the temporary `R0O150` CSECT and that all six
installed CSECTs, including BLIB, came from installed `BOOT_OBJ`.
The actual application trailer must show G!1 at offset 4, G!150 at
600 and G!151 at 604, with independently relocated addresses.
No outcome is accepted from IFOX source literals alone.

## Run on Morkies

From the clean, fast-forwarded GitHub `main` checkout, with TK5
running and normal local `dspal` credentials configured:

```sh
cd ~/Source/Repos/BCPL-for-MVS
git pull --ff-only
bash bootstrap-toolchain/probes/r0-g150-startup-probe/run.sh
```

The script performs host tests and JCL checks, compiles the BCPL test
under the demoted Cambridge compiler as `R0G150C`, generates a
private job card/JCL in ignored `workarea/runtime-extensions-r0-g150/`,
then submits IFOX/IEWL/GO job **`R0G150`**. It writes a source/hash
manifest, captures the full JES report, checks each step, and prints
the dynamic G!150 addresses if the probe passes. **A final human
IEWL MAP/XREF check is required** before accepting the observed
linker ownership. No accepted object member is modified.

Offline checks only (no submitted job):

```sh
probe=bootstrap-toolchain/probes/r0-g150-startup-probe
python3 -B -m unittest discover -s "$probe" -p 'test_*.py' -v
python3 -B "$probe/make-job.py" --check
bash -n "$probe/run.sh"
```

The output report and JCL may contain local credentials. They stay
under ignored `workarea/`; commit only sanitized evidence and source.
No claim about **G!150 remediation**, historical compatibility, or
R.1's pre-START transactional collision rejection follows from a
probe run. **R.0 stays open; R.1 has not started.**
