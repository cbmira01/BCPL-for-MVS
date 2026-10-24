# Milestone BCPLTIME — T.1 owner closure (24 October 2026)

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** BCPLTIME — primitive System/370 and MVS time access  
**March:** **T.1 — Packaging and Acceptance**  
**Owner decision:** **CLOSE T.1** (explicit owner approval, 24 October 2026)  
**Source revision tested:** [`1914279246e02ff01594bab9396289e24d1246c3`](https://github.com/cbmira01/BCPL-for-MVS/commit/1914279246e02ff01594bab9396289e24d1246c3)  
**Installation:** MVS 3.8J TK5 under Hercules, installed optional System Extension objects  
**Disposition:** **Milestone BCPLTIME CLOSED**; T.0 and T.1 are both CLOSED. No additional marches are established.

## Owner acceptance and scope

The owner explicitly directed **"Let's close and commit T.1"** after reviewing
the successful installed-mode test results and full production-panel transcript.
This is the formal closure of **T.1 — Packaging and Acceptance** in the
owner-approved accelerated two-march **Milestone BCPLTIME**. T.0 had already
closed on 24 October 2026; see the [T.0 owner closure](bcpltime-t0-closure-20261024.md).
The superseded original 15 October T.0–T.4 proposal remains historical, not
additional active work.

The accepted package is `BCPLTIME`, an **optional project-created System
Extension**, independently selectable by the BCX/IEWL mechanism. Its public
dispatcher `TIMESVC` uses **G!201** and BCEX/BCRG version 1; the single
relocatable object contains `TIMDESC` and `TIMDISP` with descriptor bounds
`TIMBEG`/`TIMEND`. The version-1 dispatcher exposes only QUERY (0), raw
System/370 STCK (1), and raw MVS `TIME DEC` (2). The accepted negative returns
are `-1` insufficient capacity, `-2` unsupported opcode, and `-3` invalid
arguments, with caller-owned vectors and no partial output writes.

The package is **not** a calendar, timer, scheduling, formatting, or portable
Standard Library facility. It does not claim original Cambridge BCPL provenance
or historical binary compatibility beyond behavior actually tested.

## Exact Git and MVS chronology

The operator's checkout was `19142792` (short SHA) for the installation and
subsequent tests. The later documentation-only closure commit records this
evidence; it is **not** claimed as the source revision executed on MVS.

| Activity | JOB | Observed evidence |
| --- | ---: | --- |
| Save accepted resident BCXCAT to ignored local workarea | **5445** | `dspal get EXT_MAC BCXCAT` succeeded |
| Stage assembler source | **5446** | `HERC02.BCPL.EXT.ASM(BCPLTIME)` written |
| Stage public BCPL header | **5447** | `HERC02.BCPL.EXT.SOURCE(TIMEHDR)` written |
| Stage installation job body | **5448** | `HERC02.BCPL.BOOT.JCL(T1TINST)` written |
| Launch resident `T1TINST` job | **5454** | JES INTRDR launcher |
| Assemble/install/read back/compare | **5455** | Payload SUCCESS; highest RC=0000 |
| Publish production package catalog | **5457** | `HERC02.BCPL.EXT.MAC(BCXCAT)` written |

These were **separately authorized member-level MVS writes**, not a blanket
`dspal populate all` operation. BCPLDEMO was preserved; no `BOOT_OBJ`,
`BOOT_DEVOBJ`, compiler, or historical `BLIB` member was rebuilt or overwritten.

### `T1TINST` binary installation evidence — payload JOB 5455

| Step | Program | Actual return code |
| --- | --- | --- |
| `ASMTIME` | `IFOX00` | `0000` |
| `PUTTIME` | `IEBGENER` | `0000` |
| `READBACK` | `IEBGENER` | `0000` |
| `VERIFY` | `IEBCOMPR` | `0000` |

The operator supplied the **actual report extract**: no assembler statements
flagged, highest assembler severity **0**, **12 records punched** and
`END OF JOB-TOTAL NUMBER OF RECORDS COMPARED = 00000012`. The installed
`EXT_OBJ` inventory contained **both `BCPLDEMO` and `BCPLTIME`**.
`PUTTIME` was the installation job's only persistent binary-object write;
`READBACK`/`VERIFY` compared the installed FB80 record stream with the
temporary assembler output.

After JOB 5457, a direct resident `dspal cat EXT_MAC BCXCAT` showed:

| Package identity | IEWL INCLUDE | BCEX descriptor extent |
| --- | --- | --- |
| `BCPLDEMO` | `EXTLIB(BCPLDEMO)` | `DMOBEG` / `DMOEND` |
| `BCPLTIME` | `EXTLIB(BCPLTIME)` | `TIMBEG` / `TIMEND` |

`BCXPRE`, `BCXPOST`, the accepted BCPLDEMO object, Core Runtime, Base
Library and the interpreter-hosted demoted Cambridge compiler remain unchanged.

## MVS installed-mode native regression acceptance

The operator selected accepted production `BOOT_OBJ` with:

```sh
export BCPL_RUNTIME_PDS=1
export BCPL_RUNTIME_LIBRARY=OBJ
export BCPL_RUNTIME_CANDIDATE=0
unset BCPL_RUNTIME_CANDIDATE_MEMBER
export BCPL_R5_EXTENSION_MODE=installed
export BCPL_R5_EXTENSION_DSN=HERC02.BCPL.EXT.OBJ
export BCPL_R5_MACRO_DSN=HERC02.BCPL.EXT.MAC
export BCPL_T1_EXTENSION_MODE=installed
export BCPL_T1_EXTENSION_DSN=HERC02.BCPL.EXT.OBJ
export BCPL_T1_MACRO_DSN=HERC02.BCPL.EXT.MAC
```

The focused command `tools/bootstrap/run-production-regression 159 162
--show-output` reported **4 PASS, 0 FAIL, 0 SKIP**. The same four cases
passed again in the full production run.

| Case | Required installed configuration | Result |
| --- | --- | --- |
| **159** | BCPLTIME required; BCPLDEMO CSECTs excluded | PASS |
| **160** | BCPLDEMO then BCPLTIME; interleaved calls | PASS |
| **161** | BCPLTIME then BCPLDEMO; reversed order | PASS |
| **162** | BCPLTIME selection/requirement upgrade and duplicate request | PASS |

**Final acceptance command:** `tools/bootstrap/run-production-regression 0 162`.

| Full panel result | Actual |
| --- | ---: |
| **PASS** | **162** |
| **FAIL** | **0** |
| **SKIP** | **1**, expected source-only instrumentation case **083** |
| **TOTAL** | **163** numbered cases 00–162 |

The full operator transcript explicitly lists **each of the 162 PASS cases**
and the one expected SKIP 083, including all prior R.5 cases 146–158 and
the four new T.1 cases 159–162. The production wrapper confirms selection
of `BOOT_OBJ` with required accepted runtime members. The existing
regression runner's PASS gate checks expected native output and actual
IEWL MAP/XREF for R.5 and T.1 package tests: expected CSECT presence/
absence, `BCPLREG` length and zero entry address. The reported PASS is
the runner's verdict; the individual raw per-case reports were **not**
independently re-audited in this closure review.

The earlier temporary source-mode T.1 run also reported **4 PASS,
0 FAIL, 0 SKIP**, and the owner's packaging preflight reported **30
unit tests PASS**, plus the canonical 13-member `BOOT_JCL` check and
all four `dspal populate --dry-run` manifest previews.

## Rebuild contract and retained limitations

The accepted installation is reconstructible from Git-controlled
`EXT_ASM(BCPLTIME)`, `EXT_SOURCE(TIMEHDR)`, the production `BCXCAT`,
`BOOT_JCL(T1TINST)`, and the accepted R.5 BCX macros/registration
architecture. The [T.1 installation procedure](bcpltime-t1-installation-design.md)
documents member-level incremental installation, read-back verification,
catalog publication after the object, and recovery. A future fresh
clean-room rebuild must separately reinstall and verify both BCPLDEMO
and BCPLTIME before running the optional-extension production panel.

**Retained limits:**

- **Non-reentrant v1 dispatcher:** private aligned scratch for `STCK`;
  no independent concurrency safety guarantee.
- **Raw timing data:** `STCK` provides the unconverted 64-bit TOD words
  and condition code; `TIME DEC` returns raw R0/R1 fullwords. No
  calendar interpretation, accuracy, timezone reconciliation or
  wall-clock validity guarantee was accepted.
- **Evidence availability:** authenticated JCL and full operator-local
  JES listings remain under ignored `workarea/`. Individual payload
  JOB numbers for cases 159–162 and all per-case raw MAP/XREF reports
  were not included in the supplied final-panel transcript. The earlier
  T.0 logical-output record had an unresolved auxiliary JES DD-attribution
  check; see its separate closure.
- **Scope:** this acceptance is for the tested native BCPL applications
  compiled by the **interpreter-hosted demoted Cambridge compiler**;
  it does not imply a native/self-hosting Cambridge compiler, dynamic
  extension loading, or full historical compatibility.

**No additional resident PDS writes or new marches are authorized by
this closure.** GitHub `main` remains the official source of project
code and documentation. **Milestone BCPLTIME: CLOSED** with **T.0 and
T.1 CLOSED** by their respective explicit owner decisions.
