# M4.2.1 — Real MVS OPEN exploratory probe

**STATUS: EXECUTED AND CHARACTERIZED — RG890R JOB 7874;
real QSAM input FIND returned a HANDLE, not the intended
OPEN failure. This was an exploratory job, not a regression.**

The operator-provided complete `real-open-report.txt` for
JOB 7874 establishes:

```text
M42 BEFORE FIND DD02
M42 DD02 RETURNED HANDLE
M42 SURVIVED FIND DD02
```

The job's printed JCL allocated `DD01 DD DATA` and
`DD02 DD SYSOUT=*,DCB=(RECFM=FB,LRECL=132,BLKSIZE=132)`.
JES shows `JES2 ALLOCATED TO DD02`, ASMAP/LKED/GO all
`RC0000`, and the link editor explicitly included the
unmodified `OBJ(BCPLM6)` and `OBJ(BCPLIO)` members
from the DEVOBJ library. No IEC error or abend was
reported. The program intentionally **did not issue RDCH
on the returned DD02 handle**, so it does not prove that
reading SYSOUT works.

The canonical DIFIND path creates a nonzero new handle
only after RDJFCB verification, descriptor allocation,
DQOPEN (which performs real SVC 19) and handle
allocation succeed. Since DD02 was not opened earlier,
this observed HANDLE rules out a pre-OPEN RDJFCB rejection
as the cause of a failed FIND. It provides source-guided
evidence that DQOPEN was entered and regarded the DCB as
opened. The alleged SYSOUT/input incompatibility was
**not actually rejected under this TK5 experiment**.

**Disposition:** M4.2.1 attempt completed, but its intended
actual failing-OPEN acceptance criterion was NOT met.
Keep M4.2 open and try a genuinely incompatible allocated
dataset/DD in a new, separately tracked exploratory job.
Do not call the SYSOUT allocation a demonstrated OPEN error.


The operator compiled source using Cambridge `JOB 7873`,
prepared `workarea/m42-real-open/real-open.jcl` and
submitted it as **RG890R JOB 7874**. On 17 October 2026,
`tools/mvs/job-summary 7874` reported `ASMAP RC0000`,
`LKED RC0000`, `GO RC0000`, overall SUCCESS,
highest RC0000, without a reported abend.
The operator saved `workarea/m42-real-open/real-open-report.txt`,
but has not supplied its contents for examination.

**Interpretation pending:** this proves the exploratory GO
task completed normally but does not show that an attempted
incompatible QSAM OPEN reached SVC19; `DDVERIFY`/RDJFCB
may instead have rejected the SYSOUT DD before OPEN.
The report must establish the program's actual markers
and any IEC/IEF messages.
It might issue a real QSAM OPEN against an incompatible DD and
produce an **S013 system abend**. Never mark an expected abend as a
successful regression or claim that a returned zero proves OPEN
was reached. Intended only for controlled TK5 development testing.

The GO JCL is generated from the ordinary PDS-linked BCPLM6 +
BCPLIO candidate, **not** from the synthetic fault-injection
module. It uses a normal FB80 `DD01 DD DATA` control stream
and supplies `DD02 DD SYSOUT=*` even though the compiled BCPL
application calls `FINDINPUT("DD02")`. This should present an
allocated DD with an incompatible intended direction, but how
RDJFCB and OPEN handle the combination on this TK5 release
**must be observed rather than assumed**.

The program emits `M42 BEFORE FIND DD02` before attempting the
FIND. If control returns, it emits either `M42 DD02 RETURNED
ZERO` or `M42 DD02 RETURNED HANDLE`, verifies DD01 selection
and read continuity, conditionally closes the unexpected DD02
handle without reading it, and emits `M42 SURVIVED FIND DD02`.

**Diagnostic interpretations:**
- S013 or another ABEND with DD02 / IEC evidence: an actual
  host OPEN failure may have been reached; record exact code
  and report. Do not call the experiment a regression PASS.
- `M42 DD02 RETURNED ZERO` and GO RC0000: recoverable
  no-stream result. Does **not** by itself establish whether
  RDJFCB or SVC19 rejected the DD.
- `M42 DD02 RETURNED HANDLE`: the allocation/OPEN combination
  was accepted; it did not supply the desired negative test.
- JCL conversion/rejection: the intended allocated-DD condition
  was not achieved; adjust experimental design separately.

Source-only JCL patch validation is available as\n`python3 tools/checks/check-m42-real-open-jcl.py`; it has not\nyet been run.\n\nThe standard builder is `tools/checks/prepare-m42-real-open-jcl.py`;
it builds a separate `RG890R` deck and inserts exactly one
`//DD02 DD SYSOUT=*` allocation. It never submits JCL or changes
any PDS member. It uses `prepare-runtime-pds-regression.py`
with `--test-number 890` solely to generate an assembler/link/GO
deck; no regression 890 is registered.

### Compile source and prepare the dangerous GO deck (without submitting GO)

```sh
cd ~/Source/Repos/BCPL-for-MVS
git pull --ff-only
python3 tools/native/compile-mvs \
  bootstrap-toolchain/probes/m42-real-open/source.bcpl \
  --job-name RG890C --listing light --timeout 180 \
  --output workarea/m42-real-open/generated.s370.asm

BCPL_RUNTIME_PDS=1 \
BCPL_RUNTIME_LIBRARY=DEVOBJ \
BCPL_RUNTIME_CANDIDATE=1 \
BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6 \
python3 tools/checks/prepare-m42-real-open-jcl.py \
  workarea/m42-real-open/generated.s370.asm \
  workarea/m42-real-open/real-open.jcl
```

The `compile-mvs` step **submits the ordinary Cambridge compilation**
job to MVS. The generated exploratory `RG890R` GO deck, which may
abend, remains **unsubmitted** until the separate command below.

Inspect the generated JCL and run **only when ready to
characterize a possible GO-step abend**:

```sh
jobnum=$(
  tools/mvs/submit-jcl --timeout 30 \
    workarea/m42-real-open/real-open.jcl |
    awk '/^JOB [0-9]+$/ {print $2}'
)
printf 'Exploratory JES job: %s\n' "$jobnum"
tools/mvs/job-summary "$jobnum"
tools/mvs/dump-report-for-job "$jobnum" \
  > workarea/m42-real-open/real-open-report.txt
```

Preserve JCL CCs, IEF/IEC messages, abend and program records.
Never paste the full JOB card to chat if it contains credentials.
The task uses one named input DD and one potentially incompatible
DD; it does not modify system DASD or broaden concurrency.
Full native regression remains deferred; installed OBJ/DEVOBJ
members remain unchanged.
