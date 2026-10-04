# `pdspal` and MVS Packaging Storage

This note records the current design direction for managing BCPL program and data products on MVS 3.8J under TK5.

The project is now large enough that MVS-side storage should be treated as a deliberate part of the build and packaging system rather than as an incidental destination for individual JCL jobs.

The central proposal is a Linux-side command-line tool called **`pdspal`**. It will provide a small, predictable interface for creating, inspecting, populating, and maintaining MVS partitioned data sets while continuing to use normal MVS facilities underneath.

## 1. Design principles

`pdspal` should follow these rules:

1. **MVS remains authoritative.** `pdspal` should request operations through ordinary MVS programs and JCL. It should not edit CKD DASD images directly.
2. **The Linux interface should be simple.** Routine operations should resemble familiar filesystem operations without pretending that a PDS is actually a Unix directory.
3. **Generated JCL should remain visible.** Every operation should be capable of emitting the JCL it would submit. This makes `pdspal` a teaching and debugging tool as well as an automation tool.
4. **Safe defaults matter.** The normal configuration should constrain destructive operations to a configured high-level qualifier, normally the logged-on development userid.
5. **Text conversion must be explicit and lossless.** Linux text and MVS record-oriented EBCDIC data are different representations. `pdspal` must never silently truncate or otherwise damage source records.
6. **Use existing project tooling.** Submission, job identification, condition-code reporting, and report extraction should build on the project's existing `submit-jcl`, `job-summary`, and report-extraction tools where practical.
7. **Keep the first version narrow.** The first useful target is PDS management and text transfer. Synchronization, complex catalog management, and generalized DASD administration can be added later.

## 2. Intended architecture

A normal operation should look roughly like this:

```text
pdspal
   |
   +-- command/argument parser
   |
   +-- configuration and safety policy
   |
   +-- JCL generator
   |
   +-- existing JCL submission tooling
   |
   +-- existing job-summary/report tooling
   |
   +-- output parser
          |
          +-- IEHLIST / catalog inspection
          +-- IEBCOPY
          +-- IEBGENER
          +-- IEHPROGM
          +-- IDCAMS where appropriate
```

The exact utility used for an operation may change as implementation experience accumulates. The command-line contract should not depend on those internal choices.

## 3. Core command set

The following commands form the initial design.

### General

```text
pdspal help
pdspal help COMMAND
pdspal info
```

`help` describes commands, operands, defaults, safety rules, examples, and exit status.

`info` reports the active configuration, for example:

```text
MVS userid:       HERC02
default HLQ:      HERC02
default volume:   USR000
write boundary:   HERC02.**
text mode:        EBCDIC/FB/80 defaults as configured
```

Values not explicitly configured should be shown as such rather than guessed.

### PDS discovery and inspection

```text
pdspal list
pdspal ls PDS
pdspal stat PDS
pdspal stat PDS MEMBER
```

Suggested meanings:

- `list` -- list cataloged PDS data sets inside the configured namespace.
- `ls PDS` -- list members of the PDS.
- `stat PDS` -- report useful data-set attributes such as DSORG, RECFM, LRECL, BLKSIZE, volume serial, allocation, and directory information when available.
- `stat PDS MEMBER` -- report member information when MVS makes useful metadata available.

### PDS creation and deletion

```text
pdspal mkpds PDS
pdspal rmpds PDS
pdspal compress PDS
```

A simple `mkpds` should use project defaults. Overrides should be available without requiring the user to write JCL, for example:

```text
pdspal mkpds BCPL.SOURCE \
    --recfm FB \
    --lrecl 80 \
    --blksize 800 \
    --space 20,5 \
    --dir 20
```

The precise defaults should be configuration rather than hard-coded policy.

`rmpds` is destructive and should be constrained by the configured write boundary.

`compress` should perform the ordinary PDS compression operation, normally through IEBCOPY.

### Member inspection and manipulation

```text
pdspal cat PDS MEMBER
pdspal rm PDS MEMBER
pdspal cp PDS OLD NEW
pdspal mv PDS OLD NEW
pdspal copy PDS1 MEM1 PDS2 MEM2
pdspal exists PDS
pdspal exists PDS MEMBER
```

Suggested semantics:

- `cat` -- emit a member to standard output.
- `rm` -- remove a member.
- `cp` -- copy a member within a PDS.
- `mv` -- rename a member.
- `copy` -- copy a member between PDS data sets.
- `exists` -- provide a script-friendly existence test and exit status.

## 4. Moving files between Linux and MVS

The preferred verbs are **`put`** and **`get`**:

```text
pdspal put PDS MEMBER ./path/to/local/file
pdspal get PDS MEMBER ./path/to/local/file
```

These are clearer than `moveinto` and `copyout` because neither operation should imply deletion of the source.

Standard input/output should eventually be supported:

```text
cat local-file | pdspal put PDS MEMBER -
pdspal get PDS MEMBER - > local-file
```

`cat` can therefore be viewed as the convenient stdout form of `get`.

A useful comparison operation should also be provided:

```text
pdspal diff PDS MEMBER ./path/to/local/file
```

This is especially useful for source-code packaging and repeatable builds.

## 5. Text and binary transfer policy

Linux source files are normally byte streams containing ASCII or UTF-8 text separated by LF characters. Traditional MVS source libraries are record-oriented and normally contain EBCDIC text, often as fixed 80-byte records.

That distinction must remain visible in the design.

The likely interface is:

```text
pdspal put --text ...
pdspal get --text ...
pdspal put --binary ...
pdspal get --binary ...
```

Text mode may be the normal default for source libraries, but the selected behavior must be discoverable through `pdspal info` and `pdspal stat`.

Critical safety rule:

> `pdspal` must never silently truncate a source line that exceeds the target LRECL.

For example:

```text
pdspal: foo.asm: line 173 is 91 characters; HERC02.BCPL.ASM has LRECL=80
```

should be an error unless the user explicitly requests some alternative policy.

Other possible text controls include:

```text
--encoding ascii|utf-8|ebcdic
--pad
--truncate
```

`--truncate`, if it is ever implemented, should require an explicit request.

## 6. JCL as a first-class output

Every operation that would normally submit MVS work should support a mode such as:

```text
pdspal --show-jcl compress BCPL.SOURCE
pdspal --show-jcl mkpds BCPL.SOURCE
pdspal --show-jcl put BCPL.SOURCE CG370 ./cg370.b
```

In this mode `pdspal` emits the generated JCL and does not submit it.

This serves several purposes:

- teaches how MVS performs the requested operation;
- makes generated jobs auditable;
- simplifies debugging;
- permits manual submission when desired;
- prevents `pdspal` from becoming opaque middleware.

A verbose mode should also be considered:

```text
pdspal --verbose ...
```

which can identify the generated job, JES job number, utilities invoked, and final condition codes without dumping unnecessary spool output.

## 7. TK5 userid policy

The normal TK5 development identities include `HERC01` and `HERC02`.

For this project, prefer **`HERC02` for routine development** and reserve `HERC01` for work that actually requires broader system administration privileges.

The exact authorization differences are part of the TK5 installation and should not be relied upon as the primary safety boundary. `pdspal` should impose its own narrower policy even when the userid technically has permission to alter more of the system.

A recommended default configuration is therefore:

```text
userid = HERC02
hlq = HERC02
write_boundary = HERC02.**
```

With that configuration:

```text
pdspal mkpds BCPL.SOURCE
```

resolves to:

```text
HERC02.BCPL.SOURCE
```

The user should normally be able to use either the abbreviated project form or a fully qualified DSN.

Destructive commands such as `rmpds` and `rm` must reject targets outside the configured write boundary unless the user supplies a deliberately conspicuous override. An override should not be implicit merely because the logged-on MVS userid has broad authority.

Possible spelling:

```text
--unsafe
```

The exact name can be decided during implementation, but the policy should remain.

## 8. There is no Unix-style home directory

An MVS user does not naturally receive the equivalent of `/home/herc02` on DASD.

For the purposes of this project, the nearest useful analogue is the namespace:

```text
HERC02.**
```

plus whichever DASD volumes are eligible for allocation.

The dataset name and the physical disk volume are separate concepts:

```text
HERC02.BCPL.SOURCE
```

is a catalog/data-set name. The catalog records which volume contains it. Unless the allocation explicitly names a volume, installation allocation rules may choose an eligible DASD volume.

`pdspal stat` and `pdspal info` should make the physical volume visible when known.

## 9. Recommended BCPL PDS namespace

The initial development namespace should be simple and purpose-oriented.

Recommended starting set:

```text
HERC02.BCPL.SOURCE
HERC02.BCPL.ASM
HERC02.BCPL.JCL
HERC02.BCPL.INTCODE
HERC02.BCPL.LOAD
HERC02.BCPL.TEST
```

Possible later additions:

```text
HERC02.BCPL.OBJ
HERC02.BCPL.DATA
HERC02.BCPL.MACLIB
```

### Intended uses

`HERC02.BCPL.SOURCE`
: BCPL source modules intended to be consumed by the reconstructed compiler.

`HERC02.BCPL.ASM`
: System/370 assembler source, including generated assembler output from a future native BCPL code generator when appropriate.

`HERC02.BCPL.JCL`
: reusable JCL members associated with development, testing, installation, and packaging.

`HERC02.BCPL.INTCODE`
: INTCODE programs, compiler phases, tests, or other persistent interpreter inputs where a PDS representation is useful.

`HERC02.BCPL.LOAD`
: link-edited executable load modules such as ICINT and, eventually, native BCPL compiler or runtime components.

`HERC02.BCPL.TEST`
: test decks, small fixtures, expected results, or test programs that belong on the MVS side.

`HERC02.BCPL.OBJ`
: optional persistent object-module library if the build process develops a need for one. Do not create it merely because object modules exist transiently during normal builds.

`HERC02.BCPL.DATA`
: project data that does not fit the source or test libraries.

`HERC02.BCPL.MACLIB`
: project assembler macro library if and when custom macros justify a distinct library.

The set should remain small. Temporary compiler work files should normally remain temporary data sets allocated by JCL rather than becoming permanent named PDSes.

## 10. Naming rules and conventions

MVS data-set qualifiers and PDS member names have stricter naming rules than normal Linux paths. `pdspal` should validate names locally before submitting JCL.

The project should use uppercase canonical MVS names. The CLI may accept lowercase convenience input and fold it to uppercase where unambiguous.

A project-relative operand such as:

```text
BCPL.SOURCE
```

should normally expand beneath the configured HLQ:

```text
HERC02.BCPL.SOURCE
```

A fully qualified name should remain available for inspection and privileged operations but should still be checked against the write boundary before modification.

Member-name mapping from Linux filenames must be explicit. Automatic transformations that can cause collisions should not be introduced casually.

## 11. Dedicated user DASD

The stock TK5 environment uses several system and public DASD volumes. Project data can be allocated there using normal MVS allocation rules, but a dedicated user volume provides cleaner separation and better persistence discipline.

TK5 documentation describes a conventional additional 3350 volume named `USR000`, attached at address `034A`.

The broad procedure is:

1. create the CKD DASD image with Hercules `dasdinit`;
2. attach it to Hercules at an unused device address;
3. initialize it for MVS with ICKDSF;
4. set it online and mount it;
5. classify it as a private volume so ordinary allocations do not spill onto it accidentally;
6. add it to the persistent Hercules and MVS configuration;
7. optionally create a user catalog on it and define an alias for the desired HLQ.

A representative Hercules creation command from current TK5 documentation is:

```text
dasdinit -z -a /tk5/dasd.usr/usr000.34a 3350 USR000
```

The exact container path must match this project's TK5 layout. In this repository's container arrangement, user DASD is intentionally kept under the separately persisted `mvs-state/dasd.usr` host area and mounted into TK5's `dasd.usr` area.

After the device is attached, ICKDSF is used to initialize the MVS volume and create its VTOC. A private mount is desirable because it means new data sets are placed on the volume only when allocation explicitly requests `VOL=SER=USR000` or equivalent policy chooses it.

For automatic availability after later IPLs, both sides must know about the device:

- Hercules configuration must attach the CKD image at the selected address.
- MVS `SYS1.PARMLIB(VATLST00)` should describe the volume so that it is mounted with the intended use class.

### User catalog

A dedicated user DASD is a natural place for a user catalog.

The preferred conceptual arrangement is:

```text
Master catalog
    |
    +-- alias HERC02 -> user catalog on USR000
                         |
                         +-- HERC02.BCPL.SOURCE
                         +-- HERC02.BCPL.ASM
                         +-- HERC02.BCPL.JCL
                         +-- HERC02.BCPL.INTCODE
                         +-- HERC02.BCPL.LOAD
                         +-- HERC02.BCPL.TEST
```

The TK5 procedure uses IDCAMS `DEFINE USERCATALOG` followed by `DEFINE ALIAS` to connect an HLQ to that user catalog.

Do not casually alter an existing catalog structure merely to satisfy `pdspal`. Initial `pdspal` development can use the existing catalog and ordinary allocation. A dedicated catalog and volume are deployment improvements, not prerequisites for the CLI.

## 12. Suggested volume policy

The long-term BCPL development arrangement should preferably be:

```text
Linux repository
      |
      | pdspal put/get
      v
HERC02.BCPL.**
      |
      v
USR000
```

Advantages include:

- project data is physically separated from the stock TK5 system volumes;
- backup of the BCPL MVS-side development state can focus on one CKD image;
- system reinstalls are less likely to disturb development data;
- the namespace and the physical storage policy reinforce one another;
- `pdspal info` can clearly report the expected project volume.

However, `pdspal` should not assume that every PDS resides on `USR000`. The catalog and VTOC remain authoritative.

## 13. PDS versus temporary data

Permanent PDSes should be used for things with library semantics: named source members, assembler sources, JCL, tests, macros, and load modules.

Do not turn every intermediate stream into a member library.

A likely future native compiler flow remains:

```text
HERC02.BCPL.SOURCE(PROGRAM)
          |
          v
     SYN / TRN
          |
          v
 temporary OCODE data set
          |
          v
        CG370
          |
          v
 temporary or requested assembler source
          |
          v
         IFOX
          |
          v
 temporary object module
          |
          v
 linkage editor
          |
          v
HERC02.BCPL.LOAD(PROGRAM)
```

Intermediate products should become persistent only where there is a debugging, packaging, or reproducibility reason to keep them.

## 14. Future commands deliberately deferred

Directory synchronization is attractive:

```text
pdspal syncinto PDS ./directory
pdspal syncout PDS ./directory
```

but should not be part of the first implementation.

It requires policy for:

- filename-to-member-name conversion;
- collisions after MVS name folding/truncation;
- deletion semantics;
- timestamps, which do not map cleanly to ordinary PDS members;
- text versus binary members;
- record format differences;
- source-of-truth conflicts.

Implement reliable single-member `put`, `get`, `diff`, and `exists` first.

Other possible future operations include:

```text
pdspal rename-pds OLD NEW
pdspal copy-pds OLD NEW
pdspal alloc-report ...
pdspal catalog ...
pdspal uncatalog ...
```

These should be added only when the project has a concrete need.

## 15. Exit-status discipline

Because `pdspal` is intended for both people and scripts, exit status should be stable.

At minimum distinguish:

- success;
- object not found;
- validation error;
- operation refused by safety policy;
- MVS job submitted but ended with nonzero condition code or abend;
- communication/submission failure;
- transfer/conversion failure.

Human-readable diagnostics should go to stderr. Commands such as `cat` and `get ... -` must keep stdout clean for data.

## 16. Initial implementation priority

A reasonable order is:

1. `help`, `info`, configuration loading, and DSN/member validation;
2. `--show-jcl` infrastructure;
3. `ls`, `stat`, and `exists`;
4. `mkpds`, `rmpds`, `compress`;
5. `cat`/`get`;
6. `put` with strict text-record validation;
7. `rm`, `cp`, `mv`, and cross-PDS `copy`;
8. `diff`;
9. only then consider synchronization or catalog administration.

This sequence makes read-only inspection available early and exercises generated-JCL transparency before destructive operations become convenient.

## 17. References

Useful primary or near-primary references for implementation work include:

- IBM, *OS/VS2 MVS Utilities*, Release 3.8 -- behavior of utilities such as IEBCOPY, IEBGENER, IEHLIST, and IEHPROGM.
- TK5 documentation and configuration examples for adding a user DASD, initializing it with ICKDSF, mounting it as private, and defining a user catalog and HLQ alias.
- Hercules documentation for CKD DASD image creation and device attachment.

The current public TK5 container documentation used while preparing this note is:

```text
https://github.com/patrickraths/MVS-TK5
```

Treat exact device addresses and host/container paths as installation-specific. The policy and sequence matter more than copying a sample path literally.

## 18. Current project policy summary

For now:

- use `HERC02` for ordinary BCPL development;
- keep normal writable names beneath `HERC02.**`;
- use `HERC02.BCPL.*` for persistent BCPL development libraries;
- prefer PDS libraries for named program artifacts and temporary sequential data sets for transient compiler streams;
- make `pdspal` a Linux-side JCL-generating front end, not a CKD editor;
- provide `help`, `info`, `--show-jcl`, `put`, and `get` as first-class concepts;
- validate record lengths and encoding conversions rather than silently losing information;
- eventually place BCPL user data on a dedicated private DASD such as `USR000`, preferably with an appropriate user catalog/HLQ alias;
- keep dedicated user DASD images in the project's separately persisted `dasd.usr` storage;
- let the MVS catalog and VTOC remain authoritative about where a particular data set actually resides.
