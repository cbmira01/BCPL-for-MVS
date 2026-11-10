# DSPAL batch population — bounded MVS read-back acceptance

**Project:** BCPL for MVS 3.8 Reconstruction  
**Date:** 9 November 2026  
**Status:** Live MVS batch-population tests completed with terminal-blank-record qualifications; subsequent whole-rebuild and independent full-regression acceptance are documented in the [clean-room improvement closure](clean-room-batch-reconstruction-closure-20261109.md)  
**Git source authority:** GitHub `main`. **Execution authority:** JES, IEBGENER and actual MVS PDS contents.

## Scope and constraints

`dspal populate --batch` groups IEBGENER member writes into bounded, per-PDS
jobs, while the original one-job-per-member method remains the default.
The reconstruction driver does **not** enable batching by default; `--batch-populate` is an explicit opt-in.

The initial live acceptance targets were `DIST_DOCS` (seven Git-backed
documentation members) and `EXT_SOURCE` (three BCPL declaration headers,
including lines beginning with `//`). Both were tested against the existing
MVS 3.8J installation without rebuilding or deleting object datasets.

The new `tools/datasets/verify-populate-batch` command uses the same
manifest mappings and input validation as `dspal populate`. It neither
creates datasets nor purges them. A missing or incompatible target PDS blocks
the batch. Nothing is committed or tagged as acceptance evidence automatically.

## Host-only checks

From a clean GitHub `main` checkout:

```bash
set +e
set +u
set +o pipefail

python3 -B -m unittest discover -s tools/checks \
    -p 'test_dspal_batch_live_acceptance.py' -v
echo "Acceptance harness unit RC=$?"

tools/datasets/verify-populate-batch --check
echo "DIST_DOCS plan RC=$?"
```

The `--check` path performs Git/manifest validation only: **no JES submission**.

## Authorized controlled live test

The operator must ensure unrelated MVS submissions are stopped and
approve the exact target dataset reported by `--check`. For the standard
HERC02 configuration:

```bash
set +e
set +u
set +o pipefail

tools/datasets/verify-populate-batch \
    --run \
    --target DIST_DOCS \
    --approve-dsn HERC02.BCPL.DIST.DOCS
echo "DIST_DOCS live batch read-back RC=$?"
```

`--run` installs exactly the selected manifest-mapped members using the
opt-in batch operation, then runs a separate MVS read-back of each member via
`dspal get`. The batch's `job-summary` must show every expected IEBGENER
step with RC=0000. Read-back data must match the prepared input after the
existing FB/80 padding-normalization convention, verified with SHA-256 and
exact text equality. A missing, failed, bypassed or mismatched member blocks
acceptance. No fallback or continuation is silently attempted.

The script writes a `summary.json`, batch output and any failure diagnostics
under `workarea/dspal-batch-acceptance/<timestamp>-<pid>/`. This directory is
disposable diagnostic evidence, not an authoritative Git record. Preserve the
actual JES receipt and review it before claiming live acceptance.

**Comparison limitation:** `dspal get` removes FB/80 right padding; the test
checks the canonical recovered text, **not byte-for-byte EBCDIC identity**.
Sources with initial or terminal blank records are refused because this read
path cannot verify those boundaries.

## Recorded live MVS results — 9 November 2026

Both tests ran at GitHub HEAD `aa51bad16599ca4c9165775223bc694bd03fdd29`:

| Target | JES job | IEBGENER steps | Member read-back | Batch duration |
| --- | --- | --- | --- | --- |
| `DIST_DOCS` | 3136 | 7/7 RC=0000 | 7/7 canonical texts matched | 8.4 s |
| `EXT_SOURCE` | 3145 | 3/3 RC=0000 | 3/3 canonical texts matched | 8.0 s |

Workstation evidence directories:
- `workarea/dspal-batch-acceptance/20261109T234013Z-64566`
- `workarea/dspal-batch-acceptance/20261109T234847Z-64881`

These are operator-reported MVS execution results, not evidence that has
been independently replayed here. No release or reconstruction acceptance
is implied.

## Split `MR10_TESTS` population — MVS verified with qualification

The manifest currently maps **61** Git-tracked members into
`HERC02.BCPL.MR10KIT.TESTS`. The opt-in batch planner should produce
**two** JES jobs (60 steps plus 1 step), subject to its additional 4,000-card
ceiling. The acceptance tool now checks the exact planned job counts,
ordered/distinct JES batch receipts, and every recoverable member text.

**Qualification:** Four members (`T01ECHO`, `T01TEXT`, `T04MOD1`,
`T04MOD2`) each have one terminal empty FB/80 record in Git sources.
The current `dspal get` parser discards trailing blank records, so it
cannot verify their terminal-record counts. For `MR10_TESTS` **only**,
the acceptance tool compares canonical recoverable text and records
`qualified: true` with those four unverifiable records in `summary.json`.
It must not be presented as full raw-record fidelity.
Other acceptance targets continue to reject such source records.

The controlled 10 November 2026 UTC live test, using GitHub HEAD
`b31c9a4305ef6014afcd4bd9d0fe7b00107f56d3`, returned:

| JES job | Steps | Measured batch execution | Result |
| --- | ---: | ---: | --- |
| 3150 | 60 | 10.5 s | All 60 IEBGENER steps verified |
| 3151 | 1 | 8.2 s | One IEBGENER step verified |
| **Combined** | **61** | **18.7 s** | **61/61 canonical texts matched, qualified** |

The operator's final `MR10_TESTS batch acceptance RC=0` was recorded with
evidence at `workarea/dspal-batch-acceptance/20261110T000314Z-65156`.
This verifies real-MVS split behavior, not raw EBCDIC identity or the four
terminal record counts. Total observed canonical-text verification across
`DIST_DOCS`, `EXT_SOURCE`, and `MR10_TESTS` is **71/71**.

Read-only planning (no JES):

```bash
set +e
set +u
set +o pipefail

tools/datasets/verify-populate-batch --check --target MR10_TESTS
echo "MR10_TESTS preflight RC=$?"
```

After separate operator approval of the exact PDS write, keep unrelated
JES submissions stopped and execute:

```bash
set +e
set +u
set +o pipefail

tools/datasets/verify-populate-batch \
    --run --target MR10_TESTS \
    --approve-dsn HERC02.BCPL.MR10KIT.TESTS
echo "MR10_TESTS split-batch acceptance RC=$?"
```

This overwrites the 61 mapped PDS members; it does not purge MVS datasets.
Review both JES jobs, individual step codes, 61 canonical read-back comparisons
and the explicit qualification on any repeat run.
Do not infer authorization for `BOOT_JCL`, native objects, full
clean-room reconstruction, or regressions.

## Acceptance gate

MVS population acceptance is now established for the tested member classes,
subject to the four terminal-record qualifications. The reconstruction driver
offers `--batch-populate` only as an **explicit opt-in** for both population
passes; its default is unchanged. The later [owner-directed scoped closure](clean-room-batch-reconstruction-closure-20261109.md)
records a successful **12m46s** opt-in reconstruction and separate full
six-suite regression (**194 PASS, 0 FAIL, one expected SKIP**).
This closes the batch-population performance improvement with its
documented JES/evidence qualifications; it does **not** make batching the
default. A Git commit alone never authorizes destructive MVS operations.
