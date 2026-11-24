# TA.8 — Initial read-only release audit — 24 November 2026 EST

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.8 — Release Audit and Controlled Publication  
**Disposition:** OPEN / IN PROGRESS; publication blocked pending disposition.  
**Audited Git HEAD:** ab27e942e8924b387d6e0bf465234474d0f17d0b  
**Frozen source:** e910de51c19c09698be139e33084a90401511cc9  
**Candidate:** BCPL-0.1.0-rc4 / BC0004 / native_compiler: absent.

## 1. Identity and inventory

Direct Git-backed audit of all four registry entries and manifest files:
SHA-256 independently computed from retrieved UTF-8 manifest bytes;
standard empty-string and abc SHA-256 test vectors passed.
All four manifest digests, candidate source revisions and VOLSER identities
match the single registry. BC0001–BC0004 are distinct. RC4 manifest digest:
72c241201a95953546923f62ea6bfb43fcf56349c5ec7618671d7802d2ee6c1a.

Direct traversal of complete frozen Git tree and frozen config/dspal.yaml
reconciles the 21 logical sequences and 150 selected PDS member entries:
8 generated installer, 125 Git-backed (all mapped paths present),
2 generated program members, 15 resident binary members. The
sequential bootstrap is not a PDS member. Selected members:

| BT | Dataset key / role | Entries |
|---|---|---:|
| 0001 | Sequential bootstrap | 0 |
| 0002 | Installer | 8 |
| 0003 | DIST_DOCS | 7 |
| 0004 | MR10_SOURCE | 5 |
| 0005 | MR10_ASM | 1 |
| 0006 | MR10_JCL | 4 |
| 0007 | MR10_LIBRARY | 9 |
| 0008 | MR10_LANGDEMO | 11 |
| 0009 | MR10_BCPLDEMO | 21 |
| 0010 | MR10_TESTS | 26 |
| 0011 | MR10_OBJ | 1 |
| 0012 | MR10_LOAD | 1 |
| 0013 | BOOT_OBJ | 10 |
| 0014 | BOOT_ASM | 9 |
| 0015 | BOOT_SOURCE | 4 |
| 0016 | BOOT_JCL | 6 |
| 0017 | EXT_OBJ | 3 |
| 0018 | EXT_ASM | 3 |
| 0019 | EXT_SOURCE | 3 |
| 0020 | EXT_MAC | 3 |
| 0021 | CAMB_SOURCE | 15 |
| | Total | 150 |

The Git path check establishes mapping/existence, not actual tape member
byte equivalence or rights clearance. RC4 source payload BT0003–BT0021 is
inherited from RC3; BT0001/BT0002 are generated separately by the RC4
installer producer. Preserve both provenance layers, not just the frozen
program-source SHA.

The recorded AWS checksum is
7cc5a1d61882bf88469fd9f9e38512f1976ef1a775e3095e12e3988600c57af1.
The accepted production and installation/functional results are consistent
with the inventory (21 logical datasets, 64 physical files; TA.7 42 PDSes,
315 restored member entries and 80/80 cases). See formal TA.2, TA.3,
TA.4, TA.5 and TA.7 closure records. TA.6 N/A. No demonstrated new
execution/restore defect, no need to rerun accepted jobs. The private
AWS bytes, raw MVS reports, seals and local checkout are unavailable
for direct inspection in this audit. A checksum of the actual
publication asset must be computed before delivery. Preserve the
qualified native binary lineage, clean-namespace acceptance and
recipient portability limits; do not convert them into broader claims.

## 2. Rights and provenance — unresolved publication gate

The October PUBLIC-RELEASE-AUDIT.md and THIRD-PARTY-NOTICES.md record
an owner-approved preservation-first repository policy, not a blanket
historical license. LICENSE.md covers original project work only.
RC4 manifest explicitly identifies BT0021 as
preservation-policy-approved-rights-unresolved.

Direct frozen Git blob identity check: MR10_SOURCE(SYNI,TRNI,CGI,BLIBI)
each exactly matches its respective richards-bcpltape/mr10/bcplkit
historical file. ICLIB is project-side support. ICINT19 ASM is a
reconstruction based on historical ICINT and its object/load inherit
the derivative provenance. RFACT is a historical/reconstruction
demonstration per PUBLIC-RELEASE-AUDIT.md. BOOT_SOURCE(LIBHDR)
is historical; BOOT_SOURCE(BLIB) is generated from historical BLIB,
and BOOT_OBJ(BLIB) inherits the lineage. BOOT_ASM(COROUTIN) is
generated from maintained BCPL source; BOOT_OBJ(COROUTIN) is resident
binary. Other native and extension members are project-created or
reconstructed as applicable, not collectively certified original.
BT0021 maps all 15 selected historical source members to the
frozen source tree; LIBHDR also occurs in BT0015. A keyword scan of
the 15 distinct selected historical Cambridge files and the 5
MR10 historical ICINT/INTCODE files found no explicit copyright/license/
public-domain/permission/redistribution text. Absence of a notice is
not proof of public-domain status. The scan is not a legal clearance
or full per-member authorship review.

External provenance checks, 24 November 2026:
- https://www.nordier.com/index.html explicitly describes the 1984
  archive, Ken Yap's contribution and Nordier's character corrections
  and public redistribution; no blanket license stated for that archive.
- https://www.cl.cam.ac.uk/~mr10/Archive.html presents Richards' historical
  archive for download, without explicit blanket redistribution terms.
- https://mcjones.org/softwarepreservation/BCPL/ lists Richards'
  archive and Nordier's curated distributions.
- https://www.cl.cam.ac.uk/~mr10/BCPL.html describes the present-day
  distribution's private/academic use; those terms do not establish
  a grant covering these particular 1984 files or their derivatives.

These facts strongly support archival provenance; they do not establish
unrestricted redistribution rights. Seek written clarification from
relevant rights holders (Martin Richards/Cambridge and other contributors
as appropriate), or obtain a documented applicable legal basis.
Do not equate owner willingness to publish with third-party rights.
The absence of a native compiler does not remove the historical
rights issue from MR10. No claim that redistribution is unlawful is
made; it is unresolved under the binding TA.8 gate.

## 3. Distribution documentation discrepancy

All seven BT0003 source files are identical Git blobs at frozen source
and audited HEAD. Frozen config maps them directly to
packaging/distribution/docs/*.txt. RC3 production only replaced
12 regression members and four installer members; RC4 producer
preserves BT0003–BT0021. Thus the frozen sources and recorded
production chain strongly indicate the following stale content is on
RC4; actual BT0003 member bytes have not been directly read in this
audit. Verify against saved evidence if available before claiming
byte identity.

- README: describes demoted Cambridge compiler as current working
  compiler, calls distribution notes draft, not the RC4 scope.
- INSTALL: proposed tape layout/installation JCL not final.
- DATASETS: development HLQ and BOOT.INTCODE(CAMBCOMP) references;
  says tape file order undecided.
- COMPILE: describes CAMBCOMP native-assembly workflow, not the
  included MR10 compilation and execution workflow.
- VERIFY: proposes native assembly/link/extension verification
  and says no tape restore accepted.
- RELEASE: draft, no release ID or accepted tape.
- LICENSE: explicitly incomplete MIT text and future notice obligation.

The generated BT0001 correctly states RC4/BC0004/21 SL datasets,
native Cambridge Compiler absent, MR10 execution and profile instructions.
BT0002 was accepted as actual on-tape installation JCL. The older
BT0003 prose conflicts with the release-specific documentation and
scope-disclosure requirements despite correct bootstrap content.
SNOTICE.txt is not among BT0021's 15 selected members; full MIT
and third-party notices are not separately selected by the manifest.
Do not represent these as present on tape without evidence.

Proposed resolution for owner design review: correct release-specific
documentation and complete accompanying notices; if actual BT0003
confirms stale contents, the existing requirement for accurate on-tape
documentation favors an explicitly approved successor image, fresh
identity/VOLSER and targeted acceptance of changed material plus
appropriate integrated proof. Alternatively, an explicit owner
change to the documentation gate could consider mandatory companion
errata with unchanged RC4, subject to rights clearance and adequate
notice compliance. This audit does not approve either approach,
reserve an identity, edit the frozen docs or rewrite BC0004.
No repeat of native functional testing is proposed.

## 4. Registry lifecycle and publication readiness

All registry entries remain state: reserved, including accepted RC4.
This is stale lifecycle metadata, not a tape defect. Historical
producer/reviewer code explicitly requires the reservation shape,
including state: reserved, and sometimes the exact candidate count.
Do not simply change state or add fields without checking those
contracts. Propose a compatible lifecycle extension, retaining
immutable reservation fields and historical readers, and record
accepted image/evidence identity and eventual publication status
within the single authoritative registry. Discuss implementation
before changes. Published identity should retain embedded version
0.1.0-rc4 unless a separately approved successor is produced.
GitHub release listing returned no releases; tag-list endpoint
not available in this connection, so tag absence is not established.

## 5. Disposition and next action

TA.8 remains OPEN / IN PROGRESS. Publication blocked by unresolved
historical redistribution rights and release documentation/notice
disposition; complete per-member rights and provenance assessment
and actual artifact digest/receipt audit remain incomplete.
Registry lifecycle and exact-byte delivery mechanism remain to be
implemented with owner agreement. No code, manifests, registry
reservations, tape or MVS datasets changed. No new MVS execution,
new tape production or publication authorized. The project charter
was not located as a named file in the inspected frozen tree;
the milestone, kickoff, owner decisions and canonical nomenclature
govern this initial audit.

Recommend resolving rights first, then the documentation approach,
then compatible registry and release tooling, then separate
publication authorization. Preserve all prior accepted evidence.
