# BCPLTIME — T.0 MVS-verified candidate; T.1 packaging in progress

Milestone BCPLTIME, **T.0 — Descriptor, Dispatcher, and Native Execution CLOSED**;
**T.1 — Packaging and Acceptance IN PROGRESS** (24 October 2026).
JOB 5436 verified source-mode native MVS operation, but **BCPLTIME is
not yet installed or accepted for installed-mode production use**.
The governing document is packaging/milestone-date-and-time-services.md.
See [the T.0 owner closure](../../../packaging/bcpltime-t0-closure-20261024.md).

## Contents

- bcpltime.asm — one object, two CSECTs: TIMDESC and TIMDISP;
  BCEX v1 public G!201/TIMESVC, no dependencies/finalizer.
- bcpltime.h — declaration header, no wrapper code.
- test.bcpl — direct three-operation native BCPL caller with guard words.
- t0-catalog.asm / t0-selection.asm — source-mode BCX selection
  of a temporary TIMEOBJ DD; not production catalog replacements.

## ABI

TIMESVC(op, vector, capacity_words) follows BCPLDEMO's tested R7/R8/R9
convention, preserving the shared QUERY version-1 six-word descriptor.
The result is a word count (6, 3 or 2) or -1/-2/-3.

STCK returns high/low raw words and instruction condition code, using
private doubleword-aligned scratch to avoid assuming the BCPL vector
starts at a doubleword boundary. This means the candidate is **not
reentrant**; it introduces no persistent application-level state.
TIME DEC copies the MVS macro's R0 and R1 fullwords. JOB 5436's IFOX
listing verifies the period macro's SVC 11 expansion, and GO passes
after preservation of permanent R0/R1. The raw words' calendar/date
encoding is not independently decoded; later documentation is not proof.

## First integrated MVS check (T.0)

1. Compile test.bcpl with the resident demoted Cambridge compiler
   through the supported tools/bootstrap/compile-mvs driver.
2. Assemble bcpltime.asm under IFOX with SYS1.MACLIB as SYSLIB;
   retain the assembler listing, especially the TIME DEC expansion.
3. Assemble the accepted BCX macro selections by concatenating, in
   order, the existing BCXPRE.asm, this directory's t0-catalog.asm,
   t0-selection.asm, and the existing BCXPOST.asm. The unchanged
   BCXREQ macro emits BCRG v1 and punches INCLUDE TIMEOBJ; point
   IEWL's TIMEOBJ DD at the **temporary** BCPLTIME object deck.
4. Link the compiled native BCPL caller, accepted BOOT_OBJ Runtime/Base
   Library/BCPLRGS, the temporary BCRG object and the selected package.
   Specify explicit application ENTRY, as in R.4/R.5. Check IEWL MAP
   for TIMDESC, TIMDISP, TIMBEG/TIMEND and G!201.
5. Run GO and check for BCPLTIME T0 PASS, plus the raw numeric fields
   from STCK and TIME. Confirm the hardware CC is 0..3. Treat returned
   words as raw bit patterns; do not infer a year from a signed BCPL word.
6. Compare actual JES/IFOX/IEWL/GO output against the three-opcode and
   no-partial-write checks; fix the **real package** instead of creating
   additional throwaway probe implementations.

The accepted BCXCAT production catalog currently selects BCPLDEMO only.
BCPLTIME's catalog entry, installation JCL, MVS member mapping and
installed-mode acceptance are T.1 work requiring owner authorization
before any permanent PDS write. Do not overwrite the existing BCPLDEMO.

## Offline validation

Run python3 tools/checks/check-bcpltime-t0.py from the repository root.
This is a source-structure check, not an MVS execution test.

## Current evidence

Source checked for strict 71-column card width, 8-character assembler
symbols, descriptor field constants and expected BCPL declarations.
JOB 5434 (24 October 2026): all five IFOX assemblies and IEWL returned
RC=0000; GO ABEND S0C4. Dump evidence showed MVS TIME DEC left R0/R1
changed on return to generated BCPL, preceding failure in BLIB WRITED.
The T.0 correction saves R0/R1 in call-frame words +24/+28, captures
raw TIME results, and restores R0/R1 before returning. **JOB 5436 PASS**:
ASMA/ASMN/ASMR/ASMT/ASMG, IEWL and GO all RC=0000; IEWL MAP PASS;
`BCPLTIME T0 PASS` emitted with STCK CC=0 and two raw TIME words.
The record checker reported that JES DD attribution was NOT VERIFIED;
see the [T.0 owner closure](../../../packaging/bcpltime-t0-closure-20261024.md).
T.1 installed-mode linkage and full regression are still outstanding.

## T.0 direct execution command (source mode, temporary datasets only)

After a clean Git pull, on the machine running Hercules/TK5:

```sh
bash tools/bootstrap/run-bcpltime-t0 --check
bash tools/bootstrap/run-bcpltime-t0
```

The second command runs the existing `tools/bootstrap/compile-mvs` driver
against `test.bcpl`, generates authenticated JCL in ignored, locally owned
`workarea/bcpltime-t0/t0time.jcl` (mode 0600), submits it once to JES, and
waits for the seven expected IFOX/IEWL/GO step results. It checks a real
IEWL cross-reference map for `R0APP`, `BCPLMAIN`, `RGINIT`, `TIMDESC`,
`TIMDISP`, and a 44-byte `BCPLREG` with zero application entry address;
then checks for the exact `BCPLTIME T0 PASS` logical record in the JES GO
suffix. The test also prints raw STCK and TIME return words.

Evidence is saved under `workarea/bcpltime-t0/`:
`test-generated.asm`, `t0time.jcl`, `last-job.txt`, `job-summary.txt`,
`job-report.txt`. These generated/operator-local files are **not** Git
sources; the job card may include local credentials and must not be committed.
A nonzero step, missing MAP, or missing PASS marker fails the runner;
inspect the complete report and debug the actual dispatcher source.

Offline tests (do not contact MVS):

```sh
python3 -m unittest discover -s tools/checks \
  -p 'test_*bcpltime_t0*.py' -v
python3 tools/checks/prepare-bcpltime-t0.py --check
```

No installed `EXT_OBJ`, `EXT_MAC`, or `BOOT_OBJ` members are overwritten.
T.0 is CLOSED on actual IFOX/IEWL/GO JOB 5436 evidence; offline checks
alone would not have met the acceptance gate. T.1 requires approved
installation design, selected/unselected linkage, installed-mode
acceptance, and full native production regression.
