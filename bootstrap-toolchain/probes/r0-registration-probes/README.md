# Milestone Runtime Extensions — R.0 link-resolved descriptor probes

**March:** **R.0 — Evidence and contract** (open). **Test-only, not MVS-executed.**
The owner approved the revised bounds/dependency/collision design **for
testing**, not as an exact accepted binary ABI. R.1 has not started.
Do not install objects into BOOT_OBJ or BOOT_DEVOBJ.

## Scope and independent linked objects

Four separately assembled IFOX objects are linked by IEWL to a **temporary
load module**:

- **validator.asm (R0CHK):** checks relocated begin/end symbols, alignment,
  physical span vs declared length, descriptor version, selected package
  export, application requirement, and selected duplicate/core collisions.
  It does **not** publish globals.
- **Generated R0REG CSECT:** exports R0RB and R0RE around a 28-byte
  candidate table header, one eight-byte package begin/end pair and
  one eight-byte required ID: **44 bytes** for the valid fixture.
- **Generated R0PKG CSECT:** exports R0PB and R0PE around a candidate
  48-byte package header and one/two eight-byte export entries:
  **56/64 bytes** for these fixtures.
- **function.asm (R0FUNC):** supplies a relocated code address,
  **never invoked**.

IEWL must resolve R0RB, R0RE, R0PB, R0PE and R0FUNC from independent
objects. Inspect the actual IEWL MAP and XREF as well as GO.
This is one bounded test fixture, **not** proof of general MVS
protection from a forged pointer or corrupted load module.

PACKA and **G!299** are test-local only. G!299 is **not assigned** to PACKA
by the Global Number Registry. The negative Core Runtime collision uses
occupied **G!14**. The validator handles only one selected descriptor,
one application requirement, at most two exports and no package-local
dependencies. It is **not** a production registration validator,
full dependency engine, slot-owner ledger, or finalizer.

## Profiles and expected evidence

| Profile | JOB | Expected *internal* code | Actual QOUT marker required |
| --- | --- | ---: | --- |
| valid | R0VALID | 0 | R0 VALID LINK BOUNDS PASS |
| badlen | R0LENG | 4 | R0 BADLEN REJECTED PASS |
| badversion | R0VERS | 8 | R0 BADVERSION REJECTED PASS |
| duplicate | R0DUP | 12 | R0 DUPLICATE EXPORT REJECTED PASS |
| corecollision | R0CORE | 16 | R0 CORE G14 COLLISION REJECTED PASS |
| missingreq | R0REQ | 24 | R0 MISSING REQUIREMENT REJECTED PASS |

Every negative case is PASS only when the **exact expected internal
status** occurs. GO then returns **RC=0000** and prints its
QOUT marker. If rejected for a different reason or erroneously accepted,
GO should return RC=0008 with no actual QOUT PASS record.
The internal validator status is **not** the JES GO condition code.

## Run on Morkies, from repository root

~~~bash
PROBE=bootstrap-toolchain/probes/r0-registration-probes
python3 -B -c 'import ast,pathlib; p=pathlib.Path("bootstrap-toolchain/probes/r0-registration-probes/test_generator.py"); ast.parse(p.read_text()); print("Syntax OK:",p)'
python3 -B -m unittest discover -s "$PROBE" -p test_generator.py -v
for profile in valid badlen badversion duplicate corecollision missingreq; do
    python3 -B "$PROBE/make-jobs.py" "$profile" --check
done

# First run ONLY the valid fixture, then inspect its actual JES report:
python3 -B "$PROBE/make-jobs.py" valid
bash tools/mvs/submit-jcl workarea/runtime-extensions-r0/r0-valid.jcl
# Replace JOBNUMBER with the actual submit result:
tools/mvs/job-summary JOBNUMBER --max-rc 0
tools/mvs/dump-report-for-job JOBNUMBER
~~~

When run, success needs **ASMD, ASMR, ASMP, ASMF, LKED and GO** all RC=0000,
plus the actual QOUT marker. A PASSREC source constant in an IFOX
listing is not an actual QOUT marker. Do **not** submit the negative
fixtures until the positive assembly/link/run has been inspected.

The dry --check uses no credentials or output files. Normal generation
uses the project's authenticated JOB-card helper; output is mode 0600
under ignored workarea/runtime-extensions-r0/. All objects/load modules
use temporary && datasets, not persistent PDSs. Do not commit
credentials or raw JES reports.

## Evidence boundary

**Validation correction (2026-10-20):** The first Morkies run
stopped before any deck generation or submission: a missing closing
parenthesis in `test_generator.py` caused `SyntaxError` at line 62.
That source typo has been corrected. Earlier text claiming four unit
tests had passed was incorrect. Re-run syntax, unit and generator
checks on Morkies; **their passing results are not yet confirmed**.
**IFOX, IEWL and MVS GO have NOT run** for these sources. Dependency transitivity/ordering,
complete collision ownership, trusted module extents, finalizer
invocation, FINISH/STOP integration and R.0 closure remain future gates.
See the [approved R.0 testing scope](../../../packaging/runtime-extensions-r0-testing-decision-20261020.md).