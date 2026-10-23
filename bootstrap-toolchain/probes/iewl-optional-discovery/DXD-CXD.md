# R.4 — DXD/CXD cumulative-length probe

**Status:** committed MVS candidate; host-only checks PASS; **not executed on MVS**.

Purpose: Test the one additional documented IFOX/IEWL mechanism that
might give a precompiled Core Runtime a **count of included packages**
without knowledge of their entry-symbol names.

This is *not* a registration mechanism. The `CXD` length counts external
dummy storage; it does not contain initialized descriptor pointers.

## Mechanism

The existing R.4 `combined_source` function supplies the unmodified BCEX
v1 descriptor/dispatcher data and code for BCPLDEMO and R2TESTB. This
candidate appends to each one object:

- A unique `DXD F` representing four bytes of uninitialized dummy storage.
- A separate CSECT holding `DC Q(<DXD-name>)` so the assembler emits an
  external-dummy-section (XD) dictionary entry.

`R4CXDOBS` is assembled **once** with `DXDLEN CXD` and no package-specific
external symbols. All four link-edits reuse the *same* observer object.
Each link selects optional objects exclusively via `INCLUDE PKGA` and/or
`INCLUDE PKGB`. The observer reads the resolved CXD field and returns its
value in register 15; the MVS GO condition code is the **measured total**.

| Link | Selected optional objects | Expected GO condition code |
| --- | --- | --- |
| L0 / G0 | None | **0000** (0 bytes) |
| LA / GA | BCPLDEMO only | **0004** (4 bytes) |
| LB / GB | R2TESTB only | **0004** (4 bytes) |
| LX / GX | Both | **0008** (8 bytes) |

**Important:** `GA`, `GB`, and `GX` returning nonzero is the expected
measurement, **not a failure**. Subsequent IEWL steps use explicit
assembly-step `COND` references to avoid being bypassed by these expected
nonzero GO results. Inspect every IFOX/IEWL return code separately and
review the IEWL MAP/XREF for the `CXD` and external dummy sections.

## Run from repository root

The generator and tests are on GitHub `main` alongside `make-job.py`:

```sh
git pull --ff-only
python3 -m unittest discover \
  -s bootstrap-toolchain/probes/iewl-optional-discovery \
  -p 'test_dxd.py' -v
python3 bootstrap-toolchain/probes/iewl-optional-discovery/make-dxd-job.py --check
python3 bootstrap-toolchain/probes/iewl-optional-discovery/make-dxd-job.py
bash tools/mvs/submit-jcl \
  workarea/runtime-extensions-r4/r4-dxd-cxd.jcl
```

The generator reads `config/dspal.yaml` for an authenticated job card.
Generated private JCL stays under the ignored `workarea` and is not
committed. All IFOX object and IEWL load-module output uses `&&`
temporary datasets. **No production code, accepted object library,
compiler, BCPLMAIN, BCPLRGS, or BCPLREG is changed.**

After JOB number is returned:

```sh
tools/mvs/job-summary JOB_NUMBER --max-rc 8
tools/mvs/dump-report-for-job JOB_NUMBER \
  > workarea/runtime-extensions-r4/r4-dxd-cxd-report.txt
```

Replace `JOB_NUMBER` with the numeric job identifier, not angle brackets.
Look for seven successfully executed ASM/IEWL steps plus four GO steps.

## Interpretation

If GO is 0/4/4/8, then IFOX and IEWL can calculate a package-independent
*total external dummy storage length* from explicitly included objects.
This does not identify or locate any BCEX descriptor. If one subsequently
tries equal dummy-section names, IBM documents merging with the maximum
length, rather than appending contributions. Independently developed
packages must have distinct XD names; even then, CXD produces only a
length, and the XD storage has **no initialized descriptor contents**.

Failure to assemble `DXD`/`CXD`/`Q`, or different GO results, would narrow
this candidate for the actual TK5 assembler/linker. Record exact source,
ESD, RLD, IEWL map, and GO results rather than assuming a workaround.

### Historical references

- IBM, *OS Assembler Language*, GC28-6514-9, Release 21, 1974:
  'External Dummy Sections (Assembler F Only)', DXD, CXD, Q-type constants.
  https://manuals.plus/m/17b6feca60f26515201385a6b4d06b419dad686ab7faea35b82105a555d1ae0b
- IBM, *OS/VS Linkage Editor and Loader*, GC26-3813-4, 1975:
  external dummy sections, relocation and linkage-editor symbol handling.
