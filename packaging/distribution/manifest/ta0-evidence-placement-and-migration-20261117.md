# TA.0 — Private evidence placement and migration correction (17 November 2026)

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone / march:** Tape artifact release / **TA.0 — Release Architecture, Inventory, and Manifest**  
**Status:** Location policy and migration implemented and tested; WSL relocation and the next live MVS executable-use run not yet observed. **TA.0 remains IN PROGRESS.**

## Correct storage policy

The earlier instructions placed private TA.0 collection output at
`$HOME/ta0-mvs-evidence-20261117`. That was an operational error. The
repository already has an ignored `workarea/`, with its own committed
`.gitignore` protecting *all* descendants. Keeping evidence outside Git did
not require creating a separate directory in the user's home.

**Effective convention for all current TA.0 tools:**

- `reporoot/workarea/ta0-mvs-evidence-20261117/` — private reports, JES
  printer windows, checksum receipts, and decoded FB80 readback artifacts.
- `reporoot/mvs-state/` — machine/Hercules state and device output, **not**
  the destination for these separate tape-release evidence receipts.
- `reporoot/packaging/distribution/manifest/` — tracked design, selected
  member inventories, qualified evidence summaries and test code; never raw
  credential-bearing JES listings or binary evidence.

`tools/distribution/ta0_evidence_paths.py` is the shared fail-closed path
policy. It requires an existing, non-symlinked repository `workarea/` and a
real child directory below it; rejects absolute paths elsewhere (including
`$HOME` and tracked `packaging/`), lexical `..` traversal, symlinks in every
component and attempts to reuse output directories. The current collection,
readback, recovery, decode, IEHLIST review and executable-use scripts call the
same policy. Unit-test sandboxes also live under ignored `workarea/`.

## One-time migration

`tools/distribution/relocate-ta0-evidence.py` moves the existing, exactly
named home directory **as one directory tree** to the corresponding path under
`reporoot/workarea/`. The move is allowed only if the destination does not
already exist. Preflight requires the previously observed `SHA256SUMS`,
`MR10_LOAD` LISTDS inventory/DCB files, and the pinned JOB 9060 pilot and
directory-review receipts. It recursively refuses symlinks, non-regular files
and hardlinked files. The deterministic SHA-256 inventory of all file paths,
sizes and bytes is compared immediately after the move. The original JES
files are not opened for modification and are not printed to the console.

A same-filesystem `os.rename` is used, preserving file bytes and names;
there is **no** copy-and-delete fallback or overwriting merge. On a
cross-filesystem move error or conflicting destination, the operation refuses
rather than risking incomplete migration. Re-invoking after a successful
migration verifies the already-local files and performs no further move.
Existing report/receipt SHA-256 values must remain unchanged; the original
source directory should no longer exist after success.

The migration is **operator-local**, not remotely executed from this ChatGPT
workspace. The operator invokes it as the preflight of the next MVS-facing
`ICINT19` executable-use pilot, with all pilot evidence paths under
`workarea/`. No MVS job is submitted by the migration itself.

## Exclusions and verification

This does **not** move the preexisting `q0-*` home experiments or the
`bcpl-mvs-state` directory. Those were not created by this TA.0 flow;
relocating an active Hercules state mount without understanding its binding
configuration risks damaging the running MVS environment. No attempt is made
to guess their destination or delete them.

The **15 local no-MVS path/migration tests** cover traversal, symlinks,
hardlinks, missing receipts, existing destinations, atomic-move failure,
byte-preservation and rerun idempotence. Existing related TA.0 tests have
been adjusted to construct their temporary evidence inside ignored
`workarea/`; no new host test burden is assigned to the operator.

**No TA.0 closure, production tape operation, new MVS dataset write, or
release publication is authorized by this storage correction.**
