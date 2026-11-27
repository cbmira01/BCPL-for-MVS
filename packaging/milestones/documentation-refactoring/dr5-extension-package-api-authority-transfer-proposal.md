# DR.5 — Individual extension package API authority transfer proposals

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Documentation Refactoring  
**March:** DR.5 — Validation and Reconciliation  
**Baseline:** `6aec1d9558368e59d4604e3cad8e38c58060e1fa`  
**Disposition:** PROPOSED — each transfer requires explicit owner approval.

The common QUERY and registration/finalizer contracts are already effective
in chapters 1 and 2 of the [Reference for System Extensions](../../../../docs/product/Reference-for-System-Extensions.md).
This proposal groups three independent public API transfers for efficient
owner review. It does not transfer package support governance, source
headers, Global Number Registry allocations, build/configuration data,
test oracles, closure evidence or historical records.

## A. BCPLDEMO — chapter 3

Original public API: [BCPLDEMO source README](../../../../system-extensions/bcpldemo/README.md),
published API section; [permanent support decision](../runtime-extensions/bcpldemo-supported-reference-decision-20261024.md)
remains governing for support and maintenance commitments.

| Provision | Destination and reconciliation |
| --- | --- |
| Identity, DEMOSVC G!203, v1.0, independently selected optional reference | Chapter 3 opening; one object DMODESC/DMODISP; source and public header match |
| QUERY 0, six words (1,1,0,6,1,0) | Chapters 1/3, cases 147–150 |
| GETVALUES 1, count 3, values 10/20/30 | Chapter 3 operation table, 151–153 |
| Null/negative -3, short -1, unsupported -2; no partial writes | Chapter 3 and common QUERY; 149/150/152–154 |
| Caller-owned word vector, stateless, no init/dependency/finalizer | Chapter 3; source checks, 155 repeated calls |
| Independent selection and exclusion, not implicit core/linkage | Chapters 1–3; 146/156–158, R.5 JOB 5108 installation/readback |

Transfer the published API behavior only. Preserve permanent optional support,
compatibility review, permanent 146–158 coverage, Git-backed rebuild and
interoperability obligations in the owner support decision. Add explicit
package-specific statement that successful calls write exactly the returned
word count and that no package-specific Core Runtime dispatch or autoload
is permitted.

## B. BCPLTIME — chapter 4

Original public behavior: [source README](../../../../system-extensions/bcpltime/README.md)
ABI section and the technical public-interface provisions of
[T.0](../bcpltime/bcpltime-t0-closure-20261024.md) and
[T.1](../bcpltime/bcpltime-t1-closure-20261024.md).

| Provision | Destination and reconciliation |
| --- | --- |
| Optional TIMESVC G!201, BCEX v1, API 1.0, TIMDESC/TIMDISP | Chapter 4; header/source; T.1 installed JOB 5455 |
| QUERY 0: (1,1,0,6,3,0) | Chapters 1/4; T.0 and 159–162 |
| STCK 1: high/low raw words and hardware CC 0–3, positive 3 | Chapter 4; aligned private scratch and T.0 CC0 evidence |
| MVS TIME DEC 2: raw R0/R1, positive 2 | Chapter 4; JOB 5434 failure and corrected JOB 5436 preserved |
| Short -1, unsupported -2, null/negative -3; no partial write | Chapter 4; source and T.0 caller guard tests |
| Nonreentrant, no dependencies/init/finalizer; selection and exclusion | Chapter 4 and common chapter 2; 159–162 installed/source panels |

Add explicit exact successful write count and unchanged trailing words.
Preserve raw-bit semantics and the absence of calendar conversion, clock
accuracy, timezone, timer, scheduling or formatting guarantees. No claim
that STCK nonzero hardware CC paths were observed; the actual T.0 DD
attribution limitation and nonreentrant scratch remain qualified. No
new tests or modification required. The acceptance/installation chronology
remains historical evidence, not superseded by this public API transfer.

## C. BCPLQSAM — chapter 5

Original [public interface](../qsam/bcplqsam-public-interface.md),
[Q.0 staging decision](../../archive/qsam/qsam-q0-staging-resource-design-decision.md)
and [Q.0 returned-error/finalization decision](../../archive/qsam/qsam-q0-error-and-r0-design-decisions-20261020.md),
read with accepted Q.1–Q.5 and DR.5 evidence. Transfer the public API
and externally observable resource/lifecycle semantics, not private
implementation details, historical milestones or closure claims.

| Original specification sections | Destination and reconciliation |
| --- | --- |
| 1–4: purpose, separation from BCPLIO, logical records, byte fidelity, native dispatch | Chapter 5 opening, 5.3; optional project-created G!200, no compiler change |
| 5–7: opcodes, four/eight word layouts, shared QUERY | Chapters 1, 5.1–5.2; header constants agree, 163 and 170 exact fields, bitmap 31/flags 7 supersede historical values |
| 8–9: OPEN DD normalization, modes, positive opaque handles and no alias on reuse | 5.1, 5.3–5.4; 164–167; reserve then publish only after successful OPEN, geometry and stage checks |
| 10: exact READ, sticky EOF, pending record and repeated short retry, unchanged buffer | 5.1–5.4; 168, 171, 173; zero payload distinguished from EOF |
| 11: WRITE lengths, private RDW, no padding/truncation, accepted count not device delivery | 5.1–5.4; 168–170, 172, 174–176 |
| 12: CLOSE retirement, returned -14, quarantine and generic cleanup | 2.3, 5.4; Q.5 and 198–200; approved primary precedence already effective |
| 13–15: INFO actual DCB fields, 1024-byte ceiling, status, private/caller ownership | 5.1–5.4; exact constants, no diagnostic R!2 encoding, honest capacity, no arbitrary pointer protection |
| 16–17: supported formats, allocation and declaration/link/register distinctions | Chapters 1–2, 5.3–5.4; F/FB/V/VB/FBA only; VBA reserved; installed selection/exclusion JOBs 1261/1263 |
| 18–23: schematic example, acceptance demonstration, march roadmap, exclusions, remaining historic gates | Retain original as history; verified how-to/tutorial and Q.1–Q.5/DR.5 records provide current evidence; exclusions preserved |
| 24: numeric assignments and ordinary result contract | 5.1–5.3; exact public header, all opcode/mode/format/capability/status values retained |

Required clarifications before effect:

- Result-vector guarantees apply only after a valid ordinary dispatch has
  cleared the result vector. Invalid opcode or nonpositive Q/R can return
  before clearing it; caller must trust function return, not stale fields.
  No overlapping public vectors or buffers. No fixed vector capacity
  argument. This preserves valid-call behavior and explicitly qualifies
  invalid-call boundary rather than promising writes through bad pointers.
- OPEN checks effective geometry and allocates the complete private stage
  before publishing a handle or issuing GET/PUT. Returned allocation
  failure does not consume a record or disturb unrelated handles.
  No guarantee of a particular job region budget; counters, private DCB
  snapshots and stage structures are implementation, not public ABI.
- Finalization attempts all live handles and continues after returned
  failures; quarantined slots are not retried/freed. Existing FINISH/STOP
  behavior and genuine exceptional CLOSE qualification remain unchanged.
- Explicitly exclude general PDS member creation, STOW and directory
  maintenance; JCL-selected members only where compatible. No mutable
  DCB exposure or public attribute changes.
- Preserve unsupported wrappers as possible future conveniences, not
  currently supplied interfaces. No extra global allocations.

Evidence: [Q.1](../qsam/qsam-q1-closure-20261028.md),
[Q.2](../qsam/qsam-q2-closure-20261029.md),
[Q.3](../qsam/qsam-q3-closure-20261030.md),
[Q.4](../qsam/qsam-q4-closure-20261030.md),
[Q.5](../qsam/qsam-q5-closure-20261101.md), and
[DR.5 migration/evidence](dr2-extension-manual-migration-20261125.md).
All 17 numbered QSAM cases have accepted evidence across separate runs;
163–176 also passed installed mode. Cases 198–200 use private diagnostic
objects. True exceptional MVS CLOSE, exhaustive geometries, general
register/pointer behavior, fresh object build/readback and consolidated
current-revision regression are not inferred from these observations.

## Recommendation

Approve A, B and C as three distinct bounded transfers, including the
clarifications and retained evidence qualifications. Preserve source
READMEs' historical chronology and add links to effective reference
chapters only after approval; keep support/governance decisions and
public headers intact. No software behavior changes, fresh MVS runs,
new numbered cases, release action or march closure are proposed.
