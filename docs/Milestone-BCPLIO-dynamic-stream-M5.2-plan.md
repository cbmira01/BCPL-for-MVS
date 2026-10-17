# Milestone — BCPLIO dynamic streams: M5.2 negative record verifier

Status: **M5.2 STAGED FOR OFFLINE AND ONE CONTROLLED MVS NEGATIVE TEST (2026-10-17); no M5.2 MVS job has yet run.**
Prerequisites: [M5.1 closure](Milestone-BCPLIO-dynamic-stream-M5.1-plan.md), accepted JOB 8184 class-separated route, and JOB 8185 positive FB132 dataset readback.

## Purpose and scope

Test the **verifier**, not BCPLIO. Positive evidence alone cannot show
that our checker rejects a bad record. M5.2 should be small: use the
existing proven verifier and its two independently allocated REPORT and
REPORT2 sequential QSAM datasets. No BCPL program changes, compiler
changes, runtime changes, managed PDS updates, SYSOUT spool internals or
full native regression run.

The checker must reliably distinguish correct FB132 data from:
a corrupted meaningful byte, altered X'40' trailing padding, swapped
destinations, missing/extra/duplicate records, bad record order and wrong
record length. The offline matrix checks the modeled full-byte sequences;
the existing printer-route checker already has offline swapped-output,
missing-record and cross-contamination cases. The one new **real MVS**
negative-control experiment concentrates on the padding byte, which a
human-readable printer report would lose.

## First negative-control job: M52PAD

Reproduce the accepted M5.1.2 v2 JOB 8185 positive JCL **byte-for-byte**,
except for the JOB name (`M52PAD`) and a single instruction inserted
into the independent VCHK verifier after OPEN and before the first GET:

```asm
         MVI   EXP11+131,C'X'
```

The original first REPORT expectation is
`EXP11 DC CL132'BCPL REPORT A'`. Its byte at offset +131 is
EBCDIC blank X'40' (the 132nd byte). The new MVI changes that **expected**
byte to EBCDIC `X`, X'E7'. It does **not** modify the actual
record, the BCPL executable, any DD assignment, the comparator's
full-length `CLC BUF1(132),EXP11` instruction, EOF logic or
return paths. The same physical dataset readback that passed in JOB 8185
must now reject the deliberately wrong comparison.

The explicit *expected* step result is:

| Step | Expected RC |
|---|---:|
| ASMAP | 0000 |
| LKED | 0000 |
| GO | 0000 |
| VASM | 0000 |
| VLINK | 0000 |
| VCHK | **0012** |

This job's overall job-summary will understandably report **FAILURE**:
VCHK's RC0012 is the intended positive result of this **negative test**.
It is accepted only if the five earlier steps RC0000, VCHK RC0012, and
there are no abends or JCL errors. Unexpected RC, missing steps or an
abend is a failed experiment, not an acceptable negative.

## Offline preparation and review (non-submitting)

```sh
cd ~/Source/Repos/BCPL-for-MVS
git pull --ff-only
python3 tools/checks/test-dd-attribution.py
python3 tools/checks/test-m52-padding-negative.py
python3 tools/checks/m52-padding-negative.py prepare
python3 tools/checks/m52-padding-negative.py review
```

The generator first validates the *original* M5.1.2 positive
`m51-fb132-dataset-v2.jcl`, independent verifier ASM, and
manifest using the already accepted M5.1.2 strict source/hash checker.
It refuses missing inputs, drifted data, or existing M5.2 outputs,
and writes only ignored workarea artifacts:

- `workarea/native-regression/124-dynamic-dd-selected-output/m52-padding-negative.jcl`
- `workarea/native-regression/124-dynamic-dd-selected-output/m52-padding-negative.asm`
- `workarea/native-regression/124-dynamic-dd-selected-output/m52-padding-negative.json`

The non-submitting review regenerates the exact negative deck and ASM
and compares their SHA256 digests with manifest values. No overwrite,
no JES submission and no source/PDS mutation.

The offline record matrix illustrates missing/extra, reordered, swapped,
payload-damaged, pad-damaged and wrong-length cases as **different from**
the 132-byte fixture. This is not a claim that each was independently
run against VCHK under MVS. The existing class A/Z checker negative
cases similarly establish printer *routing* rejections, not physical
QSAM record corruption.

## One MVS run (only after offline PASS)

```sh
tools/mvs/submit-jcl \
  workarea/native-regression/124-dynamic-dd-selected-output/m52-padding-negative.jcl
tools/mvs/job-summary JOB_NUMBER
```

Save the job number, the six step codes and any diagnostics. **Never
interpret an isolated VCHK RC0012 as normal BCPL execution failure**:
here that outcome is deliberately demanded by the verifier test.

**M5.2 gate exit:** real JOB M52PAD VCHK RC0012 with all other steps
RC0000, plus negative offline tests PASS and an evidence note.
Do not begin M5.3 or rerun the entire native panel before reviewing
this evidence. The combined SYSOUT text tool need not preserve JES2
internal spool records; M5.1's QSAM responsibility boundary stands.
