# Release version and VOLSER tracking — design decisions (8 November 2026)

**Status: Owner-approved distribution design direction, documentation only.**
This records a cross-release tracking convention for the prospective native
Cambridge Compiler for MVS 3.8J. No registry schema, release, version,
VOLSER, artifact or Git tag is created or reserved by this note. No official
milestone or march changes; no MVS/JES/tape operation is authorized.

## One Git-controlled registry; two logical tracking views

Maintain a single **release registry** in the GitHub `main` source tree,
provisionally under `packaging/distribution/registry/`. It supplies:

1. **Version tracking:** every planned, candidate, rejected, accepted
   and published version; associated source commit, release manifest,
   build/acceptance evidence, publication status and Git release tag.
2. **VOLSER tracking:** every reserved or used six-character volume
   serial and its corresponding candidate image, status, release
   identity, volume ordinal (if multi-volume), and checksum.

These are two **logical views of the same registry**, not competing
registries or independently maintained authoritative lists. A
`registry/releases.yaml` file is a possible implementation, not yet an
approved schema or an existing production registry. The producer
should eventually validate/update it through reviewable, controlled
operations and reject conflicting allocations.

## Identity definitions

| Identifier | Means | Scope |
| --- | --- | --- |
| Release/version (e.g. `1.0.0-rc1`) | Product version or candidate | Release |
| Git SHA | Frozen authoritative source revision | Source tree |
| Release manifest | Exact logical tape inventory and source-to-tape-to-target mapping | One release/candidate |
| VOLSER (e.g. `BC0001`) | One tape volume, physical or virtual | Volume |
| SHA-256 | Exact bytes of the built AWS tape image | Artifact |
| Git tag | Published source/release association | Publication |

All shown values are illustrative, **not assignments**. The exact
version syntax, VOLSER allocation pattern and registry schema remain
to be specified before implementation.

A release may eventually need several tape volumes: **each volume
requires its own VOLSER**, and the registry must associate ordered
volumes with one release. The current initial architecture is
one AWS image / one VOLSER with multiple logical datasets
`BCPL.BT0001`, `BCPL.BT0002`, etc. Tape dataset names and
their positions are governed by the **per-release manifest**, not
the cross-release registry.

## Assignment and non-reuse rules

- Before constructing a release candidate, assign a version identity
  and reserve its **new, unused VOLSER** (or a set if multi-volume).
  Record the reservation in Git; validate uniqueness against *all*
  recorded active, rejected, failed and published allocations.
- **Never recycle a VOLSER after an image has been created**, even if
  the candidate is rejected or never published. Maintain historical
  entries for audit and to prevent collisions.
- Assign a **different VOLSER to each distinct new tape volume image**
  and build candidate. Rebuilding or changing the candidate produces
  a newly identified artifact, not a stealth replacement.
- An **exact byte-for-byte copy of the same artifact** keeps the
  same VOLSER and checksum. Treat coexisting copies with the same
  VOLSER cautiously: a receiving site may require unique volume
  identities for its media management. Relabeling a copy would alter
  its bytes/checksum and create a distinct artifact requiring a
  tracked identity and verification.
- Store the assigned VOLSER in the candidate's release manifest and
  its tape `VOL1` label. The producer checks they agree.
- Retain reserved, built, rejected, accepted and published states
  along with traceable evidence. Neither a reserved VOLSER nor a
  reserved version implies a finished or approved artifact.

## Version and artifact lifecycle

1. **Prepare:** review release scope, freeze source Git SHA, assign a
   version/candidate identity, reserve distinct VOLSER(s), and
   construct a release-specific manifest.
2. **Build:** generate MVS distribution materials and a **new AWS
   tape image** from the frozen inputs. Record bytes, VOLSER, label
   inventory, generated JCL provenance and SHA-256 checksum.
3. **Verify:** independently inspect label sequence, restore onto a
   clean MVS installation, test native compiler execution and
   source self-rebuild, and store acceptance evidence.
4. **Publish:** with separate owner approval, publish the **exact
   image bytes that passed acceptance** together with checksum,
   source commit, manifest and release tag. Do not quietly rebuild
   after approval.

An important versioning policy remains to be resolved: whether an
accepted release-candidate version is promoted *without changing
its embedded release identity*, or whether a final-version label
requires building and testing a distinct new artifact. In either
case **the tape's embedded identity must match the published
identity**; it is forbidden to change tape metadata after
acceptance while claiming the original checksum or testing.
The eventual registry workflow must make this explicit.

## Separation of responsibilities

- **`config/dspal.yaml`:** managed MVS development dataset definitions;
  no release version or tape order authority.
- **`packaging/distribution/manifest/`:** authoritative *one-release*
  selection, ordered `BCPL.BTnnnn` aliases, transfer methods,
  source DASD mapping, destination HLQ template, attributes and
  checks. Contains a copy/reference to the assigned version and VOLSER.
- **Proposed `packaging/distribution/registry/`:** authoritative
  *cross-release* history of version and VOLSER allocations, artifact
  lifecycle, source commits, SHA-256, acceptance and publication.
- **Producer:** validates consistency between registry, manifest,
  source inputs and actual standard tape labels before declaring a
  candidate valid.
- **Installer:** relies on tape-resident manifest and installation
  instructions; no access to the cross-release Git registry required.

## Open implementation questions

The registry schema and filename; version semantics (including candidate
versus final naming); VOLSER allocation format and race/conflict
handling; immutable artifact retention; multi-volume packaging;
publication/tag procedure; and read-only audit/validation commands
remain to be designed and tested.

**No AWS tape, managed MVS dataset, release registry data file,
real version or VOLSER assignment is created by this documentation.**

Related: [native compiler distribution design](native-cambridge-compiler-distribution-decisions-20261108.md);
[multi-dataset/append experiments](multi-dataset-tape-and-append-experiment-20261108.md).
