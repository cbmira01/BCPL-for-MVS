# TA.2 — Private BC0002 write: MVS checks passed; HETMAP physical-map review pending

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.2 — Manifest-Driven Tape Producer  
**Date:** 21 November 2026 EST / 21 November 2026 UTC  
**State:** **One owner-authorized stateful candidate write attempted; no retry; post-write physical tape-map verification pending.**

## Owner-reported original operation

The owner executed `packaging/distribution/create-tape/scripts/ta2-rc2-produce-once --run` from `main` after the specifically committed third-attempt authorization. Reported terminal output:

```text
TA.2 RC2 WRITE PREFLIGHT PASS: 21 accepted inputs, 21 tape aliases absent; 5 existing images checked. LISTDS JOB 9338.
Initialize and mount ONE NEW private BC0002 AWS image on 0480? [y/N]: y
BC0002 initialized and mounted at 0480. Next confirmation submits exactly one 21-step job.
Submit the ONE 21-step TA2RC2WR MVS job to BC0002? [y/N]: y
TA.2 RC2 AWS WRITE HALTED: HETMAP file number/block count missing, repeated or out of order
NO RETRY; preserve media, mount, attempt marker and evidence: workarea/ta2-rc2-production-operations/20261121T231644Z-27163
TA.2 RC2 private AWS production RC=2
```

**Source-order finding:** The committed `--run` code reaches the error text only **after** a fresh HETINIT, mount, authenticated `TA2RC2WR` submission, `submit_and_wait(max_rc=0)`, saved original `write-summary.txt` and `write-report.txt`, and `validate_job` requiring **all 21 ordered IEBGENER/IEBCOPY and original MVS `IEF142I` step records at RC=0000**. The independent standard-label reviewer also finished without refusal (expected 1 VOL1 and 21 HDR1/HDR2/EOF1/EOF2 groups). The last failing check is HETMAP `-f` physical file number/block counts; its parser already found **64 file headers** before refusing a per-file number or count.

This is a **qualified code-path interpretation** of the actual owner-reported run, **not yet independent inspection** of the private original JES/HETMAP bytes. Neither the actual MVS TA2RC2WR job number nor the AWS SHA-256 has yet been reported in a verified post-write receipt. No restore, clean installation, binary fidelity acceptance or publication is claimed.

**Permanent state:** The original `BC0002` AWS under `mvs-state/tape/bcpl-0.1.0-rc2-BC0002.aws`, drive mount and one-shot `workarea/ta2-rc2-production-operations/BC0002-one-shot-attempt.json` must be preserved. **Do not rerun the producer, remount, rewind, initialize, rename, overwrite or unmount this tape** pending evidence review.

## Consolidated read-only MVS/HETMAP forensic tool

The new tracked `scripts/ta2-rc2-postwrite-audit` does **not** issue any tape positioning, mount, initialize, JCL submission or MVS state change. It:

- Replays SHA256SUMS for the exact original operation `20261121T231644Z-27163` and requires the observed exact refusal reason and original JES/HETMAP files;
- Checks the permanent no-retry marker, candidate identity and image presence, hashes the existing AWS bytes without changing them;
- Independently checks all 21 `TA2RC2WR` summary entries and actual `IEF142I` records for RC=0000;
- Performs three bounded read-only Hercules HETMAP displays (`-f`, `-l`, `-a`) for this *existing* image, retains the raw reports, and compares current `-f`/`-l` reports with the sealed saved originals;
- Preserves actual file numbers and per-file `Blocks` values, diagnoses zero/one-based numbering, missing or duplicate counts, and individual 21-dataset 3-file-layout differences **without renumbering or claiming acceptance**;
- Records an SHA256SUMS-sealed JSON report under ignored `workarea/ta2-rc2-postwrite-audit/` and prints only the MVS job, labels, candidate hash, bounded map diagnosis and evidence path.

**Assistant-workspace verification:** the exact Git-controlled script and tests passed **12/12 executable offline regression cases** and Python AST validation, including tampered source receipts, 21-step JES mismatch, layout anomalies, saved/live HETMAP drift, marker/image identity, and no-write audit invocation. Git blob content was compared to local tested bytes before commit. These tests are not themselves MVS tape acceptance.

## Next gate

Run the **single read-only post-write audit** and use its original JES report, HETMAP file numbers/block counts and immutable AWS SHA-256 to determine whether the physical-map failure reflects incorrect assumptions in the independent parser, or an actual tape-format defect. Fix parsers only after observing those real values. Keep the existing AWS and no-retry marker; continue TA.2 toward independent readback only when the original candidate can be accepted on evidence. **TA.2 — Manifest-Driven Tape Producer remains IN PROGRESS.**
