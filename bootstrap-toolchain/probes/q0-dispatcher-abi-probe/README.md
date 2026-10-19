# Q.0 — QSAMSVC (G!200) native dispatcher ABI probe

**Status: PASS on MVS 3.8J (2026-10-19, JOB 2156 and JOB 2157).**

This is an isolated probe for the BCPLQSAM public ABI, *not* BCPLQSAM
implementation. The dispatcher does no QSAM I/O. No compiler, BCPLMAIN,
BCPLIO, manifest, accepted BOOT_OBJ or candidate BOOT_DEVOBJ object is changed.

## Repository location

This test is retained under `bootstrap-toolchain/probes/`. The generated
JCL and compiled application code live under `workarea/` and are not
checked into Git. Do not use the old downloadable ZIP as the authority.

## Run

With the installed BOOT_OBJ production profile:

    bash bootstrap-toolchain/probes/q0-dispatcher-abi-probe/run-q0.sh OBJ

Or with the accepted historical DEVOBJ BCPLM6 candidate profile:

    bash bootstrap-toolchain/probes/q0-dispatcher-abi-probe/run-q0.sh DEVOBJ

The first step calls the **demoted Cambridge compiler** (CAMBCOMP through
ICINT19), generating application assembler in `workarea/qsam-q0-abi/`.
`prepare-job.py` then adds a **test-only** trailer record for G!200,
relocating to the separate assembler symbol `Q0DISP`. This uses the exact
trailer format already proven in native regression 26. Only the generated
application assembler is modified, not BCPLMAIN.

The GO JCL independently assembles the application and dispatcher, links
with *existing* BOOT_OBJ/BOOT_DEVOBJ object members, and runs. No objects
are written to persistent PDSs; work goes to temporary `&&` datasets.

Submit output prints a JOB number. Examine it with:

    tools/mvs/job-summary <job-number> --max-rc 0
    tools/mvs/dump-report-for-job <job-number>

## Test behavior

- G!200/`QSAMSVC` resolves through the application trailer to `Q0DISP`.
- Three arguments cross the call in R7, R8 and R9.
- Request and result **BCPL word pointers** are converted to byte addresses.
- An INFO-like dummy operation validates four request words, fills result
  word 1 with 42 and word 7 with 777, and returns status zero.
  **These dummy values deliberately do not implement real INFO semantics:**
  they prove that arguments and results cross the assembler ABI.
- QUERY size probe returns 6; too-small query returns -1 and leaves its
  buffer unchanged; full QUERY fills the six-word version 1 descriptor.
- Unknown opcode 99 returns -2 and sets result word 0 to -2.
- All subsequent BCPL execution continues, ending with `DEBUGINT(42)`.
- Any BCPL assertion failure calls STOP(8).

**PASS requires** compile, ASMAP, ASMNAT, LKED and GO success (RC=0000),
observed integer output `42`, correct generated `L 4,800(12)` or equivalent
G!200 call sequence, and verified `DC F'800'` / `DC A(Q0DISP)` in the
assembled application trailer. Inspect the IEWL MAP for Q0DISP resolution.

**NOT covered:** MVS QSAM OPEN/GET/PUT/CLOSE; real INFO dataset attributes;
resource and record staging; generic optional-module registration through
BCPLREG; missing/unregistered extension recovery; Q.0 milestone closure.

## Files

- `caller.bcpl` — one native BCPL test caller; assertions stop with RC8.
- `dispatcher.asm` — independently assembled no-I/O dispatcher.
- `prepare-job.py` — generated-application G!200 trailer patch and GO JCL.
- `run-q0.sh` — compile, prepare and submit using existing project tools.

## Observed acceptance

The owner ran the demoted Cambridge compiler as **JOB 2156**, which
returned the compiled application assembler in
`workarea/qsam-q0-abi/caller.s370.asm`. After correcting the initial
whitespace-sensitive `EXTRN BCPLMAIN` validation in `prepare-job.py`,
**JOB 2157** assembled and linked the application plus the separately
assembled dispatcher, executed on MVS 3.8J/TK5, and printed `42`.

- `ASMAP` IFOX00 RC=0000
- `ASMNAT` IFOX00 RC=0000
- `LKED` IEWL RC=0000
- `GO` RC=0000
- IFOX reported no flagged statements in either assembly
- G!200 at byte offset 800 used `L 4,800(12)`
- App trailer exported `DC F'800'` / `DC A(Q0DISP)`
- IEWL MAP resolved `Q0DISP`, application and six accepted BOOT_OBJ objects
- `42` was printed after the BCPL assertions passed

See [the retained evidence](../../../packaging/qsam-q0-dispatcher-abi-evidence-20261019.md).
This is **not** proof of real QSAM calls or Runtime Extensions R.0
registration. The program intentionally uses a test-only generated-trailer
patch; no production registrar or accepted runtime source was altered.
