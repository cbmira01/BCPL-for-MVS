# Milestone Runtime Extensions — R.0 Decision A stage-1 MVS evidence

**Date:** 21 October 2026. **March:** **R.0 — Evidence and contract (open)**.
**Result:** **PASS — ten isolated trusted-link test profiles, JOBs 2207–2216.**
**Source revision:** `075e2cc56ad02c6d2d0e9a6b9c2014d5f7c52a3c`, pulled
from GitHub `main` by the operator. No registrar or installed-object
identity claim follows from these tests.

**Authority:** [Owner-approved Decision A](runtime-extensions-r0-owner-abi-decisions.md),
[Decision G diagnostics](runtime-extensions-r0-decision-g-contract-20261021.md),
[probe](../bootstrap-toolchain/probes/r0-trusted-link-probe/README.md),
[stage-1 plan](runtime-extensions-r0-decision-a-stage1-20261021.md).

## Actual MVS outcomes

The owner ran `run.sh valid`, supplied its full JES, IFOX and IEWL
report, reviewed the positive map, then executed `goodhook` and all
eight negative profiles in order.

| Profile | Actual JOB | Expected internal status | Outcome |
| --- | ---: | ---: | --- |
| `valid` | 2207 | 0 | PASS |
| `goodhook` | 2208 | 0 | PASS |
| `regzero` | 2209 | 1001 | PASS |
| `regunal` | 2210 | 1001 | PASS |
| `pkgbound` | 2211 | 1004 | PASS |
| `reglen` | 2212 | 1003 | PASS |
| `pkglen` | 2213 | 1006 | PASS |
| `regvers` | 2214 | 1002 | PASS |
| `pkgvers` | 2215 | 1005 | PASS |
| `badhook` | 2216 | 1013 | PASS |

Every submitted job completed **ASMD/ASMR/ASMP/ASMF (IFOX00),
LKED (IEWL), and GO**, all **RC=0000**, JES **SUCCESS**,
highest assembler severity **0**, and **no flagged statements**.
Each submitted deck contained 265 JES cards; the host synthetic
generator checked 263 cards per profile. Each operator run passed
**11 Python unit tests** and all ten dry-run JCL checks. The runner's
report verifier confirmed exactly the expected actual QOUT record
for **each** profile. A negative profile earns GO RC=0000 only
when the expected internal Decision G diagnostic is matched.

`goodhook` verified that a relocated `R0FIN` address was accepted
as a finalizer target; **the hook was not called**. `badhook`
rejected a linked but wrong finalizer target (1013); it did
**not** dereference an arbitrary invalid address.

## Independently examined IEWL MAP/XREF — JOB 2207 only

The complete actual JOB 2207 listing was supplied. IEWL confirmed:

| Linked CSECT | Origin (hex) | Length (hex) | Symbol ownership |
| --- | ---: | ---: | --- |
| `R0ATST` | 000000 | 000340 | test validator |
| `R0AREG` | 000340 | 00002C | `R0RB=000340`; `R0RE=00036C` |
| `R0APKG` | 000370 | 000038 | `R0PB=000370`; `R0PE=0003A8` |
| `R0AFUN` | 0003A8 | 000004 | `R0FUNC=0003A8`; `R0FIN=0003AA` |

The registry's exclusive begin/end extent is **44 bytes** and the
package descriptor's extent is **56 bytes**. The exclusive end
`R0PE` correctly coincides with the next CSECT's beginning
`R0FUNC`; code is **not** part of descriptor data. Total linked
image length: **0x3B0**. The IEWL XREF identifies reference sites
`2F8/2FC` to R0AREG, `31C/320` and `35C/360` to R0APKG,
and `338/33C` to R0AFUN; `3A4` is the R0APKG export
reference to R0FUNC. IEWL RC=0000 and no unresolved
references were shown. Its temporary-member creation message
(`R0ATRST DOES NOT EXIST BUT HAS BEEN ADDED TO DATA SET`)
does not describe a change to `BOOT_OBJ`.

The actual GO record is `R0 A VALID LINK PASS`.

## Evidence limits

- Actual full IEWL MAP/XREF **was inspected for JOB 2207 only**.
  For JOBs 2208–2216, the supplied evidence comprises actual step
  summaries and individually verified GO markers. The tracked
  generator independently checked source CSECT ownership in all
  cases; no claim is made of a separate full-map review for each.
- Per-profile JSON files under ignored
  `workarea/runtime-extensions-r0-a/` contain rendered assembler
  source SHA-256 hashes and the run's Git revision. **The literal
  recorded hash values were not supplied**, so independent comparison
  with Git source hashes remains unperformed. The Git revision and
  build recipe are identified, but installed binary provenance is not.
- This is **test-only static metadata validation**, not general
  hostile-pointer protection, production BCPLREG, transactional
  publication, complete Decision G coverage, FINISH/STOP finalizer
  invocation, or a cryptographic attest of executing object bytes.
- All objects/load modules were temporary; **accepted `BOOT_OBJ`
  and `BOOT_DEVOBJ` members were not replaced**.

**Stage-1 disposition:** The ten-case isolated MVS panel has
**passed and is complete within the approved fixture scope**.
The separate [stage-2 read-only binary comparison design](runtime-extensions-r0-decision-a-stage2-design-20261021.md)
remains pending owner design acceptance. R.0 open; R.1 not started.
