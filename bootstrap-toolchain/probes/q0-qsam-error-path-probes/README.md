# Milestone QSAM — March Q.0 DD and incompatible-OPEN reconnaissance

## Recorded DD inquiry: JOB 2170

The already-tracked `dd-inquiry.asm` / `make-jobs.py` experiment **PASSED** on 20 October 2026. `RDJFCB` returned R15=0 for allocated DD `QPRES` and R15=4 for absent `QMISS`, without opening either. The assembler, link-edit and GO steps all returned RC=0000. See [JOB 2170 evidence](../../../packaging/qsam-q0-dd-inquiry-evidence-20261020.md).

## Prepared experiment: deliberately incompatible OPEN

**Status: PREPARED ONLY — NOT RUN ON MVS. An MVS abend is possible and is an expected kind of observation, NOT proof of recoverable OPEN.**

An isolated disposable job `QS0BADOP` will attempt to open a temporary OUTPUT data set using JCL `DCB=(RECFM=FB,LRECL=80,BLKSIZE=801)`. For FB data, 801 is not a multiple of 80, so this deliberately violates the QSAM blocking relationship. An abend such as S013-20 is plausible; other outcomes (JCL rejection, another abend, or ordinary return) must be recorded exactly as observed. The job does not write a production PDS and does not read or modify any existing dataset.

The IFOX test module contains one `OPEN` on `QBAD`, with no `GET`, `PUT`, or `CLOSE` on that DCB. If OPEN returns, GO ends RC=12 to mark the result **unexpected/needs inspection**; it does not assume that OPEN succeeded, and it avoids operating on a potentially partially opened DCB. An MVS abend is a negative-experiment result, not a successful program return. Runtime behavior may differ from later IBM systems and must be determined using the actual JES report.

### Step A — safe static check

```sh
PROBE=bootstrap-toolchain/probes/q0-qsam-error-path-probes
python3 "$PROBE/make-open-incompatible.py" --check
```

### Step B — explicit operator opt-in

Only after reviewing this README and confirming the disposable environment, generate and inspect the deck:

```sh
python3 "$PROBE/make-open-incompatible.py" --allow-open-abend
less workarea/qsam-q0-error-path/q0-open-incompatible.jcl
```

### Step C — submit *only the disposable test job*

```sh
bash tools/mvs/submit-jcl workarea/qsam-q0-error-path/q0-open-incompatible.jcl
# Then, using the returned job number:
tools/mvs/dump-report-for-job JOBNUMBER
```

Retain the full JES log, including IEC messages, completion/abend code and unit/volume assignment, whether or not GO actually runs. **Do not label an expected abend as RC=0000.** Unexpected RC=12 is also not a PASS. No Q.0 or Q.1 acceptance can be based solely on this deliberately failing experiment. Do not run this job in the clean-room baseline or on a production system.

Generated JCL lives in ignored `workarea/` with mode 0600 and may contain locally configured JOB-card credentials. Never commit it.

**Design boundary:** BCPLQSAM should reject obvious incompatible requests where it can do so reliably; it cannot promise to turn every MVS OPEN/GET/PUT/CLOSE abend into a negative API status. This experiment characterizes the boundary; it does not implement a recovery exit or approve the pending R.0 finalizer design.

**March Q.0 remains open; Q.1 has not started.**