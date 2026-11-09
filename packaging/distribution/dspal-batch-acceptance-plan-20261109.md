# DSPAL batch population — bounded MVS read-back acceptance

**Project:** BCPL for MVS 3.8 Reconstruction  
**Date:** 9 November 2026  
**Status:** Host-only tests passed; live MVS acceptance pending  
**Git source authority:** GitHub `main`. **Execution authority:** JES, IEBGENER and actual MVS PDS contents.

## Scope and constraints

`dspal populate --batch` groups IEBGENER member writes into bounded, per-PDS
jobs, while the original one-job-per-member method remains the default.
The reconstruction driver **does not** enable batching.

The first live acceptance target is `DIST_DOCS`: seven Git-backed text members
in the managed `BCPL.DIST.DOCS` PDS (full DSN resolved from the effective HLQ).
This is an actual PDS write, but it does not replace compiled program objects.
An optional later target, `EXT_SOURCE`, covers BCPL declaration headers with
leading `//` lines. It is a separate write and must be separately approved.

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

If the first live run succeeds and the operator approves a second target,
repeat `--check --target EXT_SOURCE` and then `--run --target EXT_SOURCE`
with the exact resolved `--approve-dsn`. Do not infer authorization for
`BOOT_JCL`, native objects, full clean-room reconstruction or regressions.

## Acceptance gate

A passing host-only suite or a successful Git commit does **not** prove batch
operation on MVS. Review the fresh live job IDs, step codes, per-member
read-back results and the saved receipt. Only then decide whether to make
batching the default in `rebuild-from-source`, with a separate decision
and a full clean-room/regression validation.
