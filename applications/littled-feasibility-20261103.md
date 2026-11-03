# LittleD-derived relational database for MVS 3.8J — research and discussion

**Date:** 3 November 2026  
**Status:** Exploratory research; **not** an approved milestone, port, product or implementation plan  
**Target of interest:** native Cambridge BCPL applications on IBM System/370, MVS 3.8J under Hercules/TK5  
**Historical reference:** Graeme Douglas and Ramon Lawrence, *LittleD: A SQL Database for Sensor Nodes and Embedded Applications* (ACM SAC 2014), and the [LittleD original source](https://github.com/graemedouglas/LittleD) (Apache-2.0).

## 1. Question and conclusion

Could a small SQL relational database inspired by LittleD be **implemented in native BCPL**, fit in MVS 3.8J virtual storage, use the project's BCPL character-stream and/or logical-record I/O, and eventually be accessed interactively from TSO or run as an MVS started task (STC)?

**Assessment:** A BCPL implementation of LittleD's core *design* is credible. The compact SQL lexer/parser, postfix expression evaluation, streaming iterator operators, and query-arena allocator are amenable to BCPL. Its original files and C pointer representations should **not** be copied indiscriminately. SQL input is easy with BCPLIO; persistent relational storage, random access, dataset lifecycle, concurrency and inter-address-space communications require new design or facilities. No native BCPL version, compiled port, SQL tests, STC, TSO interface or MVS verification has been demonstrated.

This is a research conclusion, not a compatibility promise.

## 2. What LittleD is

LittleD is a small relational SQL system created for microcontrollers and sensor nodes with very small RAM budgets. It is **not** SQLite: it is a restricted SQL implementation, built around a handwritten lexer and parser, an iterator-based relational operator tree, compact expressions, and an abstraction for persistent storage. The paper describes a direct-to-executable-plan parsing approach and query processing within approximately 1 KB of RAM for the benchmark queries; its roughly 55 KB compiled footprint on a Zolertia Z1 test platform includes benchmark support. **These are original-platform figures, not total MVS memory requirements or an MVS executable size.**

The source is organized into `src/dbparser/`, `src/dbops/`, `src/dblogic/`, `src/dbobjects/`, `src/dbmm/`, `src/dbstorage/`, `src/dbindex/`, `src/dboutput/` and tests. `db_ctconf.h` exposes platform and feature switches.

Its Apache-2.0 licensing permits a new project implementation under its terms, with appropriate copyright/license/notice handling if source is actually reused. Designing a new BCPL engine based on published algorithms is distinct from translating or copying its licensed source.

## 3. Native BCPL architecture

Suggested boundaries, **not yet accepted**:

1. **SQL input / shell:** accumulate EBCDIC characters until a semicolon, return diagnostic/result text through an appropriate character-stream interface.
2. **Lexer/parser:** recognize the deliberately small SQL subset; construct a compact executable operator representation directly, as in LittleD.
3. **Expression evaluator:** bytecode or postfix instruction stream for arithmetic, comparison and Boolean predicates.
4. **Iterator executor:** SCAN, SELECT (filter), PROJECT, nested-loop JOIN; avoid fully materializing large result sets where possible.
5. **Query memory arena:** BCPL-owned vectors with explicit word/byte arithmetic, offsets, bounds checks and lifetime rules, inspired by LittleD's two-ended allocator.
6. **Database storage API:** abstract record scanning, row append, schema reads, optional positioning, open/close, creation, and future keyed access. Keep storage independent of SQL execution.
7. **Host front ends:** batch, TSO foreground, or eventually an STC with an explicit request/response protocol.

BCPL's 32-bit word and byte primitives can represent the required structures, including packed tuples, null bitmaps, small operation codes, and signed integer values. On MVS, prefer explicit serialized formats instead of C `struct` layouts, architecture-dependent pointer sizes, or host-endian implicit data.

## 4. SQL repertoire — verified source observations versus untested claims

Source examination identified active parser dispatch for SELECT, FROM, WHERE, CREATE and INSERT, plus SCAN/SELECT/PROJECT and join operator implementations. The parser handles ordinary inner-join syntax and multiple FROM tables; the research paper demonstrates nested-loop joins, calculated projections and combined comparison/Boolean predicates. `src/dbparser/dbcreate.c` implements a restricted `CREATE TABLE`; `dbinsert.c` implements `INSERT` with one `VALUES` tuple, optionally using an explicit column list. The implementation's parser and lexer should be tested against a formal fixture set before claiming all dialect details.

| SQL feature | Evidence/qualification |
| --- | --- |
| `CREATE TABLE`, `INT`, `STRING(n)` | Implemented in `dbcreate.c` |
| `INSERT ... VALUES (...)` | Implemented in `dbinsert.c`; single tuple per statement |
| Explicit INSERT column list | Source code handles a column-list form; needs regression tests |
| `SELECT`, `FROM`, `WHERE`, projection | Parser and operator implementations |
| Arithmetic/comparison/Boolean expressions | Code and original paper; verify precise operators/precedence with tests |
| Inner / comma joins | Code and original paper; exact syntax variants need test |
| Indexed lookup | `src/dbindex/dbindex.c` implements an inline sorted lookup using seek/binary search; this is not a general B-tree |
| `ORDER BY` | Lexer and sort operator exist but default feature flag is off; not claimed working |
| `GROUP BY`, `HAVING`, aggregates | Experimental source exists; aggregation default flag is off, parser integration incomplete/unverified |
| `UPDATE`, `DELETE`, `DROP`, `ALTER`, subqueries, `UNION`, `LIMIT` | Not established as implemented; do not promise |
| ACID transactions, journal, rollback, multiuser locking | No general implementation identified |

`src/db_ctconf.h` defaults to `DB_CTCONF_SETTING_FEATURE_AGGREGATION=0` and `DB_CTCONF_SETTING_FEATURE_SORT=0`. Lexing a keyword, or having a named operator file, does **not** prove the SQL statement is implemented.

### Illustrative, not executed, SQL

```sql
CREATE TABLE EMPLOYEE (EMPID INT, NAME STRING(30), DEPT INT, SALARY INT);
CREATE TABLE DEPARTMENT (DEPT INT, NAME STRING(30));
INSERT INTO EMPLOYEE VALUES (1001, 'SMITH', 10, 52000);
INSERT INTO EMPLOYEE VALUES (1002, 'JONES', 20, 61000);
INSERT INTO DEPARTMENT VALUES (10, 'ACCOUNTING');
INSERT INTO DEPARTMENT VALUES (20, 'ENGINEERING');
SELECT * FROM EMPLOYEE;
SELECT NAME, SALARY FROM EMPLOYEE WHERE SALARY > 55000;
SELECT NAME, SALARY * 2 FROM EMPLOYEE WHERE DEPT = 10;
SELECT E.NAME, D.NAME FROM EMPLOYEE E JOIN DEPARTMENT D ON E.DEPT = D.DEPT;
```

These are proposed representative tests for a LittleD-like dialect; **not** a record of successful stock LittleD or MVS execution. Expected unsupported functions such as UPDATE/DELETE and GROUP BY should be tested as negative cases, not documented as supported.

## 5. Data types and portability

The source declares just two principal SQL column types: platform C `int` and fixed-capacity `STRING(n)`. Internally it has explicit 8-, 16- and 32-bit integer typedefs and uses a **per-row NULL bitmap**. The standard configuration specifies `DB_CTCONF_SETTING_MAXSTRINGLENGTH=200`; its relation metadata uses many unsigned **8-bit** fields (attribute count, offsets, sizes and tuple size), imposing stricter combined-row layout limits than string length alone suggests. The original insert code serializes native `db_int` bytes directly and zero-terminates/pads fixed-size strings.

Recommended BCPL choices for discussion:
- Define SQL `INT` explicitly as signed 32-bit, independent of original C `int` variation.
- Store bytes in packed row buffers with documented field offsets; convert BCPL length-prefixed strings at the boundary.
- Preserve a separate NULL bitmap, distinguishing NULL, empty string and integer zero.
- Define EBCDIC lexical character rules and comparison/case rules; no silent ASCII conversion.
- Version the persistent schema/row format; consider 16-bit or 32-bit offsets rather than copying original 8-bit metadata.
- Specify byte order, signedness, overflow, character padding, and alignment before recording data.

A BCPL representation is feasible; **binary compatibility with LittleD's C files is not assumed**.

## 6. I/O and persistent storage

### SQL text

The established `BCPLIO` character-at-a-time stream model is enough for a local batch/interactive SQL input loop and formatted results. It does **not** by itself provide persistent random-access relational storage.

### Storage abstraction examined

`src/dbstorage/dbstorage.h` defines file-exists, open-read/write/append, read bytes, write bytes, rewind, relative seek, close and remove. The standard backend uses C file I/O; Contiki and Arduino use other adapters. `dbindex.c` uses rewind/seek and binary search. The original table file begins with schema metadata and then contains packed tuples.

### MVS design options

- **QSAM:** A potential simple implementation would map rows onto F/FB or V/VB logical records and keep schema metadata separately. `BCPLQSAM` is a sequential-record **System Extension**, not a random-access engine. Its accepted public interface has INPUT/OUTPUT but no general APPEND or dynamic allocation; reopening/repositioning cannot be presumed. Creation, append, delete and sharing require a separate design. Record-per-tuple is a *proposed new format*, not original LittleD file compatibility.
- **VSAM (e.g. KSDS/RRDS):** Potential future keyed or relative access, subject to actual MVS 3.8J service/API verification. It could replace some LittleD inline-index techniques, but requires independent native access-method integration.
- **BDAM or another direct-access facility:** Possible alternative when record positioning is required. Again, outside current BCPLQSAM scope.

Initial development can avoid index-based seeking entirely by using scans and nested-loop joins over small relations. A QSAM-only design still must resolve dataset creation, append and repeatable scans **before** claiming persistent INSERT works.

## 7. MVS storage consumption

The original research reported benchmark query-memory figures below roughly 1 KB and a platform-specific compact executable. Those values are **not** the entire database working set, and cannot be carried over literally to BCPL's 32-bit vectors.

MVS 3.8J uses System/370's 24-bit, 16 MiB virtual-address space; available private region is smaller and depends on the MVS configuration, region parameters, resident code, runtime, stack and buffers. A **provisional engineering budget** of hundreds of KiB to around 1 MiB for a basic engine is plausible, **not measured**. A port must separately measure object/load-module size, GETMAIN allocations, query arena, table metadata and active I/O buffers on real MVS.

Risk is likely greater in I/O, dataset lifecycle and concurrency than in base memory size. No benchmark, linkage or MVS memory measurement has yet been run.

## 8. Foreground TSO versus resident STC

**TSO foreground (preferred first interactive route):** Build a native BCPL SQL command program that runs in the TSO user's address space. It receives SQL from terminal services (through a verified BCPLIO adaptation or suitable native interface), queries datasets and returns formatted rows. The exact TSO terminal services and command-processor linkage must be verified under TK5/MVS 3.8J; ordinary batch SYSIN/SYSPRINT semantics should not be assumed identical.

**STC (later, separate engineering objective):** A native BCPL executable could be started through a cataloged procedure and retain table handles/caches. TSO cannot directly call procedures in that STC's private address space: a verified inter-address-space request/response transport is necessary. Concurrent sessions also require ownership, ENQ/DEQ discipline, serialization, authorization, cancellation, recovery, and resource cleanup. Original LittleD contains no ready-made MVS server, network transport, transaction manager, or concurrency protocol.

A possible *illustrative future* TSO session, not observed execution:

```
READY
BCPLSQL
SQL> SELECT NAME FROM EMPLOYEE WHERE DEPT = 10;
NAME
SMITH
1 ROW RETURNED
SQL> QUIT
READY
```

An STC is possible **architecturally**, but not an inherent capability of LittleD or the current BCPL runtime.

## 9. Integrity, persistence and operational limits

LittleD may persist table files, but no general journal, WAL, rollback or full ACID transaction facility was verified. A future MVS engine must state its guarantees precisely. Single-writer operation and sequential-only tables may be reasonable first restrictions. OPEN/WRITE/CLOSE success is not equivalent to atomic multi-statement commit or crash recovery. Protect dataset integrity with explicit recovery and failure tests before multiuser use.

Practical unknowns include schema/data naming and allocation, maximum row/table/SQL text lengths, aggregate correctness, join cost, index administration, table deletion, concurrent access, TSO command linkage and appropriate data-security controls.

## 10. Source-review risks

Important details encountered while reading original C:
- `dbcreate.c`: limited schema types, 8-bit metadata and file-based creation.
- `dbinsert.c`: one-row append, fixed-capacity text, NULL bitmap, native-integer serialization.
- `dbstorage.c`: byte-stream read/write, append and relative positioning; MVS QSAM cannot directly implement every operation.
- `dbindex.c`: assumes sorted inline indexing and seekable storage; includes FIXME comments.
- `dbparser.c` and `db_ctconf.h`: selected core clauses versus optional/incomplete sorting and aggregation.
- `dbmm/db_query_mm.c`: two-ended arena based on C pointer arithmetic; adapt its ownership model to BCPL rather than translating pointers mechanically.

Some implementation paths have assumptions and TODO/FIXME comments; this is a research prototype. Do not inherit unsafe allocation, length, index or error semantics without separate tests and review.

## 11. Suggested sequence if the owner later authorizes development

1. Obtain a reproducible source revision and compile/run original tests on a host; inventory actual accepted SQL grammar (positive *and* negative tests).
2. Capture a formal behavioral baseline for types, NULL, expressions, aliases, joins, bounds and failures.
3. Implement an **in-memory, native BCPL** table, scan/select/project and small SQL front end; compile and run it on MVS.
4. Add postfix expression evaluation and nested-loop joins, with repeatable native regression tests.
5. Decide and verify persistent storage API/format, allocation, append, scan restart and failure recovery. Do not alter `BCPLQSAM`'s accepted public contract casually.
6. Demonstrate batch execution, then verified TSO foreground execution.
7. Evaluate indexed access, UPDATE/DELETE, transactional semantics and a resident STC *only if requirements justify them*.

**No milestone, march numbering, implementation authorization, or API assignment is established by this note.**

## 12. Open design decisions

- Faithful small, append-oriented LittleD-style relational query engine versus a more general MVS DBMS?
- Original C file format compatibility versus clean MVS-native versioned row/schema formats?
- QSAM-only bounded design versus direct-access/VSAM storage?
- Data definition via preallocated DDs and schema tables versus MVS-managed allocation?
- Which tested SQL grammar is the minimum useful subset?
- Standalone TSO command first, with STC left for later?
- Degree of recovery, locking and multiuser functionality required?

## 13. Primary sources and project references

LittleD:
- [Original source repository](https://github.com/graemedouglas/LittleD).
- [Original research paper (Douglas & Lawrence, 2014)](https://cmps-people.ok.ubc.ca/rlawrenc/research/Papers/LittleD.pdf).
- [SQL parser sources](https://github.com/graemedouglas/LittleD/tree/master/src/dbparser).
- [Relational operators](https://github.com/graemedouglas/LittleD/tree/master/src/dbops).
- [Storage interface/backends](https://github.com/graemedouglas/LittleD/tree/master/src/dbstorage).
- [Index implementation](https://github.com/graemedouglas/LittleD/blob/master/src/dbindex/dbindex.c).
- [Compile-time feature flags](https://github.com/graemedouglas/LittleD/blob/master/src/db_ctconf.h).
- [Data types](https://github.com/graemedouglas/LittleD/blob/master/src/db_types.h).
- [Original unit tests](https://github.com/graemedouglas/LittleD/tree/master/src/unit_tests).

Project:
- [Runtime/library nomenclature](../packaging/architecture/runtime-and-library-nomenclature.md).
- [Repository map](../packaging/operations/repository-map.md).
- [QSAM milestone records](../packaging/milestones/qsam/).
- [General BCPL programming guide](../docs/Guide-to-BCPL-Programming-on-MVS.md).

**Evidence boundary:** This document records an architectural research discussion with selectively examined source files; no exhaustive source audit, host execution, native BCPL compile, TSO session, STC, JES job or MVS storage test was performed in support of it.
