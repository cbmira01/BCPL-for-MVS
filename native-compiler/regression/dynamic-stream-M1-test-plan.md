# M1 native BCPL regression gate — dynamic streams

Status: **contract accepted; cases planned, not yet implemented or run**.
Milestone: [BCPLIO dynamic stream](../docs/Milestone-BCPLIO-dynamic-stream.md).
The M1 gate requires the real native BCPL source-to-MVS execution path,
not only the private assembler ABI probes.

## Existing evidence and baseline

The current numbered panel has 00..123 (124 positions). The last
reported baseline for this milestone was 123 PASS, 0 FAIL,
one source-only SKIP (083). Reconfirm at the actual candidate SHA;
do not treat this historical result as proof of a new candidate.

M1 infrastructure probes are accepted separately:

| Probe | Function | MVS GO |
|---|---|---|
| IONMPRB | DD normalization | JOB 5586 RC=0000 |
| IODRPRB | Descriptor registry | JOB 5595 RC=0000 |
| IOHPRB | Stable handles | JOB 5604 RC=0000 |
| IODVPRB | RDJFCB inquiry | JOB 5620 RC=0000 |

These are **not native BCPL panel tests**.

## Proposed contiguous new BCPL cases

Numbers below are **reserved in the plan only**, not test directories,
and may be adjusted only before the first corresponding case is
committed. Each committed case must own source.bcpl, README.md and
expected.txt and use the existing runner/numbering rules.

| ID | BCPL observable assertion | Required job setup |
|---|---|---|
| 124 | FINDINPUT of CUSTOMER returns nonzero and selects/reads input | CUSTOMER allocated with deterministic FB80 input |
| 125 | FINDOUTPUT of REPORT returns nonzero and writes an FB132 record | REPORT allocated separately; inspect DD-specific output |
| 126 | Mixed/lowercase spelling resolves to the same live handle | Allocated CUSTOMER |
| 127 | Repeated FINDINPUT returns the same live handle | Allocated CUSTOMER |
| 128 | Invalid and unallocated names return zero; INPUT unchanged | CUSTOMER plus intentionally absent ZXYZ1234 |
| 129 | Two allocated DDs have distinct handles and direction behavior | CUSTOMER, REPORT (independent DDs) |
| 130 | Closing and reopening yields new handle; stale one rejected | CUSTOMER allocated |
| 131 | Thirteen concurrent DDs yield valid distinct handles | DD01..DD13 allocated |

M1 minimum acceptance shall include 124..130 (or equivalent
individual cases covering all public behaviors actually introduced);
131 may execute in M2 as its multiplicity gate, but it must not
be represented as an M1 passing result until run. Preserve existing
fixed-DD tests 114..119 as compatibility witnesses. M2/M3 add
record cursor, EOF/UNRDCH, interleave, and precise output DD
attribution; M4 expands failure/cleanup paths. The M1 case 125
must verify the actual REPORT DD artifact, not just stdout.

## Runner integration prerequisite

At the documented baseline the regression runner links the
monolithic BCPLMAIN path rather than the independently staged
BCPLIO DEVOBJ object. Before treating any new result as dynamic
BCPLIO evidence, explicitly identify and document the runner's
link-mode choice, selected BCPLIO module, and OBJ/DEVOBJ
provenance. Introduce a development-only test mode if necessary;
do not silently change the production default or promote DEVOBJ
objects into production NATIVE.OBJ.

Tests needing arbitrary DD statements must supply them in
generated JCL or a reproducible test-specific job step. Do not
misattribute the aggregated printer file to a particular DD.

## M1 acceptance checklist

- Each public dynamic FIND feature lands with a compiled BCPL
  regression covering success, negative cases and identity.
- Full native regression re-run at the implementation SHA, with
  no new failures; retain the documented source-only skip if still
  applicable.
- Include compiler, IFOX, IEWL, GO codes, exact output comparison,
  and DD-specific evidence where applicable.
- Confirm the candidate used independently rebuilt BCPLIO from
  repository source and did not modify production OBJ.
- Keep infrastructure probes as separate permanent checks.
- No M1 gate acceptance from assembler-only probe successes.
