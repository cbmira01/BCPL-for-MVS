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
5. otherwise preserves Cambridge source text and semantics.

The GET-name mapping is a host accommodation only. It does not alter header
contents or compiler semantics.

## Deterministic generation

Run from repository root with:

```sh
python3 native-compiler/bootstrap-cambridge/make-demoted.py
```

The generator asserts the expected historical section boundaries, `~=` counts,
and header-GET counts before writing anything. Unexpected source drift therefore
fails loudly rather than silently broadening the bootstrap transformation.

## First SYN compile probe

The first experiment is deliberately only `demoted/syn`. The Cambridge System/370
`LIBHDR` is exposed as DD `LIBHDR`, and Cambridge `synhdr` is exposed as DD
`SYNHDR`:

```sh
tools/compile-and-run --results --save-ocode \
    --dd LIBHDR=richards-bcpltape/sys3/bcpl/libhdr \
    --dd SYNHDR=richards-bcpltape/bcplib/bcpl/synhdr \
    "$(tools/current-icint)" \
    native-compiler/bootstrap-cambridge/demoted/syn
```

This is a probe, not yet a claim that the resulting unit is runnable by itself.
The immediate objective is to learn the first genuine MR10 compile incompatibility
after the known surface and DD-name adaptations. If compilation reaches OCODE,
that is already useful evidence; a later final RUN failure from the absence of a
complete compiler driver is not the result being tested here.

No header-content, runtime, word-size, `SKIPREC`, driver-initialization, or
compiler-semantic accommodation has yet been made.
