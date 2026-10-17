# M4.2.3 — invalid FB block size during QSAM OPEN

**Status: EXECUTED — RG892R JOB 7876 returned a HANDLE,
not an unsuccessful OPEN (2026-10-17).** This was an
exploratory diagnostic, **not a regression**.

The operator submitted the prepared `RG892R` deck as
**JOB 7876** and supplied the complete JES report.
The report shows:

```text
//DD02     DD SYSOUT=*,DCB=(RECFM=FB,LRECL=80,BLKSIZE=81)
IEF237I JES2 ALLOCATED TO DD02
IEW0000     INCLUDE OBJ(BCPLM6)
IEW0000     INCLUDE OBJ(BCPLIO)
M42 BEFORE FIND DD02
M42 DD02 RETURNED HANDLE
M42 SURVIVED FIND DD02
```

IFOX `ASMAP`, IEWL `LKED` and `GO` each
returned RC0000, without a reported IEC OPEN error
or abend. The ordinary installed DEVOBJ BCPLIO
was linked, not a fault-injected private version.

The invalid FB `LRECL=80,BLKSIZE=81` **JCL**
attributes did not cause a rejected `FINDINPUT`.
No GET was attempted on the returned handle;
the effective in-storage DCB BLKSIZE/LRECL and
QSAM record behavior remain unmeasured. A
returning handle shows that the canonical DIFIND
path got past RDJFCB, DALLOC, DQOPEN/SVC19,
and HNEW, and judged the DCB opened.

**Disposition: complete exploratory job, actual failed-OPEN
gate NOT MET.** After three separate DD-only probes
returned valid handles (7874 SYSOUT; 7875 PDS without
member; 7876 malformed FB SYSOUT), further blind
JCL substitutions are not justified. Next inspect
and instrument the effective in-storage DCB at
the precise SVC19 call site, using a disposable
private BCPLIO object, before proposing another
live MVS test. Preserve installed PDS objects and
deferred full regression.


The operator pulled `main` through `19e658a`, then ran
`tools/checks/prepare-m42-fb-open-jcl.py` with the required
DEVOBJ/BCPLM6 candidate environment. The builder reported:

```text
Prepared DEVOBJ runtime PDS regression: workarea/m42-real-open/fb-open.jcl.base
Prepared M4.2.3 INVALID-FB real OPEN exploratory deck:
workarea/m42-real-open/fb-open.jcl
RG892R: DD02 SYSOUT,RECFM=FB,LRECL=80,BLKSIZE=81
INVALID: 81 is not divisible by 80; JES or OPEN may reject
GO job NOT submitted. No installed PDS member changed.
```

**Only preparation has been accepted.** The operator's
output confirms no exploratory GO submission, and neither
JES acceptance nor SVC19 behavior is yet known.


## Why this candidate differs

M4.2.1 JOB 7874 requested `FINDINPUT("DD02")`
where DD02 was `SYSOUT=*`. M4.2.2 JOB 7875
requested `FINDINPUT("DD02")` for the read-only
PDS `SYS1.MACLIB` without a member. Both returned
a nonzero handle; neither produced an unsuccessful OPEN.
Neither read from DD02.

An FB QSAM DCB must have a BLKSIZE divisible by its
LRECL. Documented S013-20 failure conditions include a
violation of this relationship. This new probe uses
`DD02 DD SYSOUT=*,DCB=(RECFM=FB,LRECL=80,BLKSIZE=81)`.
A JCL allocation/conversion error, a failed OPEN/S013,
or a successful OPEN are all possible under actual TK5
behavior. The user must not assume S013-20 will occur.

The GO job is `RG892R`, separate from the earlier
RG890R and RG891R diagnostics. It uses the previously
compiled application assembler:
`workarea/m42-real-open/generated.s370.asm`, produced
by Cambridge compiler JOB 7873; no new compilation is
required. The candidate links normal installed
`DEVOBJ(BCPLM6)` and `DEVOBJ(BCPLIO)`.
The GO BCPL source prints the before/returned-zero/
returned-handle/survived markers. It **does not** GET
from DD02 when a handle is returned.

The generated GO JCL uses only a DD02 SYSOUT allocation;
it neither opens system PDS members nor writes to
user system DASD. The generator validates its exact job
and DD anchors, limits card width, and **does not submit**.
There are no permanent fault injections or modified
installed objects.

## Operator preparation — no GO submission

```sh
cd ~/Source/Repos/BCPL-for-MVS
git pull --ff-only

BCPL_RUNTIME_PDS=1 \
BCPL_RUNTIME_LIBRARY=DEVOBJ \
BCPL_RUNTIME_CANDIDATE=1 \
BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6 \
python3 tools/checks/prepare-m42-fb-open-jcl.py \
  workarea/m42-real-open/generated.s370.asm \
  workarea/m42-real-open/fb-open.jcl
```

This produces the `RG892R` GO deck but does not
send it to the JES reader. Review that the generated
DD02 has the intended invalid RECFM/LRECL/BLKSIZE
combination before submission.

## Submission and evidence collection — separate action

A GO step ABEND (possibly S013-20) is an expected
**diagnostic possibility**, **not** an automatic PASS.
A JCL rejection, normal zero FIND, and normal nonzero
handle have different meanings.

```sh
cd ~/Source/Repos/BCPL-for-MVS

submission=$(tools/mvs/submit-jcl --timeout 30 \
  workarea/m42-real-open/fb-open.jcl)
printf '%s\n' "$submission"
job=$(printf '%s\n' "$submission" |
  awk '/^JOB [0-9]+$/ {print $2; exit}')

tools/mvs/job-summary "$job" || true
tools/mvs/dump-report-for-job "$job" \
  > workarea/m42-real-open/fb-open-report.txt
```

Show the report with an executable `cat` command
when evidence is requested. Redact JOB-card credentials
before sharing, if present. The operator is not asked
to run source-only checks or the full regression suite.

M4.2 stays open until an actual failed SVC19 has been
distinguished from early JCL/RDJFCB failure, or the
owner explicitly accepts a narrower historical contract.
