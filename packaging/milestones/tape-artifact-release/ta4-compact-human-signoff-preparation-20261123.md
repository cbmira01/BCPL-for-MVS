# TA.4 — compact human sign-off of the preserved 12-case MRREGRES evidence

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.4 — MR10 Kit Compiler Distribution and Verification  
**Status:** IMPLEMENTED AND LOCALLY TESTED; human signature **NOT YET RECEIVED**  
**Date:** 23 November 2026 EST

## Why a compact option is appropriate

The accepted predecessor MVS **JOB 9369** contains 63/63 successful
`MRREGRES` steps and twelve automated `TEST:`/`EXP:`/`RP:`/`CODE=0`
semantic passes. Its original private sealed record is under
`workarea/ta2-rc3-installed-mr10-continuation/20261123T000015Z-32502`.
The completed RC4 TA.4 interpreter rebuild and 11+17 demonstrations are
independently recorded in
[the TA.4 technical acceptance checkpoint](ta4-rc4-mvs-technical-verification-checkpoint-20261123.md).

The approved human acceptance contract requires **twelve distinct human
PASS/FAIL verdicts**, an identified reviewer, and explicit final uppercase
`SIGN` against *visually inspected* adjacent expected and actual
records, not merely an automatic green status.

The original `ta2-rc3-human-review --signoff` required **14 prompts**
(twelve verdicts, reviewer identifier, final `SIGN`).
This change retains that legacy operation and adds
`--compact-signoff`, which displays all twelve MVS case records
but collects the same required decisions and signature in **one terminal
input**.

## Review procedure

Run the source-controlled `ta2-rc3-human-review --compact-signoff` from
the repository root. It first recomputes the original saved MVS provenance,
SHA-256 seal, accepted job/step contract, source selection and all twelve
semantic comparisons, and authenticates the original `BC0003` tape hash.
It has **no** MVS submission, tape operation, PDS modification or
historical job replay.

The script prints the twelve ordered `R01`–`R12` cases in full,
including each `TEST:`, literal `EXP:`, actual `RP:` and
`ICINT CODE=0`, then requests a single line:

```text
12 P/F verdicts, reviewer identifier, then uppercase SIGN:
```

The answer contains exactly **twelve** consecutive letters `P` or `F`
(in `R01`–`R12` order), a space, the **reviewer's own identifier**,
another space, and the exact token **`SIGN`**. For example, if
the reviewer has individually examined all twelve cases and judges
every case correct, `PPPPPPPPPPPP cm SIGN` represents their twelve
separate PASS decisions and identified sign-off. The script **never
provides or defaults** the verdicts, identifier or signature.

A missing, malformed or lowercase final token is rejected without
a signed receipt. Any human `F` is preserved in the signed receipt
and **blocks release acceptance**. Successful review creates a new
sealed `workarea/ta2-rc3-human-review/review-*/` directory with twelve
explicit `human_verdict` values, `reviewer_identifier`,
`human_signature_token: SIGN`, `signoff_input_mode: COMPACT_ONE_LINE`,
original MVS job and image identity. The original JOB 9369 seal remains
unmodified. `publication_authorized` remains `false` even on PASS.

## Implementation and testing

- Updated `packaging/distribution/create-tape/scripts/ta2-rc3-human-review`:
  optional one-response mode without changing the default read-only review
  or the legacy per-case signed review.
- Extended `packaging/distribution/create-tape/tests/test_ta2_rc3_human_review.py`:
  tests for single-response signed PASS, signed FAIL, invalid/missing
  `SIGN`, missing/extra verdicts, case order, review display before
  input, and refusal to use compact mode without a signature.
- The new compact decision helper passed **7 local isolated tests**
  in the assistant's separate project workspace, including positive
  and failure/refusal cases. GitHub content was checked for the
  expected integration points. This is **not** a claim that an actual
  human has signed or that the private JOB 9369 evidence was opened
  in the assistant workspace.

## Closure boundary

Once an actual human completes the review and reports the resulting
sealed receipt, inspect the receipt's status and signature against the
accepted milestone before proposing **TA.4 formal closure**.
Do not prematurely close TA.4 based on this source commit alone.
TA.5, TA.7, TA.8 and publication remain independent release gates.

## 23 November — correction after first compact review refusal

The initial invocation refused before the signature prompt because the
old RC3 producer `plan()` demanded exactly three release registry
candidates, while the accepted registry now includes RC4. Current RC3
and RC4 manifest digests match their reservations. The historical
reviewer is now decoupled from that producer restriction without relaxing
the original sealed MVS/JES/semantic/BC0003 hash checks. See the
[TA.4 RC3 registry correction](ta4-rc3-signed-review-historical-registry-correction-20261123.md).
The signed review must still be performed; **no receipt was forged**.
