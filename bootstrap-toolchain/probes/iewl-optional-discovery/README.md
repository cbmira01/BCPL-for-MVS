# R.4 — IEWL-Driven Extension Selection: isolated first probe

**Milestone:** Runtime Extensions. **March:** R.4 — IEWL-Driven Extension Selection.
**Scope:** Owner-approved investigation, not implementation of a new registrar.

This is a test-only IFOX/IEWL experiment. It asks a narrow question:
when the programmer explicitly uses IEWL `INCLUDE` to select a
combined extension object, can a preassembled observer find a known
BCEX descriptor by a `WXTRN` reference, while omitted extensions
remain absent? No production `BCPLMAIN`, `BCPLRGS`, or `BCPLREG` is linked.

## First experiment — 0/A/B/A+B

- A is the existing BCPLDEMO (permanent G!203).
- B is the existing R2TESTB (test-only G!299).
- The generator combines each package's *unchanged* descriptor and
  dispatcher assembler sources into one object with two CSECTs. The
  now-local dispatcher reference replaces the descriptor's `EXTRN`.
  This is assembly-source packaging only; BCEX version 1 is unchanged.
- Four independently assembled observers contain `WXTRN` declarations
  for the **known** BCEX begin/end and dispatcher symbols.
- In each link, the observer is primary input. **Only** optional code
  selected via `INCLUDE PKGA` and/or `INCLUDE PKGB` enters from its
  separate temporary sequential object dataset; an omitted package is
  not concatenated into primary SYSLIN. `PKGA`/`PKGB` are experiment
  DD names; final extension-library PDS member syntax is a later test.
- Each GO checks weak address resolution, `BCEX` magic/version,
  descriptor span (56 bytes), and relocated dispatcher address.
  GO returns **RC=0** for a passing profile and **RC=12** otherwise.

| Link | Explicit IEWL selection | Expected CSECTs |
| --- | --- | --- |
| 0 | none | no optional package CSECTs |
| A | `INCLUDE PKGA` | `DMODESC`, `DMODISP` |
| B | `INCLUDE PKGB` | `R2BDSC`, `R2BDISP` |
| A+B | both | all four |

This is **not yet a claim that IFOX supports WXTRN or that TK5's IEWL
zero-resolves omitted weak references**. Actual JES and IEWL reports
must decide that. A failed assembly/link is useful negative evidence.

## Generate and run

On an up-to-date repository checkout, first run host checks:

```sh
python3 -m unittest discover \
  -s bootstrap-toolchain/probes/iewl-optional-discovery \
  -p 'test_*.py' -v
python3 bootstrap-toolchain/probes/iewl-optional-discovery/make-job.py --check
```

If both pass, generate authenticated private JCL using the existing
`config/dspal.yaml` dataset tools, then submit with the normal MVS
operator command:

```sh
python3 bootstrap-toolchain/probes/iewl-optional-discovery/make-job.py
bash tools/mvs/submit-jcl \
  workarea/runtime-extensions-r4/r4-iewl-wxtrn.jcl
```

All newly assembled objects and load modules are `&&` temporary
MVS datasets. Generated JCL and reports belong under ignored
`workarea/runtime-extensions-r4/`; no accepted MVS PDS is written.
Run on the owner's TK5/Hercules instance, not in a simulated shell.

## Evidence to retain

Save JOB identification, step RCs, IFOX ESD/RLD listings, IEWL
MAP/XREF for all four links, and full GO messages/RCs. In particular:

1. Confirm that each package's *single* object produces descriptor
   and dispatcher CSECTs, including a relocated pointer in the BCEX.
2. Confirm IEWL MAP has exactly the selected CSECTs in each profile.
3. Confirm unresolved WXTRN symbols resolve to zero, not strong-link
   failures or implicit package inclusion.
4. Confirm selected symbol addresses are nonzero and the BCEX span,
   header and dispatcher address match at GO.
5. Check IFOX and IEWL diagnostics even when a GO returns zero.

**Not covered by this first probe:** descriptor enumeration for
independently developed *unknown* packages; package order,
dependencies, duplicate-global rejection, finalization, pre-START
registration, and BCPL omitted-extension behavior. Those remain
explicit R.4 gates, to be tested only if discovery is demonstrably
feasible. A known-symbol `WXTRN` table does not, by itself, remove the
need to maintain a list when new packages are introduced.

## Contemporary reference

IBM, *OS/VS Linkage Editor and Loader*, GC26-3813-4 (1975), and
*OS Linkage Editor and Loader*, GC28-6538-9 (1972), especially weak
external references, INCLUDE of sequential datasets and members,
common areas, and automatic replacement of same-named CSECTs.

Source text: https://device.report/m/2ac6649093cd5119f79815f865a9605d821c984195e9eccbae4eeb10e306f778

These manuals document expected semantics. Only actual MVS results
will establish behavior on this TK5 installation.
