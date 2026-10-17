# M4.2.1 — Real MVS OPEN exploratory probe

**STATUS: STAGED; NOT EXECUTED.** This is **not** a normal regression.
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

The standard builder is `tools/checks/prepare-m42-real-open-jcl.py`;
it builds a separate `RG890R` deck and inserts exactly one
`//DD02 DD SYSOUT=*` allocation. It never submits JCL or changes
any PDS member. It uses `prepare-runtime-pds-regression.py`
with `--test-number 890` solely to generate an assembler/link/GO
deck; no regression 890 is registered.

### Prepare the deck (non-submitting)

```sh
cd ~/Source/Repos/BCPL-for-MVS
git pull --ff-only
python3 tools/native/compile-mvs \
  native-compiler/probes/m42-real-open/source.bcpl \
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

Inspect the generated JCL and run **only when ready to
characterize a possible GO-step abend**:

```sh
tools/mvs/submit-jcl --timeout 30 \
  workarea/m42-real-open/real-open.jcl
# Use the actual JOB number returned by the previous command:
tools/mvs/job-summary <JOB_NUMBER>
tools/mvs/dump-report-for-job <JOB_NUMBER> \
  > workarea/m42-real-open/real-open-report.txt
```

Preserve JCL CCs, IEF/IEC messages, abend and program records.
Never paste the full JOB card to chat if it contains credentials.
The task uses one named input DD and one potentially incompatible
DD; it does not modify system DASD or broaden concurrency.
Full native regression remains deferred; installed OBJ/DEVOBJ
members remain unchanged.
