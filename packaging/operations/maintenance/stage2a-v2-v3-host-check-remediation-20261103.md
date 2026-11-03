# Stage 2A — V2/V3 host-check remediation (3 November 2026)

**Project:** BCPL for MVS 3.8 Reconstruction  
**Baseline:** Stage 2A source-location commit `d8a2588dd3ee6076acc14bcd43dc8e59641b44f8`  
**Scope:** host-only tests, historical-path expectations, Q.5 deck safety guard and a byte-exact synthetic IFOX/IEWL/JCL deck comparison tool  
**Status:** remediation prepared for owner-run WSL verification; **not an acceptance record**

## Evidence prompting this change

The owner ran V2 and V3 under WSL on `d8a2588` and supplied the transcript. The checkout was clean before Python execution. Recorded results:

| Check | Result before remediation |
| --- | --- |
| `tools/checks` unit tests | 106 tests, 3 FAIL, 7 ERROR |
| `system-extensions/bcplqsam` unit tests | 236 tests, 1 FAIL |
| `system-extensions/template` unit tests | 8 tests, 1 ERROR |
| Python compilation and shell syntax | Both RC=0 |
| T.0, R.5, T.1 synthetic deck checks | All RC=0 |
| Q.5 synthetic Q5PKG check | RC=1, “permanent library operation forbidden” |

These were failures of **offline checks**, not new MVS native test failures. The original accepted QSAM and Runtime Extensions milestone records are unchanged.

## Specific remediations

1. **QSAM numbered test coverage:** `test_q2_numbered_regression.py` formerly asserted 163–170 only but the accepted suite is 163–176. Test all fourteen cases and dispatch each case to its actual native JCL generator, including V/VB and SYSOUT types. Preserve every case ID, source/expected marker and existing generator contract.
2. **Q.2 source-contract test:** It expected two `MVCL` cards and QUERY capability bitmap 25. The unchanged current `bcplqsam.asm` has three `MVCL` sites (read copy, fixed write, V/VB write) and advertises bitmap 31 for the accepted five operations. Update the positive and negative assertions; do **not** modify assembler code.
3. **R.5 runbook test:** Update its removed `packaging/clean-room-mvs-reconstruction.md` reference and obsolete 00–162 transcript expectations to the current `docs/Rebuild-BCPL-for-MVS-from-source.md` and documented installed R.5/T.1 invocation 0–176.
4. **Template test:** Resolve the R.3 historical linkage guide in `packaging/archive/runtime-extensions/`, accounting for the relocated package depth.
5. **JCL width tests:** The canonical BCPLDEMO/BCPLTIME installation JCL files have unchanged **72-character comment cards** in column 1. Allow up to 80 columns on `//*` comments; retain the 71-column check on operative JCL cards. Do not edit the accepted install decks.
6. **Q.5 false positive:** `prepare-q5-release-campaign.py` scanned every row for `BOOT_DEVOBJ`, including an existing `BCPLMAIN` assembler comment explaining that there is **no** promotion to `BOOT_DEVOBJ`. Ignore full-line JCL/assembler comments in that prohibition while still rejecting active `CATLG`, `DISP=MOD` and `BOOT_DEVOBJ` references. Add a focused negative-safety test and a complete synthetic two-application deck test.

## V3 generated-deck parity

`tools/checks/verify-stage2a-deck-parity.py` is a **host-only** reproducibility checker. It archives Git revisions in temporary directories and synthesizes **49** comparable ASCII decks using the existing generators: T.0 source, 13 R.5 source and 13 installed, four T.1 source and four installed, and 14 numbered BCPLQSAM source-mode decks. It compares SHA-256 of the complete generated deck for each case against the pre-Stage 2A Git revision `efb461f3c90a8de93e7d7ddc4dcc3529a9a60a4c`.

Run from the repository root after updating WSL to the verified remediation commit:

```sh
python3 -B tools/checks/verify-stage2a-deck-parity.py
```

The **Q5PKG synthetic generator is intentionally excluded from the old/new equality panel**: its old implementation rejects a harmless embedded assembler comment and cannot produce a baseline deck. Its corrected generator has a new direct positive and negative host unit test plus the `--check` command. Do not claim a pre-Stage 2A Q5PKG deck comparison.

The comparison uses `git archive` and a temporary directory, never calls MVS or credential-bearing preparation, and never submits JCL. It requires the pre-Stage 2A commit to remain available in the local Git repository.

## Required WSL checks (not yet re-executed here)

- `python3 -B -m unittest discover -s tools/checks -p 'test_*.py' -v`
- `python3 -B -m unittest discover -s system-extensions/bcplqsam -p 'test_*.py' -v`
- `python3 -B -m unittest discover -s system-extensions/template -p 'test_*.py' -v`
- `python3 -B tools/checks/prepare-bcpltime-t0.py --check`
- `python3 -B tools/checks/prepare-r5-extension-regression.py --check`
- `python3 -B tools/checks/prepare-t1-time-regression.py --check`
- `python3 -B system-extensions/bcplqsam/prepare-q5-release-campaign.py --check`
- `python3 -B tools/checks/verify-stage2a-deck-parity.py`

Record actual test counts, RCs, any residual failures and parity hashes in a *separate* verified acceptance record after operator execution. No V2/V3 PASS or native MVS gate is inferred from staging or committing these changes.

**Operating boundaries:** No JES submission, dataset population/install, `EXT_OBJ` promotion, closure modification, historical regression renumbering or changes to canonical System Extension assembly or installation JCL.
