# Native Cambridge Compiler distribution and tape naming decisions — 8 November 2026

**Status: Owner-approved distribution design direction; not implemented or MVS release-accepted.**
These are product/package decisions, **not** a new project milestone or march.
Do not infer operational approval to submit JES, change resident datasets,
initialize tape, or publish a release.

## Release product and reconstruction boundary

The initial release target is the **native Cambridge Compiler for MVS 3.8J**,
not a distribution of the entire BCPL historical bootstrap/reconstruction
toolchain. The Git repository retains the full historical reconstruction.

The planned tape includes the ready-to-run native compiler; its complete
source, build JCL and supporting assembly; required Core Runtime and
historical Base Library (`BLIB`), including needed source and objects;
documentation, sample BCPL programs, and MVS installation/verification
materials. The compiler should be able to compile itself using the
**supplied native compiler executable**, with IFOX and IEWL to assemble
and link the result. This is a self-hosted source rebuild, **not** an
independent bootstrap from an empty MVS environment.

The MR10-kit compiler, ICINT19, the interpreter-hosted/demoted Cambridge
compiler, and developer host-side bootstrap tools are **not required
payloads** for this focused product. Optional System Extensions and
Standard Libraries do not automatically enter this initial scope;
specific inclusion and redistributability require deliberate review.
This is a prospective release definition: the native compiler's full
self-compilation and clean-target acceptance remain to be demonstrated.

## Canonical release inventory versus development inventory

- `config/dspal.yaml` describes managed **development** datasets and
  their logical names, attributes and resident locations. It is not
  the release selection or tape ordering authority.
- `packaging/distribution/manifest/` will contain **one authoritative
  release inventory** identifying only selected deliverables.
- Producer-side JCL and consumer-side restore/install JCL must be
  derived from that same release manifest. Do not independently
  maintain two lists of tape datasets or hand-enter divergent mappings.
- Each manifest entry associates the development source (preferably
  resolved from `dspal` where applicable), its tape alias and 1-based
  position, its installation destination template, the transfer method,
  dataset attributes and verification expectations. The release manifest
  also carries version, source revision, VOLSER, file order and checks.
- The producer validates the resolved input dataset and inventory
  before writing tape. The installer must have the corresponding mapping
  and instructions **on the tape**, without Git, WSL, Python or `dspal`.

## Position-based tape dataset naming — approved

Every logical tape dataset **selected for release** has a short,
systematic standard-label DSN:

    BCPL.BT0001
    BCPL.BT0002
    BCPL.BT0003
    ...

`BTnnnn` is a zero-padded **1-based logical dataset sequence number**:
`BCPL.BT0003` names the third **logical tape dataset** in that
particular release. It does **not** permanently identify a type of PDS.
Reordering a later release may reassign an alias. The manifest preserves
the semantic mapping for each release.

The alias numbering must be contiguous and unique and correspond to
MVS standard-label dataset sequence (`LABEL=(n,SL)`), not to physical
AWS/HET file numbers shown by Hercules `hetmap`. A single standard-
labeled MVS dataset spans multiple physical tape files/label groups
in `hetmap` (as demonstrated by the 8 November BTO001 test);
**physical file number 3 is not necessarily logical dataset 3**.

All aliases are comfortably below the 17-character standard HDR1
dataset-ID field length. They never contain the source or target
installation's user-specific HLQ.

### Reserved bootstrap roles

| Logical dataset sequence | Tape DSN | Intended purpose and transport |
| ---: | --- | --- |
| 1 | `BCPL.BT0001` | Initial human-readable installation instructions, sequential EBCDIC FB80 file retrievable using ordinary MVS utilities |
| 2 | `BCPL.BT0002` | MVS installation JCL and procedures, IEBCOPY sequential unload of an installation PDS |
| 3 and later | `BCPL.BTnnnn` | Manifest-selected documentation, native compiler, runtime, source, samples, tests |

`BCPL.README` and `BCPL.INSTALL` are convenient **logical content
names/roles**, not exceptions to the numbered **on-tape DSN** convention.
The complete contents and order after the reserved bootstrap datasets
remain to be specified in a real release manifest.

### Example mapping (illustrative; not yet an inventory entry)

| Role | Value |
| --- | --- |
| Sequence | `3` |
| Tape DSN | `BCPL.BT0003` |
| Development DASD | `HERC02.BCPL.DIST.DOCS` |
| Installation DASD | `{HLQ}.BCPL.DIST.DOCS` |
| Transfer | `IEBCOPY` unload/restore for PDS |

`HERC02` is an example **development** HLQ, not a distribution
dependency. The receiving MVS operator supplies an authorized
destination HLQ, e.g. `USER01`, producing
`USER01.BCPL.DIST.DOCS`. Site allocation, DASD volume, catalog
and overwrite choices must be explicit and validated. The exact
installer JCL symbolic substitution and safety policy require later
implementation and on-system verification.

Each entry must clearly distinguish the *source/restored PDS DCB*
from the **sequential IEBCOPY unload dataset DCB** on tape; these
formats differ, as the accepted BTO001 object-library test showed.

## Self-documenting tape and MVS-only installation

The *external release package* supplies a short `INSTALL.txt` and
`BOOTSTRAP.jcl` (or an equivalent printed one-page bootstrap),
plus release identification and an artifact checksum. These let
a new operator mount the tape, supply a site JOB card/device details,
and retrieve the **first tape dataset** without knowing BCPL.

The first dataset contains enough EBCDIC plain-text explanation to
identify the release, interpret the logical tape inventory, locate
subsequent installation material, and proceed on an existing MVS 3.8J
system. The tape must carry the full installation instructions, the
source/target DSN map relevant to the recipient, and verification jobs.
The initial bootstrap is **read-only**; installation changes begin
only after the operator reviews the plan and supplies site parameters.

No special tape IPL or installed BCPL environment is required.
The installation path must work with ordinary MVS batch/JES utilities;
TSO editing may be supported but cannot be mandatory. Developer-side
AWS creation may use the project host tools, but the **consumer**
must not need them.

The sequential bootstrap, multi-dataset standard-label ordering,
installer JCL, and a full clean-MVS installation have **not yet**
been demonstrated; the earlier one-dataset PDS and object-library
round trips do not establish these capabilities.

## Version and artifact lifecycle

1. **Prepare:** choose and review deliverables, freeze the source Git
   revision, assign a release candidate version, and prepare a
   release-specific manifest and documentation.
2. **Build:** generate JCL and the candidate AWS tape **from that
   frozen inventory**. Record release identity and provenance.
3. **Verify:** inspect tape labels/order, restore/install to a separate
   clean MVS environment, run the supplied compiler and self-rebuild
   tests, and capture evidence. A failed candidate is replaced by a
   new identified candidate, not silently patched.
4. **Publish:** only after acceptance and separate owner approval,
   publish the **exact tested tape bytes**, checksum, source revision
   and Git release tag. Do not rebuild a different image and present
   it as the tested release.

Release version, source commit, and tape SHA-256 are distinct identities.
The complete release must be reconstructible from authoritative Git
sources and approved MVS build dependencies, with redistribution rights
and provenance established for every included component.

## Validation and scope boundaries

Future tooling should reject missing/extra manifest entries, gaps or
duplicate tape sequence numbers/aliases, mismatches between requested
`LABEL=(n,SL)` and tape labels, unexpected members/DCBs, and
unreviewed source-to-installation mappings. It must preserve the
position-to-name correspondence for each published release.

These decisions define the **design contract**, not a committed schema,
release list, generated JCL, or authorization for live tape operations.
Detailed manifest syntax, exact installation HLQ parameterization,
overwriting/rollback policy, compiler self-hosting acceptance, and
multi-file tape mechanics remain implementation and MVS test work.
