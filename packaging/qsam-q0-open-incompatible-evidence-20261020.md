# Milestone QSAM — Q.0 incompatible OPEN negative-test evidence (2026-10-20)

**March:** Q.0 — Reconnaissance & contract (open). **Test:** standalone,
intentionally invalid MVS 3.8J/TK5 QSAM OPEN. Not a BCPLQSAM module.

## JOB 2171 — QS0BADOP

The owner submitted generated job
`workarea/qsam-q0-error-path/q0-open-incompatible.jcl`, from the
tracked `bootstrap-toolchain/probes/q0-qsam-error-path-probes/`
source, and supplied the full JES, assembler, link-editor and SYSUDUMP
report. The JOB completed 20 October 2026 with these observations:

| Step | Program | Observed outcome |
| --- | --- | --- |
| ASM | IFOX00 | RC=0000; no source errors |
| LKED | IEWL | RC=0000 |
| GO | Q0BADOP | **ABEND S013 U0000 (S013-20)** |

JCL assigned `//QBAD DD DSN=&&Q0BAD,DISP=(NEW,DELETE),UNIT=SYSDA,`
with `DCB=(RECFM=FB,LRECL=80,BLKSIZE=801)`. This is an invalid FB
blocking relationship: 801 is not a multiple of 80. MVS allocated the
temporary data set on WORK01 (device 0290).

Verbatim diagnostic lines from the owner-provided JES report:

```text
IEC141I 013-20,IGG0191A,QS0BADOP,GO,QBAD,290,WORK01,
IEC141I SYS26293.T134748.RA000.QS0BADOP.Q0BAD
IEF450I QS0BADOP GO - ABEND S013 U0000 - TIME=13.47.48
```

The IFOX expansion shows `OPEN (QDCB,(OUTPUT))` issued SVC 19.
The test deliberately contained no QSAM PUT/GET/CLOSE on `QBAD`.
The S013 occurred during OPEN, so the test-only post-OPEN diagnostic
`RC=12` path was not reached. JES deleted the temporary `Q0BAD` data
set. This is **a successful negative experiment, not RC=0000**.

## Narrow conclusion

For this exact FB80/801 case on the tested MVS/TK5 configuration,
OPEN did **not** return a recoverable ordinary status to the caller;
instead the GO step was terminated by system abend S013-20.
This proves neither that *every* malformed DCB causes an abend nor
that *every* S013 subcode has this cause. It does demonstrate why
`BCPLQSAM` must reject inconsistent input where reliable pre-OPEN
attributes are available, and must not promise to turn all OPEN/GET/
PUT/CLOSE system abends into the public `QS_ERR_OPEN` return code.

## Follow-up

The separate [geometry precheck](../bootstrap-toolchain/probes/q0-qsam-followup-probes/README.md)
checks actual `RDJFCB` fields **without opening the invalid DD**.
Until that job executes, the proposed MVS 3.8 JFCB field-offset
assumptions remain unverified. The approved BCPLQSAM public interface
and Q.0 scope remain unchanged. **Q.0 open; Q.1 unstarted.**