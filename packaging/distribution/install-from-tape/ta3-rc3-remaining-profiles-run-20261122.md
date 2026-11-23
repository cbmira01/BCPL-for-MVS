# TA.3 — BC0003 remaining native-only and combined recipient trials

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** **TA.3 — MVS Bootstrap and Installation**, IN PROGRESS  
**Candidate:** `BCPL-0.1.0-rc3`; VOLSER `BC0003`  
**Immutable AWS SHA-256:** `6c54c4df2b75020a698110061c4f8003b09adbe21f738848dcaed3da495d81e1`

## Preflight diagnostic and correction (22 November 2026 EST)

The first owner invocation of `ta3-rc3-remaining-profiles --run`
halted with `TA3N1 essential MVS records missing`.
The initial runner incorrectly required `directory-report.txt`
for accepted TA3N1. The original successful TA3N1 runner's
`inventory` job writes `inventory-report.txt`, not that filename.
This is a runner receipt-naming error, **not** an MVS failure.

The checkpoint requirement now uses the actual
`inventory-report.txt` while preserving all original
SHA-256 seal checks, required receipts, successful MVS job
identities, and semantics checks. An added synthetic sealed
TA3N1 fixture test verifies successful recognition and
tamper refusal; local Python acceptance/refusal checks pass.

**State:** This halt occurred before the new runner created its
stateful marker, issued any new MVS jobs, or allocated any
TA3N2/TA3N3 datasets. The corrected `--run` command can
safely be issued again after `git pull --ff-only`; its
normal preflight and one operator confirmation remain mandatory.
The already accepted TA3N1 and immutable BC0003 remain unchanged.

## Accepted prerequisite

The owner supplied a successful MR10-only `HERC02.BCPL.TA3N1.*`
recipient operation, MVS JOBS 9370–9377; see
[TA.3 N1 operator report](ta3-rc3-n1-operator-result-20261122.md).
The next runner checks the original sealed `TA3N1` receipt and
`go-semantic.json` on the owner's machine, including its saved SHA256SUMS,
before allowing the new stateful operation. It never changes `TA3N1`
or repeats accepted TA.2 stateful operations.

## New recipient profiles

| Tape profile | New isolated prefix | Included logical datasets | New PDSes (including installer) | Expected members |
| --- | --- | --- | ---: | ---: |
| native-only | `HERC02.BCPL.TA3N2` | `BT0002`, `BT0003`, `BT0013`–`BT0021` | 11 | 67 |
| combined | `HERC02.BCPL.TA3N3` | `BT0002`, `BT0003`–`BT0021` | 20 | 146 |

The source-controlled JCL jobs are `TA3BOOT` (print BT0001),
`TA3BT2` (IEBCOPY BT0002), `TA3VIEW` (print INSTALL/DATASETS/
RELEASE/RESTORE), followed by `TA3NATV` for native-only or
`TA3BOTH` for combined. Each is executed only within its own
recipient prefix. The combined profile additionally executes
`TA3GO`: compile SCALVEC using installed MR10 SYNI/TRNI, generate
INTCODE using CGI, and run under the **combined recipient's**
`MR10KIT.LOAD(ICINT19)`, requiring `TEST:`/`EXP:`/`RP:`/`CODE=0`.

The native-only selection contains the distributed Core Runtime,
Base Library, Coroutine Support and System Extensions sources,
assembler, object and JCL, plus unfinished Cambridge Compiler
sources. This is an **installation and inventory proof only**:
there is no runnable native Cambridge Compiler in the candidate.

## One-shot guarded operator procedure

Run from the project repository root after `git pull --ff-only`:

```text
python3 -B packaging/distribution/install-from-tape/scripts/ta3-rc3-remaining-profiles --run
```

1. Read-only checks: accepted `TA3N1` sealed MVS evidence, exact
   `BC0003` image SHA, immutable manifest/profile/JCL mapping,
   drive 0480 empty or already holding the accepted `BC0003`.
2. One fresh MVS `LISTDS` inquiry: **all 31** target DSNs absent.
   Neither accidental catalog reuse nor other tape media is accepted.
3. One operator `Y` confirmation creates the no-retry marker before
   the first allocation.
4. For each profile separately, actual MVS `IEBGENER`/`IEBCOPY`
   bootstrap/restoration, `LISTDS` DCB/volume and full PDS directory
   checks, with exact JES/IEF142I RC0000 acceptance.
5. Combined only: eight-step installed-MR10 SCALVEC execution with
   golden `EXP:`/`RP:`/`CODE=0` comparison.
6. Reconfirm the original `BC0003` SHA and seal per-job JES reports
   under `workarea/ta3-rc3-remaining-profiles/` in the project root.
   The WSL console prints only compact summaries and evidence location.

The supplied `BC0003` remains read-only; no `hetinit`, restaging,
scratch, overwrite, retry or publication is permitted. All target PDSes
use `DISP=(NEW,CATLG,DELETE)` and site-verified `TSO002` /`SYSDA`
allocation. An ambiguous result after operator approval consumes the
marker and requires a new MVS-led investigation, **not** a blind retry.

## Static checks completed; MVS results outstanding

- Local Python syntax check passed.
- Six native/combined unit and refusal tests passed; five existing
  MR10-recipient tests passed.
- Checked actual GitHub `main` JCL for both selection mappings,
  10/19 IEBCOPY steps, tape labels, new allocations, card widths
  and all site parameter substitutions.
- Committed runner and six-test file match locally tested bytes.

No actual MVS `TA3N2`/`TA3N3` result exists yet. A successful trial
completes profile-installation and installed-MR10-use evidence within
the existing MVS system, **not** a separate clean IPL acceptance or
complete TA.3 closure. `BT0002` on frozen `BC0003` retains its
original inert `RESTORE` template; tape-resident fully operational
site-parametric profile selection would require a **new authorized
candidate**, not alteration of accepted `BC0003`.
