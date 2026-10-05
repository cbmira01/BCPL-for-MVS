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
    source/
        syn
        trn
    demotion.patch
    demoted/                 # generated derivative
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

For each derivative unit:

1. omit the `SECTION "..."` wrapper, which MR10 does not recognize;
2. omit the inter-section `.` delimiter because the files are now physically
   separate compilation units;
3. rewrite the Cambridge not-equal spelling `~=` as the older `NE` spelling;
4. otherwise preserve the Cambridge source text and semantics.

This is preferable to concatenating `SYN` with `LEX` or `TRNA` with `TRNB`.
Keeping four compilation units preserves the historical module boundaries and
avoids introducing accidental name-scope or declaration interactions during
bootstrap.

## Deterministic generation

`make-demoted.py` performs exactly that transformation from the staged source
copies.  It asserts the expected historical section boundaries and the current
number of `~=` spellings before writing anything, so unexpected source drift
fails loudly instead of silently broadening the bootstrap changes.

Run from repository root with:

```sh
python3 native-compiler/bootstrap-cambridge/make-demoted.py
```

The generated files are intentionally derivatives.  `source/` remains the
pristine checkpoint against which every bootstrap source change can be audited.

No header, runtime, stream, word-size, driver, or compiler-semantic changes are
part of this source demotion. In particular, this step does **not** resolve
`BYTESPERWORD`, `SKIPREC`, `GET` naming, compiler initialization, or any other
runtime question.

The intended lineage is:

```text
historical Cambridge tape files
        |
        | copied unchanged
        v
bootstrap-cambridge/source/{syn,trn}
        |
        | make-demoted.py
        | split by historical SECTION boundary
        | remove SECTION wrapper
        | ~= -> NE
        v
bootstrap-cambridge/demoted/{syn,lex,trna,trnb}
        |
        v
MR10 compilation units
```

The Cambridge compiler logic is not to be simplified or rewritten merely to
make bootstrap easier. Source adaptations should remain minimal, auditable,
and removable once the Cambridge frontend is no longer dependent on the MR10
source dialect.

## Current boundary

The deterministic demotion transformation is now recorded. No bootstrap compile
has yet been attempted, and no runtime/header accommodation has yet been made.
