# Milestone QSAM — Q.0 non-opening DD allocation inquiry

**Status: PREPARED; NOT YET RUN ON MVS.** This is an isolated assembler reconnaissance probe, not a BCPLQSAM implementation and not evidence that arbitrary QSAM OPEN errors are recoverable.

The experiment follows the RDJFCB method used by BCPLIO.DDVERIFY (bootstrap-toolchain/asm/bcplio.asm): an unopened DCB with a JFCB exit list and a fullword-aligned, 176-byte JFCB area. In the period MVS interface, a single allocated DD should produce R15=0, while an absent DD should produce R15=4. This experiment tests those results in TK5 instead of assuming them.

| Case | JCL DD | Operation | Expected RDJFCB R15 |
| --- | --- | --- | --- |
| Positive control | QPRES, temporary DASD | RDJFCB only | 0 |
| Missing allocation | QMISS, intentionally no DD | RDJFCB only | 4 |

**Safety:** QMISS is never passed to OPEN, GET, PUT or CLOSE. No PDS objects are written. The only OPEN/PUT/CLOSE serves QOUT to emit the marker if both inquiries pass. Do not add a missing-DD OPEN to this probe. Test incompatible OPEN separately after reviewing abend and recovery risks.

## Run from repository root

    PROBE=bootstrap-toolchain/probes/q0-qsam-error-path-probes
    python3 "$PROBE/make-jobs.py" --check
    python3 "$PROBE/make-jobs.py"
    bash tools/mvs/submit-jcl workarea/qsam-q0-error-path/q0-dd-inquiry.jcl

Then use the reported JOBNUMBER:

    tools/mvs/job-summary JOBNUMBER --max-rc 0
    tools/mvs/dump-report-for-job JOBNUMBER

Expected three steps (ASM, LKED, GO), each RC=0000, plus the QOUT record:

    Q0 DD RDJFCB PRESENT=0 MISSING=4 PASS

If the probe fails or abends, retain the full JES listing. The probe's RC=8 means one of the expected return-code checks failed; use the JES messages for initial diagnosis. Generated JCL is written mode 0600 in ignored workarea/ and may contain local job-card credentials. Never commit generated decks.

Historical reference: IBM, *OS/VS2 MVS System Programming Library: Data Management*, section “RDJFCB—Read a Job File Control Block”, which describes R15=0 for success and R15=4 for absent DD. The accepted BCPLIO precedent maps nonzero RDJFCB outcomes to its private “not available” indication; this probe requires 4 specifically to distinguish the missing-DD case. Production QS_ERR_NO_DD translation must not treat **every** nonzero RDJFCB code as proof of an absent DD.

**Q.0 remains open; Q.1 has not started.**
