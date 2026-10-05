# Cambridge frontend bootstrap staging

This directory is the working area for bootstrapping the surviving Cambridge
BCPL frontend through the MR10 kit compiler.

The historical sources remain untouched under:

- `richards-bcpltape/bcplib/bcpl/syn`
- `richards-bcpltape/bcplib/bcpl/trn`

## Historical structure discovered

The two tape files are containers for four Cambridge BCPL sections:

```text
bcplib/bcpl/syn
    SECTION "SYN"
    ...
    .
    SECTION "LEX"
    ...

bcplib/bcpl/trn
    SECTION "TRNA"
    ...
    .
    SECTION "TRNB"
    ...
```

The standalone `.` is significant: it terminates one source section before the
next `SECTION` begins. Therefore simply deleting the first `SECTION` line from
each historical file would be wrong; an MR10 compilation would stop at the
first `.` and never see `LEX` or `TRNB`.

## Bootstrap layout

```text
native-compiler/bootstrap-cambridge/
    README.md
    make-demoted.py
    make-icintv18.py
    options-large-tree.txt
    source/
        syn
        trn
    demotion.patch
    demoted/
        syn
        lex
        trna
        trnb
```

`source/syn` and `source/trn` are byte-identical working copies of the
historical Cambridge tape sources at the time this staging area was created.

The bootstrap derivative preserves Cambridge section granularity by splitting
the historical containers into four MR10 compilation units:

```text
historical SECTION "SYN"   -> demoted/syn
historical SECTION "LEX"   -> demoted/lex
historical SECTION "TRNA"  -> demoted/trna
historical SECTION "TRNB"  -> demoted/trnb
```

For each derivative unit the generator:

1. omits the `SECTION "..."` wrapper, which MR10 does not recognize;
2. omits the inter-section `.` delimiter because the files are now physically
   separate compilation units;
3. rewrites the Cambridge not-equal spelling `~=` as the older `NE` spelling;
4. maps historical member-style header names to MVS DD-friendly names:
   `HEADERS(SYNHDR)` -> `SYNHDR` and `HEADERS(TRNHDR)` -> `TRNHDR`;
5. for LEX only, splits the two large packed reserved-word literals into a
   sequence of shorter `D("...//")` calls so each literal fits MR10's 255-byte
   source-string limit while preserving reserved-word order and CODEP mapping;
6. otherwise preserves Cambridge source text and semantics.

The GET-name and LEX packed-string rewrites are bootstrap accommodations only.
They do not alter header contents or intended compiler semantics.

## Deterministic generation

Run from repository root with:

```sh
python3 native-compiler/bootstrap-cambridge/make-demoted.py
```

The generator asserts the expected historical section boundaries, `~=` counts,
header-GET counts, and LEX packed-word-table text before writing anything.
Unexpected source drift therefore fails loudly rather than silently broadening
the bootstrap transformation.

## SYN compile probes

The first experiment is deliberately only `demoted/syn`. The Cambridge
System/370 `LIBHDR` is exposed as DD `LIBHDR`, and Cambridge `synhdr` is exposed
as DD `SYNHDR`.

Job 881 reached Cambridge source successfully through both GET files, then the
MR10 compiler stopped with `PROGRAM TOO LARGE` near line 166. The MR10 master
driver defaults `TREESIZE` to 5500 and accepts an `OPTIONS` record `L<number>`
to raise it.

Job 882 used `L12000` with ICINT v17 and abended S0C4. The loaded compiler image
is 9,972 words, so a 12,000-word APTOVEC request cannot fit in v17's 20,001-word
PROGVEC once stack overhead is included.

Job 883 used `L8000`. That fits v17, but Cambridge SYN still exhausted the
compiler tree near line 447. This is the empirical reason to enlarge PROGVEC
rather than reduce the tree workspace further.

`make-icintv18.py` therefore generates a capacity-only candidate from v17 with:

```text
PROGCNT 20001 -> 40001
PROGLEN 80004 -> 160004 bytes
```

Job 884 exposed one additional capacity dependency in v17: the OP1 store guard
hard-codes a maximum address of `PROGWORD+20000`. With a 40,001-word PROGVEC,
that guard falsely trapped a legitimate store at D=194995 and returned -2.
Accordingly the v18 generator expands both the allocation and the matching OP1
guard:

```text
PROGCNT                 20001 -> 40001
OP1 PROGVEC upper bound 20000 -> 40000 words above PROGWORD
```

Job 885, using corrected v18 and `L12000`, successfully compiled Cambridge SYN
to nonempty OCODE. CGI converted that OCODE to an INTCODE unit whose loaded
program size was 4,040 words. The subsequent standalone RUN error is not a
compiler failure: SYN is a compiler section, not a complete BCPL START program.

This establishes the first successful Cambridge frontend-section bootstrap:

```text
Cambridge SYN source -> MR10 compiler -> OCODE -> CGI -> INTCODE
```

## LEX compile probe

Job 886 reached Cambridge LEX with v18 and `L12000` but failed first with:

```text
SYNTAX ERROR NEAR LINE 286: STRING TOO LONG
```

The source at that point is the first of two packed slash-delimited reserved-word
strings consumed by `D(WORDS)`. MR10's lexer limits a source string to 255
characters. Cambridge LEX depends on a later compiler that permits the larger
literal.

The safe bootstrap demotion is to split each packed string into several shorter
`D("...//")` calls. `CODEP` is static and advances across D calls, so the exact
reserved-word sequence and its parallel `S.*` table mapping are preserved. The
subsequent `ERROR IN COMMAND`, comment-termination, and `$)` diagnostics in job
886 are treated as parser fallout from the first overlong-string error until a
rerun proves otherwise.

The MVS step return code for an interpreted compiler failure remains zero; the
host `compile-and-run` wrapper detects the BCPL execution code afterward. Thus
CG and RUN may still execute on empty compiler output in a failed interpreted
probe. A true MVS abend propagates and flushes later steps.

No header-content, runtime, word-size, `SKIPREC`, driver-initialization, or
compiler-semantic accommodation has yet been made.
