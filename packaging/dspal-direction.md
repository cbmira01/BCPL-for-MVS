# `dspal`: Unified MVS Data-Set Tool

This note supersedes the earlier assumption that the proposed Linux-side management tool would be limited to partitioned data sets under the name `pdspal`.

The canonical tool name is now **`dspal`**, meaning "data-set pal". PDS management remains a major capability, but the tool is intended to cover multiple MVS data-set organizations through one interface.

The earlier `pdspal` design notes remain useful as design history and for PDS-specific behavior; references to `pdspal` in those notes should be read as `dspal` unless a specifically PDS-only behavior is being discussed.

## Why one tool

The project needs both:

- partitioned data sets for named source, JCL, assembler, tests, libraries, and load modules; and
- sequential data sets for large listings, reports, dumps, compiler streams, generated output, and other record-oriented artifacts that do not benefit from PDS member semantics.

Keeping separate `pdspal` and `dspal` tools would duplicate configuration, safety policy, encoding conversion, JCL generation, JES submission, condition-code handling, catalog awareness, and host/MVS transfer logic.

Therefore there should be one coherent Linux-side interface to MVS data sets.

## Core command direction

Representative commands include:

```text
dspal help
dspal help COMMAND
dspal info
dspal list
dspal stat DSN

dspal mkpds DSN
dspal mkseq DSN
dspal rmds DSN

dspal ls PDS
dspal cat PDS MEMBER
dspal put PDS MEMBER file
dspal get PDS MEMBER file
dspal rm PDS MEMBER
dspal compress PDS

dspal putseq DSN file
dspal getseq DSN file

dspal initbcpl
dspal purgebcpl
```

Exact verbs may evolve during implementation, but the architectural decision is fixed: PDS and sequential data-set handling belong in the same tool.

## Sequential data sets

Large textual output should normally be stored as a sequential data set when member-library semantics add no value.

A typical 133-column listing or report might use:

```text
DSORG=PS
RECFM=FB
LRECL=133
```

or `FBA`/`VBA` where ASA carriage-control is part of the record format.

Likely sequential-data-set uses include:

- assembler and compiler listings;
- large diagnostic reports;
- dumps;
- OCODE/intermediate streams;
- generated source or output retained for inspection;
- temporary or archival build products.

The same text-conversion and no-silent-truncation rules established for PDS transfer apply to sequential text data sets.

## PDS defaults for the BCPL layout

Most initial managed BCPL PDSes are expected to be ordinary 80-column text libraries, typically `RECFM=FB,LRECL=80`.

The managed set is currently:

```text
HERC02.BCPL.SOURCE
HERC02.BCPL.ASM
HERC02.BCPL.JCL
HERC02.BCPL.INTCODE
HERC02.BCPL.LIBRARY
HERC02.BCPL.BCPLDEMO
HERC02.BCPL.LANGDEMO
HERC02.BCPL.REGRESS
HERC02.BCPL.TEST
HERC02.BCPL.LOAD
```

The first nine are expected to be source/data libraries and therefore normally 80-column text PDSes unless a later concrete need says otherwise.

`HERC02.BCPL.LOAD` is the exception: it is a load-module library and should use load-library attributes, normally `RECFM=U`, rather than being treated as an 80-column text library.

## Reproducibility commands

The project-layout commands are now:

```text
dspal initbcpl
dspal purgebcpl
```

`initbcpl` idempotently creates the defined managed BCPL data-set layout. `purgebcpl` removes only that defined managed set and remains deliberately conspicuous and destructive.

The previously agreed safety semantics remain:

- `purgebcpl` displays the deletion set and requires confirmation for interactive use;
- `purgebcpl --yes` suppresses confirmation for automation but does not bypass safety boundaries;
- `--show-jcl` applies to both commands and emits the exact MVS job without submitting it.

## Naming transition

No compatibility burden is required at this stage because implementation has not progressed far enough for `pdspal` to be a public interface that must be preserved.

Use **`dspal`** in new code, documentation, examples, tests, and command names. `pdspal` is superseded terminology.
