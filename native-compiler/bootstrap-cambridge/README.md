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

## First SYN compile probes

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

Job 881 reached Cambridge source successfully through both GET files, then the
MR10 compiler stopped with:

```text
SYNTAX ERROR NEAR LINE 166: PROGRAM TOO LARGE
```

This diagnostic is the MR10 compiler's AE-tree workspace limit, not exhaustion
of ICINT's 20,001-word PROGVEC. The MR10 master driver defaults `TREESIZE` to
5500 and accepts an `OPTIONS` record `L<number>` to raise it.

A first enlargement to `L12000` in job 882 caused the COMP step to abend S0C4
immediately after the OPTIONS record was accepted. This is consistent with the
current ICINT memory geometry rather than a Cambridge syntax failure: the
loaded compiler image is 9,972 words, so an `APTOVEC` request for 12,000 words
requires at least 21,973 PROGVEC words before normal call-stack overhead. The
current PROGVEC capacity is only 20,001 words.

The next probe therefore uses a smaller workspace that should fit while still
being substantially larger than the MR10 default:

```text
L8000
```

`options-large-tree.txt` contains that value. The controlled rerun is:

```sh
tools/compile-and-run --results --save-ocode \
    --dd OPTIONS=native-compiler/bootstrap-cambridge/options-large-tree.txt \
    --dd LIBHDR=richards-bcpltape/sys3/bcpl/libhdr \
    --dd SYNHDR=richards-bcpltape/bcplib/bcpl/synhdr \
    "$(tools/current-icint)" \
    native-compiler/bootstrap-cambridge/demoted/syn
```

With a 9,972-word loaded image, `L8000` leaves roughly 2,000 PROGVEC words above
the requested vector for call-stack and execution overhead. If Cambridge SYN
still reports `PROGRAM TOO LARGE` at this size, that will be direct evidence
that the present 20,001-word PROGVEC is too small for this bootstrap and should
then be enlarged deliberately rather than guessed at.

The MVS step return code for an interpreted compiler failure remains zero; the
host `compile-and-run` wrapper detects the BCPL execution code afterward. Thus
CG and RUN may still execute on empty compiler output in a failed interpreted
probe. A true MVS abend such as job 882's S0C4 does propagate and flushes later
steps.

This remains a probe, not yet a claim that the resulting unit is runnable by
itself. If compilation reaches OCODE, that is already useful evidence; a later
final RUN failure from the absence of a complete Cambridge compiler driver is
not the result being tested here.

No header-content, runtime, word-size, `SKIPREC`, driver-initialization, or
compiler-semantic accommodation has yet been made.
