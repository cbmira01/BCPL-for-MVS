# M4.2.2 — read-only PDS without member: real QSAM OPEN probe

**Status: EXECUTED AND CHARACTERIZED — RG891R JOB 7875
RETURNED HANDLE, not a failed OPEN (2026-10-17).**

The operator supplied the complete JOB 7875 JES report. GO
JCL allocated `DD02 DD DSN=SYS1.MACLIB,DISP=SHR`
with no member. JES reported `390 ALLOCATED TO DD02`
and retained `SYS1.MACLIB` as KEPT. ASMAP/LKED/GO
all returned `RC0000`; the GO step recorded one
device I/O operation on 390, not necessarily a GET.
The linker includes `OBJ(BCPLM6)` and
`OBJ(BCPLIO)` from the ordinary development library,
not a test-only fault-injection module.

Actual primary BCPL SYSOUT markers:

```text
M42 BEFORE FIND DD02
M42 DD02 RETURNED HANDLE
M42 SURVIVED FIND DD02
```

Thus, the allocated nonmember PDS was **accepted by
BCPLIO's FINDINPUT OPEN path**. The canonical DIFIND
requires success from DDVERIFY, DALLOC, DQOPEN
(real SVC19), and HNEW to return the handle.
The program deliberately performs **no RDCH on DD02**;
no successful input data transfer, nor a subsequent
GET-path error, has been demonstrated.

**Disposition:** M4.2.2 experiment completed, but it
did not supply the desired actual failed OPEN.
Do not count it as a successful failed-OPEN recovery
regression. Keep M4.2 OPEN. Next consider a deliberately
invalid *record-format/length* DCB combination that
should trigger an OPEN-time check, using a separate
development-only probe and not modifying SYS1.MACLIB.


The operator ran the non-submitting generator and then submitted
`workarea/m42-real-open/pds-open.jcl` as RG891R JOB 7875.
`tools/mvs/job-summary 7875` reported:

```text
JOB 7875  RG891R
17 OCT 26  05.42.27 - 05.42.27
ASMAP      IFOX00       RC=0000
LKED       IEWL         RC=0000
GO         PGM=*.DD     RC=0000
JOB RESULT: SUCCESS
HIGHEST RC: 0000
Assembler: Statements flagged: 0; Highest severity: 0
Resources: Cards 271; SYSOUT 502 records
```

The operator saved the complete spool in
`workarea/m42-real-open/pds-open-report.txt`, but that
file's contents have not been provided. There was **no
reported GO-step abend**, but the summary cannot establish
whether `FINDINPUT("DD02")` returned a zero or a handle;
it cannot distinguish RDJFCB rejection from an actual
unsuccessful SVC19. This probe is not a native regression
PASS. **No further workstation checks or job runs are
needed before reviewing the saved report.**

The operator pulled through `3235115` and generated
`workarea/m42-real-open/pds-open.jcl` from the earlier
Cambridge output. The generator confirmed
`RG891R: DD01=DATA; DD02=SYS1.MACLIB,DISP=SHR (no member)`
and printed that the GO job was NOT submitted and no PDS
object was modified. This records preparation only;
there is no RG891R JES/GO evidence yet.
**Exploratory only, NOT a native-regression PASS/FAIL case.**

M4.2.1 `RG890R` (JOB 7874) used `DD02 DD SYSOUT=*`
and returned a valid `FINDINPUT("DD02")` handle.
The complete JES report showed no OPEN error. Therefore
the initial mode mismatch did **not** create the desired
genuinely unsuccessful SVC 19.

M4.2.2 changes only the DD allocation. The existing
version-controlled Cambridge BCPL application and `DD01`
fixture under `bootstrap-toolchain/probes/m42-real-open/`
are reused. Its **previously generated** assembler at
`workarea/m42-real-open/generated.s370.asm` from compiler
JOB 7873 is also reusable. No new Cambridge compilation
or source check needs to be run on the operator workstation.

The GO DDs for the new `RG891R` deck are:
- `DD01 DD DATA` (two known input records, A and B).
- `DD02 DD DSN=SYS1.MACLIB,DISP=SHR` (read-only
  partitioned dataset **without any selected member**).

The BCPL code calls `FINDINPUT("DD02")` without GETting
from DD02 even if FIND succeeds, so this is an OPEN
diagnostic rather than a data-read experiment. Current
IBM QSAM documentation describes access to a PDS without
a member as a possible error. MVS 3.8J may reject earlier
at RDJFCB, fail at OPEN (including system x13 abend),
or accept the allocation. **All outcomes are diagnostic.**

The builder `tools/checks/prepare-m42-pds-open-jcl.py`
starts from canonical source and the existing PDS regression
JCL generator, uses test number 891 strictly as a unique
job identity (not a registered regression), inserts the
read-only SYS1.MACLIB DD, and refuses duplicate DD02 or
malformed JCL. It does not submit the generated job,
modify the actual PDS or write to any installed OBJ/DEVOBJ.
JCL statements are checked for assembler/JCL card width
inside the generator. No separately invoked workstation
checks are required.

## Operator preparation — NO MVS GO submission

```sh
cd ~/Source/Repos/BCPL-for-MVS
git pull --ff-only

BCPL_RUNTIME_PDS=1 \
BCPL_RUNTIME_LIBRARY=DEVOBJ \
BCPL_RUNTIME_CANDIDATE=1 \
BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6 \
python3 tools/checks/prepare-m42-pds-open-jcl.py \
  workarea/m42-real-open/generated.s370.asm \
  workarea/m42-real-open/pds-open.jcl
```

Expected JCL generator output identifies `RG891R`,
`DD02=SYS1.MACLIB,DISP=SHR`, and explicitly says
the GO job was not submitted.

## Exploratory submission (separate deliberate action)

Only after checking the prepared deck's intended DD
and read-only mode, submit it to the TK5 reader:

```sh
submission=$(tools/mvs/submit-jcl --timeout 30 \
  workarea/m42-real-open/pds-open.jcl)
printf '%s\n' "$submission"
job=$(printf '%s\n' "$submission" |
  awk '/^JOB [0-9]+$/ {print $2; exit}')
tools/mvs/job-summary "$job" || true
tools/mvs/dump-report-for-job "$job" \
  > workarea/m42-real-open/pds-open-report.txt
```

Supply the job summary and complete `pds-open-report.txt`
with credentials redacted. Preserve IEC/IEF messages and
all three step condition codes. A GO ABEND is possible
and **must not be recorded as a successful regression**.

No source-only test checks or full native regression
panel are required of the operator. The full panel remains
owner-deferred. The still-open M4.2 actual failure gate
will be interpreted against the observed control flow,
rather than assumed from DD allocation alone.
