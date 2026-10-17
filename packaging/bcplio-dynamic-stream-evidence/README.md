# BCPLIO dynamic streams — historical evidence

This directory collects **selected contemporaneous verification metadata** from
the ignored local `workarea/` after the M0–M5.5 milestone was accepted.
The authoritative narrative is
[BCPLIO dynamic stream final acceptance](../../docs/Milestone-BCPLIO-dynamic-stream-final-acceptance.md).
The [runtime contract](../../docs/BCPLIO-dynamic-runtime-contract.md)
and the historical march documents remain in `docs/`.

## Organization

| Directory | Evidence | Limitation |
|---|---|---|
| `m5.1/` | Printer-class route result/checkpoint; FB132 sequential dataset verifier preparation manifest | Preparation metadata alone does not prove JOB 8185 executed |
| `m5.2/` | Negative padding-byte verifier preparation manifest | Must be interpreted with the accepted JOB 8186 result |
| `m5.5/` | Fresh regression verification receipt; matched checkpoint and job/step TSV where available | The later duplicate regression overwrote normal transcript and some case logs |
| `historical/m5.1/` | First-stage FB132 verification preparation metadata | Superseded v1 verifier was **not** suitable for submission; corrected v2 is accepted |
| `historical/m5.5/` | Original pre-parser-fix M5.5 beginning checkpoint | **Rejected** checkpoint, not the accepted run's start |

The final accepted run was **145 PASS, 0 FAIL, one expected SKIP 083**,
verified for the DEVOBJ/BCPLM6 candidate; it did **not** promote that
candidate to production. Physical QSAM records were independently examined
under JOB 8185; do not confuse this with complete JES2 spool-byte proof.

The M5.5 receipt includes SHA-256 digests of the original runner transcript
and M4.4 job manifest. Only an audit TSV matching the receipt's recorded
digest is copied; a later overwritten TSV is deliberately excluded.
The ordinary `m55-full-panel.log` is **not** copied, because a second
run truncated it. The earlier operator paste is not assumed byte-identical
unless its digest matches the receipt.

## Preserving local evidence

From the repository root:

```sh
git pull --ff-only
python3 tools/checks/archive-bcplio-evidence.py
python3 tools/checks/archive-bcplio-evidence.py --apply
git status --short
```

This helper does not run MVS jobs, delete original files, or copy private
JCL, JES/printer captures, per-case logs, compiled binaries or scratch
assembler. It lists any other Markdown notes for **manual review** rather
than automatically treating them as authoritative documentation.

Before an existing checksum manifest is extended, the helper verifies every\npreviously listed file. It refuses to bless changed evidence as a new hash.\n\nReview the resulting JSON/TSV for confidential content and correctness
before `git add` / `git commit`. `sha256sums.txt` records the
archived contents, not the identity of the original accepted JES output.
Do not empty `workarea/` until this review is complete.
