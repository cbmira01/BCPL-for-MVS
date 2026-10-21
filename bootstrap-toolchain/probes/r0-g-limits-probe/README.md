# R.0 — Decision G defensive limits, isolated test-only probe

**March:** R.0 — Evidence and contract (open). **Decision G numeric
limits and diagnostics: owner approved 21 October 2026.**
[R.0 Decision G contract](../../../packaging/runtime-extensions-r0-decision-g-contract-20261021.md).
**Status:** **MVS PASS, JOB 2203**, ASMC/ASMD/LKED/GO RC=0000;
14 expected GO markers verified; 14 host tests PASS. See the
[actual MVS evidence](../../../packaging/runtime-extensions-r0-decision-g-job-2203-evidence-20261021.md).
**R.1:** Generic registration foundation not started.

Two layers of deliberately isolated evidence:

1. `limits.py` is a **host-side reference validator** of the approved
   binary `BCRG` (28+8N+8M) and `BCEX` (48+8K+16D) structures. It uses
   trusted byte arrays and simulated independent extents, models registry,
   export, requirement and dependency rejection, and returns proposed
   stable numeric diagnostics. It is **not** machine-code registrar,
   live MVS pointer verifier, or finalizer. Its example ownership map is
   fixture-provided, **not** a substitute for the Global Number Registry.
2. `check.asm` (IFOX) validates the **numerical upper and lower
   boundaries** of N, M, K and D in 14 scenarios linked from an
   independent data CSECT, comparing actual assembler results against
   expected **1003/1006/0** before printing each GO marker. The driver
   does not parse complete BCRG/BCEX records, test finalizer pointers,
   import BLIB or write BCPL globals. No START execution occurs. This
   explicitly **does not prove** R.1 pre-START rejection or transactional
   no-publication in the real Core Runtime.

## Run on Morkies

```bash
cd ~/Source/Repos/BCPL-for-MVS
git pull --ff-only
bash bootstrap-toolchain/probes/r0-g-limits-probe/run.sh
```

The runner executes host unit tests and a credential-free JCL check,
then creates an authenticated deck under ignored
`workarea/runtime-extensions-r0-g-limits/` with private file mode,
submits one `R0GLIMIT` job, saves its complete report, checks all four
step RCs (ASMC, ASMD, LKED, GO) and independently requires **all 14**
actual QOUT markers. The object decks and load module are **temporary
`&&` datasets**; none of the accepted `BOOT_OBJ` members are touched.

### Offline-only

```bash
probe=bootstrap-toolchain/probes/r0-g-limits-probe
PYTHONPATH="$probe" python3 -B -m unittest discover -s "$probe" -p 'test_*.py' -v
python3 -B "$probe/make-job.py" --check
bash -n "$probe/run.sh"
```

The **actual** MVS `R0GLIMIT` JOB 2203 completed: ASMC/ASMD IFOX
RC=0000, LKED IEWL RC=0000, GO RC=0000, with 14 exact
`R0 Gnn ... PASS` markers verified in the GO report.
Do not commit password-bearing JCL or full JES printer output.

### Acceptance boundaries

- Host reference tests do not establish safe dereference of arbitrary
  pointers. Independently linked trusted begin/end and reproducible
  source/IEWL evidence are Decision A requirements.
- The 14-case assembler driver checks arithmetic and internal diagnostic
  categories for **counts only**. Remaining 1001–1014 validation
  categories, 2001, R.1 startup RC=12, and finalizer behavior are not
  end-to-end tested by this probe.
- The approved G numbers, effective owner collisions and genuine
  linked application/BLIB trailers still require the true registrar's
  integration in R.1 and regression testing. Do not declare R.0 closed
  based on this isolated test.
