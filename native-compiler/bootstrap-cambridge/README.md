# Cambridge frontend bootstrap staging

This directory is the working area for bootstrapping the surviving Cambridge
BCPL frontend through the MR10 kit compiler.

The historical sources remain untouched under:

- `richards-bcpltape/bcplib/bcpl/syn`
- `richards-bcpltape/bcplib/bcpl/trn`

## Layout

```text
native-compiler/bootstrap-cambridge/
    README.md
    source/
        syn
        trn
    demotion.patch
```

`source/syn` and `source/trn` are byte-identical working copies of the
historical Cambridge sources at the time this staging area was created.

`demotion.patch` records the first, deliberately tiny source-language
demotion required by the MR10 frontend:

1. neutralize the top-level `SECTION` directive;
2. rewrite the Cambridge not-equal spelling `~=` as the older `NE` spelling.

No header, runtime, stream, word-size, driver, or compiler-semantic changes are
part of this staging step. In particular, this step does **not** resolve
`BYTESPERWORD`, `SKIPREC`, `GET` naming, compiler initialization, or any other
runtime question.

The point of the directory is to make the lineage explicit:

```text
historical Cambridge source
        |
        | copied unchanged
        v
bootstrap-cambridge/source
        |
        | demotion.patch
        v
MR10-compilable Cambridge derivative
```

The Cambridge compiler logic is not to be simplified or rewritten merely to
make bootstrap easier. Source adaptations should remain minimal, auditable,
and removable once the Cambridge frontend is self-hosted or otherwise no
longer dependent on the MR10 source dialect.

## Current boundary

This commit only stages the sources and the first demotion patch. It does not
apply the patch and does not attempt a compile. That separation is intentional:
the directory structure and exact proposed source edits can be inspected before
the first bootstrap derivative is produced.
