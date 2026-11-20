# TA.2 — RC2 readback mismatch, preserved MVS evidence and diagnostic gate

**Project:** BCPL for MVS 3.8 Reconstruction  
**March:** TA.2 — Manifest-Driven Tape Producer  
**Date:** 20 November 2026  
**State:** MVS source-PDS population and 15-member directory accepted; **record content not accepted**.

The owner executed the committed, read-only
`rc2-cambsource-record-readback.py --read-only` after completing
MVS source population JOBs **9325** and **9326**. The verifier stopped:

```text
TA.2 RC2 READBACK HALTED: MVS readback differs from frozen normalized source
Inspect retained readback evidence: workarea/ta2-rc2-cambsource-record-readback
```

The available response does **not** identify the failing member, MVS
readback job, exact record, or whether the difference arose in source
population, SYSOUT extraction, EBCDIC conversion, or record normalization.
The saved original private readback files have not been supplied to the
assistant and therefore have not been inspected. The established 15/15
MVS directory result is not overturned merely by this content failure,
but neither does it prove the records are correct.

**Do not rerun the one-time source population or overwrite the saved
readback directory. Do not stage BT0021 to the release candidate.**

The new `rc2-cambsource-diagnose-readback.py --saved-evidence` reads
only the existing `workarea/ta2-rc2-cambsource-record-readback`
receipt and member text, and the frozen historical Git source files.
It checks the recorded SHA-256 values, the candidate and accepted
population-job identities, and selected member order, then prints
only compact MVS evidence diagnostics: member/job, record and line
length counts, first differing record/column, and character-code
values. It does **not** print or alter the source files, run a new
MVS GET, submit JES, allocate a PDS, invoke IEBCOPY or write tape.

Assistant-workspace verification: exact source and test Git blobs
matched the local tested files; **10/10 focused offline tests PASS**,
covering insertion/deletion, altered content, trailing-line-format
differences, and refusal of inconsistent or forged saved receipts.
The actual result remains unresolved until the owner returns the
saved-evidence diagnostic output.

Next, use the specific observed record difference to decide whether
the source PDS needs repair or only the readback/extraction tool
needs correction. Trust actual MVS evidence and perform no new MVS
write without explicit authorization. The original 20 staged inputs,
the 21-dataset `rc2` selection, the `BC0002` reservation, and
the GitHub-only demoted compiler boundary remain unchanged.
**TA.2 remains IN PROGRESS.**
